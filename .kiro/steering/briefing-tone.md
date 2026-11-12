---
inclusion: always
---

# NightRiver Briefing — Tone and Structure Constraints

This steering file is active for every Kiro session in this project. It constrains
how NightRiver briefings are structured and what language they use.

## Required structure

Every generated briefing (Markdown or HTML) must have:

1. **Header block** containing:
   - Title: `NightRiver Daily Briefing — YYYY-MM-DD`
   - Generation timestamp in UTC: `Generated: YYYY-MM-DD HH:MM UTC`
   - Mode indicator: `Mode: River` or `Mode: Grouped`
   - Item and source counts: `N items from M sources`

2. **Per-item block** containing (in this order):
   - Linked headline (item title as a hyperlink to the item URL)
   - Source feed name
   - Published timestamp (ISO 8601, UTC preferred)
   - One-sentence summary of the item content

## Tone rules

- **Neutral and informational.** State what happened; do not editorialize.
- **No engagement bait.** Forbidden phrases include but are not limited to:
  - "You won't believe…"
  - "This will change everything"
  - "Must-read"
  - "Breaking:" (unless the item's own title uses it)
  - "Click here"
  - "Don't miss"
  - Rhetorical questions designed to provoke clicks
- **No superlatives** unless present in the original item title.
- **No commentary** on whether items are "interesting", "exciting", or "important".
- **Concise.** The one-sentence summary must be a single sentence (ending with a period),
  no longer than 280 characters.

## Mode defaults

- Default mode is **river** (chronological, most-recent first, all sources interleaved).
- Use **grouped** mode only when the user explicitly passes `--grouped`.
- Within grouped mode, each group is sorted chronologically (most-recent first).

## What the briefing is NOT

- It is not a newsletter. Do not add sign-up prompts, unsubscribe links, or marketing copy.
- It is not social media. Do not add share buttons, like counts, or engagement metrics.
- It is not curated. Every item from cached feeds is eligible; no algorithmic filtering.

## Applying these rules in code

The `nightriver/briefing.py` module enforces the structure above.
If this steering file and the code diverge, the steering file describes the intended
behavior and the code should be updated to match.
