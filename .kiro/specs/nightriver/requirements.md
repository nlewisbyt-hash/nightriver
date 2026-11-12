# NightRiver — Requirements

**Product:** NightRiver (River of News / RSS)  
**Track:** Kiroween 2026 — Resurrection  
**Style:** Local-first CLI, no cloud accounts, no login, no paid services.

---

## User Stories and Acceptance Criteria

### US-01 Add a feed source

**As a** user who reads multiple RSS/Atom feeds,  
**I want to** add a feed by URL,  
**So that** NightRiver stores it and immediately shows me the feed title, site, and recent items.

**Acceptance Criteria:**
- AC-01-1: `python -m nightriver add <URL>` fetches the URL and parses it as RSS or Atom.
- AC-01-2: On success, the feed's title, site URL (link), and the five most-recent item titles are printed.
- AC-01-3: The subscription is persisted to `data/subscriptions.json`.
- AC-01-4: If the URL is a duplicate, the command reports it and exits without adding a second copy.
- AC-01-5: If the URL returns a non-2xx HTTP status, a clear error message is printed and nothing is stored.
- AC-01-6: If the URL times out (>10 s), a clear timeout error is printed.
- AC-01-7: If the response is not valid RSS/Atom, a clear parse error is printed.
- AC-01-8: Fixture (local file) URLs (`file://` paths or relative paths) are accepted for offline demos.

### US-02 List subscriptions

**As a** user,  
**I want to** see all my subscribed feeds,  
**So that** I can review what NightRiver is tracking.

**Acceptance Criteria:**
- AC-02-1: `python -m nightriver list` prints each feed's title, URL, and item count from cache.
- AC-02-2: If no feeds are subscribed, a friendly "no feeds yet" message is shown.

### US-03 Refresh feeds

**As a** user,  
**I want to** fetch the latest items from all subscribed feeds,  
**So that** my local cache is up to date.

**Acceptance Criteria:**
- AC-03-1: `python -m nightriver refresh` fetches every subscribed feed.
- AC-03-2: Successfully fetched items are merged into `data/cache/` (one JSON file per feed, keyed by feed URL).
- AC-03-3: Feeds that fail (timeout, non-2xx, parse error) are reported individually with the error reason; other feeds still refresh.
- AC-03-4: The refresh summary prints: how many feeds succeeded, how many failed, and how many new items were added.

### US-04 Generate today's briefing

**As a** user,  
**I want to** generate a local Markdown and HTML briefing from cached items,  
**So that** I can read today's news without being online.

**Acceptance Criteria:**
- AC-04-1: `python -m nightriver brief` generates both `.md` and `.html` files in `data/`.
- AC-04-2: Default output path is `data/brief-YYYY-MM-DD.md` / `.html`.
- AC-04-3: `--river` flag (default) shows all items sorted chronologically across all feeds.
- AC-04-4: `--grouped` flag shows items grouped by feed, each group sorted chronologically.
- AC-04-5: Each item shows: headline (linked), source feed name, ISO timestamp, and a one-sentence summary.
- AC-04-6: If no cached items exist, the command prints a clear warning and exits without creating empty files.
- AC-04-7: `--out PATH` overrides the output file base path (extensions `.md`/`.html` are appended automatically).
- AC-04-8: The briefing tone is neutral and informational; no engagement-bait phrases (see steering).

### US-05 Offline cache

**As a** user who is sometimes offline,  
**I want** already-fetched items to be available locally,  
**So that** I can open a briefing without network access.

**Acceptance Criteria:**
- AC-05-1: After `refresh`, items are stored in `data/cache/<feed_id>.json`.
- AC-05-2: `python -m nightriver cache` prints statistics: number of feeds cached, total items, oldest and newest item dates.
- AC-05-3: `brief` and `list` work entirely from cache; they never make network requests.

### US-06 Clear error reporting

**As a** user,  
**I want** feed errors to be reported clearly,  
**So that** I never have a silent empty river without understanding why.

**Acceptance Criteria:**
- AC-06-1: Every error includes the feed URL/title, the error type (timeout, HTTP status, parse error), and a suggested action.
- AC-06-2: Errors are written to stderr; successful output goes to stdout.
- AC-06-3: Exit code is non-zero if any feed fails during `refresh`; zero if all succeed.

### US-07 Offline demo with fixtures

**As a** developer or evaluator,  
**I want** a set of local fixture RSS/Atom XML files,  
**So that** I can demo NightRiver without network access.

**Acceptance Criteria:**
- AC-07-1: At least three fixture XML files exist under `fixtures/`.
- AC-07-2: A `fixtures/load_fixtures.sh` script (or equivalent `python -m nightriver add-fixtures`) adds all fixtures as subscriptions.
- AC-07-3: After loading fixtures and running `refresh`, `brief` produces a non-empty briefing.
- AC-07-4: Fixture files are valid RSS 2.0 or Atom 1.0.

### US-08 Validate subscriptions and fixtures

**As a** developer,  
**I want** a validation command,  
**So that** broken URLs or malformed fixture XML are caught early.

**Acceptance Criteria:**
- AC-08-1: `python -m nightriver validate` checks every URL in `data/subscriptions.json` for syntactic validity.
- AC-08-2: Fixture XML files under `fixtures/` are parsed; malformed XML is reported with a filename and line number.
- AC-08-3: Exit code is 0 if all checks pass, non-zero otherwise.
- AC-08-4: This command is called by the Kiro hook on file save events.
