# US2: actual interruption and recovery

On the rebuilt image, worker-loss cases for both families passed, including pre-commit rollback and one post-commit application. The 201-job recovery cohort finished in 2.494s against bound 2553s, with a locked row revisited, a later arrival deferred, and a competing leader blocked. Private Redis was stopped after durable intake and restored; the same dispatch deadline reached done, followed by a healthy import. Two actual importers confirmed one commit for MSP and P6. See [runtime/manifest.json](runtime/manifest.json), [runtime/broker-outage.json](runtime/broker-outage.json), and [runtime/concurrent-delivery.json](runtime/concurrent-delivery.json).



The retained root extended matrix killed actual Celery child processes for MSP and P6 before apply, after domain writes before transaction commit, after commit before acknowledgment, and during failure recording. Every pre-commit case preserved zero domain writes; the post-commit replay retained its successful figures without another application. Conversion parent death also stopped the helper and recovery recorded an actionable failure. Each adverse case completed a later healthy import.

An actual201-row aged recovery cohort crossed both job families. One real PostgreSQL row was locked temporarily, one later job arrived after the captured cutoff, and a competing maintainer returned blocked. The cohort drained/revisited the locked row without later arrivals overtaking it; a subsequent pass handled the later job. Root observed1.754s versus the documented W_recovery(N). Full IDs/cutoff/N/timings/results are in worker_loss.observed.bulk_maintenance.

Timestamps of disposable abandoned attempts were advanced only after confirmed SIGKILL to avoid a180-second wall wait; actual queues, death, transaction rollback and maintenance processing were real. The private broker-outage script separately stopped Redis after durable intake and before publish, restored it, reconciled DONE with the same dispatch deadline, and completed a healthy follow-up. See runtime/broker-outage.json and reproduction.md for final independent results.

Host97-test regression evidence remains a separate category. Its finite publication and maintenance-budget tests use controlled clocks/blocked transport to prove bounded decisions, not a real broker outage.

Final independent clean matrix passed all10 groups on source44c00c17b99275157900da0c3fe0f23d9b9d307ae033d36c21b55a13cf3bff36. See runtime/manifest.json for exact attempts, counts, controls, versions and results. Recovery/purge each processed201 rows (1.449s/1.796s; bounds2553s/6093s), including a temporary real row lock, later arrival and competing leader;201 owned scratch workspaces were removed with unrelated content preserved. These are fixture-sized observations under the recorded engineering profile, not a throughput SLA. Additional broker/concurrent/browser checks are in reproduction.md.
