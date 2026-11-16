#!/usr/bin/env bash
# Sequential real-browser runs: fixture fault controls must never overlap.
set -euo pipefail
cd "$(dirname "$0")/../.."
umask 077
evidence="$PWD/specs/056-a7-p6-delivery-acceptance/evidence"
export A7P6_API_ORIGIN=http://127.0.0.1:18000
export A7P6_WEB_BASE=http://127.0.0.1:15173
python3 ops/a7-p5/seed-delivery.py
export A7P6_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-delivery.json"
PLAYWRIGHT_JSON_OUTPUT_NAME="$evidence/final-browser-general.json" pnpm exec playwright test \
  --config=e2e/playwright.a7-p6.config.ts --reporter=list,json \
  --grep='lifecycle suspend|lifecycle and WBS|schedule import wizard|cancel after preview|project-switch and viewer|human login|reference project:'
python3 ops/a7-p5/browser-recovery-fixture.py seed > ops/a7-p5/.runtime-recovery.json
export A7P6_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-recovery.json"
PLAYWRIGHT_JSON_OUTPUT_NAME="$evidence/final-browser-recovery.json" pnpm exec playwright test \
  --config=e2e/playwright.a7-p6.config.ts --reporter=list,json \
  --grep='real worker import|planner cannot read'
python3 ops/a7-p5/seed-viewer-browser.py > ops/a7-p5/.runtime-viewer.json
export A7P6_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-viewer.json"
PLAYWRIGHT_JSON_OUTPUT_NAME="$evidence/final-browser-viewer.json" pnpm exec playwright test \
  --config=e2e/playwright.a7-p6.config.ts --reporter=list,json \
  --grep='viewer project and baseline'
python3 ops/a7-p5/seed-browser.py
export A7P5_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-auth.json"
PLAYWRIGHT_JSON_OUTPUT_NAME="$evidence/final-browser-retry.json" pnpm exec playwright test \
  --config=e2e/playwright.a7-p5.config.ts --reporter=list,json
