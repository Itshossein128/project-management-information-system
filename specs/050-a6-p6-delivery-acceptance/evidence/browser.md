# Browser path

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

Command:

```bash
A6_E2E_PLAYWRIGHT_CONFIG=e2e/playwright.a6-p6.config.ts \
  apps/api/.venv/bin/python e2e/a6-p1/run.py
```

Final result: **2 passed** (21.4s). The API was not mocked.

In Persian and in English, the manager used the screen to:

- search for a missing person and see the localized not-found message
- search for and select an existing synthetic person
- assign the viewer and project-manager roles and save one membership
- open advanced permissions and choose Deny for the wage permission
- close the editor, reopen it, and see Deny still selected
- move to Grant with the keyboard, then choose Inherit and see it selected
- set that membership to inactive
- open access history and see that person's name

The direct member read showed the same person inactive with more than one role. The direct history read included a before and after record for that person. No customer data was used.
