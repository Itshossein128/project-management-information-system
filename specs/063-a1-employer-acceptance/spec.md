# A.1.04 — Delivery status and employer review

**Decision ratified by the project owner on 2026-11-24.** The owner delegates all completion decisions on the delivery plan to Velora agents. This supersedes the former GOV-01 employer sign-off gate. The employer reviews items marked complete after deployment to the test environment and reports problems to the project owner. Items still in progress are outside that feedback request.

## Requirements

- **FR-001** Before changing a delivery status, the delivery agent verifies the frozen 061 bundle and complete 062 QA for the same manifest digest. The independent QA agent reviews T008 separately from the implementer. Blocking findings, missing evidence and mismatched identities keep the affected item `remaining`.
- **FR-002** The reference day may use realistic, clearly labeled synthetic data (`SIM-A1-001`, 1406-03-01). The employer-facing deployment is the test environment at `https://www.toop-e-ghelgheli-2.ir/login`. Give the employer a versioned guide and limited access through the existing authorization rules. Any changed source SHA, report version or artifact requires re-verification of affected evidence.
- **FR-003** The agent records the delivery disposition with the check date, evidence links, candidate and full source SHA, reference report ID and version, manifest digest, and unresolved findings. The delivery-plan page displays the agent’s status to the employer, who uses the plan to identify items ready for review and communicates issues through the project owner.
- **FR-004** The agent may mark an item `implemented` after its technical evidence passes. Feedback after deployment is triaged against the affected item and version. A confirmed blocking defect returns that item to `remaining` until the fix is verified. A delivery status does not wait for employer feedback, a meeting, or sign-off.

## Success criteria

- **SC-001** Each implemented item has a traceable QA decision for the verified candidate and package.
- **SC-002** A candidate mismatch, incomplete verification or confirmed blocking defect leaves the affected item in progress.
- **SC-003** The employer can follow the guide and inspect the same version when deployed to the test environment. Employer feedback is relayed via the project owner.

[Candidate evidence](../061-a1-candidate-evidence/spec.md) · [Deployment QA](../062-a1-deployment-verification/spec.md)
