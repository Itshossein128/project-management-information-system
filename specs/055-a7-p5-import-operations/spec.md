# Feature Specification: Reliable Schedule Import Operations

**Feature Branch**: `develop` (observed checkout; no branch-creation hook registered)

**Feature Directory**: `specs/055-a7-p5-import-operations`

**Created**: 2026-11-12

**Status**: Draft — specification validated; integrated local P1–P4 prerequisite handoff verified; P5 implementation/runtime acceptance still pending

**Input**: User description: A.7-P5, short-name `a7-p5-import-operations`, from [05-import-operations.md](../../output/a7-requirements-2026-11-10/speckit-prompts/05-import-operations.md). Direct audit owners: I09, I19, I20, D02. Make existing schedule import processing bounded, recoverable, confidential, and demonstrably usable in the delivery environment. Preserve integrated P1–P4 behavior and do not start subsequent phases.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Follow an import to a trustworthy result (Priority: P1)

An authorized project planner confirms a preview, receives an attempt identifier, and follows processing to a recorded success or actionable failure, including after reopening the existing import screen.

**Why this priority**: An ambiguous attempt encourages unsafe repeat submissions and prevents planners from knowing which schedule was applied.

**Independent Test**: Submit valid input through actual independent background processing and follow its durable identifier/result. Reject unreadable input before admission with no job or schedule writes, then separately induce a failure after admitting a valid file and follow that job to FAILED with unchanged schedule data.

**Acceptance Scenarios**:

1. **Given** an authorized member and valid confirmed input, **When** processing proceeds, **Then** the same attempt is identifiable through pending, running, and done, with meaningful progress and a final result matching stored work.
2. **Given** corrupt, protected, unsupported, or unreadable input is rejected during preview or start validation before durable admission, **When** that validation ends, **Then** the user receives an actionable Persian or English rejection without a business job or schedule changes. **Given** a durably admitted attempt subsequently fails during background preparation or application, **When** processing ends, **Then** its existing identifier reports failed with an actionable localized reason and no partial schedule changes.
3. **Given** an existing attempt, **When** the planner returns to its status, **Then** the existing attempt is shown without creating or applying another import.
4. **Given** membership, permission, project state, or protected history changes after confirmation, **When** final application begins, **Then** P2 safety rules are rechecked and any refusal leaves the schedule unchanged.

---

### User Story 2 - Recover from interruption and excessive processing (Priority: P1)

A planner can recover from slow or failed conversion and interrupted background processing without losing existing work or creating duplicate work.

**Why this priority**: Untrusted input and interrupted services must not monopolize resources or silently reapply a schedule.

**Independent Test**: In an isolated environment, exceed configured processing bounds and interrupt execution before application, during application, and after commit before acknowledgment. Inspect outcomes, then submit a healthy file.

**Acceptance Scenarios**:

1. **Given** an input exceeds an effective processing or resource bound, **When** the bound is reached, **Then** its work actually stops, temporary resources are released, a clear failure is recorded, and a subsequent healthy attempt can finish.
2. **Given** processing is interrupted before commit, **When** service returns, **Then** the attempt safely recovers or fails within the documented recovery bound, leaving no partial WBS, activity, relationship, or schedule-copy changes.
3. **Given** a successful commit followed by interrupted acknowledgment or result recording, **When** delivery repeats, **Then** the committed outcome is reconciled without reapplication or a misleading failure inviting reapplication.
4. **Given** concurrent or repeated deliveries for one attempt, **When** they execute, **Then** there is at most one committed application and one consistent terminal outcome; distinct attempts retain P2 concurrency behavior.
5. **Given** a failed attempt and a permitted explicit Retry action, **When** retry starts, **Then** its new attempt is mandatorily linked to that failed predecessor and safety is rechecked. A fresh import is a separate action without retry linkage; repeated message delivery is neither action and cannot reapply a completed attempt.

---

### User Story 3 - Keep files private and remove processing residue (Priority: P1)

Project members can rely on uploaded and converted files being available only for their authorized purpose, with cleanup preserving enough history to explain an outcome.

**Why this priority**: Raw schedules may contain confidential information; cleanup must preserve accountability and active inputs.

**Independent Test**: Exercise success, failure, timeout, and interrupted cleanup using two disposable projects. Verify restricted access, exact expiry boundaries, cleanup after restart, and surviving action history.

**Acceptance Scenarios**:

1. **Given** an original or derived artifact, **When** a person without required project and sensitive-file permission requests it, **Then** neither content nor a usable storage location is disclosed.
2. **Given** conversion succeeds, fails, or times out, **When** its temporary artifacts are no longer needed, **Then** they are removed; interrupted cleanup resumes after restart within the documented cleanup bound.
3. **Given** an attempt reaches terminal success or failure at time T, **When** fewer than seven elapsed days have passed, **Then** its original bytes remain available only for authorized diagnostics; **When** seven elapsed days have passed, **Then** cleanup removes those bytes at its first eligible run while retaining action metadata and sanitized results.
4. **Given** an active attempt, an unexpired upload, or another project's file, **When** expiry cleanup runs repeatedly, **Then** it does not remove those protected or unrelated inputs.
5. **Given** an error contains sensitive source text or credentials, **When** diagnostics are recorded or shown, **Then** public logs and user feedback contain only a sanitized reason and correlation information.
6. **Given** original bytes have expired, **When** a user tries to retry, **Then** a fresh authorized upload is requested, and reading the earlier outcome remains possible.

---

### User Story 4 - Reproduce the delivery check (Priority: P2)

A delivery operator can reproduce the existing import journey using the employer's actual schedule and documented delivery configuration, distinguishing verified behavior from missing evidence.

**Why this priority**: Local synchronous tests do not establish independently running processing in the delivery environment.

**Independent Test**: Another operator follows the startup and smoke procedure in an authorized isolated environment, processes the unchanged reference file, and repeats failure and recovery checks.

**Acceptance Scenarios**:

1. **Given** the documented delivery configuration, **When** the operator previews and imports `real-data/plan.mpp`, **Then** reading and final application succeed with the integrated P3 meanings and P4 figures/warnings, rather than merely demonstrating installed dependencies.
2. **Given** the verification record, **When** another operator repeats the procedure, **Then** code version, file identity, dependency versions, selected conversion route, effective limits, and background-processing settings are reproducible without exposed secrets.
3. **Given** a required environment dependency is unavailable, **When** readiness is reported, **Then** the missing service/access and each unrun scenario are named and operational acceptance remains incomplete.

### Edge Cases

- Service loss while queued, during conversion, during application, after commit before acknowledgment, or during cleanup; a recovery/expiry backlog larger than one batch must not starve older attempts or postpone their deadlines indefinitely.
- Duplicate delivery while running or completed; overlapping starts; explicit retries after input expiry; the same in-flight confirmation while the only processing slot is occupied must return its existing identifier before any busy refusal.
- Conversion timeout followed by fallback: combined processing must remain within the effective total bound.
- A small input produces excessive output; temporary storage is exhausted; conversion dependencies are missing.
- Progress advances immediately before failure; 100% must not imply a commit that did not occur.
- Membership or permission is revoked, project state changes, or history becomes protected after confirmation.
- Cleanup races with active processing, repeats, or encounters artifacts abandoned by a crash.
- Identical filenames across projects; sensitive content embedded in error text; an old attempt has an uncertain outcome.
- Expiry exactly at seven elapsed days; restart after expiry; duplicate delivery cannot extend the retention deadline.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every durably admitted attempt MUST expose a stable identifier, pending/running/done/failed status, meaningful progress, and a recorded terminal result or actionable error. Input-validation and capacity/dependency rejections before admission MUST be actionable and create no business job. Existing safety refusals that persist a FAILED history job MUST retain that job identifier and terminal timestamps. Status reads MUST NOT restart work. (US1)
- **FR-002**: Background processing MUST execute independently of the submitting request and remain traceable after reconnection. Success and 100% progress MUST describe committed schedule work. (US1)
- **FR-003**: Failures or interruptions before commit MUST leave no partial WBS, activities, relationships, baseline contents, or current-copy changes and MUST preserve protected history. A commit followed by reporting interruption MUST be reconciled rather than applied again. (US1, US2)
- **FR-004**: Final application and every retry MUST preserve P2 membership, permission, project-state, protected-history, concurrency, and repeat-operation safeguards, P3 fidelity, and P4 feedback. An authorized confirmation matching an existing in-flight attempt MUST return that identifier before processing-capacity admission; only genuinely new work may receive a capacity refusal. (US1, US2)
- **FR-005**: Each untrusted-file attempt, across all conversion routes/fallbacks, MUST have documented effective time, memory, temporary-storage, and concurrent-processing bounds. Reaching a bound MUST stop the affected work and release its resources; stopping only the caller's wait is insufficient. Planning MUST identify existing settings and resolve necessary missing bounds before implementation; no new customer SLA is implied. (US2)
- **FR-006**: After service restoration, affected attempts MUST reach a reconciled success or actionable failure within a documented bound computed from the finite recovery cohort size and effective processing/maintenance budgets. Oldest cohorts MUST drain fairly without new arrivals resetting their position or deadlines; unsuccessful maintenance MUST be reported as blocked rather than as successful recovery. (US2)
- **FR-007**: Duplicate delivery and recovery MUST cause at most one committed application per attempt. An explicit Retry action MUST create a new authorized attempt linked to its failed predecessor; the request must identify that intent and predecessor. Fresh imports are distinct and need no predecessor; message redelivery does not create a new attempt. Expired input requires a fresh authorized upload. (US2, US3)
- **FR-008**: Healthy subsequent imports MUST remain possible after every tested failure, timeout, resource-limit event, and restart, without manual schedule repair or resetting shared services. (US2)
- **FR-009**: Original bytes MUST be retained for seven elapsed days from the attempt's terminal success/failure time for authorized diagnostics, then removed at the first eligible cleanup run. Repeated delivery or reads MUST NOT reset that deadline. An active attempt's input MUST NOT expire; recovery MUST resolve abandoned attempts under FR-006. Each original upload, derived artifact, and diagnostic record MUST have a documented location category, access rule, retention/cleanup trigger, and recovery behavior. (US3)
- **FR-010**: Cleanup MUST remove no-longer-needed conversion artifacts after success, failure, timeout, and restart, and expired originals under FR-009. It MUST be safe to repeat, avoid active/unexpired/unrelated artifacts, and preserve the actor, project, attempt identifier, file identity, mode, timestamps, outcome, and permitted diagnostic summary. Planning MUST document the cleanup execution interval, fair finite-cohort draining, and backlog-dependent completion bound; reaching the processing batch limit MUST NOT defer remaining eligible items by another full scan interval. This phase MUST NOT introduce expiry of durable action history. (US3)
- **FR-011**: Artifact and diagnostic access MUST enforce organization/project isolation and the applicable sensitive-file permission. Public logs and user feedback MUST exclude uploaded contents, credentials, and unrestricted storage locations. Cleanup MUST NOT confer new download rights. (US3)
- **FR-012**: Existing error identifiers MUST remain stable; actionable feedback MUST work in Persian and English for unreadable input, timeout, unavailable conversion, interruption, and retry after expiry. (US1, US3)
- **FR-013**: Delivery readiness MUST be supported by repeatable checks with independently running background processing, the unchanged employer file, corrupt/heavy inputs, effective limit enforcement, interruption, duplicate delivery, cleanup, and a later healthy attempt. Synchronous/simulated checks MUST be labeled separately and cannot satisfy this gate. (US4)
- **FR-014**: The delivery procedure and evidence MUST identify tested code, file identity, dependency versions, effective settings, conversion route, required services, secret-free commands, actual results, and open access/environment blockers. Universal Microsoft Project year compatibility MUST NOT be claimed. (US4)

### Key Entities *(include if feature involves data)*

- **Import attempt**: A durably admitted operation for one project, actor, input identity, and append/replace mode; has delivery correlation, status, progress, timestamps, outcome, and any retry linkage.
- **Original upload**: Source bytes retained for active processing and the agreed seven-day terminal diagnostic period; distinct from durable history.
- **Derived artifact**: Restricted temporary conversion input/output associated with an attempt and removed when no longer needed.
- **Import action record**: Attributable history explaining the operation after byte cleanup, without retaining raw sensitive contents.
- **Operational policy and verification record**: Effective limits, recovery/cleanup bounds, retention decisions, tested environment/file identity, evidence, and unresolved gates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every durably admitted attempt in the valid, background-failure, timeout, resource-limit, and interruption acceptance set has an identifiable terminal result within its documented processing/recovery bounds, including a multi-batch recovery cohort; none remains indefinitely ambiguous. All invalid/corrupt/protected/unreadable inputs rejected before admission receive an actionable rejection without a business job or schedule writes. (FR-001/002/005/006)
- **SC-002**: All pre-commit failure/interruption checks preserve the original schedule and protected history; every duplicate-delivery and post-commit interruption check yields at most one committed application with a consistent reported outcome. (FR-003/004/007)
- **SC-003**: A healthy import succeeds after each failure, timeout, resource-limit, and recovery case without manual schedule repair. (FR-008)
- **SC-004**: In success, failure, timeout, and restart checks, 100% of expired originals and no-longer-needed temporary artifacts are removed by their documented cleanup deadline; zero active, unexpired, or unrelated inputs are deleted, zero unauthorized disclosures occur, and all action records remain attributable. Seven-day boundary cases and an expired cohort larger than one maintenance batch are included. (FR-009–011)
- **SC-005**: The unchanged employer schedule completes preview and import in the authorized delivery test environment, and a second operator reproduces the documented outcome from its recorded configuration. (FR-013/014)
- **SC-006**: Every tested terminal job error has an actionable Persian and English explanation identifying the affected attempt and permitted next action without raw processing logs. Pre-admission rejections identify the rejected operation and correction without inventing a business job identifier. (FR-012)

## Assumptions

- This phase owns I09, I19, I20, and the A.7 audit's D02 only. A separate D02 in the delivery-plan decision register concerns communications and does not expand this scope.
- Scope derives from the original prompt, R0, and corrected A.7 delivery plan. Historical audit statuses are not employer decisions or proof of current failures. See [traceability.md](traceability.md).
- Existing Microsoft Project XML/native MPP and Primavera XER entry points remain the supported family. Independent WBS CSV/Excel import, preview rewrite, live P6 synchronization, full financial/EVM/A.10 work, and relaxed A6 access policy are excluded.
- Integrated P1–P4 handoffs are required before dependent execution. On 2026-11-12 the user-authorized P4 handoff preparation added the actual [P4 handoff](../054-a7-p4-import-experience/handoff.md) and refreshed P1/P2/P3 downstream-readiness notes, backed by 93 passing integrated tests and fresh typecheck. The local baseline is ready for P5 implementation with documented limits; this does not certify employer/production acceptance or the still-unrun P5 operational evidence. See [handoff.md](handoff.md).
- Existing processing/conversion tools are extended. Technical route selection and effective resource, recovery, and cleanup values belong in planning, starting with existing settings and evidence rather than invented customer capacity promises. Missing necessary bounds are implementation gates.
- Seven days means 168 elapsed hours after terminal success/failure, independent of display calendar. The clock definition and unchanged deadline on redelivery are explicit specification interpretations of the user's seven-day retention choice. A new retry attempt has its own lifecycle; it does not extend its predecessor's deadline.
- Destructive verification uses only phase-specific disposable projects and a separate test database/environment. Deployment or destructive production actions are not authorized.
- Runtime completion requires actual evidence. This specification and checklist do not establish that conversion, background processing, recovery, or cleanup worked in this session.

## Clarifications

### Session 2026-11-12

- Q: What original-file retention should apply after terminal success or failure? → A: User chose “نگهداری محدود ۷ روزه برای عیب‌یابی، سپس حذف”. Original bytes therefore have a seven-day diagnostic window; temporary conversion artifacts are removed after processing, and action history/results remain. The alternatives of immediate deletion and 24-hour retention were not adopted.
