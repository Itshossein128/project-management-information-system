# Contract: AHP Workspace and History

Surface: `/projects/:projectId/decision-support`, AHP panel for a saved case selecting `ahp`.

## Owned matrix state

- Parent owns actual full-precision criteria/matrix. Rendering and submission use the same values; rendering never invents judgments.
- Initialize diagonal 1 and off-diagonal null. n=1 owns `[[1]]` and runs without editing a disabled cell. Blank never silently becomes equality.
- Reconcile criteria changes by exact trimmed names/order: preserve retained pairs, blank new/renamed pairs, remove deleted ones. Malformed saved values produce visible validation rather than silent replacement. Shared criteria changes still honor ranking consistency checks.
- Editing either direction synchronizes full-precision inverse; clearing clears both. Invalid/non-finite values do not trigger invalid division.
- Offer Saaty labels 1..9 and 1/2..1/9, submitted as numbers, plus finite positive custom decimals. Out-of-standard-scale values show pair advice, not a hidden cap.
- Diagonal locked/read-only at 1; rounded display never rounds submitted state.

## Save/run and result lifecycle

Local validation can check completeness, dimensions, types, diagonal/reciprocal structure. Weighting, matrix-vector calculation, lambda, CI and CR remain in backend. Consume server consistency boolean; client may format and synchronize reciprocals.

Save only changed AHP fields, await success, then POST the method. No run after failed save. Requests are separate; execution snapshots server case state at its read. Pending state prevents repeat clicks; no new global idempotency guarantee. Refresh relevant case/history queries on success. No automatic weight transfer.

Display criterion/rank/decimal/percent/visual weight and lambda/CI/CR. Inconsistent success shows localized `role='alert'` with actual CR and revision advice; consistent status is accessible. Results remain identified by their frozen criterion names when draft criteria change.

## Independent history

Method selection exposes AHP-specific paginated history without removing SAW/TOPSIS history. Selected run shows identity/timestamp/actor, frozen criteria/matrix and stored result. Historical view is clearly labeled/read-only; never overwrite editable draft when inspecting it. Handle older stub/non-AHP runs without casting them to completed AHP results.

Switching cases resets results/errors/history selection; key/reset panel by case ID and ignore late responses from another case/project. A successful run updates only its owning case view.

## Accessibility and bilingual behavior

Localize all labels, scale advice, errors, warnings, empty/pending/current/history states through en/fa JSON. AHP empty copy never asks for alternatives. Stable codes/paths remain untranslated. Verify English LTR/Persian RTL without swapping row/column criterion identity.

Use row/column header scopes and cell names containing both criteria. Associate errors with cells (`aria-invalid`, descriptions) and provide keyboard-accessible issue navigation. Explain locked diagonal. Browser checks cover keyboard scale selection, ten-criterion horizontal scrolling, announcements, language switching and reopen/reload persistence.

Source-boundary tests fail on missing targets and cover client components/helpers. Permit reciprocal updates, input validation and formatting; prohibit geometric means, AHP normalized weight derivation, matrix-vector/eigenvalue computation, CI/CR implementations. Source checks complement API/browser proof.
