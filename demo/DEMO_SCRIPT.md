# NightRiver demo script (≤ 3 minutes)

Kiroween 2026 requires a demonstration video under three minutes, showing
the project running on the device it was built for, in English or with
English subtitles, later uploaded to a public YouTube URL.

This file is the shot list. It uses only the offline fixture path so the
demo cannot fail on the network.

## Target device

A Linux desktop or terminal with Python 3.13+ (the environment used to
build NightRiver). No login screen.

## What to show (three required beats)

1. **Add a source** — `add-fixtures` or `add fixtures/tech-blog.xml`, then
   `list`, so titles and item counts are visible.
2. **Today’s briefing** — `refresh` then `brief`, then open the HTML
   river briefing in a browser. Optionally show `--grouped`.
3. **Open `.kiro`** — show `specs/`, `hooks/validate-on-save.json`, and
   `steering/briefing-tone.md` so the project is visibly Kiro-built.

Do not add copyrighted music. No paid tools are required. The presenter
does not need to appear on camera. Speak or subtitle in English.

## Timed script (~2 minutes 30 seconds)

| Time | Visual | Spoken / subtitle |
| --- | --- | --- |
| 0:00–0:12 | Title card: “NightRiver — a local River of News. Kiroween 2026, Resurrection.” | “NightRiver is a local-first River of News. It merges RSS and Atom feeds into one chronological briefing, with no cloud account.” |
| 0:12–0:35 | Terminal: `python -m nightriver add-fixtures` then `python -m nightriver list` | “First, add the three offline demo sources. The list shows each feed title and how many items are cached.” |
| 0:35–0:55 | Terminal: `python -m nightriver refresh` then `python -m nightriver brief` | “Refresh reads the local fixture feeds — no network. Then we generate today’s briefing as Markdown and HTML.” |
| 0:55–1:40 | Browser: `demo/briefing-preview-river.html` (or the just-generated `data/brief-*.html`). Scroll a few items. Optional cut to the grouped preview. | “This is the river: seventeen items from three sources, newest first, each with a source, a timestamp, a link, and a one-sentence summary.” |
| 1:40–2:15 | Editor or pager: `.kiro/specs/nightriver/tasks.md`, `.kiro/hooks/validate-on-save.json`, `.kiro/steering/briefing-tone.md` | “The project was created with Kiro CLI during the contest window. The repository keeps specs, a PostFileSave validation hook, and steering that constrains the briefing format.” |
| 2:15–2:30 | Closing card: repo layout reminder; “Not yet submitted.” | “NightRiver runs locally. Testing steps are in TESTING.md.” |

## Assets already produced

- Reproducible HTML/Markdown previews from a verified CLI run:
  `demo/briefing-preview-river.html` and `demo/briefing-preview-grouped.html`
- This script: `demo/DEMO_SCRIPT.md`
- A real local screen recording (1280×720, 1 minute 45 seconds, English
  burned-in subtitles, no music) of the CLI happy path and the HTML river
  briefing, made on 2026-11-12 (Asia/Shanghai):
  `demo/nightriver-demo.mp4`

The recording was captured from a virtual 1280×720 Linux display on the
same machine used to build the project, running the real CLI against the
offline fixtures and then opening the generated HTML briefing in Chrome.
It is not a YouTube URL.

## What still has to happen before formal Submit

- Review the local recording (`demo/nightriver-demo.mp4`). If a tighter or
  voice-over version is preferred, re-record from this script.
- Upload the chosen video to a **public YouTube** URL (required by the
  official rules). This repository must not invent a YouTube link before
  that upload exists.
