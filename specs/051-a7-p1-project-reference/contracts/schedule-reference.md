# Contract: Schedule reference for phase 3

This phase does not change import behavior. The matrix records what the current MSP XML parser keeps, so phase 3 can compare an importer without treating that parser as an independent golden source.

## Employer file

- Path: `real-data/plan.mpp`
- Must remain byte-for-byte unchanged.
- Fingerprint and size are recorded in `evidence/control-figures.json` by SHA-256 of the file bytes.
- Version is the file's observed container identity recorded beside the hash. It is not a product version.

## Hand-counted examples

Each example under `evidence/fixtures/` has expected counts in `evidence/control-figures.json`. Those counts are taken from the authored file text (task rows, summary flags, predecessor links), not from an importer run.

| Example | Intent |
| --- | --- |
| `branch.xml` / `branch.xer` | One parent and two sibling leaves |
| `milestone.xml` / `milestone.xer` | A zero-duration milestone whose milestone flag is outside current support |
| `relation.xml` / `relation.xer` | One finish-to-start link between two leaves |
| `dangling-predecessor.xml` / `dangling-predecessor.xer` | A predecessor identifier that is not in the file |
| `not-a-project.xml` | An XML root that is not a project file |

## Field support recorded for phase 3

Supported on the current MSP XML task mapping when present:

- Task UID, name, outline level, outline number, WBS code, summary flag
- Start and finish dates in `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`
- Duration `P{n}D` or `PT{n}H` with a non-zero hour count, converted with an 8-hour day
- Percent complete, total slack, free slack, critical flag
- Predecessor UID, type (`1` FS, `2` SS, `3` FF, `4` SF), and link lag

Outside current support, to be decided in phase 3 rather than dropped silently to force a total:

- Milestone flag as its own field
- Duration `PT0H0M0S` (zero). The current duration rule does not turn it into zero days.
- A predecessor UID that is not among the parsed tasks
- Calendars, constraints, resources, baselines, and cost fields

XER examples use the same intents. Their column layout follows the existing tab-separated `ERMHDR` / `%T` / `%F` / `%R` shape. They are not a second golden produced by the P6 parser.

## Historical probe (not a target)

Source: `output/a7-requirements-2026-11-10/evidence/import-probe-observations.json`, observation date 2026-11-10. Produced by the product's importer family. Not an approved expected total.

| Id | Historical observation | Cause recorded with it |
| --- | --- | --- |
| H-COUNT-80 | 80 parsed tasks | 6 summary tasks and 74 leaves in that probe |
| H-LINK-83-79 | 83 predecessor links in the parsed source, 79 relations created | Four links were not created. They are historical observations, not an approved target that 83 must equal 79 |
| H-PRED-8055 | Predecessor UID 8055 not found for پایان | UID 8055 is present among the 80 tasks as the summary «تکمیل تاسیسات و نازک کاری بلوک 31-30». The activity map used at import contains only leaves, so this is not a missing identifier |
| H-PRED-8084 | Predecessor UID 8084 not found for پایان | UID 8084 is present among the 80 tasks as the summary «تکمیل تاسیسات و نازک کاری بلوک 39-38». The activity map used at import contains only leaves, so this is not a missing identifier |
| H-PRED-8102 | Predecessor UID 8102 not found for پایان | UID 8102 is present among the 80 tasks as the summary «تکمیل تاسیسات و نازک کاری بلوک 29-28». The activity map used at import contains only leaves, so this is not a missing identifier |
| H-PRED-8120 | Predecessor UID 8120 not found for پایان | UID 8120 is present among the 80 tasks as the summary «تکمیل تاسیسات و نازک کاری بلوک 37-36». The activity map used at import contains only leaves, so this is not a missing identifier |
| H-DUR-شروع | Duration `PT0H0M0S` not parsed for شروع | Zero-duration form is outside the current duration rule |
| H-DUR-پایان | Duration `PT0H0M0S` not parsed for پایان | Zero-duration form is outside the current duration rule |

No link is removed or reinterpreted in this phase to make 83 equal 79.
