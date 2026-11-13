# US3: retention, cleanup and surviving history

On the rebuilt image, 201 expired originals across both families were purged in 2.793s against bound 6093s. A locked row was revisited, a later arrival stayed in the next cohort, and a competing purge was blocked. Scratch cleanup removed a 201-workspace cohort in 0.858s and preserved an unrelated file. An expired quarantined slot stayed occupied while a later workspace was removed. A maintenance budget failure closed admission and was reopened only after that observation. See [runtime/manifest.json](runtime/manifest.json) groups `expiry`, `cleanup`, `scratch_quarantine`, and `maintenance_budget`.



Original bytes expire at immutable terminal anchor+168 elapsed hours. Host boundary checks cover before/exactly/after for DONE/FAILED in both concrete families, repeated no-op, unchanged attribution/result/digest and active/unexpired protection. Actual MigrationExecutor checks exercise old schema→legacy rows→additive upgrade→reverse schema→upgrade, preserving original domain/history data; purged bytes cannot be restored by schema rollback.

Root real maintenance purged201 aged two-family originals in consecutive pages while preserving active/unexpired bytes and results/digests. It exercised a temporary row lock, later arrival after cutoff and competing leadership; observed1.976s compared with W_purge(N). Explicit isolated timestamps accelerate eligibility without changing system time. Source of full observations: retained extended matrix expiry group; final repeat manifest and reproduction record supersede its image identity.

Success/failure/timeout/worker-death cases left no owned manifests; unrelated file content survived cleanup. The final harness adds201 expired owned scratch workspaces. New scratch leadership/cohort/per-item budgets and recovery gate coupling were covered by meaningful failing-then-passing regressions: failed verification/budget closes admission; dry-run preserves bytes/workspaces and does not reopen admission. Final actual-runtime confirmation is recorded by the independent operator.

Private source bytes and tokens are not copied into evidence. Public statuses use stable sanitized errors; no download endpoint or new sensitive-file privilege was added. Cross-project status denial remains in the host/API regressions.

Final independent clean matrix passed all10 groups on source44c00c17b99275157900da0c3fe0f23d9b9d307ae033d36c21b55a13cf3bff36. See runtime/manifest.json for exact attempts, counts, controls, versions and results. Recovery/purge each processed201 rows (1.449s/1.796s; bounds2553s/6093s), including a temporary real row lock, later arrival and competing leader;201 owned scratch workspaces were removed with unrelated content preserved. These are fixture-sized observations under the recorded engineering profile, not a throughput SLA. Additional broker/concurrent/browser checks are in reproduction.md.
