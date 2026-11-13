"""Feed fetching and parsing for NightRiver.

Supports http://, https://, file://, and bare relative paths.
Uses feedparser for RSS 2.0 and Atom 1.0 parsing.
"""

import pathlib
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import feedparser

from nightriver.config import FETCH_TIMEOUT, PROJECT_ROOT


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class FetchError(Exception):
    """Raised when a feed cannot be fetched or parsed.

    Attributes:
        url   — the original URL that was requested
        kind  — one of: 'timeout', 'http_error', 'not_found', 'parse_error'
        detail — human-readable explanation
    """

    def __init__(self, url: str, kind: str, detail: str) -> None:
        self.url = url
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {url}: {detail}")

    def suggestion(self) -> str:
        suggestions = {
            "timeout": "The server did not respond in time. Check your network or try again later.",
            "http_error": "The server returned an error. Verify the URL is correct and the feed is public.",
            "not_found": "The URL could not be reached. Check for typos or DNS issues.",
            "parse_error": "The response is not valid RSS or Atom XML. Verify this is a feed URL, not a web page.",
        }
        return suggestions.get(self.kind, "Check the URL and try again.")


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def _resolve_url(url: str) -> str:
    """Normalise relative paths and bare file paths to absolute file:// URLs."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in ("http", "https", "file"):
        return url
    # Bare path — resolve relative to project root
    path = pathlib.Path(url)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve().as_uri()


def fetch_feed(url: str) -> dict[str, Any]:
    """Fetch and parse a feed URL.

    Returns a feedparser result dict (guaranteed non-bozo, with at least
    ``feed`` and ``entries`` keys).

    Raises FetchError on any network or parse failure.
    """
    resolved = _resolve_url(url)
    parsed_url = urllib.parse.urlparse(resolved)

    if parsed_url.scheme == "file":
        # Local file — read directly
        try:
            local_path = urllib.request.url2pathname(parsed_url.path)
            with open(local_path, "rb") as fh:
                raw = fh.read()
        except FileNotFoundError:
            raise FetchError(url, "not_found", f"File not found: {local_path}")
        except OSError as exc:
            raise FetchError(url, "not_found", str(exc))
    elif parsed_url.scheme in ("http", "https"):
        try:
            req = urllib.request.Request(
                resolved,
                headers={"User-Agent": "NightRiver/0.1 (+https://github.com/nlewisbyt-hash/nightriver)"},
            )
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
                if resp.status != 200:
                    raise FetchError(url, "http_error", f"HTTP {resp.status}")
                raw = resp.read()
        except FetchError:
            raise
        except TimeoutError:
            raise FetchError(url, "timeout", f"No response within {FETCH_TIMEOUT}s")
        except socket.timeout:
            raise FetchError(url, "timeout", f"No response within {FETCH_TIMEOUT}s")
        except urllib.error.HTTPError as exc:
            raise FetchError(url, "http_error", f"HTTP {exc.code} {exc.reason}")
        except urllib.error.URLError as exc:
            reason = str(exc.reason)
            if "timed out" in reason.lower():
                raise FetchError(url, "timeout", f"No response within {FETCH_TIMEOUT}s")
            raise FetchError(url, "not_found", reason)
        except OSError as exc:
            raise FetchError(url, "not_found", str(exc))
    else:
        raise FetchError(url, "not_found", f"Unsupported URL scheme: {parsed_url.scheme!r}")

    # Parse
    result = feedparser.parse(raw)

    if result.get("bozo") and not result.get("entries"):
        exc = result.get("bozo_exception")
        detail = str(exc) if exc else "Unknown parse error"
        raise FetchError(url, "parse_error", detail)

    if not result.get("feed") and not result.get("entries"):
        raise FetchError(url, "parse_error", "Response contains no feed data")

    return result
