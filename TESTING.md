# Testing instructions (NightRiver)

These instructions are for judges and anyone reproducing the offline demo.
No login and no cloud account are required. English only.

## Requirements

- Python 3.13+ (3.13 was used in development)
- Network is **not** required for the fixture demo

On distributions that block system-wide `pip` (PEP 668), use a virtual
environment as shown below.

## Offline happy path

```bash
cd /path/to/nightriver   # repository root; must contain /.kiro and nightriver/
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m nightriver add-fixtures
python -m nightriver list
python -m nightriver refresh
python -m nightriver cache
python -m nightriver brief            # river view (default)
python -m nightriver brief --grouped
python -m nightriver validate
```

Expected result after `add-fixtures` and `refresh`:

- three subscriptions (Open Source Release Watch, Web Standards Weekly,
  Tangent Tech Blog)
- 17 cached items
- Markdown and HTML briefings written under `data/brief-YYYY-MM-DD.md`
  and `.html` (or a path you pass with `--out`)

Checked-in previews from a verified run are in:

- `demo/briefing-preview-river.html`
- `demo/briefing-preview-grouped.html`

Open the HTML files in a browser. They are generated output, not a hosted
app URL.

## Add a single source

```bash
python -m nightriver add fixtures/tech-blog.xml
```

`add` also accepts `http://`, `https://`, or `file://` URLs. A live public
feed needs network and is optional. A failing URL should print a clear
error and must not be stored.

## Kiro artifacts to inspect

At the repository root:

- `.kiro/specs/nightriver/requirements.md`
- `.kiro/specs/nightriver/design.md`
- `.kiro/specs/nightriver/tasks.md`
- `.kiro/steering/briefing-tone.md`
- `.kiro/hooks/validate-on-save.json`

The How-you-used-Kiro write-up is `HOW_YOU_USED_KIRO.md`.
