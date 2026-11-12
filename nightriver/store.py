"""Subscription and cache persistence for NightRiver.

All state is stored as plain JSON files under data/.
"""

import hashlib
import json
import pathlib
from typing import Any

from nightriver.config import (
    CACHE_DIR,
    MAX_ITEMS_PER_FEED,
    SUBSCRIPTIONS_FILE,
    ensure_dirs,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def feed_id(url: str) -> str:
    """Return a stable 12-char hex identifier for a feed URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def item_id(link: str, title: str) -> str:
    """Return a stable 12-char hex identifier for a feed item."""
    key = (link or "") + "|" + (title or "")
    return hashlib.sha256(key.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

def load_subscriptions() -> list[dict[str, Any]]:
    """Return the list of subscribed feeds (empty list if none yet)."""
    ensure_dirs()
    if not SUBSCRIPTIONS_FILE.exists():
        return []
    try:
        with open(SUBSCRIPTIONS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_subscriptions(subs: list[dict[str, Any]]) -> None:
    """Persist the subscription list atomically."""
    ensure_dirs()
    tmp = SUBSCRIPTIONS_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(subs, fh, indent=2, ensure_ascii=False)
    tmp.replace(SUBSCRIPTIONS_FILE)


def find_subscription(url: str) -> dict[str, Any] | None:
    """Return the subscription dict for *url*, or None if not found."""
    for sub in load_subscriptions():
        if sub.get("url") == url:
            return sub
    return None


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def _cache_path(fid: str) -> pathlib.Path:
    return CACHE_DIR / f"{fid}.json"


def load_cache(fid: str) -> dict[str, Any] | None:
    """Load cache for a given feed_id.  Returns None if not cached yet."""
    path = _cache_path(fid)
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(fid: str, data: dict[str, Any]) -> None:
    """Write cache for a feed, keeping at most MAX_ITEMS_PER_FEED items."""
    ensure_dirs()
    # Trim to limit
    items = data.get("items", [])
    data["items"] = items[:MAX_ITEMS_PER_FEED]
    tmp = _cache_path(fid).with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    tmp.replace(_cache_path(fid))


def merge_items(
    existing_items: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Merge new_items into existing_items, deduplicating by item id.

    Returns (merged_list, count_of_truly_new_items).
    """
    seen = {it["id"] for it in existing_items}
    added = 0
    result = list(existing_items)
    for item in new_items:
        if item["id"] not in seen:
            result.append(item)
            seen.add(item["id"])
            added += 1
    # Sort by published descending, keeping newest first
    result.sort(key=lambda x: x.get("published", ""), reverse=True)
    return result, added


def all_cache_entries() -> list[dict[str, Any]]:
    """Return all cache dicts for every cached feed."""
    ensure_dirs()
    entries = []
    for path in sorted(CACHE_DIR.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                entries.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            pass
    return entries
