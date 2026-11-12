"""NightRiver CLI — entry point for `python -m nightriver`.

Commands:
  add <URL>                  Add a feed source.
  add-fixtures               Add all fixtures/*.xml files as subscriptions.
  list                       List all subscribed feeds.
  refresh                    Fetch latest items for all feeds.
  brief [--river|--grouped] [--out PATH]
                             Generate today's briefing (Markdown + HTML).
  cache                      Show cache statistics.
  validate                   Validate subscriptions and fixture XML files.
"""

import argparse
import datetime
import sys
import urllib.parse

from nightriver import __version__
from nightriver.config import DATA_DIR, FIXTURES_DIR, ensure_dirs
from nightriver.fetcher import FetchError, fetch_feed
from nightriver.store import (
    all_cache_entries,
    feed_id,
    find_subscription,
    item_id,
    load_cache,
    load_subscriptions,
    merge_items,
    save_cache,
    save_subscriptions,
)
from nightriver.summarizer import first_sentence


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _feed_to_cache_dict(url: str, parsed: dict) -> dict:
    """Convert a feedparser result to our cache dict format."""
    feed = parsed.get("feed", {})
    feed_title = feed.get("title") or feed.get("subtitle") or url
    feed_site = feed.get("link") or ""

    items = []
    for entry in parsed.get("entries", []):
        title = entry.get("title", "(untitled)")
        link = entry.get("link", "")
        # feedparser normalises published_parsed but stores as time.struct_time
        # We prefer the string form
        published = ""
        if entry.get("published"):
            published = entry["published"]
        elif entry.get("updated"):
            published = entry["updated"]

        # Normalise published to ISO-8601 from feedparser's struct_time if needed
        pub_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if pub_parsed:
            try:
                import calendar
                ts = calendar.timegm(pub_parsed)
                published = datetime.datetime.fromtimestamp(
                    ts, tz=datetime.timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                pass

        # Summary: prefer summary field, fall back to content
        summary_raw = entry.get("summary", "")
        if not summary_raw and entry.get("content"):
            for c in entry["content"]:
                if c.get("value"):
                    summary_raw = c["value"]
                    break

        items.append(
            {
                "id": item_id(link, title),
                "title": title,
                "link": link,
                "published": published,
                "summary": first_sentence(summary_raw),
                "description": summary_raw,
            }
        )

    return {
        "feed_url": url,
        "feed_title": feed_title,
        "feed_site": feed_site,
        "fetched_at": _now_iso(),
        "items": items,
    }


def _validate_url_scheme(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme in ("http", "https", "file") or (
        not parsed.scheme and url  # bare path treated as file
    )


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

def cmd_add(url: str) -> int:
    ensure_dirs()

    if not _validate_url_scheme(url):
        print(f"Error: Unsupported URL scheme in {url!r}.", file=sys.stderr)
        print("  → Use http://, https://, file://, or a relative path.", file=sys.stderr)
        return 1

    # Duplicate check
    if find_subscription(url):
        print(f"Already subscribed to: {url}")
        return 0

    print(f"Fetching {url} …", flush=True)
    try:
        parsed = fetch_feed(url)
    except FetchError as exc:
        print(f"Error ({exc.kind}): {exc.detail}", file=sys.stderr, flush=True)
        print(f"  → {exc.suggestion()}", file=sys.stderr, flush=True)
        return 1

    feed = parsed.get("feed", {})
    feed_title = feed.get("title") or feed.get("subtitle") or url
    feed_site = feed.get("link") or ""

    # Persist subscription
    subs = load_subscriptions()
    subs.append(
        {
            "url": url,
            "title": feed_title,
            "site": feed_site,
            "added": _now_iso(),
        }
    )
    save_subscriptions(subs)

    # Persist initial cache
    fid = feed_id(url)
    cache_data = _feed_to_cache_dict(url, parsed)
    save_cache(fid, cache_data)

    # Print feed info
    print(f"\n✓ Added feed: {feed_title}")
    if feed_site:
        print(f"  Site: {feed_site}")
    print(f"  URL:  {url}")
    items = cache_data["items"]
    print(f"\n  Recent items ({min(5, len(items))} of {len(items)}):")
    for item in items[:5]:
        pub = item.get("published", "")
        pub_str = f"  [{pub}]" if pub else ""
        print(f"    • {item['title']}{pub_str}")

    return 0


# ---------------------------------------------------------------------------
# add-fixtures
# ---------------------------------------------------------------------------

def cmd_add_fixtures() -> int:
    if not FIXTURES_DIR.exists():
        print("No fixtures/ directory found.", file=sys.stderr)
        return 1

    xml_files = sorted(FIXTURES_DIR.glob("*.xml"))
    if not xml_files:
        print("No *.xml files found in fixtures/.", file=sys.stderr)
        return 1

    any_error = False
    for xml_path in xml_files:
        url = xml_path.resolve().as_uri()
        rc = cmd_add(url)
        if rc != 0:
            any_error = True

    return 1 if any_error else 0


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def cmd_list() -> int:
    subs = load_subscriptions()
    if not subs:
        print("No feeds subscribed yet.")
        print("  → Run: python -m nightriver add <URL>")
        print("  → Or:  python -m nightriver add-fixtures  (for offline demo)")
        return 0

    print(f"{'#':<3}  {'Title':<35}  {'Items':>5}  URL")
    print("-" * 80)
    for i, sub in enumerate(subs, 1):
        fid = feed_id(sub["url"])
        cached = load_cache(fid)
        n_items = len(cached["items"]) if cached else 0
        title = sub.get("title", "(unknown)")[:34]
        url = sub["url"]
        print(f"{i:<3}  {title:<35}  {n_items:>5}  {url}")

    return 0


# ---------------------------------------------------------------------------
# refresh
# ---------------------------------------------------------------------------

def cmd_refresh() -> int:
    subs = load_subscriptions()
    if not subs:
        print("No feeds to refresh. Add one first with: python -m nightriver add <URL>")
        return 0

    ok = 0
    failed = 0
    total_new = 0

    for sub in subs:
        url = sub["url"]
        title = sub.get("title", url)
        print(f"  Refreshing: {title} …", end=" ", flush=True)
        try:
            parsed = fetch_feed(url)
        except FetchError as exc:
            print(f"FAILED", flush=True)
            print(f"    ✗ {exc.kind}: {exc.detail}", file=sys.stderr)
            print(f"    → {exc.suggestion()}", file=sys.stderr)
            failed += 1
            continue

        fid = feed_id(url)
        new_data = _feed_to_cache_dict(url, parsed)
        existing = load_cache(fid)

        if existing:
            merged, n_new = merge_items(existing["items"], new_data["items"])
            new_data["items"] = merged
        else:
            n_new = len(new_data["items"])

        save_cache(fid, new_data)
        ok += 1
        total_new += n_new
        print(f"OK (+{n_new} new)")

    print(
        f"\nRefresh complete: {ok} succeeded, {failed} failed, {total_new} new item(s)."
    )

    if failed:
        print(
            f"  ✗ {failed} feed(s) failed — see errors above.",
            file=sys.stderr,
        )
        return 1
    return 0


# ---------------------------------------------------------------------------
# brief
# ---------------------------------------------------------------------------

def cmd_brief(mode: str = "river", out: str | None = None) -> int:
    import pathlib
    from nightriver.briefing import generate_brief

    out_path = pathlib.Path(out) if out else None
    try:
        md_path, html_path = generate_brief(mode=mode, out_path=out_path)
    except ValueError as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        return 1

    print(f"✓ Briefing generated ({mode} mode):")
    print(f"  Markdown: {md_path}")
    print(f"  HTML:     {html_path}")
    return 0


# ---------------------------------------------------------------------------
# cache
# ---------------------------------------------------------------------------

def cmd_cache() -> int:
    entries = all_cache_entries()
    if not entries:
        print("Cache is empty. Run: python -m nightriver refresh")
        return 0

    total_items = 0
    oldest = None
    newest = None

    for entry in entries:
        for item in entry.get("items", []):
            total_items += 1
            pub = item.get("published")
            if pub:
                if oldest is None or pub < oldest:
                    oldest = pub
                if newest is None or pub > newest:
                    newest = pub

    print(f"Cache statistics")
    print(f"  Feeds cached:  {len(entries)}")
    print(f"  Total items:   {total_items}")
    print(f"  Oldest item:   {oldest or 'unknown'}")
    print(f"  Newest item:   {newest or 'unknown'}")
    print(f"  Cache dir:     {DATA_DIR / 'cache'}")
    return 0


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def cmd_validate() -> int:
    from nightriver.validator import run_validation

    ok = run_validation(verbose=True)
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nightriver",
        description="NightRiver — local-first River of News / RSS briefing tool.",
    )
    parser.add_argument(
        "--version", action="version", version=f"NightRiver {__version__}"
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # add
    p_add = sub.add_parser("add", help="Add a feed by URL.")
    p_add.add_argument("url", metavar="URL", help="RSS or Atom feed URL.")

    # add-fixtures
    sub.add_parser(
        "add-fixtures",
        help="Add all fixtures/*.xml files as subscriptions (offline demo).",
    )

    # list
    sub.add_parser("list", help="List all subscribed feeds.")

    # refresh
    sub.add_parser("refresh", help="Fetch latest items for all subscribed feeds.")

    # brief
    p_brief = sub.add_parser(
        "brief", help="Generate today's briefing (Markdown + HTML)."
    )
    mode_group = p_brief.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--river",
        dest="mode",
        action="store_const",
        const="river",
        default="river",
        help="Chronological river view (default).",
    )
    mode_group.add_argument(
        "--grouped",
        dest="mode",
        action="store_const",
        const="grouped",
        help="Group items by source feed.",
    )
    p_brief.add_argument(
        "--out",
        metavar="PATH",
        default=None,
        help="Output file base path (.md and .html are appended).",
    )

    # cache
    sub.add_parser("cache", help="Show cache statistics.")

    # validate
    sub.add_parser(
        "validate",
        help="Validate subscriptions and fixture XML files.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0
    elif args.command == "add":
        return cmd_add(args.url)
    elif args.command == "add-fixtures":
        return cmd_add_fixtures()
    elif args.command == "list":
        return cmd_list()
    elif args.command == "refresh":
        return cmd_refresh()
    elif args.command == "brief":
        return cmd_brief(mode=args.mode, out=args.out)
    elif args.command == "cache":
        return cmd_cache()
    elif args.command == "validate":
        return cmd_validate()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
