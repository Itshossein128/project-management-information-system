# Handoff recheck: integrated P1–P4 baseline

**Date**: 2026-11-12
**Code**: `develop`, HEAD `ea38dda2eda939184afd502fa027680b40af7870`
**Purpose**: User requested preparation of the missing P4 handoff so P5 has a real integrated predecessor baseline. This is local downstream readiness, not production/employer acceptance.

## Fresh verification

From `apps/api/core`, exported repository `.env` without printing it, then used phase-specific isolated pytest database selection:

```bash
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
export TEST_DATABASE_NAME="test_a7_p4_handoff_20261112_${BASHPID}"
../.venv/bin/python -m pytest   wbs/tests/test_tree_ordering.py wbs/tests/test_services.py   projects/tests/test_a7_p1_reference_project.py   master_data/tests/test_org_refs.py master_data/tests/test_units.py   schedule/tests/test_a7_p4_import_experience.py   schedule/tests/test_a7_p3_import_fidelity.py   schedule/tests/test_a7_p2_import_safety.py   schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py   schedule/tests/test_mpp_import.py schedule/tests/test_mpp_equivalence.py   -q --junitxml=/home/hossein/Desktop/projects/building-management/specs/054-a7-p4-import-experience/evidence/handoff-pytest.xml
```

Result: **93 passed, 0 failures, 0 errors, 0 skips**, two dependency deprecation warnings, **101.72 seconds**, exit 0. [JUnit evidence](handoff-pytest.xml). No `--reuse-db` was used; pytest created/dropped its isolated test database. The configured TEST_DATABASE_NAME override is explicit in `config/settings.py`. No shared project was imported into or reset.

From repository root: `pnpm typecheck` → **exit 0**. Django **4.2.11**, Python **3.12.3**. No dependency install/upgrade, product-source change or migration generation/application against the development database was performed. Fresh test-database setup exercises committed migrations only; it is not migration rollback evidence or a repository-wide model-drift check.

The suite covers selected P1 reference/catalog rules, structural WBS insertion/move/renumbering, P2 safety/history and apply-time checks, P3 import meaning/omissions and nonempty native MPP/XML equivalence, and P4 preview/count/error/in-flight behavior. Its scope is the downstream import baseline, not every feature in the project.

## Existing browser evidence carried forward

Reviewed [browser.md](browser.md), [browser-results.json](browser-results.json), [wbs-path-root-cause.md](wbs-path-root-cause.md) and the four native MPP screenshots. JSON records four successful language/width cases (English/Persian × desktop/phone), stale preview discarded, and XML/MPP starts distinguished. Native screenshots are present at 1280×844 and 390×844. This session checked their presence/PNG dimensions and source correspondence; it did not rerun the browser.

The relevant wizard, API client, P4 regression, WBS model/service and committed browser-results artifact match HEAD with no product diff. The recorded final matrix includes XML, unchanged employer MPP, XER, protected replacement, held-preview second-file drop, keyboard actions, interrupted status recovery and choose-another-file. The recorded first MPP application stored 6 packages/72 activities/72 relationships; these are prior-session observations, not fresh writes to the shared development database.

`real-data/plan.mpp` remains SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`.

## Interpretation and retained limits

The mutable WBS-sort-key correction is present (`WBS.node_order_by=[]` and structural move semantics) and its PostgreSQL regression passes in the fresh integrated suite. This resolves the recorded root-path failure as a local downstream handoff blocker; no tree rebuild/reset was used.

Pytest uses synchronous tasks and the global test in-memory cache fixture. It does not establish real broker/worker, Redis integration, hard containment/resource limits, restart recovery or seven-day byte cleanup. These remain P5 obligations. Browser observations are historical, automated file attachment is not native OS file-picker testing, and a live project/account-switch browser scenario and employer-alone guide review are not established by this handoff. Those limits remain explicit; no full P4 acceptance or deployment is claimed.

No product code, active service, schema, original fixture or predecessor task checkbox was changed in preparing the handoff. The phase map's existing P1–P5 directory entries remain intact.
