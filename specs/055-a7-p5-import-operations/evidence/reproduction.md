# Independent reproduction

## Implementer rerun — not a second operator

2026-11-13. The same implementer rebuilt `a7p5-api:acceptance` as `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5` and reran the acceptance matrix, broker-outage check, and two-importer check. The matrix status was ready, with schedule-tree SHA-256 `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`. This is not the second-operator gate. T049 stays open until a different operator repeats the quickstart from a clean stack and records their own results.



Operator: a second Codex agent, explicitly authorized by the user and given a separate task context. This is independent agent reproduction, not human or employer acceptance. Observations below came from execution, not the implementer’s reported outcomes.

## First clean run — blocked

2026-11-12 UTC (2026-11-13 Asia/Tehran). The existing `a7p5-import` stack was inspected, the implementer’s matrix preserved as `runtime/implementer-extended-matrix.json`, and only this exact Compose identity removed with `down -v`. After its containers stopped, the dedicated `/run/a7p5-scratch` tmpfs was unmounted and only `a7p5-containment.service` stopped. The guide recreated delegation, bounded tmpfs, PostgreSQL, Redis, API and independent workers from a clean database.

Actual commands, from repository root:

```bash
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml ps
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml down -v
sudo -n umount /run/a7p5-scratch
sudo -n systemctl stop a7p5-containment.service
A7P5_BUILD_NETWORK=host A7P5_BUILD_PROXY=http://127.0.0.1:2080 ops/a7-p5/run-acceptance.sh
```

Image: `sha256:e75025123fa91c1adf198596ebb50f240da8e80615e84c9d16e2de7f25901415`. Schedule source-tree SHA256: `a032f0294118279cb2d6a568e6f578fc12413ad94d07a84a25a3300d53bb818a`. The snapshot preceded T055–T057 corrections and later harness refinements; these observations cannot establish acceptance of those changes. API startup applied 216 migrations in the new private database. Preflight initially waited for workers, then passed with actual attachable cgroup containment, eager=false and inline=false. Protected env mode was 0600; resolved environment was not exported.

Source fixture SHA256: `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Native import passed JPype and forced-unavailable-JPype Java CLI fallback with equal stored figures; P6 import also passed. Unreadable input, admitted failure, duplicate delivery and real timeout groups passed.

The resource group failed on actual pids exhaustion: expected `processing_resource_limit`, observed `processing_timeout`. The preceding memory probe reached the configured 1 GiB peak and returned the resource error, followed by a healthy import. The script exited 1 and exported the incomplete report. Worker-loss, expiry, cleanup and final healthy groups remained not-run after this first failure. Broker outage, browser, maintenance and schema checks were not run against the superseded failed image. No product code was changed by this operator to make checks pass.

Evidence: `runtime/independent-precorrection-matrix.json`, `runtime/independent-precorrection-preflight.json`, `runtime/independent-precorrection-run.log`, `runtime/independent-precorrection-workers.log`, `runtime/independent-precorrection-image.txt`. `runtime/independent-compose.json` contains only `compose ps --format json` metadata, not resolved configuration or credentials.

The knowledge-context command was attempted; it refused the stale hybrid index. The index was not rebuilt during read-only review. Current owning guides and source were read directly. Shared services and system proxy/DNS were untouched.

T049 remains open pending a corrected clean independent repeat. The failure was reported immediately; runtime mutation paused and the still-running private stack handed back to the coordinator for diagnosis.

## Second clean run — blocked

The same exact-project teardown/delegation/tmpfs recreation and proxy-scoped build commands were independently repeated. Image `sha256:d66f0a8bdbe86f6efac7def4bb0c906b5b0a95367e8a60d1e5ce207a94665047`; schedule source-tree SHA256 `bbfcbd116db0fd370796efcebb0a30d41b331f243e71710845d73d153b8a13b4`. Preflight passed and native JPype/CLI/P6 group passed. The strengthened unreadable group then failed: `bad.xml` expected `msp_invalid_xml`, but the real response code was `conversion_failed`. The matrix exited 1; all later groups, broker/concurrent/browser/maintenance checks were not-run on this image. This failure was immediately reported without code changes by the independent operator. Artifacts: `runtime/independent-final-attempt1-{matrix,preflight,run,image}`. Independent `pnpm typecheck` exited 0; it does not imply runtime acceptance.

## Third clean image — focused taxonomy checks passed

Image `sha256:94a0eb7b4db6745ce6f04bf41c22f0b0cdcd138c2fee7194266e9a5ad960946e` was independently rebuilt from another clean private stack using the same teardown, delegation and build-only proxy steps. Manual build/up/preflight followed the guide’s exact file/env identity, allowing focused inputs before full matrix. Preflight passed. The independent script’s first project-code prefix exceeded the model’s 30-character limit; that operator-owned evidence script was shortened and rerun, without product changes. The failed operator command is preserved as `runtime/independent-focused-inputs.log`; the successful run is `runtime/independent-focused-inputs-retry.log`.

Actual authenticated start-route results were HTTP400 with no job or schedule writes: bad.xml → msp_invalid_xml; readme.txt → invalid_file_type; password-protected.mpp → mpp_password_protected; truncated-ole.mpp → mpp_unsupported; renamed-not-mpp.mpp → invalid_file_type. Valid 52,428,800-byte XML reached DONE; 52,428,801 bytes were refused; healthy follow-up reached DONE. Sanitized structured results: `runtime/independent-focused-inputs.json`; reproducible operator script: `runtime/independent-focused-inputs.py`. Full matrix was deliberately paused before execution because the coordinator identified a separate cumulative application-budget issue requiring a new product image. This image therefore establishes only the recorded focused results.

## Fourth clean image — synchronous resource fixture blocked

The same clean teardown/reprepare/build procedure produced image `sha256:c71dce3db68399b211aaea5853db1b6632156cfe09f6be2d031cdb7288d949e5`. Preflight, native JPype/CLI/P6, input rejection/50MiB boundary, admitted failure, both-family duplicate delivery and real timeout passed. The background memory/pids/output/disk probes each reached the expected resource error and a healthy follow-up; in particular, the earlier pids timeout is corrected on this candidate. The resource group then failed on synchronous preview: its `SimpleUploadedFile('plan.xml', XML)` used the default text/plain content type, and intake correctly refused invalid_file_type before the expected output-limit fault. The matrix exited1; worker_loss/expiry/cleanup/final follow-up remained not-run. No product or harness change was made by the independent operator. Evidence: `runtime/independent-candidate-attempt3-{matrix,preflight,run,image,workers}`. The failure was reported immediately for the coordinator to distinguish a fixture issue from product behavior.

## Fifth clean run — independent second-operator reproduction on rebuilt candidate image

2026-11-13 UTC (`2026-11-13T16:24–16:41+03:30`). An independent second agent operator in an isolated conversation context (explicitly authorized by the user; independent agent reproduction, not human or employer acceptance) inspected the running `a7p5-import` stack, tore down only that private Compose project (`down -v`), unmounted `/run/a7p5-scratch`, stopped `a7p5-containment.service`, and executed the full `quickstart.md` / `ops/a7-p5/README.md` sequence from a clean private database, broker, tmpfs, and delegated cgroup v2 subtree without modifying any product code, test code, or `ops/a7-p5/` scripts, and without touching shared services (`8000`, `5173`, `5433`, `6379`) or global DNS/proxy settings:

```bash
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml ps
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml down -v
sudo -n umount /run/a7p5-scratch || true
sudo -n systemctl stop a7p5-containment.service || true
A7P5_BUILD_NETWORK=host A7P5_BUILD_PROXY=http://127.0.0.1:2080 ops/a7-p5/run-acceptance.sh
python3 ops/a7-p5/check-broker-outage.py
python3 ops/a7-p5/check-concurrent-delivery.py
python3 ops/a7-p5/seed-browser.py
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm --filter web exec vite --host 127.0.0.1 --port 15173 --strictPort
A7P5_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-auth.json" pnpm exec playwright test --config=e2e/playwright.a7-p5.config.ts
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py maintain_import_jobs --dry-run
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py maintain_import_jobs --operation recovery
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py makemigrations schedule --check --dry-run
ops/a7-p5/check-host.sh
pnpm typecheck
```

- **Image & Source Identity**: `a7p5-api:acceptance` digest `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5` (`runtime/independent-complete-image.txt`); schedule source-tree SHA-256 `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`; `real-data/plan.mpp` SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Versions: Python `3.12.15`, OpenJDK `21.0.13`, Django `4.2.11`, Celery `5.7.0`, MPXJ `16.10.0`, JPype1 `1.7.1`, redis-py `8.1.0`.
- **Preflight & 13-Group Runtime Matrix (`runtime/independent-complete-preflight.json`, `runtime/independent-complete-matrix.json`, `runtime/independent-complete-run.log`)**: `status: "ready"`, `not_run: []`, `problems: []`. All 13 groups passed (`valid_native` JPype job `bc083862-d340-40fd-a0aa-cbc0de13d0d8` & forced-CLI fallback job `7f7ffd93-8f7b-4144-846a-7441f28e5df2` both `[6, 72, 72]` plus P6 job `5c2acb16-a9cc-45a6-8532-d15bfc0e66cf` `[2, 1, 0]`; `unreadable` 5 taxonomy HTTP 400 rejections + `52,428,800`-byte job `47ecada4-4f39-48d2-b38a-8c2e6d965f47` DONE + `52,428,801` refused; `admitted_failure` `import_not_permitted`; `duplicate_delivery` MSP & P6 single commit + `503 queue_unavailable` capacity precedence; `timeout` `processing_timeout`; `resource_limit` memory/pids/output/disk + sync preview/start + `2,100,184`-byte expansion refusal; `worker_loss` 8 MSP/P6 stage kills + `kill-parent` + 201-row recovery drain in `1.739s` with locked-row revisit, new-arrival deferral, and competing leader block; `expiry` 201-row purge drain in `2.007s` + active/unexpired preservation + idempotent repeat `n=0`; `cleanup` 201 scratch directories removed in `0.506s` preserving `faults` and `unrelated-a7p5.txt`; `request_intent` MSP & P6 retry linkage/rejection; `maintenance_budget` overrun closes admission; `scratch_quarantine` active PID token `00000000-0000-4000-8000-0000000000a7` quarantined then cleaned after exit; `healthy_follow_up` job `a1f5504b-14ce-4801-acb6-2a827d39fc59` DONE).
- **Broker Outage & Concurrent Importers (`runtime/broker-outage.json`, `runtime/concurrent-delivery.json`)**: `check-broker-outage.py` passed (`job=d21fa655-a397-43fa-96bc-c784427e96e3`, `http_elapsed_seconds=8.785`, `terminal=done`, `healthy_follow_up=b9fc4792-9d3e-4299-8578-6a3a68d27b9d`, `fixed_dispatch_deadline=true`). `check-concurrent-delivery.py` passed across 2 live importer consumers (`msp` job `78c7e844-ee6e-4f02-8b43-235c930a3e19`, `p6` job `fcb88eaf-6aa5-4109-ae58-b7f8b2c7a151`, live duplicate returned `{"duplicate": true}` while original paused, single commit, `healthy_follow_up=45cc673b-fe38-41a6-93bf-7126903236ca`).
- **Browser Retry, Maintenance, Host Regressions & Typecheck**: `seed-browser.py` wrote mode-`0600` fixtures without printing tokens; Playwright passed `4/4` (`real retry en 1280`, `fa 1280`, `en 390`, `fa 390` in `52.6s`, `runtime/independent-browser.log`), and the port `15173` Vite server was cleanly terminated. Private-stack `maintain_import_jobs --dry-run`, `maintain_import_jobs --operation recovery`, and `makemigrations schedule --check --dry-run` (`No changes detected in app 'schedule'`) all exited `0`. Host `ops/a7-p5/check-host.sh` passed `110 passed` in `161.77s` (`runtime/host-pytest-junit.xml`), and `pnpm typecheck` exited `0` (`runtime/independent-final-typecheck.log`).
