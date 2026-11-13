# How you used Kiro

This is the Kiroween 2026 required write-up for NightRiver (Resurrection track).
It describes only what actually happened during the contest submission window.
It does not invent sessions, surfaces, or features that were not used.

Official rule: “Provide a write up on how Kiro was used.”
Source: https://kiroween.devpost.com/rules

## One-sentence problem

NightRiver revives the River of News: a local-first RSS/Atom briefing that
merges many independent feeds into one chronological river, without an
algorithmic timeline or a cloud account.

## Which Kiro surfaces were used

**Kiro CLI (used to create the project).**
On 2026-11-12, Kiro CLI 3.2.1 was installed on a Debian 13 Linux machine
from the official installer (`https://cli.kiro.dev/install`). Sign-in used
AWS Builder ID over the CLI device-flow (`kiro-cli login --license free
--use-device-flow`). After sign-in, `kiro-cli whoami` reported a Builder ID
session, and `/usage` reported **KIRO FREE** with 50 plan credits (reset
2026-12-01).

The contest project was created in an empty directory,
`/workspace/competitions/kiroween-nightriver/app/`, by a non-interactive
Kiro CLI V3 session (`kiro-cli chat --v3 --no-interactive --trust-all-tools
--trust-workspace --model auto`) starting about **16:36 Asia/Shanghai,
Thursday 12 November 2026** and finishing about **16:41** the same day
(exit code 0). Kiro read a sibling offline design note
(`../设计说明.md`) as reference only, then wrote the Python package,
offline fixture feeds, README, and the `.kiro` tree (specs, steering, and
a hook). No starter template was copied in.

A second, smaller Kiro CLI V3 session the same evening (about **21:22
Asia/Shanghai**) aligned the hook file with the official current v1 hook
schema (see Hooks below). Free-plan credits were used for both sessions.
No paid Kiro plan was started.

**Kiro Web (not used to build).**
Earlier in account setup, the Kiro web app showed a subscription /
“Subscription Required” style prompt for Pro / Pro+ / Power. The Upgrade
control was not used. The project was therefore built with the Free-plan
CLI, not Kiro Web.

**Kiro IDE and Kiro Crew (not used in these sessions).**
The official Linux IDE is a GUI desktop app. These build sessions used the
CLI only. Kiro Crew was not installed or run for this project. Because only
the CLI was used in depth, this write-up cannot compare IDE / Web / Crew
behavior from first-hand use on NightRiver.

**Custom agents, MCP, property-based testing, and Kiro powers**
were not used in these sessions. That is a gap, not a hidden feature.

## Spec-driven development

Kiro wrote a feature spec under `.kiro/specs/nightriver/`:

- `requirements.md` — user stories and acceptance criteria (add source,
  list, refresh, briefing, cache, validation, errors).
- `design.md` — local-first architecture, modules, data layout, error
  handling.
- `tasks.md` — 17 implementation tasks, marked done as Kiro implemented
  them.

The first build was a single non-interactive session: Kiro was asked to do
a “Quick Spec” (write the three spec files, then implement immediately)
because there was no human at an interactive checkpoint. That is closer to
spec-then-build than to unstructured vibe coding: the CLI, data files, and
briefing format were specified before the Python modules were finished, and
the task list was used as the implementation checklist.

Compared with vibe coding, the spec made the minimum demo path explicit
(add a source, generate today’s briefing, keep `.kiro` evidence) and gave
a place to record acceptance criteria. A limitation of the non-interactive
run is that we did not stop for a human review of `requirements.md` before
design, or of `design.md` before tasks, as a fully interactive spec
workflow would.

## Agent hooks

Kiro first wrote `.kiro/hooks/validate-on-save.json` in the create session.
The intent was: when subscription or fixture files are saved in a Kiro
session, run `python -m nightriver validate` and fail clearly on invalid
URLs or broken fixture XML.

The first hook JSON used `"version": "1"` and a nested
`trigger.event: "file_save"` object with `filePatterns`. That did not
match the official current hook schema in the Kiro docs (`"version":
"v1"`, a top-level `hooks` array, PascalCase `PostFileSave`, and a
`matcher` regex). The file was **not** rewritten by hand. A second Kiro
CLI session on 2026-11-12 aligned it to the official v1 shape. The hook
now contains:

- `version`: `"v1"`
- one hook named `validate-on-save`
- `trigger`: `PostFileSave`
- `matcher`: `(data/subscriptions\\.json|fixtures/[^/]+\\.xml)$`
- `action`: `{ "type": "command", "command": "python -m nightriver validate" }`

This hook improves the development process by catching a broken fixture or
subscription as soon as the agent saves it, rather than waiting for a
later manual `validate`. It is a **session event hook**, not an operating
system cron job. Periodic feed refresh is a documented CLI command
(`python -m nightriver refresh`) that the user can schedule with cron or
an equivalent.

This was the main course-correction in the build: the first session’s hook
worked as a description of intent but was not contest-safe against the
published schema; the second session fixed the schema without changing the
product behavior.

## Steering docs

Kiro wrote `.kiro/steering/briefing-tone.md` with `inclusion: always`.
It requires a briefing header (title, UTC generation time, river or
grouped mode, item and source counts) and, for each item, a linked
headline, source name, published timestamp, and a single-sentence summary.
It forbids engagement bait (“must-read”, “click here”, and similar) and
makes chronological river the default unless `--grouped` is requested.

The briefing generator in `nightriver/briefing.py` follows that structure.
A verified river briefing from the offline fixtures
(`demo/briefing-preview-river.md`) starts with
`NightRiver Daily Briefing — 2026-11-12`, shows `Mode: River` and
`17 items from 3 sources`, and lists items with source, timestamp, and a
one-sentence summary — the steering constraints, not an algorithmic feed.

## What Kiro corrected during the first session

While implementing, Kiro ran the CLI against the fixture feeds, found a
malformed attribute in a fixture XML file, fixed it, then fixed stdout /
stderr flush order so fetch errors printed after “Fetching …” rather than
before it. It also cleaned a duplicate subscription created during
testing. Those fixes were part of the original Kiro create session, not
hand-edits made later to disguise the project.

## Disclosure of pre-existing work and libraries

- The sibling files `../README.md` and `../设计说明.md` are offline design
  notes written before the Kiro create session. They are **not** the
  contest repository and were not created by Kiro. No application code was
  copied from them.
- The only third-party library is `feedparser==6.0.11` (BSD-2-Clause),
  listed in `requirements.txt`.
- All other code uses the Python 3 standard library.
- Fixture XML under `fixtures/` is original demo content, not a dump of a
  live site.
- No starter template or scaffolding was used. The `app/` directory was
  empty when the first Kiro session began.

## Surfaces and features not used (honest gaps)

We did not use Kiro IDE, Kiro Web (for building), Kiro Crew, custom
agents, MCP, property-based testing, or Kiro powers in the sessions that
built NightRiver. Calendar or folder MCP export was an optional stretch in
the pre-Kiro design notes and was not implemented, so this write-up does
not claim it.

## Contest status (verified)

- Formally **Joined** on Devpost as `nlewisbyt` on 2026-11-12
  (Asia/Shanghai).
- **Not** formally Submitted to Devpost.
- Public repository: [`nlewisbyt-hash/nightriver`](https://github.com/nlewisbyt-hash/nightriver).
- A local demo video is in `demo/nightriver-demo.mp4`. A public YouTube
  URL will be added after upload; no YouTube link is invented here.
- The application remains a local CLI; judges can follow `TESTING.md`.
