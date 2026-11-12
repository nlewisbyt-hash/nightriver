"""Briefing generator for NightRiver.

Produces both Markdown and HTML briefings from cached feed items.
Structure and tone are governed by .kiro/steering/briefing-tone.md.
"""

import datetime
import pathlib
from typing import Any

from nightriver.store import all_cache_entries
from nightriver.summarizer import first_sentence

# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _parse_date(value: str | None) -> datetime.datetime:
    """Parse an ISO-8601 string to a datetime; return epoch on failure."""
    if not value:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    # feedparser already normalises dates to 9-tuples, but we store as strings.
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except ValueError:
            continue
    return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def _fmt_dt(value: str | None) -> str:
    dt = _parse_date(value)
    return dt.strftime("%Y-%m-%dT%H:%MZ")


# ---------------------------------------------------------------------------
# Flat item list
# ---------------------------------------------------------------------------

def _collect_items(
    entries: list[dict[str, Any]],
) -> list[tuple[datetime.datetime, dict[str, Any], str, str]]:
    """Flatten all cache entries into (dt, item, feed_title, feed_site) tuples."""
    rows = []
    for entry in entries:
        feed_title = entry.get("feed_title", "Unknown Feed")
        feed_site = entry.get("feed_site", "")
        for item in entry.get("items", []):
            dt = _parse_date(item.get("published"))
            rows.append((dt, item, feed_title, feed_site))
    return rows


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _md_header(now: datetime.datetime, mode: str, n_items: int, n_sources: int) -> str:
    return (
        f"# NightRiver Daily Briefing — {now.strftime('%Y-%m-%d')}\n\n"
        f"Generated: {now.strftime('%Y-%m-%d %H:%M')} UTC  "
        f"|  Mode: {mode}  "
        f"|  {n_items} item{'s' if n_items != 1 else ''} from "
        f"{n_sources} source{'s' if n_sources != 1 else ''}\n\n"
        "---\n\n"
    )


def _md_item(item: dict[str, Any], feed_title: str) -> str:
    title = item.get("title", "(untitled)")
    link = item.get("link", "")
    published = _fmt_dt(item.get("published"))
    summary = first_sentence(item.get("summary") or item.get("description"))

    headline = f"[{title}]({link})" if link else title
    return (
        f"## {headline}\n\n"
        f"**Source:** {feed_title}  |  **Published:** {published}\n\n"
        f"> {summary}\n\n"
    )


def _render_md_river(
    rows: list[tuple[datetime.datetime, dict[str, Any], str, str]],
    now: datetime.datetime,
) -> str:
    rows_sorted = sorted(rows, key=lambda x: x[0], reverse=True)
    n_sources = len({r[2] for r in rows_sorted})
    body = _md_header(now, "River", len(rows_sorted), n_sources)
    for _, item, feed_title, _ in rows_sorted:
        body += _md_item(item, feed_title)
    return body


def _render_md_grouped(
    rows: list[tuple[datetime.datetime, dict[str, Any], str, str]],
    now: datetime.datetime,
) -> str:
    # Group by feed title
    groups: dict[str, list[tuple[datetime.datetime, dict[str, Any], str, str]]] = {}
    for row in rows:
        groups.setdefault(row[2], []).append(row)

    n_sources = len(groups)
    n_items = len(rows)
    body = _md_header(now, "Grouped", n_items, n_sources)

    for feed_title in sorted(groups):
        group = sorted(groups[feed_title], key=lambda x: x[0], reverse=True)
        body += f"# {feed_title}\n\n"
        for _, item, ft, _ in group:
            body += _md_item(item, ft)

    return body


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _html_header(now: datetime.datetime, mode: str, n_items: int, n_sources: int) -> str:
    date_str = now.strftime("%Y-%m-%d")
    gen_str = now.strftime("%Y-%m-%d %H:%M") + " UTC"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NightRiver Daily Briefing — {date_str}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #222; background: #fafafa; }}
  h1 {{ font-size: 1.4rem; border-bottom: 2px solid #333; padding-bottom: .4rem; }}
  .meta {{ color: #555; font-size: .85rem; margin-bottom: 1.5rem; }}
  .item {{ border-left: 3px solid #ccc; padding: .6rem .9rem; margin-bottom: 1rem; background: #fff; }}
  .item h2 {{ font-size: 1rem; margin: 0 0 .3rem; }}
  .item h2 a {{ color: #0056b3; text-decoration: none; }}
  .item h2 a:hover {{ text-decoration: underline; }}
  .item .byline {{ font-size: .8rem; color: #666; margin-bottom: .4rem; }}
  .item blockquote {{ margin: .3rem 0 0; padding: 0; color: #444; font-style: italic; font-size: .9rem; }}
  .group-header {{ font-size: 1.1rem; font-weight: bold; margin: 1.5rem 0 .5rem; border-bottom: 1px solid #ddd; padding-bottom: .2rem; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 1rem 0; }}
</style>
</head>
<body>
<h1>NightRiver Daily Briefing &mdash; {date_str}</h1>
<p class="meta">Generated: {gen_str} &nbsp;|&nbsp; Mode: {_html_escape(mode)} &nbsp;|&nbsp; {n_items} item{'s' if n_items != 1 else ''} from {n_sources} source{'s' if n_sources != 1 else ''}</p>
<hr>
"""


def _html_item(item: dict[str, Any], feed_title: str) -> str:
    title = _html_escape(item.get("title", "(untitled)"))
    link = _html_escape(item.get("link", ""))
    published = _fmt_dt(item.get("published"))
    summary = _html_escape(first_sentence(item.get("summary") or item.get("description")))
    feed_title_esc = _html_escape(feed_title)

    headline = f'<a href="{link}">{title}</a>' if link else title
    return (
        f'<div class="item">\n'
        f'  <h2>{headline}</h2>\n'
        f'  <p class="byline"><strong>Source:</strong> {feed_title_esc} &nbsp;|&nbsp; '
        f'<strong>Published:</strong> {published}</p>\n'
        f'  <blockquote>{summary}</blockquote>\n'
        f'</div>\n'
    )


def _render_html_river(
    rows: list[tuple[datetime.datetime, dict[str, Any], str, str]],
    now: datetime.datetime,
) -> str:
    rows_sorted = sorted(rows, key=lambda x: x[0], reverse=True)
    n_sources = len({r[2] for r in rows_sorted})
    body = _html_header(now, "River", len(rows_sorted), n_sources)
    for _, item, feed_title, _ in rows_sorted:
        body += _html_item(item, feed_title)
    body += "\n</body>\n</html>\n"
    return body


def _render_html_grouped(
    rows: list[tuple[datetime.datetime, dict[str, Any], str, str]],
    now: datetime.datetime,
) -> str:
    groups: dict[str, list[tuple[datetime.datetime, dict[str, Any], str, str]]] = {}
    for row in rows:
        groups.setdefault(row[2], []).append(row)

    n_sources = len(groups)
    n_items = len(rows)
    body = _html_header(now, "Grouped", n_items, n_sources)

    for feed_title in sorted(groups):
        group = sorted(groups[feed_title], key=lambda x: x[0], reverse=True)
        body += f'<div class="group-header">{_html_escape(feed_title)}</div>\n'
        for _, item, ft, _ in group:
            body += _html_item(item, ft)

    body += "\n</body>\n</html>\n"
    return body


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_brief(
    mode: str = "river",
    out_path: pathlib.Path | None = None,
) -> tuple[pathlib.Path, pathlib.Path]:
    """Generate a briefing in both Markdown and HTML.

    Args:
        mode: 'river' (chronological) or 'grouped' (by source).
        out_path: Base path for output files (extensions added automatically).
                  Defaults to data/brief-YYYY-MM-DD.

    Returns:
        (md_path, html_path) — absolute paths to the generated files.

    Raises:
        ValueError if cache is empty.
    """
    from nightriver.config import DATA_DIR

    entries = all_cache_entries()
    rows = _collect_items(entries)

    if not rows:
        raise ValueError(
            "No cached items found. Run 'python -m nightriver refresh' first."
        )

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    if out_path is None:
        date_str = now.strftime("%Y-%m-%d")
        out_path = DATA_DIR / f"brief-{date_str}"
    else:
        out_path = pathlib.Path(out_path)

    md_path = out_path.with_suffix(".md")
    html_path = out_path.with_suffix(".html")

    if mode == "grouped":
        md_content = _render_md_grouped(rows, now)
        html_content = _render_html_grouped(rows, now)
    else:
        md_content = _render_md_river(rows, now)
        html_content = _render_html_river(rows, now)

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_content, encoding="utf-8")
    html_path.write_text(html_content, encoding="utf-8")

    return md_path, html_path
