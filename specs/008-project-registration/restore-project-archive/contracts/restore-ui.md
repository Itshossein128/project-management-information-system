# Contract: Restore Action and History in Project Overview

**Status**: Proposed, not implemented.
**Spec**: [spec.md](../spec.md) · **Transport**: [restore-api.md](restore-api.md)

## Placement and authority

Extend existing overview/lifecycle UI. Show “خروج از بایگانی” / “Restore from archive” only for an archived project whose server detail reports `can_restore_from_archive=true`. Do not gate this on `edit_project`, `approve_project` or frontend admin-role names. Rework the lifecycle bar's early return only enough to allow this independent capability; preserve other actions.

Add a small read-only restoration history section driven by server `can_view_restore_history` (current project-view authority). Show actor, timestamp, reason and origin/destination; an empty state is localized. Do not expose the restore action merely because history is visible. Paginate with the API's safe receipt projection.

## Dialog and confirmation

Use existing accessible Dialog, form fields and button patterns. Opening fetches a fresh preview. Dialog shows project name, fixed target, effects, reason field, Confirm and Cancel. No destination selector. Keyboard focus enters the dialog, validation is announced, errors use an accessible alert, and focus returns to the originating action on close. Persian uses RTL and current Persian typography; English uses LTR.

Target effects:

- Active: the project resumes availability under existing active-project rules; new definitive baseline/commitment actions become available according to their existing permissions, but none is executed by restoration.
- Suspended: suspension remains; new definitive baselines and binding commitments remain blocked.
- Completed: completion remains; no automatic activation and no new definitive baselines or binding commitments.
- Every target: documents, financial records, prior approvals and history remain unchanged.

Reason is required after trimming; whitespace-only input keeps confirmation disabled and shows localized guidance after attempted submission. Cancel, Escape and dismissal before sending leave status and history unchanged. Once POST starts, disable duplicate confirmation; if the dialog is dismissed afterward, preserve the unresolved operation and expose its pending/result state in the overview. Do not label dismissal as cancellation of an already-sent operation.

## Missing activation information

Preview or POST `activation_gates_failed` displays every missing field together. Preserve typed reason while showing the failure, but obtain a fresh preview before another confirmed submission after remediation.

- Manager: link to project settings and its manager selector using existing `lookupUsers`; retain current edit/global authority and submitted-FK validation.
- Scope/amount: link to the existing project change-request panel with only the missing protected field(s) suggested, available under the narrowly scoped archived remediation rule. Explain submit/approval and the existing non-self-approval rule for group admins. Do not pre-approve a request or save protected values directly.
- If there is an existing open request, point to it and its current review actions; explain the conflict rather than displaying a dead Create action.
- After changes/approval, returning to overview fetches a new preview; the original restore token is invalidated. Completion does not itself restore the project.

For nonmember global admins, membership-permissions lookup may return 404 and `has(edit_project)`/`has(approve_project)` may be false. Settings must independently expose only the manager completion control using `can_edit_manager_for_restore`; do not unlock the full form by pretending membership exists. The CR panel uses `can_create_restore_remediation` for its scoped create form and per-record `restore_remediation_actions` for review buttons, without loosening ordinary field or SoD rules. An open CR remains visible and reviewable under these contextual server actions. History uses its own server capability. Do not broadly change `usePermission` or use frontend role names as a substitute.

No activation checklist is shown for a suspended/completed target. Do not require a new budget approval timestamp or a new positive-value threshold.

## Client operation states and recovery

States: idle → loading preview → ready/incomplete → submitting → confirmed success, known rejection, conflict, or outcome unknown.

Create one UUID `request_id` for each explicit confirmed submission. Freeze its reason and signed confirmation context. Automatic authentication refresh and transport retry reuse that body. A new confirmed submission after actual context change gets a fresh preview and new UUID.

While unresolved, retain `{authenticated_user_id, project_id, request_id, confirmation_token, reason}` in tab-scoped session storage so refresh can resume result checking/retry. Never put these in URLs or analytics. Clear on resolved outcome, sign-out or account switch; another account must not reuse the saved operation. Switching display locale does not change the attempt identity. A separate browser tab acts as a separate attempt and relies on the server's cycle uniqueness.

On network error or an ambiguous server failure:

1. Show an unresolved state with “Check result” and safe-retry guidance; do not optimistically update status/history.
2. Query the saved request-result endpoint. `completed` confirms this operation; show its original receipt plus current state.
3. `not_recorded` is inconclusive while the original request might be running. Offer retry of the exact saved POST, never a new blind operation. Preserve unknown state if checking/retrying still cannot reach the server.
4. `archive_already_restored` explains another operation completed this cycle, uses its actual actor/reason/time, and refreshes current state. Do not claim this user independently restored it.
5. `restore_context_changed` discards old confirmation for writes, refreshes detail/history and requires explicit new preview/confirmation. An old-cycle request must never be transparently adapted to the new cycle.
6. If authority is lost, hide the restore action, stop automatic retries and show a localized permission message; no details unavailable to this user are displayed.

After confirmed success or replay, invalidate project detail, portfolio/status lists and restore history queries. Render `current_project` separately from the historical receipt target; if a later action changed state, say so rather than showing an incorrect active-project success message. Replaying a receipt does not produce a second history entry or a second fresh-success notification.

## Localized message requirements

Use frontend `fa.json`/`en.json` plus backend Persian gettext catalog. Both locales cover: title/action, project/target/effect labels, required reason, pending, every missing gate/remediation, known failure, unavailable permission, stale confirmation, another completed operation, exact replay, unknown outcome, result check and safe retry.

Representative meaning pairs (wording may be polished while retaining meaning):

- Success: «پروژهٔ {name} به وضعیت {status} بازگردانده شد.» / “{name} was restored to {status}.”
- Unknown: «نتیجهٔ درخواست مشخص نیست. وضعیت درخواست را بررسی کنید؛ تلاش مجدد همین درخواست ایمن است.» / “The result is unknown. Check this request's result; retrying the same request is safe.”
- Stale: «وضعیت پروژه از زمان تأیید تغییر کرده است. اطلاعات تازه را بررسی و دوباره تأیید کنید.» / “The project changed after preview. Review the latest details and confirm again.”
- Another success: «این دورهٔ بایگانی قبلاً بازگردانی شده است. سابقه و وضعیت فعلی را بررسی کنید.» / “This archive cycle was already restored. Review its history and current status.”

No raw technical keys, tracebacks or network exception messages as the user explanation. Keep programmatic API codes stable for tests and mappings.
