# A.7 final defect disposition — 2026-11-16

نسخه منبع: `2090da13f90756e9512070ffcd4feb87dcf5fd7a`؛ تصویر API: `sha256:0e4bef19068e6b36da9f7de2169486cd3fe73b7ec1f2f3a1c96ae60a62067066`؛ محیط: `a7p5-import:API18000/PostgreSQL55434/Redis56379/Web15173`؛ Django: `4.2.11`.

Known open in-scope technical defects: **0**. Human acceptance remains pending. Earlier dated runs in predecessor evidence are historical; the current lock is release-verification.json.

- P6-GATE-001: historical P5 independent reproduction retained. Current candidate additionally reruns all 13 real-worker groups, broker outage, duplicate consumers, host containment and browser recovery. The new runs are implementer-run.
- P6-DOC-001: phase traceability artifacts exist; the final 56-row ledger now preserves exact original titles/acceptance and owning phases.
- P6-CONV-001: protected replace rejects with baseline_replace_forbidden and retains baseline/progress/report/change-request/measurement history.
- P6-CONV-002: missing lifecycle/charter, duplicate import, indirect-cycle rollback, cancel-without-job, actual offline/reload recovery, cross-project baseline/schedule and viewer project/baseline checks are executed. The final OPS-04 matrix is rebound to the final image/source hash.
- P6-DELIVERY-001: measurement unit API field now has create/settings selectors, including clearing and reselecting; persisted FK is checked in the browser.
- P6-DELIVERY-002: template/empty-WBS text is localized; template and charter fields have associated labels; project-list sort typecheck is fixed.
- P6-DELIVERY-003: a valid MPP chosen through the native browser chooser was rejected because host MIME associated .mpp with audio/x-musepack. MPP detection now relies on extension plus mandatory OLE signature and the bounded parser; non-OLE remains rejected. MIME variants have regression tests and native upload passes.
- P6-DELIVERY-004: archive read-only enforcement inadvertently blocked legitimate missing-data remediation. Only a missing manager on an active-origin archive may be repaired by a global admin with active project permission; scope/budget use an independently approved cycle-bound CR. Generic and stale serializer/CR writes remain denied under the root row lock. Cancelling stale completion remediation remains allowed without writing project data. Real concurrency tests pass.
- P6-DELIVERY-005: stale audit/scenario mappings, file hashes/counts, role descriptions, version IDs and readiness summaries were regenerated and validator now enforces their ties to successful current reports.

Recorded policy boundaries (not defects): M03 fixed project lifecycle; M04 no dynamic Excel in the A.7 journey; calendar_not_applied; parentless-row omission; fixture-scoped compatibility. No unsupported behavior is presented as implemented.
