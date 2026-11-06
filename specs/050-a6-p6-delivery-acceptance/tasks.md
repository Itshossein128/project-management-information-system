# Tasks: آزمون مستقل، راهنمای مدیر و پذیرش کارفرما (A6-P6)

**Input**: Design documents from `/specs/050-a6-p6-delivery-acceptance/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/delivery-acceptance.md, quickstart.md

**Tests**: Required. This feature is the retest and the evidence package. Existing behavior is retested, not rebuilt. A new test is added only for a gap or for a blocking defect, and that test is recorded before the fix.

**Organization**: Tasks follow the seven user stories in spec.md. All seven are P1. The traceability shell starts early; its final rows are filled only after the evidence exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US7)
- Every task includes an exact file path

## Path Conventions

- Evidence and the guide: `specs/050-a6-p6-delivery-acceptance/`
- API checks: `apps/api/core/`
- Browser check: `e2e/tests/`
- No new product app, endpoint, permission, or table

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Name the candidate version and open the evidence files

- [X] T001 Record `version_id` and `tree_dirty` in `specs/050-a6-p6-delivery-acceptance/evidence/version.md` from `git rev-parse HEAD` and `git status --short`. Constraint from data-model.md: "version_id | Git commit of the tree under test. Required." and "tree_dirty | True when the tested tree had uncommitted changes. Required."
- [X] T002 [P] Name the synthetic roles, and no secrets, in `specs/050-a6-p6-delivery-acceptance/evidence/accounts.md`. Constraint: "accounts_note | Names the synthetic roles used. No password, reset link, or session secret."
- [X] T003 [P] Open `specs/050-a6-p6-delivery-acceptance/evidence/package.md` with `environment_name` empty, `acceptor` empty, `decision` `pending`, and `report_label` `ready_for_acceptance`. Constraint: "environment_name | Named acceptance environment. Empty means the package is not ready to send." and "decision | `pending`, `accepted`, or `rejected`."

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the history handoff and install the evidence validator

**Critical**: No user story work starts until this phase is complete

- [X] T004 Run the pytest command in `specs/049-a6-p5-access-history/quickstart.md` from `apps/api/core` and write the result in `specs/050-a6-p6-delivery-acceptance/evidence/p5-handoff.md`. If it does not pass, stop and report the missing A6-P5 handoff. Do not rebuild `specs/049-a6-p5-access-history/`.
- [X] T005 [P] Add a failing sample at `specs/050-a6-p6-delivery-acceptance/evidence/fixtures/not-run-counted-as-pass.json` whose matrix `result` is `not_run` and whose roll-up says pass
- [X] T006 Make `specs/050-a6-p6-delivery-acceptance/evidence/validate_package.py` exit non-zero on that fixture and on any shared file containing a password, recovery link, access token, or refresh token. Enforce: "`result` | `pass`, `fail`, `not_run`, or `not_applicable`", "`na_reason` | Required when `result` is `not_applicable`", "`not_run` is not a pass", and "`fail` cites a defect"

**Checkpoint**: History handoff is either recorded or explicitly blocked, and the validator rejects a false pass

---

## Phase 3: User Story 1 - ردیابی کامل الزام‌های غیر اختیاری (Priority: P1)

**Goal**: Every non-optional requirement has a row that cannot be closed without evidence

**Independent Test**: The A6-R01–A6-R53 list sits beside the candidate package. A row with neither a witness nor an explicit limitation stays open. A6-R54 is not a commitment.

### Implementation for User Story 1

- [X] T007 [US1] Create `specs/050-a6-p6-delivery-acceptance/evidence/traceability.md` with one open row for each of A6-R01 through A6-R53. A closed row may use only `حفظ شد`, `اصلاح شد`, `اضافه شد`, or `جزئی باقی است`, and only with a witness for the `version_id` in `specs/050-a6-p6-delivery-acceptance/evidence/version.md` or an explicit limitation.
- [X] T008 [US1] In `specs/050-a6-p6-delivery-acceptance/evidence/traceability.md`, record A6-R54 as outside this commitment and not a barrier to the A.6 core

**Checkpoint**: The map exists and every unfilled row is open. Final status is T033.

---

## Phase 4: User Story 2 - ماتریس دسترسی همه حوزه‌های موجود (Priority: P1)

**Goal**: Re-execute the existing 29-area inventory on this version

**Independent Test**: One existing operation has input, expectation, actual result, version, evidence, and defect when it fails. An empty cell is not a pass. An unrelated cell is `not_applicable` only with a reason.

### Tests for User Story 2

- [X] T009 [P] [US2] Start `specs/050-a6-p6-delivery-acceptance/evidence/matrix/batch-1.md` from `specs/048-a6-p4-module-access/matrix/package-1.md` for M01–M10 and M14. Set each inherited row to `not_run`. Columns: `module_id`, `operation`, `actor_kind`, `project_slot` (`A` or `B`), `surface` (`screen` or `direct`), `input_ref`, `expected`, `actual`, `result`, `na_reason`, `evidence_ref`, `defect_id`, `version_id`.
- [X] T010 [P] [US2] Start `specs/050-a6-p6-delivery-acceptance/evidence/matrix/batch-2.md` from `specs/048-a6-p4-module-access/matrix/package-2.md` for M13, M15–M21, and M26, with the same columns and every row `not_run`
- [X] T011 [P] [US2] Start `specs/050-a6-p6-delivery-acceptance/evidence/matrix/batch-3.md` from `specs/048-a6-p4-module-access/matrix/package-3.md` for M11, M12, M22–M25, and M27–M29, with the same columns and every row `not_run`
- [X] T012 [US2] Run the pytest list in `specs/050-a6-p6-delivery-acceptance/quickstart.md` section 2 from `apps/api/core` and update only the covered rows in `specs/050-a6-p6-delivery-acceptance/evidence/matrix/batch-1.md`, `batch-2.md`, and `batch-3.md`. A skipped or expected-failure result stays non-pass.

### Implementation for User Story 2

- [X] T013 [US2] List operations those tests do not cover in `specs/050-a6-p6-delivery-acceptance/evidence/matrix/gaps.md` as `not_run`. Add a focused test in the existing owning module under `apps/api/core/` before changing such a row, and record that the direct surface is not more permissive than the screen.

**Checkpoint**: Every inventory row is `pass`, `fail`, `not_run`, or `not_applicable` with `na_reason`. `not_run` is visible and is not success.

---

## Phase 5: User Story 3 - مسیر واقعی مدیر مشتری (Priority: P1)

**Goal**: A manager completes membership, exception, revoke, and history in the browser without a developer explaining the clicks

**Independent Test**: Using the guide and synthetic data, the manager creates a multi-role member, sets and clears a deny, revokes membership, and reads before/after history, once in Persian and once in English.

### Tests for User Story 3

- [X] T014 [P] [US3] Add `e2e/tests/a6-p6-manager-path.e2e.spec.ts` following `e2e/tests/a6-p1-real.e2e.spec.ts`. Call the running API, do not mock responses, and cover `fa` and `en` for member create, exception, revoke, and history on `apps/web/src/app/routes/project-members.tsx` and `apps/web/src/app/routes/access-history.tsx`.

### Implementation for User Story 3

- [X] T015 [P] [US3] Write `specs/050-a6-p6-delivery-acceptance/guide.md` for create, assign, revoke, and recover using `apps/web/src/app/routes/hr/users.tsx`, `apps/web/src/app/routes/project-members.tsx`, `apps/web/src/app/routes/settings-roles.tsx`, `apps/web/src/app/routes/access-history.tsx`, `apps/web/src/app/routes/login.tsx`, `apps/web/src/app/routes/forgot-password.tsx`, and `apps/web/src/app/routes/reset-password.tsx`. Include Persian and English labels and the current one-hour access-token lifetime. Omit passwords and links.
- [X] T016 [US3] Run `e2e/tests/a6-p6-manager-path.e2e.spec.ts` and record the screen result beside the direct-request result in `specs/050-a6-p6-delivery-acceptance/evidence/browser.md`. Synthetic data must stay separate from customer data.

**Checkpoint**: The browser note shows both languages and matching screen and direct results.

---

## Phase 6: User Story 4 - سرویس واقعی، نشست و خطای کنترل‌شده (Priority: P1)

**Goal**: File, send, and session evidence come from the delivery environment or stay explicitly external

**Independent Test**: A private file from the other project, an allowed download, an invite or the secure account path, a sign-out, and a retry after revoke are recorded. A missing sender does not show a success message. Shared evidence has no secrets.

### Tests for User Story 4

- [X] T017 [US4] When `AWS_S3_ENDPOINT_URL` is set, run `apps/api/core/storage/tests_integration.py` and record upload, other-project refusal, and post-revoke download in `specs/050-a6-p6-delivery-acceptance/evidence/file-channel.md`. Otherwise set `file_service` to `blocked_external` there. Do not copy `apps/api/core/storage/tests/test_stored_file_access.py` into that live-file result.
- [X] T018 [P] [US4] Record the existing delivery gate from `apps/api/core/notifications/services/delivery.py` in `specs/050-a6-p6-delivery-acceptance/evidence/send-channel.md`. `sent` counts only for `TEAM_DELIVERY_TEST_RECIPIENT` on an operational channel. Console email and console SMS stay `not_configured`, and the secure account path must not be described as a sent message.
- [X] T019 [P] [US4] Re-run `apps/api/core/authentication/tests/test_account_lifecycle.py` and `apps/api/core/permissions/tests/test_revocation_retry.py`, and record sign-out refresh refusal plus retry-after-revoke in `specs/050-a6-p6-delivery-acceptance/evidence/session-channel.md`

### Implementation for User Story 4

- [X] T020 [US4] Copy `file_service` and `send_channel` into `specs/050-a6-p6-delivery-acceptance/evidence/package.md` using only `operational`, `not_configured`, or `blocked_external` as allowed by data-model.md

**Checkpoint**: Live file and live send are either evidenced or `blocked_external`. Unit ACL tests remain in the API channel.

---

## Phase 7: User Story 5 - بیست سناریوی مشتری روی نسخه کاندید (Priority: P1)

**Goal**: U01–U20 have technical results separate from customer confirmation

**Independent Test**: Each group is executed once on the candidate. The technical result is written. The customer column stays empty.

### Tests for User Story 5

- [X] T021 [P] [US5] Create `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u01-u06.md` for U01–U06 with `requirement_ids`, `technical_status` (`ready_for_test`, `tested_by_developer`, or `blocked_external`), `technical_result` (`pass`, `fail`, or `not_run`), empty `customer_status`, `evidence_ref`, `defect_id`, and `version_id`
- [X] T022 [P] [US5] Create `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u07-u12.md` for U07–U12 with the same columns and an empty customer column
- [X] T023 [P] [US5] Create `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u13-u17.md` for U13–U17 with the same columns and an empty customer column
- [X] T024 [P] [US5] Create `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u18-u20.md` for U18–U20 with the same columns and an empty customer column

### Implementation for User Story 5

- [X] T025 [US5] Fill U01–U12 in `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u01-u06.md` and `u07-u12.md` from the current API tests, including `apps/api/core/projects/tests/test_team_lifecycle.py`, `apps/api/core/projects/tests/test_local_roles.py`, and `apps/api/core/permissions/tests/test_permission_origin.py`. Leave `customer_status` empty.
- [X] T026 [US5] Fill U13–U20 in `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u13-u17.md` and `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u18-u20.md` from `specs/050-a6-p6-delivery-acceptance/evidence/matrix/`, `specs/050-a6-p6-delivery-acceptance/evidence/browser.md`, `specs/050-a6-p6-delivery-acceptance/evidence/file-channel.md`, `specs/050-a6-p6-delivery-acceptance/evidence/session-channel.md`, and `specs/050-a6-p6-delivery-acceptance/evidence/p5-handoff.md`. U18 stays `not_run` when the handoff did not pass. U20 stays `not_run` while any matrix row is `not_run`. Leave `customer_status` empty.

**Checkpoint**: Twenty groups have technical results. None are marked confirmed by the customer.

---

## Phase 8: User Story 6 - رفع نقص مسدودکننده و بازآزمایی (Priority: P1)

**Goal**: In-scope blocking failures are fixed without weakening the scenario text

**Independent Test**: A blocking failure is stored with its requirement and scenario. The affected check fails before the edit and passes after it on the corrected version. An out-of-scope item is listed and not built.

### Implementation for User Story 6

- [X] T027 [US6] Create `specs/050-a6-p6-delivery-acceptance/evidence/defects.md` with `defect_id`, `requirement_ids`, `scenario_ids`, `blocking`, `in_scope`, `status` (`open`, `fixed`, or `deferred_external`), `before_evidence`, `after_evidence`, and `criteria_unchanged`. Constraint: "`criteria_unchanged` | Must stay true."
- [X] T028 [US6] For each in-scope blocking failure, add the failing test under the existing test module in `apps/api/core/` that owns the behavior, then fix that owner, then re-run the test and the affected scenario. Update `specs/050-a6-p6-delivery-acceptance/evidence/version.md` if the tree changes. If nothing failed, write that zero blocking defects are open.
- [X] T029 [US6] Append out-of-scope gaps and A6-R54 to `specs/050-a6-p6-delivery-acceptance/evidence/defects.md` with `in_scope` false and do not change product code for them

**Checkpoint**: Every failure has a defect row. No acceptance sentence was edited to obtain a pass.

---

## Phase 9: User Story 7 - تحویل واقعی بدون امضای جعلی (Priority: P1)

**Goal**: The unsigned minutes and guide are ready for a person to accept or reject

**Independent Test**: The package contains the version, the guide, the technical scenario results, and the minutes. The signer line is blank. The label is ready for acceptance, not employer confirmed.

### Implementation for User Story 7

- [X] T030 [US7] Write `specs/050-a6-p6-delivery-acceptance/evidence/minutes.md` for the `version_id` in `specs/050-a6-p6-delivery-acceptance/evidence/version.md`, with U01–U20 technical results, the `blocked_external` and `not_applicable` limitations, `signer` empty, and `signed_at` empty
- [X] T031 [US7] In `specs/050-a6-p6-delivery-acceptance/evidence/package.md`, keep `decision` `pending` and `report_label` `ready_for_acceptance`. When `sent_at` is known, set `response_due_at` to `sent_at` plus two calendar days and state that this is not a repair deadline. Constraint: "A `decision` of `accepted` is the only employer confirmation. It requires a non-empty human signer and `response_at`." Do not set `accepted`.
- [X] T032 [US7] Run `specs/050-a6-p6-delivery-acceptance/evidence/validate_package.py` on the evidence directory and write its output to `specs/050-a6-p6-delivery-acceptance/evidence/validation.md`

**Checkpoint**: The minutes are complete and unsigned. The validator accepts the package and still rejects the false-pass fixture.

---

## Phase 10: Close User Story 1

**Goal**: Attach the final witness or limitation to every non-optional requirement

**Independent Test**: A reader can see, for A6-R01–A6-R53, either evidence from this `version_id` or an explicit limitation. No historical checkbox closes a row.

- [X] T033 [US1] Update every A6-R01–A6-R53 row in `specs/050-a6-p6-delivery-acceptance/evidence/traceability.md` from `specs/050-a6-p6-delivery-acceptance/evidence/matrix/`, `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/`, `specs/050-a6-p6-delivery-acceptance/evidence/defects.md`, and `specs/050-a6-p6-delivery-acceptance/evidence/p5-handoff.md`. Leave a row open if neither a witness nor a limitation exists. Keep A6-R54 outside the commitment.

**Checkpoint**: The traceability file matches the evidence and does not call partial coverage complete.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Show that the evidence channels stayed separate and the old snapshot was not edited

- [X] T034 Run `specs/050-a6-p6-delivery-acceptance/quickstart.md` and record in `specs/050-a6-p6-delivery-acceptance/evidence/channels.md` that data preservation, direct requests, browser, live file, live send, and customer confirmation are separate results
- [X] T035 [P] Record in `specs/050-a6-p6-delivery-acceptance/evidence/snapshot-untouched.md` that `output/a6-requirements-2026-11-04/` has no status edits from this feature
- [X] T036 [P] Record in `specs/050-a6-p6-delivery-acceptance/evidence/secret-scan.md` that `specs/050-a6-p6-delivery-acceptance/evidence/` and `specs/050-a6-p6-delivery-acceptance/guide.md` contain no password, recovery link, access token, or refresh token

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks every story
- US1 shell (Phase 3) depends on Foundational
- US2, US3, and US4 depend on Foundational and can proceed in parallel
- US5 depends on US2, US3, and US4 for U13–U20, and on Foundational for U01–U12
- US6 depends on the failures recorded by US2–US5
- US7 depends on US3, US5, and US6
- US1 close (Phase 10) depends on US2–US7
- Polish depends on Phase 10

### User Story Dependencies

- US1 shell: after Foundational. No dependency on later stories.
- US2: after Foundational. Independent matrix files.
- US3: after Foundational. Independent browser spec and guide.
- US4: after Foundational. Independent channel files; only T020 edits `package.md`.
- US5: after the channels it cites. Customer column does not depend on the employer.
- US6: after there is a failure list. Zero failures is a valid result.
- US7: after technical results exist. It must not invent a signature.
- US1 close: after the evidence files exist.

### Within Each User Story

- A new test is written and seen failing before a production fix
- Retest tasks record the observed result and do not change the scenario text
- `package.md` has one writer per phase after Setup: T020 for channels, T031 for the acceptance label

### Parallel Opportunities

- T002 and T003 can run with each other after T001 starts the evidence directory
- T005 can run with T004
- T009, T010, and T011 can run together
- T014 and T015 can run together
- T018 and T019 can run with T017 because they write different evidence files
- T021, T022, T023, and T024 can run together
- T035 and T036 can run together

---

## Parallel Example: User Story 2

```bash
# Three inventory files, no shared writes:
Task: "T009 batch-1.md from specs/048-a6-p4-module-access/matrix/package-1.md"
Task: "T010 batch-2.md from specs/048-a6-p4-module-access/matrix/package-2.md"
Task: "T011 batch-3.md from specs/048-a6-p4-module-access/matrix/package-3.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 shell)

1. Finish Phase 1 and Phase 2
2. Finish T007 and T008
3. Stop and check that every A6-R01–A6-R53 row is open and A6-R54 is excluded

This proves the map cannot be closed by an old checkbox. It is not the employer package.

### Incremental Delivery

1. Add US2 and stop when no uncovered operation is marked pass
2. Add US3 and stop when Persian and English browser results match the direct requests
3. Add US4 and stop when file and send are live or `blocked_external`
4. Add US5 and stop when twenty technical results exist and the customer column is empty
5. Add US6 only for reproduced in-scope failures
6. Add US7, close US1, then run polish

### Parallel Team Strategy

After Phase 2, one person can own the matrix files, another the browser spec and guide, and another the file and send notes. Do not edit `evidence/package.md` from two stories at the same time. Fill US5 only after the cited evidence files exist.

---

## Notes

- Do not add a Django model or a new permission for these records
- Do not reset the development database
- Do not install the full API development requirements file or move Django off 4.2
- Do not sign `evidence/minutes.md`
- Commit evidence with the version it describes


## Phase 12: Convergence

- [X] T037 CRITICAL [US3] Give the inherit/grant/deny radio controls in `apps/web/src/components/projects/add-member-drawer.tsx` localized accessible names that identify both the permission and the choice; verify named selection, keyboard operation, persistence, and reopening in Persian and English through `e2e/tests/a6-p6-manager-path.e2e.spec.ts`, and record the result in `specs/050-a6-p6-delivery-acceptance/evidence/browser.md`. Observed F1: the radio inputs at lines 450–470 have no associated label or accessible-name attribute. Per Constitution VII and III; FR-004 (contradicts).
- [X] T038 CRITICAL [US4] Correct the unsupported full pass for U19 in `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/u18-u20.md`, `evidence/minutes.md`, and `evidence/traceability.md`: separate the verified logout/refresh/lifetime checks from real recovery delivery and used-link rejection, retain the latter as `blocked_external` / `not_run` while the operational channel or agreed recipient is unavailable, and record a pass only after the complete scenario runs on the named candidate environment. Reuse `apps/api/core/authentication/tests/test_account_lifecycle.py` and `test_credential_security.py` for API evidence without presenting them as live delivery. Observed F2: `evidence/send-channel.md` records no sent message, while U19 and A6-R06 are closed as passed/preserved using session-only evidence. Per Constitution VI; FR-005, FR-011, FR-031; US5/AC19; T026 (contradicts).
- [X] T039 [US6] Run and record the final candidate verification after the remaining in-scope fixes: the P5 handoff, the direct-request list in `specs/050-a6-p6-delivery-acceptance/quickstart.md`, the additional module-gap and account/session/wage checks cited by the package, and the completed bilingual browser path. Update `specs/050-a6-p6-delivery-acceptance/evidence/version.md`, `evidence/channels.md`, `evidence/p5-handoff.md`, `evidence/defects.md`, and dependent matrix/scenario references to the same corrected candidate; retain separate API, browser, data-preservation, live-service, and customer results and explicit external blocks. Observed F3: `evidence/channels.md` combines a 122-pass/1-fail run and separate narrow reruns after D001/D003/D004 without a final candidate verification record. Per FR-007, FR-012, FR-033; SC-005, SC-009; plan: execution order and candidate identity; Constitution VI; T028, T034 (partial).
- [X] T040 [US2] Expand `specs/050-a6-p6-delivery-acceptance/evidence/matrix/batch-1.md`, `batch-2.md`, `batch-3.md`, and `gaps.md` from representative summaries into the complete existing-operation inventory for M01–M29, with distinct applicable actor/project/surface cells, positive and negative outcomes, safe input identifiers, actual responses, exact test or browser references, candidate identity, defect links for failures, and reasons for genuinely inapplicable combinations. Execute the uncovered operations with focused tests in their existing owning modules and compare screen/direct behavior where both exist; keep unexecuted cells non-pass. Resolve M14 against the actual `POST` open action in `apps/api/core/sub_reports/urls.py` rather than treating its GET 405 probe as a missing successful read. Reuse completed scenario checks rather than duplicating them and update U20 only when coverage warrants it. Observed F4: each module currently has one aggregate row, actors and A/B are combined, no screen cells are recorded, and create/update/delete/import/approve/export remain generically `not_run`. Per FR-002, FR-003, FR-032; US2/AC1–AC4; SC-002; T009–T013 (partial).
- [X] T041 [US3] Replace the heading-only coverage in `e2e/tests/a6-p6-manager-path.e2e.spec.ts` with independent Persian and English browser journeys on the isolated real API: create or select a person, create one membership, assign multiple roles, set and clear an exception, reopen to verify inherited origin, revoke membership, and inspect the matching before/after history rows. Perform the user actions through the existing controls, compare their outcomes with equivalent direct requests, verify localized validation and controlled-failure feedback, and record the actual journey in `specs/050-a6-p6-delivery-acceptance/evidence/browser.md`. Keep external/customer observation distinct from developer automation. Observed F5: mutations happen through `request` in `beforeAll`; browser assertions only locate Add member and Access history. Per FR-004, FR-006, FR-016; US3/AC1–AC3; SC-003; T014–T016 (partial).
- [X] T042 [US5] Complete the unproven acceptance combinations in the existing owning test modules and map each to precise candidate evidence: U02 must exercise the same person's editor role in A, observer role in B, and inaccessible third project; U03 must submit a real finalization request after a two-role member receives an explicit approval deny; U12 must check sensitive-export refusal as well as edit/delete/approve on the selected data; U17 must exercise the browser's queued work across account switch and revoke/reconnect/retry without submitting the first actor's work as the second. Extend the relevant project, permission, schedule/export, and offline browser tests, repairing product behavior only for reproduced in-scope defects. Audit the other U01–U20 rows against their full acceptance sentences, add safe input/expected/actual details, and correct `specs/050-a6-p6-delivery-acceptance/evidence/scenarios/`, `evidence/traceability.md`, and `evidence/minutes.md` wherever a partial test was presented as a whole-scenario pass. Observed F6: U02 cites two-project reads, U03 cites permission-origin checks without finalization, U12's activity test omits export, and U17 cites server checks without the client queue/account-switch journey. Per FR-001, FR-014, FR-015, FR-024, FR-029; US5/AC2, AC3, AC12, AC17; T025, T026, T033 (partial).
- [X] T043 [US1] Make `specs/050-a6-p6-delivery-acceptance/evidence/validate_package.py` validate the Markdown records actually used by the package, not just standalone JSON samples: reject invalid matrix results, reasonless `not_applicable`, failures without defects, false-pass rollups, missing or mismatched candidate/evidence references, and inconsistent scenario/minutes/customer-decision records. Add negative samples for these real record shapes and retain the existing false-pass fixture as a negative check. Keep structural validity distinct from technical completion and external readiness. Observed F7: directory mode runs `check_payload` only on JSON and accepts the current Markdown package without applying its result rules. Per FR-001, FR-003, FR-009, FR-011; T006, T032; plan: versioned evidence package (partial).
- [X] T044 [US4] Complete secret detection in `specs/050-a6-p6-delivery-acceptance/evidence/validate_package.py` for the evidence and sibling `guide.md`, including standalone JSON mode, quoted JSON values, Markdown assignments, bearer credentials, and recovery URLs/token parameters. Redact diagnostic values rather than echoing any matched secret; exercise these paths using synthetic non-secret samples and update `evidence/secret-scan.md` and `evidence/validation.md` with the actual scan scope and results. Observed F8: the scan root excludes the sibling guide, quoted JSON credentials and recovery URLs are missed, standalone JSON bypasses `check_text`, and `check_text` copies the first 40 matched characters into stderr. Per FR-006; SC-008; T006, T036 (partial).
- [X] T045 [US3] Complete `specs/050-a6-p6-delivery-acceptance/guide.md` as usable Persian and English instructions for account/member creation, role assignment, individual grant/deny/reset, revocation, history, and recovery. Replace source-file paths used as navigation instructions with the actual application locations and the controls visible to the relevant authorized manager; include the advanced-permissions control and inherit choice, expected localized outcomes/errors, and distinguish project-local role editing from organization role settings. Preserve the one-hour session contract, external-send limitation, and absence of secrets, and validate the instructions through the completed manager journey. Observed F9: the guide contains mainly English prose and generic steps, gives no control path for the exception reset, and sends recovery users to `.tsx` source paths. Per FR-004, FR-009; SC-003, SC-007; T015 (partial).
- [X] T046 [US7] Complete the delivery context in `specs/050-a6-p6-delivery-acceptance/evidence/package.md` and `evidence/accounts.md`: name the actual safe candidate environment, identify the synthetic projects/accounts through non-secret roles or identifiers, and name the expected customer acceptance role when known. Explicitly record unknown external inputs as `blocked_external` with the needed action and keep send readiness false until resolved; do not invent an environment, acceptor, delivery time, human signature, or acceptance. Synchronize these limitations into `evidence/minutes.md` and keep the two-calendar-day response rule conditional on actual sending. Observed F10: `environment_name` and `acceptor` remain empty at handoff, with only generic role names supplied. Per FR-009, FR-010, FR-012; plan: candidate environment and safe handoff; T002, T003, T030, T031 (partial).
