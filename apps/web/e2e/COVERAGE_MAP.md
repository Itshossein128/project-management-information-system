| Module | Flow | Tested Branches | Total Branches | Coverage Score |
|---|---|---|---|---|
| AUTH | Standard login and session management | 2 | 8 | 25% |
| AUTH | Role-based redirect after login | 1 | 8 | 12% |
| PROJECT | List & Create | 4 | 10 | 40% |
| WBS | Tree Operations | 3 | 10 | 30% |
| ACTIVITIES | CRUD & Relations | 3 | 10 | 30% |
| SCHEDULE | Baseline & Import | 2 | 10 | 20% |
| DAILY REPORT | Create & Workflow | 5 | 20 | 25% |
| OFFLINE | Sync & Conflict | 2 | 15 | 13% |
| FINANCE | Budget & Cost | 2 | 15 | 13% |

## Sprint 3 coverage notes

- `e2e/tests/sprint3-schedule.spec.ts` — WBS rename + reparent (`sorted_child`), activity create + FS relation + cycle reject, MSP XML preview→import
- WBS DnD affordance asserted via `draggable`; reparent exercised through the same move API the drop handler calls
- BoQ linkage on activities is deferred (not in e2e scope)
