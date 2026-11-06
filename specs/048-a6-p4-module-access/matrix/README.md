# A6-P4 operation matrix

Columns for every active operation row:

| Column | Meaning |
|--------|---------|
| module area | M01–M29 id and name |
| operation | Human action name |
| methods/paths | HTTP methods and URL/action |
| roles | Accounts tested |
| projects A/B | Two independent projects |
| expected allow/deny | Policy expectation |
| result | pass / fail / N/A |
| evidence | Test module, command, or note |
| defect class | `policy` \| `project-scope` \| `sensitive-field` \| `action/SoD` \| `file` \| `UI` \| `queue/session` |
| N/A reason | Required when result is N/A |

Do not mark a row green without evidence. Package trackers live beside this file.
