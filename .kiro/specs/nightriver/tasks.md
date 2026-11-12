# NightRiver — Implementation Tasks

Tasks are ordered by dependency. Each task maps to one or more acceptance criteria from requirements.md.

---

## Task 01 — Project scaffold and config [DONE]
- Create `nightriver/` Python package with `__init__.py` and `__main__.py` stub.
- Create `nightriver/config.py` with all path constants.
- Create `data/`, `data/cache/`, `fixtures/` directories with `.gitkeep` files.
- Create `requirements.txt` listing `feedparser`.
- Covers: AC-07-1 (dirs exist), project structure from design.md.

## Task 02 — Subscription store [DONE]
- Implement `nightriver/store.py`:
  - `load_subscriptions()` → list of dicts
  - `save_subscriptions(subs)` → write to JSON
  - `load_cache(feed_id)` → dict or None
  - `save_cache(feed_id, data)` → write to JSON
  - `all_cache_entries()` → list of all cache dicts
  - `feed_id(url)` → sha256 hex[:12]
- Covers: AC-02-1, AC-03-2, AC-05-1, AC-05-2.

## Task 03 — Fetcher and feed parser [DONE]
- Implement `nightriver/fetcher.py`:
  - `FetchError` exception class with `url`, `kind`, `detail`.
  - `fetch_feed(url)` → feedparser result dict.
  - Handle `file://` and relative paths.
  - Handle HTTP timeout, non-2xx, DNS failure, parse error (feedparser `bozo`).
- Covers: AC-01-1, AC-01-5, AC-01-6, AC-01-7, AC-01-8, AC-06-1.

## Task 04 — Summarizer [DONE]
- Implement `nightriver/summarizer.py`:
  - `first_sentence(text)` → str
  - Strip HTML tags, split sentences, truncate at 280 chars.
- Covers: AC-04-5 (one-sentence summary).

## Task 05 — `add` command [DONE]
- Implement `add(url)` in `__main__.py`:
  - Validate URL scheme.
  - Fetch and parse feed.
  - Deduplicate.
  - Persist subscription and initial cache.
  - Print feed title, site, 5 recent items.
- Covers: AC-01-1 through AC-01-8.

## Task 06 — `list` command [DONE]
- Implement `list_feeds()` in `__main__.py`:
  - Load subscriptions; for each, load cache and count items.
  - Print title, URL, item count.
  - Handle empty list.
- Covers: AC-02-1, AC-02-2.

## Task 07 — `refresh` command [DONE]
- Implement `refresh()` in `__main__.py`:
  - Fetch all subscribed feeds.
  - Merge new items into cache (deduplicate by item id).
  - Report per-feed errors to stderr.
  - Print summary.
  - Exit 1 if any failures.
- Covers: AC-03-1 through AC-03-4, AC-06-1 through AC-06-3.

## Task 08 — `cache` command [DONE]
- Implement `cache_stats()` in `__main__.py`:
  - Count feeds, total items, oldest/newest item dates.
  - Print stats table.
- Covers: AC-05-2, AC-05-3.

## Task 09 — Briefing generator [DONE]
- Implement `nightriver/briefing.py`:
  - `generate_brief(mode, out_path)` → (md_path, html_path)
  - River mode (default): all items sorted by date desc.
  - Grouped mode: by feed, then date desc within group.
  - Both Markdown and HTML output.
  - Header: title, generated time, mode, item/source counts.
  - Per-item: linked headline, source, timestamp, one-sentence summary.
- Covers: AC-04-1 through AC-04-8.

## Task 10 — `brief` command [DONE]
- Wire `briefing.py` to `__main__.py` with `--river`/`--grouped` and `--out`.
- Covers: AC-04-1 through AC-04-8.

## Task 11 — Validator [DONE]
- Implement `nightriver/validator.py`:
  - Validate URL schemes in subscriptions.json.
  - Parse fixture XML files; report bozo errors with filename.
  - Exit 0/1 appropriately.
- Covers: AC-08-1 through AC-08-4.

## Task 12 — `validate` and `add-fixtures` commands [DONE]
- Wire `validator.py` to `__main__.py`.
- Implement `add-fixtures` subcommand to load all `fixtures/*.xml` files.
- Covers: AC-07-2, AC-08-1 through AC-08-4.

## Task 13 — Fixture RSS/Atom XML files [DONE]
- Create at least three fixture files in `fixtures/`:
  - `fixtures/tech-blog.xml` — RSS 2.0, technology topic.
  - `fixtures/open-source.xml` — Atom 1.0, open-source releases.
  - `fixtures/standards.xml` — RSS 2.0, web standards / specs.
- Covers: AC-07-1, AC-07-3, AC-07-4.

## Task 14 — Kiro steering file [DONE]
- Create `.kiro/steering/briefing-tone.md`.
- Document: neutral tone, no engagement bait, chronological river by default,
  required fields (title, time, source, link, one-sentence summary).
- Inclusion: always (auto).

## Task 15 — Kiro hook [DONE]
- Create `.kiro/hooks/validate-on-save.json`.
- Trigger: file-save on `data/subscriptions.json` and `fixtures/*.xml`.
- Action: run `python -m nightriver validate`.
- Fail clearly on non-zero exit.

## Task 16 — README [DONE]
- Write comprehensive English README.md covering all required disclosure points.
- Include: what NightRiver is, how it was created, install/usage commands,
  how Kiro was used, library disclosures, note about sibling design notes.

## Task 17 — End-to-end smoke test [DONE]
- Install feedparser.
- Load fixtures with `add-fixtures`.
- Run `refresh`.
- Run `brief`.
- Verify output files exist and are non-empty.
- Fix any failures found.
