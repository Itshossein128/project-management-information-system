# Evidence tooling

Local inventory rechecked on 2026-11-23 UTC.

- Google Chrome 158.0.8127.36 via `google-chrome --version`.
- Playwright 1.63.0 via `pnpm exec playwright --version`.
- API virtual environment with Python 3.12.3, Django 4.2.11 and openpyxl 3.1.5.
- LibreOffice Calc 24.2.7.2 at `/usr/bin/soffice`. The Codex PATH override resolves to a LibreOfficeDev 26.8 alpha build. Use an explicit binary path and record it in the recalculation log.
- Poppler `/usr/bin/pdfinfo` and `/usr/bin/pdftoppm` 24.02.0. The PATH overrides report 26.05.0.
- GNU `sha256sum` 9.4 via `sha256sum --version`.

`bash apps/api/django.sh seed_a1_reference_fixture --help` resolved the synthetic fixture loader. For isolated regression work, use a separately configured PostgreSQL test database and local cache configuration per the repository test setup. Capture that environment's identity with its evidence. The synthetic report has not been loaded on a confirmed candidate. The focused regressions below use their own pytest fixtures in an isolated database.

For the candidate workbook, use a separate Calc profile and recalculate a copy. Use Poppler for PDF captures. Check the original bytes with `sha256sum -c manifest.sha256` and `sha256sum -c artifacts.sha256` when the frozen archive is available. [Validation quickstart](../quickstart.md)

## Local regression results

The [quickstart](../quickstart.md) suite ran with Django 4.2.11 against a fresh PostgreSQL test database selected by a unique `TEST_DATABASE_NAME`. The root pytest fixture supplied an in-memory cache. It returned **34 passed, 2 deprecation warnings in 129.18 seconds**. Coverage included the B02 version-integrity module, the B03 Excel/PDF unknown-versus-zero machinery regression, and the B04 filter/totals module. These are checkout regression results. Candidate provenance, downloads, latency and employer review are pending.
