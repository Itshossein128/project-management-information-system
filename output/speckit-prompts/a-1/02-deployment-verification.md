/speckit-specify

Specify the deployment verification for A.1.04 (B06) on the exact candidate and reference version identified in 01-candidate-evidence.md. Source: ../../phase-a1/a1-04-qa-findings.json.

DEF-A104-04 (E09) — Require a recorded download authorization matrix on the candidate, using controlled accounts and reference projects. Cover authorized downloads and denial for signed-out users, users lacking the required role, and users outside the report's project. Include direct report/version download access for Excel and PDF. Record expected and actual authorization outcomes, candidate identity and evidence references. For allowed downloads, record file identity against the frozen manifest. Denials must withhold the report and its artifacts.

DEF-A104-05 (Q03) — Require evidence for all 18 daily report sections in Persian RTL and English LTR, on desktop and a 390×844 mobile viewport. Record the report journey, readability and layout, correct version selection and same-version Excel/PDF download. Record locale, viewport, observed results and evidence for each combination.

DEF-A104-06 (Q04) — Require the decision tree under docs/decision-tree/ to be verified against the candidate's deployed export routes and authorization decisions. Record each reviewed route and outcome and reconcile any discrepancies with the intended access rules.

Write observable acceptance scenarios for the roles and environments above. Hand off the candidate-linked verification matrix, decision-tree references and unresolved findings to 03. Give a clear disposition where evidence is missing or the deployment differs from the frozen candidate.
