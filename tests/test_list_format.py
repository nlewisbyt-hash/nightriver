"""Tests for `python -m nightriver list` table formatting.

Long file:// URLs used to overflow a typical 80-column terminal and wrap
onto column 0 mid-path. format_list_table() must keep every line within
the given width, preserve the full URL, and break at '/' when possible.
"""

from __future__ import annotations

import contextlib
import io
import os
import unittest
from unittest import mock

from nightriver.__main__ import cmd_list, format_list_table

# Realistic fixture URL from the offline demo (79 chars).
FIXTURE_URL = (
    "file:///workspace/competitions/kiroween-nightriver/app/fixtures/"
    "open-source.xml"
)

SHORT_URL = "https://example.com/feed.xml"


def _data_lines(text: str) -> list[str]:
    """Return table body lines (after the header and separator)."""
    lines = text.splitlines()
    self_sep = next(i for i, line in enumerate(lines) if set(line) <= {"-"})
    return lines[self_sep + 1 :]


def _joined_url_from_row(row_lines: list[str]) -> str:
    """Reassemble a URL from a hanging-wrapped row.

    The URL may start on the first row line (wide terminal) or on the
    following indented line (narrow terminal).
    """
    parts: list[str] = []
    started = False
    schemes = ("file://", "http://", "https://")
    for line in row_lines:
        stripped = line.strip()
        if not started:
            for scheme in schemes:
                idx = stripped.find(scheme)
                if idx != -1:
                    parts.append(stripped[idx:])
                    started = True
                    break
            continue
        parts.append(stripped)
    return "".join(parts)


class FormatListTableTests(unittest.TestCase):
    def test_short_url_stays_on_one_line(self) -> None:
        text = format_list_table(
            [(1, "Example Feed", 3, SHORT_URL)],
            width=80,
        )
        body = _data_lines(text)
        self.assertEqual(len(body), 1, text)
        self.assertTrue(body[0].endswith(SHORT_URL), body[0])
        self.assertLessEqual(len(body[0]), 80)
        self.assertIn("Example Feed", body[0])
        self.assertIn("3", body[0])

    def test_long_file_url_lines_do_not_exceed_width(self) -> None:
        text = format_list_table(
            [(1, "Open Source Release Watch", 6, FIXTURE_URL)],
            width=80,
        )
        for line in text.splitlines():
            self.assertLessEqual(len(line), 80, repr(line))

    def test_long_file_url_is_fully_preserved(self) -> None:
        text = format_list_table(
            [(1, "Open Source Release Watch", 6, FIXTURE_URL)],
            width=80,
        )
        body = _data_lines(text)
        self.assertGreater(len(body), 1, "expected the long URL to wrap")
        self.assertEqual(_joined_url_from_row(body), FIXTURE_URL)

    def test_continuation_lines_are_indented(self) -> None:
        text = format_list_table(
            [(1, "Open Source Release Watch", 6, FIXTURE_URL)],
            width=80,
        )
        body = _data_lines(text)
        self.assertGreater(len(body), 1)
        # First line starts with the row index, not a hanging indent.
        self.assertTrue(body[0].startswith("1"))
        for line in body[1:]:
            self.assertTrue(line[:1].isspace(), f"unindented wrap: {line!r}")
            self.assertTrue(line.startswith(" " * 49), f"indent misaligned: {line!r}")

    def test_prefers_breaks_at_slash(self) -> None:
        text = format_list_table(
            [(1, "Open Source Release Watch", 6, FIXTURE_URL)],
            width=80,
        )
        body = _data_lines(text)
        # The first wrap should land after a path separator, not mid-segment.
        self.assertTrue(body[0].rstrip().endswith("/"), body[0])
        self.assertNotIn("kiroween", body[0])
        self.assertIn("kiroween-nightriver", body[1])

    def test_narrow_terminal_respects_width_and_keeps_url(self) -> None:
        text = format_list_table(
            [(1, "Open Source Release Watch", 6, FIXTURE_URL)],
            width=40,
        )
        for line in text.splitlines():
            self.assertLessEqual(len(line), 40, repr(line))
        self.assertEqual(_joined_url_from_row(_data_lines(text)), FIXTURE_URL)

    def test_hard_wraps_segment_longer_than_width(self) -> None:
        url = "file:///" + ("a" * 60) + "/end.xml"
        text = format_list_table([(1, "Wide", 1, url)], width=80)
        for line in text.splitlines():
            self.assertLessEqual(len(line), 80, repr(line))
        self.assertEqual(_joined_url_from_row(_data_lines(text)), url)

    def test_header_and_separator_fit_width(self) -> None:
        text = format_list_table(
            [(1, "Example Feed", 3, SHORT_URL)],
            width=80,
        )
        lines = text.splitlines()
        self.assertGreaterEqual(len(lines), 3)
        self.assertIn("Title", lines[0])
        self.assertIn("Items", lines[0])
        self.assertIn("URL", lines[0])
        self.assertTrue(set(lines[1]) <= {"-"})
        for line in lines:
            self.assertLessEqual(len(line), 80, repr(line))

    def test_long_title_is_truncated_to_34_characters(self) -> None:
        title = "A" * 50
        text = format_list_table([(1, title, 0, SHORT_URL)], width=80)
        body = _data_lines(text)[0]
        self.assertIn("A" * 34, body)
        self.assertNotIn("A" * 35, body)

    def test_multiple_rows_each_preserve_their_url(self) -> None:
        url_b = FIXTURE_URL.replace("open-source.xml", "standards.xml")
        text = format_list_table(
            [
                (1, "Open Source Release Watch", 6, FIXTURE_URL),
                (2, "Web Standards Weekly", 6, url_b),
            ],
            width=80,
        )
        body = _data_lines(text)
        # Split rows on lines that start with a non-space (the index).
        rows: list[list[str]] = []
        for line in body:
            if line and not line[0].isspace():
                rows.append([line])
            else:
                rows[-1].append(line)
        self.assertEqual(len(rows), 2)
        self.assertEqual(_joined_url_from_row(rows[0]), FIXTURE_URL)
        self.assertEqual(_joined_url_from_row(rows[1]), url_b)


class ListCommandTests(unittest.TestCase):
    @mock.patch("nightriver.__main__.load_cache")
    @mock.patch("nightriver.__main__.load_subscriptions")
    @mock.patch("nightriver.__main__.shutil.get_terminal_size")
    def test_cmd_list_wraps_to_terminal_width(
        self,
        mock_size: mock.Mock,
        mock_subs: mock.Mock,
        mock_cache: mock.Mock,
    ) -> None:
        mock_size.return_value = os.terminal_size((80, 24))
        mock_subs.return_value = [
            {"url": FIXTURE_URL, "title": "Open Source Release Watch"}
        ]
        mock_cache.return_value = {"items": list(range(6))}

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_list()

        self.assertEqual(rc, 0)
        output = buf.getvalue()
        for line in output.splitlines():
            self.assertLessEqual(len(line), 80, repr(line))
        self.assertEqual(_joined_url_from_row(_data_lines(output)), FIXTURE_URL)
        mock_size.assert_called()

    @mock.patch("nightriver.__main__.load_subscriptions")
    def test_cmd_list_empty(self, mock_subs: mock.Mock) -> None:
        mock_subs.return_value = []
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_list()
        self.assertEqual(rc, 0)
        self.assertIn("No feeds subscribed yet.", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
