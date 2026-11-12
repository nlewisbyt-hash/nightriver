# NightRiver — Design

## Architecture Overview

NightRiver is a pure-Python, local-first CLI tool. It has no server, no database engine, and no cloud dependency. All state lives in the `data/` directory next to the source code.

```
app/
├── nightriver/          # Python package (python -m nightriver)
│   ├── __main__.py      # CLI entry point (argparse)
│   ├── config.py        # Paths, constants
│   ├── store.py         # Subscription and cache persistence (JSON files)
│   ├── fetcher.py       # HTTP + file:// fetch, feedparser wrapper
│   ├── briefing.py      # Markdown + HTML briefing generation
│   ├── validator.py     # Subscription + fixture validation
│   └── summarizer.py    # One-sentence summary extraction
├── fixtures/            # Offline demo XML files (RSS 2.0 / Atom 1.0)
├── data/
│   ├── subscriptions.json
│   └── cache/           # <feed_id>.json per feed
├── .kiro/
│   ├── specs/nightriver/{requirements,design,tasks}.md
│   ├── steering/briefing-tone.md
│   └── hooks/validate-on-save.json
├── requirements.txt
└── README.md
```

---

## Module Design

### `config.py`
Defines all paths relative to the project root:
- `DATA_DIR`, `CACHE_DIR`, `FIXTURES_DIR`
- `SUBSCRIPTIONS_FILE`
- `FETCH_TIMEOUT` = 10 seconds
- `MAX_ITEMS_PER_FEED` = 50 (cached items per feed)

### `store.py`
Two JSON stores:

**Subscriptions** (`data/subscriptions.json`):
```json
[
  {
    "url": "https://example.com/feed.xml",
    "title": "Example Blog",
    "site": "https://example.com",
    "added": "2026-11-12T10:00:00Z"
  }
]
```

**Cache** (`data/cache/<feed_id>.json`), where `feed_id` is `sha256(url)[:12]`:
```json
{
  "feed_url": "https://example.com/feed.xml",
  "feed_title": "Example Blog",
  "feed_site": "https://example.com",
  "fetched_at": "2026-11-12T10:05:00Z",
  "items": [
    {
      "id": "sha256(link+title)[:12]",
      "title": "Some Article",
      "link": "https://example.com/some-article",
      "published": "2026-11-12T09:00:00Z",
      "summary": "One-sentence summary extracted from description."
    }
  ]
}
```

### `fetcher.py`
Fetching strategy:
1. Detect `file://` prefix → read local file directly (supports relative paths resolved from project root).
2. HTTP(S) URL → `urllib.request.urlopen` with 10 s timeout; check HTTP status; read body.
3. Pass raw bytes to `feedparser.parse()`.
4. On error, raise a typed exception: `FetchError(url, kind, detail)` where `kind` ∈ `{timeout, http_error, parse_error, not_found}`.

`feedparser` is used for parsing (declared in `requirements.txt`). No other third-party library is used.

### `briefing.py`
Briefing generation:
1. Load all cache files.
2. Flatten items into a list of `(published_dt, item, feed_title, feed_site)` tuples.
3. For `--river` mode: sort by `published_dt` descending.
4. For `--grouped` mode: group by `feed_title`, then sort each group by `published_dt` descending.
5. Render to Markdown and HTML using Python f-strings (no template engine needed).

Briefing header format (enforced by steering):
```
# NightRiver Daily Briefing — YYYY-MM-DD
Generated: YYYY-MM-DD HH:MM UTC  |  Mode: River / Grouped  |  N items from M sources
```

Each item format:
```
## [Item Title](link)
**Source:** Feed Title  |  **Published:** YYYY-MM-DDTHH:MMZ
> One-sentence summary.
```

### `summarizer.py`
Summary extraction (no LLM, pure Python):
1. Strip HTML tags from the item's description/summary field.
2. Split into sentences (split on `.`, `!`, `?` followed by whitespace or end).
3. Return the first sentence, truncated to 280 characters if needed.
4. If no description, return `"(No summary available.)"`.

### `validator.py`
Validation checks:
1. For each URL in `subscriptions.json`: check it is a valid URL (`urllib.parse.urlparse` — scheme must be `http`, `https`, or `file`).
2. For each `*.xml` file in `fixtures/`: attempt `feedparser.parse()` and check `bozo` flag; if bozo, report the exception message and line number.
3. Exit 0 on all pass, exit 1 on any failure.

---

## Data Flow

### `add` command
```
user input URL
  → validate URL scheme
  → fetch feed (fetcher.py)
  → extract feed metadata + 5 recent items
  → check duplicate in subscriptions.json
  → append to subscriptions.json
  → store initial items in cache
  → print feed title, site, item titles
```

### `refresh` command
```
load subscriptions.json
  for each feed:
    → fetch feed (fetcher.py)
    → on error: print error (stderr), continue
    → merge new items into cache/<feed_id>.json (deduplicate by item id)
    → count new items added
  → print summary: N feeds ok, M failed, K new items
  → exit 1 if any failures
```

### `brief` command
```
load all cache/*.json files
  → build flat item list (or grouped)
  → sort / group
  → render Markdown and HTML
  → write to data/brief-YYYY-MM-DD.md and .html
  → print path to files
```

---

## Error Handling

| Situation | Behavior |
|---|---|
| HTTP non-2xx | `FetchError(url, 'http_error', f'HTTP {code}')` → stderr message |
| Timeout (>10s) | `FetchError(url, 'timeout', '...')` → stderr message |
| Not-found / DNS | `FetchError(url, 'not_found', str(exc))` → stderr message |
| Invalid RSS/Atom | `FetchError(url, 'parse_error', bozo_exception)` → stderr message |
| Duplicate URL on add | Informational message → exit 0 |
| No cache for brief | Warning message → exit 1 |
| Empty subscriptions | Friendly message → exit 0 |

Errors are always explicit. The river is never silently empty.

---

## Offline Demo Strategy

Fixture files are stored in `fixtures/` as plain XML. The `add` command accepts `file://` URLs or bare paths like `fixtures/tech-blog.xml`. The `add-fixtures` subcommand loads all `fixtures/*.xml` files automatically, enabling a full offline demo.

---

## Kiro Integration

- **Steering** (`briefing-tone.md`): Always-on constraint on briefing output format and tone.
- **Hook** (`validate-on-save.json`): Fires on file-save events within the Kiro session for `data/subscriptions.json` and `fixtures/*.xml`; runs `python -m nightriver validate`; fails clearly on any error.
- **Specs**: This directory. Requirements and tasks guide the implementation and serve as evaluation evidence.

Hooks are Kiro session-event hooks (not OS cron jobs). The user should schedule `python -m nightriver refresh` via their own OS scheduler (cron, systemd timer, Task Scheduler) for periodic refresh.
