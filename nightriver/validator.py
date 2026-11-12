"""Subscription and fixture validator for NightRiver.

Called by the Kiro hook on file-save events. Also available as:
    python -m nightriver validate
"""

import sys
import urllib.parse
from typing import Any

import feedparser

from nightriver.config import FIXTURES_DIR
from nightriver.store import load_subscriptions

VALID_SCHEMES = {"http", "https", "file"}


def _url_is_valid(url: str) -> bool:
    """Return True if url has an acceptable scheme OR is a bare non-empty path."""
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    # Explicit scheme check
    if parsed.scheme in VALID_SCHEMES:
        return True
    # Bare relative path (no scheme) — accepted by the `add` command
    if not parsed.scheme and url:
        return True
    return False


def validate_subscriptions() -> list[str]:
    """Check every URL in subscriptions.json for a valid scheme.

    Returns a list of error strings (empty = all OK).
    """
    errors: list[str] = []
    subs = load_subscriptions()
    for sub in subs:
        url = sub.get("url", "")
        if not url:
            errors.append("Subscription entry missing 'url' field.")
            continue
        if not _url_is_valid(url):
            parsed = urllib.parse.urlparse(url)
            errors.append(
                f"Invalid URL scheme {parsed.scheme!r} in subscription: {url}\n"
                f"  → Allowed schemes: {', '.join(sorted(VALID_SCHEMES))}, or a relative path"
            )
    return errors


def validate_fixtures() -> list[str]:
    """Parse every *.xml file in fixtures/.

    Returns a list of error strings (empty = all OK).
    """
    errors: list[str] = []
    if not FIXTURES_DIR.exists():
        return errors  # No fixtures directory is fine

    xml_files = sorted(FIXTURES_DIR.glob("*.xml"))
    if not xml_files:
        return errors  # No fixtures is fine

    for xml_path in xml_files:
        try:
            content = xml_path.read_bytes()
        except OSError as exc:
            errors.append(f"{xml_path.name}: Cannot read file — {exc}")
            continue

        result = feedparser.parse(content)
        if result.get("bozo"):
            exc = result.get("bozo_exception")
            detail = str(exc) if exc else "unknown parse error"
            # Try to extract line number if available
            line_info = ""
            if hasattr(exc, "lineno") and exc.lineno:
                line_info = f" (line {exc.lineno})"
            errors.append(
                f"{xml_path.name}: Invalid RSS/Atom XML{line_info} — {detail}"
            )
        elif not result.get("feed") and not result.get("entries"):
            errors.append(
                f"{xml_path.name}: Parsed without errors but contains no feed data."
            )

    return errors


def run_validation(*, verbose: bool = True) -> bool:
    """Run all validation checks.  Returns True if everything passes."""
    all_errors: list[str] = []

    sub_errors = validate_subscriptions()
    fix_errors = validate_fixtures()
    all_errors.extend(sub_errors)
    all_errors.extend(fix_errors)

    if verbose:
        subs = load_subscriptions()
        xml_files = sorted(FIXTURES_DIR.glob("*.xml")) if FIXTURES_DIR.exists() else []
        print(
            f"Validated {len(subs)} subscription(s) and "
            f"{len(xml_files)} fixture file(s)."
        )
        if all_errors:
            print(f"\n{len(all_errors)} error(s) found:", file=sys.stderr)
            for err in all_errors:
                print(f"  ✗ {err}", file=sys.stderr)
        else:
            print("  ✓ All checks passed.")

    return len(all_errors) == 0
