# Validation Guide for A.1.02 and A.1.04 Candidate Evidence

Use this guide during evidence collection after planning approval. Runtime results belong in the candidate archive.

## 1. Establish candidate identity

- Obtain the target and authorized test access from the release owner. Record the exact deployed source SHA and running API/web build identifiers. Verify provenance against the running target and the release record. Repeat the identity check before handoff.
- Resolve the synthetic report SIM-A1-001-12-1406-03-01 (Solar Hijri 1406-03-01, day 12) to the deployed project and selected report UUID/version. Reuse the fixture and contract linked in [the plan](plan.md). If fixture setup is needed for local regression work, inspect `manage.py seed_a1_reference_fixture --help` and use an isolated test database. Evidence from that environment has its own identity.
- Record the controlled input and form revision. Build and independently review expected figures from those sources before comparison.

## 2. Capture section and lifecycle evidence

1. Inventory every section from the pinned contract. Identify the source for each expected value or expected empty state. The seed only populates some sections. Record the applicable source rule for any section expected to be empty.
2. In an authorized synthetic scope, open the initial Draft in the browser and capture matching API details and applicable provenance. Submit using the preparer role and approve with a separate approver. Archive the approved UUID, version, relevant source values and snapshot observations.
3. Open a correction through the product, capture the correction Draft and its parent link, and approve through the same separation of duties. Reopen the earlier approved version and compare its snapshot and the original source data with the before state. Use the contract's browser and API surfaces at each lifecycle point. Record isolated reproduction under its own environment identity.
4. Expect 100% of inventoried sections to have matching values or states and traceable browser/API evidence across the lifecycle. Capture gaps by section/version and keep them unverified. Record the approved version selected for the employer bundle before downloads.

## 3. Download and verify original files

1. Open the selected version with an authorized account. Capture the complete Excel FILE 4 and PDF downloads in each effective export locale through the existing browser journey. Verify the direct version routes under the approved authorization checks.
2. Repeat the downloads for each manifest slot. Compare byte counts and SHA-256 on the untouched files. A different candidate, version or checksum produces an unverified result.
3. Complete recalculation and independent comparison in section 4 before freezing the manifest. Check the archive after linking reconciliation, prerequisite evidence, original files and recalculated Excel by their specified roles. Run the following after preparing both checksum lists per the [contract](contracts/candidate-evidence.md).

   ```bash
   sha256sum -c manifest.sha256
   sha256sum -c artifacts.sha256
   ```

   Expect all files to pass. Re-run verification after moving the archive to its controlled storage location.

## 4. Collect proof for the five B05 findings

- **01** — Record original cache values and formula expectations. Recalculate a copy with an isolated LibreOffice profile and keep the original and recalculated copy in separate directories. For example, from a local evidence working directory with `input/report.xlsx` copied from the original:

  ```bash
  mkdir -p recalc
  calc_profile="$(mktemp -d)"
  soffice --version
  soffice "-env:UserInstallation=file://${calc_profile}" --headless \
    --convert-to xlsx --outdir recalc input/report.xlsx
  ```

  Confirm that Calc actually recalculated the formulas. If the conversion leaves that unverified, open the copy in Calc, run its hard recalculation command, and save the resulting copy. Record the tool result, before/after formula and value comparisons, and errors. Judge missing cached values using the governing export contract. Verify the original digest still passes and record the recalculated workbook checksum and original linkage for each applicable slot.

- **02** — On the same release, use a controlled typical workload with 15–30 activities and 20 materials/equipment rows under recorded standard broadband conditions. Time each format through full file receipt. The criterion passes when both measured times are under 3.0 seconds.
- **03** — Compare figures, units, rounding and null/zero treatment against the independently reviewed expectations. Record discrepancies with the source and cell/page references.
- **04** — Open the candidate workbook print preview or render its print output separately. Capture official PDF pages with Poppler, then compare the workbook and PDF page by page with the reference, including applicable long-report coverage. Record page sizes/counts, mappings, captures and discrepancies. For example:

  ```bash
  mkdir -p comparison
  pdfinfo input/report.pdf
  pdftoppm -r 144 -png input/report.pdf comparison/official
  ```

- **05** — Check the B02/B03/B04 release applicability and relevant regressions. Where isolated pytest verification is needed, use the repo's PostgreSQL/Redis test setup and the candidate checkout:

  ```bash
  cd apps/api/core
  ../.venv/bin/python -m pytest \
    field_reports/tests/test_a1_b02_version_integrity.py \
    field_reports/tests/test_pdf_summary_parity.py::test_b03_legacy_equipment_zero_and_unknown_across_exports \
    field_reports/tests/test_a1_b04_filters_totals.py
  ```

  Attach code-test results separately from deployed evidence. Reconcile the current A.1.02 timeout, earlier export-parity evidence and direct A.1.03 pass against the current A.1.04 QA assertion. Record the A.1.03 evidence and candidate applicability before manifest freeze. Compare the candidate's executed activity count, version and inputs with the historical records reporting five and six rows. Keep applicability unverified where the discrepancy is unexplained. After freeze, attach all five dispositions to the manifest digest.

## 5. Validate the handoff

- Verify one disposition per B05 finding. On copies, independently vary the build, report version, original file checksum, recalculated workbook checksum and downstream manifest digest. Include a section with missing lifecycle evidence. Expect each affected check to stay unverified and required gaps to block handoff.
- Pass the manifest, reconciliation and register to [deployment verification](../062-a1-deployment-verification/spec.md). Verify that the authorization and browser matrices and decision-tree comparisons reference the frozen identity, original download slots, recalculated workbook checksum and unresolved findings.
- Route the complete bundle to [delivery status and employer review](../063-a1-employer-acceptance/spec.md) after candidate and deployment QA pass. Record the agent’s disposition for the same digest. Leave A.1.04 open for missing evidence or a blocking defect.
