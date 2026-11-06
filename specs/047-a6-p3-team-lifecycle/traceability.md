# A6-P3 traceability

Recorded 2026-11-06. This is technical readiness, not customer acceptance or a release.

The messaging channel is not configured. The customer channel owner still has to set an operational email or SMS backend and `TEAM_DELIVERY_TEST_RECIPIENT`. Until then, invitation and recovery responses stay `not_configured` or `not_sent`.

| Requirement | Result | What changed | Evidence |
|-------------|--------|--------------|----------|
| A6-R01, A6-R02, A6-R18 | اصلاح شد | The same person can be selected into two projects. Account creation stays with superuser, admin, or hr, not staff alone and not `manage_members`. | `projects/tests/test_team_lifecycle.py`, `authentication/tests/test_account_lifecycle.py` |
| A6-R03 | اصلاح شد | Duplicate username and mobile, password confirmation, and invalid passwords return translated errors on create and profile edit. | `authentication/tests/test_account_lifecycle.py` |
| A6-R04, A6-R08 | اصلاح شد | Visible account status controls sign-in. Alignment does not re-enable a blocked person. A project dossier can no longer change that status. | `authentication/tests/test_account_lifecycle.py` |
| A6-R05, A6-R06, A6-R07 | اصلاح شد | Logout refuses another person's refresh token. Password reset does not claim delivery when the channel is not operational. Suspended accounts cannot refresh. | `authentication/tests/test_credential_security.py`, `authentication/tests/test_account_lifecycle.py` |
| A6-R19 | اصلاح شد | The team list keeps a null last sign-in empty and does not move it on a membership update. | `projects/tests/test_team_lifecycle.py` |
| A6-R20, A6-R23, A6-R24, A6-R25 | اصلاح شد | Archiving one membership leaves the other project and the account unchanged. Delegation can be removed. A person with history cannot be deleted. | `projects/tests/test_team_lifecycle.py` |
| A6-R21, A6-R22 | اضافه شد | Invitations connect, expire, and cancel without granting a second membership. Concurrent uniqueness returns `already_member`. | `projects/tests/test_team_lifecycle.py` |

Browser on project `3164541f-810b-4a56-bb45-d6502b9b9914`, Persian UI: the member screen showed search, five statuses, a blank last sign-in, and the create-person form. The account screen showed active, inactive, and suspended. No live account was changed.
