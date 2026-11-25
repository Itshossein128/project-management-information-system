# A.1.04 candidate evidence

**Status** Isolated synthetic candidate established. Candidate evidence collection is in progress.

The user confirmed an isolated test environment with synthetic data on 2026-11-24. This tracked index points to the controlled archive at `/home/hossein/.local/state/velora/a104-isolated-433dc98` (mode `0700`). Keep credentials and session tokens outside the archive.

- **Phase selection** The Stage 4.1 dispatch selected A.1 from `/delivery-plan`. The selected candidate is `a104-isolated-433dc98`. Its web app runs at `http://127.0.0.1:5178` and API at `http://127.0.0.1:8171/api`.
- **Evidence ownership** The user selected the target class. The local operator built and identified the candidate, and the Speckit Implementer collects 061 evidence. A separate verifier must review the expected values and B05 evidence. Deployment QA owns 062 verification. The delivery agent owns the 063 status decision. The employer may review completed items after deployment to the designated test site. The candidate has distinct project-scoped synthetic preparer, approver and read-only verifier accounts. Authentication and the verifier's read of the starting Draft succeeded.
- [Tooling and isolated fixture procedure](tools.md)
- [Pinned deployment and runtime evidence](deployment.json)
- [Baseline hashes, API snapshot and starting Draft](inputs/reference-version.json)
- [T008 independent QA](#t008-independent-qa)
- [Controlled day 13 lifecycle inputs and independent API and database review](/home/hossein/.local/state/velora/a104-isolated-433dc98/lifecycle/independent-review.json) and [browser observations](/home/hossein/.local/state/velora/a104-isolated-433dc98/lifecycle/browser-observations.json)
- [Historical QA reconciliation](b05/prior-evidence.md) and [draft B05 register](b05/dispositions.json)
- [Blocked candidate receipt](handoffs/061-candidate.md)

## T008 independent QA

Independent QA passed all 113 expectations across 18 contract sections for Draft v1 at SHA-256 `aef5d6efed8b2ca56aaa9e77b17b8282c3207748b3a9d70a301245428632064d`. [Reviewed revision 2](/home/hossein/.local/state/velora/a104-isolated-433dc98/expectations/expected-values-r2.json) · [Passing receipt](/home/hossein/.local/state/velora/a104-isolated-433dc98/expectations/review.md) · [Revision 1 receipt](/home/hossein/.local/state/velora/a104-isolated-433dc98/expectations/review-r1.md)

T023 remains open for the browser source-link 404, the legacy 192.00 person-hours display and full lifecycle reconciliation. The API process and web bundle identities are recorded in `runtime-verification.json` in the controlled archive.

On 2026-11-24 UTC, Stage 4.2 verified the local archive mode and both recorded baseline hashes. An unauthenticated request to the local delivery plan redirected to login, and API health returned OK without a build identifier. The browser access host was unavailable for a fresh authenticated check. The latest listed deploy workflow was still verifying required CI checks. See the [deployment record](deployment.json) and [workflow run](https://github.com/Itshossein128/project-management-information-system/actions/runs/45356211206).

A.1.04 remains open pending a verified 061 bundle, 062 evidence for the same manifest, and an evidence-based delivery status under 063.

[Tasks](../tasks.md) · [Evidence contract](../contracts/candidate-evidence.md) · [Validation quickstart](../quickstart.md) · [062 specification](../../062-a1-deployment-verification/spec.md) · [063 specification](../../063-a1-employer-acceptance/spec.md)
