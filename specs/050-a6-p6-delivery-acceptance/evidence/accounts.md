# Synthetic roles

accounts_note: the checks use synthetic roles only. No password, reset link, or session secret is written here.

Roles named for the matrix and scenarios:

- organization administrator
- human-resources account administrator
- project manager on project A
- planner / editor on project A
- observer on project A
- observer on project B for the same person
- inactive member
- non-member of project A
- multi-role member
- second approver
- visitor on the legacy item catalog

The customer acceptance environment and the customer acceptor are `blocked_external` because neither was named. Developer checks used synthetic roles on an isolated pytest database and an isolated browser database. These names are roles, not real customer people. No password, reset link, or session secret is recorded.
