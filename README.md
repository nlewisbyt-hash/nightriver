# NightRiver

**Local-first River of News / RSS briefing tool**

NightRiver subscribes to RSS and Atom feeds, caches items locally, and
generates a plain Markdown + HTML briefing. No cloud account, no login, no
paid service required. The classic "River of News" format — all sources
merged into one chronological stream — lives again, entirely on your machine.

---

## What it is

The River of News format, popularised by Dave Winer, presents items from
many feeds in reverse-chronological order rather than separating them into
per-source columns. NightRiver revives this format as a local CLI tool:

- Subscribe to any number of RSS 2.0 or Atom 1.0 feeds.
- Refresh all feeds with one command; each feed's items are cached to disk.
- Generate today's briefing as Markdown and HTML — either as a
  chronological river or grouped by source.
- Work entirely offline once feeds are cached.
- Clear, never-silent error messages when a feed fails.

---

## How this project was created

NightRiver was created using **Kiro CLI** (`kiro-cli chat`) during the
**Kiroween 2026 contest window** (submission period: 2026-10-30 to
2026-12-05).

The project was built from scratch in the directory
`/workspace/competitions/kiroween-nightriver/app/` — an empty directory
at the start of the session. No starter template or scaffolding was used.

The sibling directory `../设计说明.md` contains offline design notes written
before the contest session began. That file is **not** part of this
repository and was not created by Kiro. It served only as a reference.

The required How-you-used-Kiro write-up is in
[HOW_YOU_USED_KIRO.md](HOW_YOU_USED_KIRO.md). Judge testing steps are in
[TESTING.md](TESTING.md). A ≤3 minute demo script and verified HTML
previews are in [demo/DEMO_SCRIPT.md](demo/DEMO_SCRIPT.md).

### Contest status (verified)

- Formally Joined on Devpost as `nlewisbyt` on 2026-11-12 (Asia/Shanghai).
- Not formally Submitted.
- No public GitHub repository has been created or pushed.

---

## Installation

Python 3.13+ is required. The only third-party dependency is `feedparser`.

```bash
cd /path/to/nightriver
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

On some Linux distributions, system `pip install` is blocked (PEP 668).
A virtual environment is the reliable path. There is no other build step.

---

## Quick start: offline demo with fixtures

Three local fixture feeds are included under `fixtures/` for a fully
offline demo.

```bash
# 1. Add the fixture feeds as subscriptions
python -m nightriver add-fixtures

# 2. Refresh (loads items from local fixture files — no network needed)
python -m nightriver refresh

# 3. Generate today's briefing
python -m nightriver brief

# 4. Open the briefing
#    Markdown: data/brief-YYYY-MM-DD.md
#    HTML:     data/brief-YYYY-MM-DD.html
```

---

## Command reference

### Add a feed source

```bash
python -m nightriver add <URL>
```

Accepts `http://`, `https://`, `file://`, or a relative path to a local
XML file. Fetches the feed, prints the title and five recent items, and
stores the subscription in `data/subscriptions.json`.

**Examples:**

```bash
# Live feed
python -m nightriver add https://feeds.feedburner.com/PythonInsider

# Local fixture file (relative path)
python -m nightriver add fixtures/tech-blog.xml

# Local fixture file (file:// URI)
python -m nightriver add file:///absolute/path/to/feed.xml
```

### Add all fixture feeds (offline demo)

```bash
python -m nightriver add-fixtures
```

Loads every `fixtures/*.xml` file as a subscription. No network required.

### List subscriptions

```bash
python -m nightriver list
```

Prints each feed's title, URL, and cached item count.

### Refresh feeds

```bash
python -m nightriver refresh
```

Fetches the latest items for every subscribed feed, merges them into the
local cache, and prints a summary. Feeds that fail (timeout, HTTP error,
parse error) are reported individually on stderr; other feeds still refresh.

Exit code is non-zero if any feed fails.

### Generate a briefing

```bash
# River view (default): all items, most-recent first
python -m nightriver brief

# Grouped view: items grouped by source feed
python -m nightriver brief --grouped

# Custom output path (extensions .md and .html are appended)
python -m nightriver brief --out /tmp/my-briefing
```

Default output: `data/brief-YYYY-MM-DD.md` and `data/brief-YYYY-MM-DD.html`.

### Cache statistics

```bash
python -m nightriver cache
```

Prints: number of feeds cached, total items, oldest and newest item dates,
cache directory path.

### Validate

```bash
python -m nightriver validate
```

Checks every URL in `data/subscriptions.json` for a valid scheme, and
parses every `fixtures/*.xml` file to catch malformed XML. Exit code 0 on
success, 1 on any failure. Called automatically by the Kiro hook on file
save.

---

## Scheduling refreshes

NightRiver is a CLI tool, not a daemon. To refresh feeds periodically,
use your OS scheduler:

**cron (Linux/macOS):**
```
# Refresh every morning at 7 AM
0 7 * * * cd /path/to/nightriver/app && python -m nightriver refresh
```

**systemd timer (Linux):** Create a `.service` and `.timer` unit file.

**Task Scheduler (Windows):** Add a Basic Task with the refresh command.

---

## Optional: real public feed URLs

These feeds were working as of the contest window. Network availability is
not guaranteed and not required for the demo.

```bash
python -m nightriver add https://feeds.feedburner.com/PythonInsider
python -m nightriver add https://this-week-in-rust.org/atom.xml
python -m nightriver add https://blog.golang.org/feed.atom
python -m nightriver add https://webkit.org/feed/
```

---

## How Kiro was used

This project was built entirely within a single Kiro CLI session.

**Specs** (`.kiro/specs/nightriver/`):
- `requirements.md` — user stories and acceptance criteria for every command.
- `design.md` — architecture, module responsibilities, data schemas, error
  handling table, data flow diagrams.
- `tasks.md` — implementation tasks with status; each task maps to acceptance
  criteria. Tasks were marked done as they were implemented.

**Steering** (`.kiro/steering/briefing-tone.md`):
- Always-on (front-matter `inclusion: always`) constraint on briefing
  structure and tone.
- Specifies required header fields, per-item fields, forbidden phrases
  (engagement bait), and the default river mode.
- Kiro reads this file on every session turn and applies the constraints
  when generating or reviewing briefing code.

**Hook** (`.kiro/hooks/validate-on-save.json`):
- Schema: `version: "v1"`, trigger `PostFileSave`, with a `matcher` regex
  `(data/subscriptions\.json|fixtures/[^/]+\.xml)$` that matches only the
  subscriptions file and fixture XML files.
- Runs `python -m nightriver validate` whenever either of those paths is
  saved inside the Kiro session.
- **Important:** Kiro hooks are session-event hooks, not OS cron jobs.
  They fire on `PostFileSave` events within the Kiro IDE/CLI session. For
  periodic refreshes, use your OS scheduler (see above).

**What Kiro generated:**
All Python source files, fixture XML, the `.kiro` tree, and this README
were written by Kiro during the contest session. No pre-written code was
brought in.

---

## Third-party libraries and disclosures

| Library | Version | License | Purpose |
|---|---|---|---|
| `feedparser` | 6.0.11 | BSD-2-Clause | RSS 2.0 and Atom 1.0 parsing |

All other code uses Python 3 standard library only (`urllib`, `hashlib`,
`json`, `argparse`, `pathlib`, `datetime`, `html`, `re`).

**No starter template** or scaffolding was used. The project was created
from an empty directory.

**Fixture XML files** (`fixtures/*.xml`) are original content created for
this project. They are not copies of real feed data.

**Sibling design notes** (`../设计说明.md`) were written offline before the
contest session and are not part of this repository. They describe intent
and planning only; no code was copied from them.

---

## Project structure

```
app/
├── nightriver/
│   ├── __init__.py        # Package, version
│   ├── __main__.py        # CLI entry point (argparse)
│   ├── config.py          # Path constants, tunables
│   ├── store.py           # JSON persistence (subscriptions + cache)
│   ├── fetcher.py         # HTTP + file:// fetch, feedparser wrapper
│   ├── briefing.py        # Markdown + HTML briefing generation
│   ├── summarizer.py      # First-sentence extractor
│   └── validator.py       # URL + XML validation
├── fixtures/
│   ├── tech-blog.xml      # RSS 2.0 fixture (engineering blog)
│   ├── open-source.xml    # Atom 1.0 fixture (OSS releases)
│   └── standards.xml      # RSS 2.0 fixture (web standards)
├── data/
│   ├── subscriptions.json (created on first add)
│   └── cache/             (one .json per feed after refresh)
├── .kiro/
│   ├── specs/nightriver/
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   ├── steering/
│   │   └── briefing-tone.md   (inclusion: always)
│   └── hooks/
│       └── validate-on-save.json
├── tests/
│   └── test_list_format.py
├── requirements.txt
└── README.md
```

---

## License

NightRiver is released under the MIT License. See [LICENSE](LICENSE).
