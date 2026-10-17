# Contract: Status Undo UI

**Status**: Proposed design, not implemented. **Authority and transport**: [status-undo-api.md](status-undo-api.md)

## Overview entry and fixed destination

Add a focused `ProjectStatusUndoSection` next to the lifecycle bar/archive restore section. Server capabilities, rather than frontend role arrays or member-permissions success, determine entry visibility:

- suspended: existing «ازسرگیری» / “Resume” opens the confirmed `resume` flow, retaining existing operation authority. Remove the immediate `run.mutate("resume")` path; exactly one resume control remains.
- completed: «بازگردانی خاتمه» / “Undo completion” opens `undo_completion`; global admin capability works for nonmember/group-less superuser even when the membership permission request returns 404.
- other current states: no new-write control for these operations. Retained owned sent attempts still have recovery UI independently of current status/capability; mount recovery controllers for saved operations rather than deriving them only from the current status. Server result/POST rechecks current operation authority.

A member editor may resume but must not see completion undo; approval-only/manager assignment alone is not enough for resume. Archive restore stays its own existing control/authority/history. Do not mount the new section behind the lifecycle bar's membership-only early return.

The normal ready user journey is exactly three business steps: choose action, enter reason, confirm. Modal dismissal, content scrolling and loading are not extra confirmations. Do not add a source/target dropdown.

## Preview and confirmation

The accessible existing Dialog contains translated action/title/description, exact project name, current status, fixed destination and effect:

- suspended→active: active-state operations become available under current rules;
- completed→active: the mistaken completion is reversed, subject to current activation readiness;
- completed→suspended: project remains suspended; baseline/commitment restrictions remain and a later resume is a separate action.

Explain that existing documents/financial data/approvals/history remain and prior financial/approval/baseline operations do not run again. Show the original event identity/time in a concise user-facing way if needed to distinguish a repeated cycle; never show internal token/hash/database details as instructions.

Reason has a visible label, whitespace validation and associated help. Confirm is disabled for pending dispatch, initial loading/refetch, query error, missing gates or blank reason; submit handler independently uses the same safeguards. No cached preview may enable confirmation until its current fetch succeeds. For target suspended there are no activation gates.

Cancel, Escape and close before dispatch clear unsent reason and write nothing. After dispatch, close/Escape hides the modal only; explain that it does not cancel a sent operation. A retained recovery notice remains available outside the modal. Keyboard focus, tab order, labels, visible focus, viewport scrolling and RTL/LTR must work on desktop/mobile.

## Preview failures are read failures

Explicit localized error states, including when older preview data exists:

- permission loss: unavailable action/access guidance; disable confirmation;
- unavailable/deleted/changed project: review refreshed detail/current state and retry only if applicable;
- network/service failure: check connection and retry preview.

Provide a read-only “Retry preview” control. No request UUID or pending POST body is created by opening/retrying preview. Never describe a failed GET as “restoration failed/rolled back” or as an unknown mutation result. Retry success supplies fresh context before an explicitly confirmed write.

## Readiness/remediation journey

Render all missing manager/scope/amount items together. Use fixed settings links with existing `#restore-manager` and `#project-change-requests` anchors; share the existing manager selector rather than build another user editor. Use server `can_perform`/remediation context so a nonmember admin can reach authorized controls and an ordinary resumable member is directed according to their actual field authority.

- Suspended: normal existing manager/CR rules remain, including edit and separate approval policy.
- Completed-origin-active: manager remains normal authorized manager-only PATCH; new CR form is limited to currently missing scope/amount. Hide employer/other protected inputs and already-filled fields. Existing open CR uses its actual server actions, including permitted cancellation, without silently becoming a bound remediation.
- Completed-origin-suspended: no mandatory repair path is added; an incomplete project can return to suspended.

Keep existing CR reason minimum, open-request uniqueness and SoD. A group-admin author sees no self-approve control; an existing eligible other approver (or current superuser exception) acts through normal CR workflow. Stale bound CR must not offer unusable submit/approve actions; show allowed cancel/rejection under current authority. Direct protected-field PATCH is never a repair shortcut.

Before following a remediation link save only the unsent reason in a draft namespace keyed by actor/project/operation. On return read that draft, obtain fresh preview and require explicit confirmation; no automatic POST or old-token reuse. Completing data leaves current status unchanged. Explicit abandonment/logout clears drafts. A different actor/project/operation never sees the text.

## Sent request state and recovery

Use typed `StatusUndoOperation = resume|undo_completion`; do not cast it into archive-only RestorePreview/Receipt. Key the controller by actor/project/operation. Pending namespace is distinct from unsent drafts and existing archive attempts; it stores the frozen three-field POST body plus origin operation/source event for display/routing.

1. Mint request UUID only on explicit valid confirm. Save the exact body before POST; while unresolved do not mint a replacement for the same operation or let edited text change its payload.
2. Unknown network/unclassified server failure preserves the original body, operation and event, including after reload/navigation. Show “result unknown”, Check result and Retry same request. Do not show a new write as if the earlier one failed.
3. Check uses the owned result route for the saved operation even when current project now has another status. `not_recorded` is inconclusive; retain the frozen request and safe retry.
4. Evidenced applied/replayed/completed lookup clears only the matching request ID, closes its modal, refreshes authoritative queries and renders original receipt separately from current state. Replayed results do not emit another fresh-success notification or add history.
5. A definite validation/context rejection resolves the rejected attempt, obtains current details/preview and requires explicit new confirmation. Known-rollback 503 keeps the exact request available for retry. “Already applied” refers to an earlier source-event outcome, not an independent new success.
6. Permission loss clears the private attempt and action; no automatic retry. Logout/account replacement clears new namespaces through existing auth cleanup only after stored-session validation is complete. Never clear a valid pending attempt during initial auth validation merely because user is temporarily unresolved.
7. Asynchronous completion handlers verify mounted actor/project/operation ownership; storage removal also compares request UUID. Late A response cannot clear B, a newer same-key request or a signed-out account's state, nor disclose its receipt in another account's toast. Preserve the origin's safe lookup when its view is abandoned.

The AppShell currently remounts route content on pathname change. That is current source evidence, not a substitute for controller ownership. Real-browser cache/account navigation tests must first demonstrate actual behavior; don't manufacture a failure by removing the shell's existing protection.

## Query refresh and safe history

On evidenced completion only, invalidate actual keys `['project',projectId]`, `['projects']`, `['status-undo-history',projectId]`, `['portfolio-summary']`, `['portfolio-dashboard']`. Current state is shown after refetch; no broad QueryClient clear or optimistic active status for cancel/unknown/not_recorded. Operation previews are stale-on-open and scoped by actor/project/operation. Both portfolio queries must be tested with warm caches within current 15-second freshness, including actual refetch.

Add `ProjectStatusUndoHistory` under `can_view_status_undo_history`; key it by project ID, default 50/max 100 pagination. Display undo operation, actual from/to, reason, performer and time; include original event's from/to/time/actor so the initial decision is preserved and distinguishable. Use a fixed safe projection, localized empty/error/retry/next/previous states and correct source labels (never hardcode archived). Do not replace or merge the existing archive history surface.

## Bilingual meaning requirements

Use new `projectStatusUndo` fa/en strings while retaining existing project.resume status/action labels. Backend Persian catalog and stable error codes must agree with client mappings. Required meanings include:

- «خاتمهٔ پروژهٔ {name} بازگردانده شد؛ وضعیت فعلی: {status}.» / “Completion was undone for {name}; current status: {status}.”
- «پروژهٔ {name} از تعلیق به فعال بازگشت.» / “{name} resumed from suspended to active.”
- «این اقدام قبلاً ثبت شده است؛ نتیجهٔ اصلی و وضعیت فعلی را بررسی کنید.» / “This action was already recorded; review its original result and the current state.”
- «نتیجهٔ درخواست مشخص نیست؛ نتیجهٔ همین درخواست را بررسی یا همین درخواست را دوباره ارسال کنید.» / “The result is unknown; check this request's result or retry the same request.”
- Preview-unavailable means the preview could not load and can be retried; it does not assert whether any earlier POST succeeded or rolled back.
- Missing gates, read/write permission loss, changed context, required reason, source/destination effects, draft retention, cancellation and post-dispatch dismissal are translated and actionable.

No raw error keys, token, traceback or implementation instructions as the product explanation. Formatting must distinguish historical event time from undo time using locale-aware display and machine-readable `time` datetime attributes.
