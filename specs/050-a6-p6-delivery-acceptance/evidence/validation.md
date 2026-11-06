# Validator

Negative samples, each exiting 1 without printing a secret value:

- `fixtures/not-run-counted-as-pass.json`: `not_run is not a pass`
- `fixtures/quoted-secret.json`: `secret pattern matched; value omitted`
- `fixtures/fail-without-defect.md`: `fail cites a defect`
- `fixtures/recovery-url.md`: `secret pattern matched; value omitted`

`validate_package.py` on `evidence/` also scans the sibling `guide.md`, skips `fixtures/`, checks Markdown `result` and `technical_result` cells, and exits 0 with `package evidence accepted`.
