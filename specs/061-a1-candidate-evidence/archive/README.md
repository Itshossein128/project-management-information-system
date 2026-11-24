# A.1.04 candidate evidence

**Status** Blocked pending release-owner confirmation.

Spec Kit selected `061-a1-candidate-evidence` and found its plan and tasks. The requirements checklist passed all 16 items. This directory is a local staging workspace with mode `0700`. The release owner still needs to confirm the controlled storage location and authorized participants before candidate artifacts are collected here.

- **Phase selection** The Stage 4.1 dispatch selected A.1 from `/delivery-plan`. Authenticated Chrome confirmed that A.1.04 still appears under the remaining filter on the local site. Its role as the delivery candidate is unverified.
- **Evidence ownership** The release owner identifies the target and supplies provenance. The independent verifier checks the running builds, selected report version, exports, and B05 evidence. Deployment QA owns 062 verification. The delivery owner coordinates 063 with the authorized employer representative. Named owners and controlled verifier access are pending.
- [Tooling and isolated fixture procedure](tools.md)
- [Unverified deployment record](deployment.json)
- [Local baseline hashes and unresolved deployed reference version](inputs/reference-version.json)
- [Historical QA reconciliation](b05/prior-evidence.md) and [draft B05 register](b05/dispositions.json)
- [Blocked candidate receipt](handoffs/061-candidate.md)

Resume at T001. The release owner needs to confirm the intended target environment and URLs, evidence owners, controlled storage location, and authorized verifier access. For T003, obtain the candidate ID and full source SHA and verify the running API and web build IDs. For T004, resolve `SIM-A1-001-12-1406-03-01` and its deployed input snapshot on that verified release.

Stage 4.2 rechecked the local archive mode, both baseline hashes, local HTTP responses, and the latest deployment workflow runs. The latest listed successful run still has workflow head SHA `460a2d629b49e43786177cb546a167a8156f7d2e`. The workflow can accept a separate deployment SHA. See the [deployment record](deployment.json) for what was observed. Candidate-specific exports, manifest freezing, and downstream deployment verification depend on the confirmed release identity. [Production workflow](https://github.com/Itshossein128/project-management-information-system/actions/runs/44354761103)

A.1.04 remains open pending a verified 061 bundle, 062 evidence for the same manifest, and explicit approval of that bundle by the authorized employer representative under 063.

[Tasks](../tasks.md) · [Evidence contract](../contracts/candidate-evidence.md) · [Validation quickstart](../quickstart.md) · [062 specification](../../062-a1-deployment-verification/spec.md) · [063 specification](../../063-a1-employer-acceptance/spec.md)
