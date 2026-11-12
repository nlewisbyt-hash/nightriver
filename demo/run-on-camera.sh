#!/bin/bash
set -u
cd /workspace/competitions/kiroween-nightriver/app
export PATH="/workspace/competitions/kiroween-nightriver/app/.venv/bin:$PATH"
export PYTHONUNBUFFERED=1
clear
echo
echo "===================================================="
echo "  NightRiver  —  a local River of News"
echo "  Kiroween 2026  ·  Resurrection track"
echo "===================================================="
echo
echo "Local-first RSS/Atom briefing. No cloud account."
echo "This demo uses offline fixture feeds only."
echo
sleep 10

echo "$ python -m nightriver add-fixtures"
echo
python -m nightriver add-fixtures
echo
sleep 6

echo "$ python -m nightriver list"
echo
python -m nightriver list
echo
sleep 7

echo "$ python -m nightriver refresh"
echo
python -m nightriver refresh
echo
sleep 6

echo "$ python -m nightriver brief --out demo/briefing-preview-river"
echo
python -m nightriver brief --out demo/briefing-preview-river
echo
sleep 6

echo "$ python -m nightriver validate"
echo
python -m nightriver validate
echo
sleep 5

echo "--- .kiro (created by Kiro CLI during the contest window) ---"
echo
echo "$ ls .kiro/specs/nightriver .kiro/hooks .kiro/steering"
ls -la .kiro/specs/nightriver .kiro/hooks .kiro/steering
echo
sleep 6

echo "$ cat .kiro/hooks/validate-on-save.json"
echo
cat .kiro/hooks/validate-on-save.json
echo
sleep 8

echo
echo "Next: the HTML river briefing in a browser."
echo "17 items from 3 sources, newest first."
sleep 5
