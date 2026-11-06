# Delivery package

| Field | Value |
| --- | --- |
| version_id | `a46161d3530edfb78c8ebf94b4786d991bea0ba7` |
| tree_dirty | true |
| environment_name | `blocked_external` — a customer acceptance environment was not named. Developer checks used the isolated pytest database and an isolated browser database only. |
| accounts_note | See `accounts.md`. Synthetic roles only. |
| file_service | `blocked_external` |
| send_channel | `not_configured` |
| acceptor | `blocked_external` — the customer acceptor was not named. |
| sent_at | |
| response_due_at | |
| response_at | |
| report_label | `ready_for_acceptance` |
| decision | `pending` |

Records in this directory are files. This phase adds no product table.

`environment_name` is empty, so the package is not ready to send. `decision` stays `pending`. A decision of `accepted` is the only employer confirmation and is not set here.
