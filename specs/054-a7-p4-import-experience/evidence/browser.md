# Browser evidence: A.7-P4 import experience

**Date**: 2026-11-12  
**Current status**: Native MPP blocker resolved; the final XML/MPP/XER matrix passes. Earlier sections retain the historical failure and narrower passes.  
**App**: `http://127.0.0.1:5173` against the local API on port 8000  
**Project**: `A7P4-IMPORT-EXPERIENCE` (`91884a98-0f32-4e73-b2ef-b6f075f18ce6`)  
**Account**: the local development administrator  
**Browser**: headless Chromium 1243. The Cursor browser connection timed out, so these journeys were driven with Playwright against the running app.

The sample file is an XML schedule whose work-package code is `ZZ1`. A first attempt with code `1` failed in this development database with the existing `wbs_path_key` collision on path `005M`. That is the same tree-insertion collision recorded in the phase 3 verification, not a second importer. The screen showed the translated failure «واردسازی برنامه ناموفق بود.» and did not show the database exception.

## Journeys

| Journey | Desktop 1280×800 | Phone 390×844 |
| --- | --- | --- |
| Persian rejection of a `.txt` file | Shown. The message names the accepted file types. | Shown. |
| Persian preview of XML | Kind «XML مایکروسافت پراجکت». Warnings «تقویم فایل اعمال نشد.» and «پیش‌نیاز در فایل نیست.» Figures include 3 rows in the file. | Same. |
| Persian confirm | «برنامه وارد شد.» Links «مشاهده ساختار شکست» and «مشاهده فعالیت‌ها». | Same, including the unchanged-plan result on the later pass. |
| English refused replacement | «Cannot replace a schedule that has activities.» Confirm stayed unavailable. | Same. |

Screenshots: `evidence/screenshots/`.

## Keyboard and interrupted status

On the desktop width in English, Preview and Import were activated with Enter after focus. The file itself was attached to the file input because a headless file dialog cannot be driven. The result was the unchanged-plan message.

The status request was then blocked. Closing and reopening the journey showed «The connection was interrupted. This import is still the same attempt.» and did not call that attempt a finished failure. Screenshot: `evidence/screenshots/desktop-interrupted-en.png`.

## Second file

While a preview or confirm request is in progress, the screen ignores another click, file choice, or drop. A separate drop during the preview was not captured: the preview returned before a second drop could be timed. The API test `test_inflight_start_returns_the_same_task_and_finished_status_does_not` shows that a second start for the same person, project, mode, and bytes returns the first task and does not create another job.

## Limits

- This is not a separately running worker. The local API completes the import task inside the request.
- The file dialog, a live drag-and-drop during a slow preview, and an employer `.mpp` click-through were not part of this browser pass.
- No shared or UAT project was imported into.

## Final implementation-session recheck

The reproducible [browser-recheck.mjs](browser-recheck.mjs) ran against the final frontend changes and the real local API on the same disposable project. It uses one authenticated session across four fresh contexts. Run from the repository root with `node specs/054-a7-p4-import-experience/evidence/browser-recheck.mjs`; an optional `IMPORT_TEST_AUTH_FILE` supplies a local development login response without committing credentials. Machine-readable outcomes are in [browser-results.json](browser-results.json).

All four combinations passed: English and Persian, each at 1280×844 and 390×844. Each exercised:

- Wrong-extension rejection followed by selecting a valid XML file.
- Real XML preview and warnings, with a real second-file drop while the preview request was held. Only one preview was sent, and the selected filename remained the original long bilingual filename.
- Refused replacement with Import disabled, followed by choosing Add.
- A real XML start followed by deliberately aborted status requests. Retrying status recovered the actual result with exactly one XML start request.
- XML result links and explicit Choose another file, which cleared the terminal remembered attempt.
- A real Primavera XER preview, confirmation, and result. The authored fixture reuses this disposable project's `ZZ1` root and adds its own child/activity.
- Closing during a held preview and reopening after the dialog finished closing. The late preview was discarded and no confirmation for it appeared.

Mode selection, Preview, Import, status retry, and the post-result choose-another action were activated by keyboard. The automated browser supplied the file input; a native operating-system file-picker interaction was not tested. The delayed-close regression uses the modal close button. A first runner attempt reopened during the closing animation and timed out; waiting for the closed dialog resolved that test timing issue. Repeated logins also hit rate limiting; the final runner reuses one session.

### Illustrated guide

1. Choose a supported file; review its name, recognized format, structure, figures, and warnings in the preview.
2. Choose Add or Replace. Protected replacement displays a reason and disables Import.
3. Confirm once. If status is interrupted, use Check the import again; this reads the same task.
4. Read the stored result and open the work breakdown or activities. Choose another file explicitly to begin again.

Final Persian phone result: [XML](screenshots/recheck-390-fa.png), [XER](screenshots/recheck-390-fa-xer.png).
Final English desktop result: [XML](screenshots/recheck-1280-en.png), [XER](screenshots/recheck-1280-en-xer.png).
Earlier preview/refusal/interrupted illustrations remain in `screenshots/`.

### Native MPP blocker — T021 remains open

The genuine `duration-test9.mpp` fixture reached a preview recognized as Microsoft Project. Its activities have no resolvable package parent, so it is fully omitted and is not suitable evidence of a successful stored import.

The unchanged employer file `real-data/plan.mpp` was then previewed and confirmed with Add on the disposable project. Its job failed with `import_failed`: the database rejected WBS insertion with `duplicate key value violates unique constraint "wbs_path_key"`, path `005M`. This is the previously recorded populated-database tree insertion defect. The wizard showed the localized generic import failure and did not expose the database exception. Native MPP success through the full browser journey remains unproven. T021 was reopened rather than treating the passing XML/XER matrix as full completion.

Remaining limits: no separately running worker, no live project/account-switch browser scenario, no operating-system file-dialog test, and no successful native MPP full journey. No dates or date controls were added to the preview tree.

## Final correction: native MPP blocker resolved

The mutable-code sorting defect was reproduced and corrected as described in [wbs-path-root-cause.md](wbs-path-root-cause.md). After restarting the local development API to load the correction and signing in with a fresh session, the unchanged browser runner passed **all four combinations** with XML, real native MPP (`real-data/plan.mpp`), and XER through preview, confirmation, and result. No database reset was performed.

The first successful MPP job was `d337aa6c-672f-48fa-b809-9c35c5af91d6`: **6 packages, 72 activities, 72 relationships** created from **80 source rows**. The next three confirmations reported no change and created zero rows/relationships. After the matrix the disposable project had 8 live packages, 75 activities and 72 relationships (including its earlier XML/XER work). Direct database reads confirmed these figures. WBS structural checks remained clean.

Final MPP illustrations: [English desktop](screenshots/recheck-1280-en-mpp.png), [Persian desktop](screenshots/recheck-1280-fa-mpp.png), [English phone](screenshots/recheck-390-en-mpp.png), [Persian phone](screenshots/recheck-390-fa-mpp.png). Machine-readable outcomes: [browser-results.json](browser-results.json). `starts: 2` means one XML and one MPP start; the XML interruption/retry assertions run before MPP and require exactly one XML start. XER has its own real start/status path.

T021 is complete. Retained limits: synchronous local task execution rather than a separately running worker, automated file attachment rather than a native operating-system chooser, and no live account/project-switch browser scenario. The original native MPP failure and older limited passes above are historical observations, not the final status.
