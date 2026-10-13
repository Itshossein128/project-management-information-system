# Data Model: Ranking Reference Verification

This feature adds no persisted application entity, migration or user-data retention policy. Existing DecisionCase/DecisionRun remain unchanged. The following are test fixture and evidence entities.

## PreservedRankingReference

Fields: repository-relative Markdown and DOCX paths; reviewed DOCX SHA-256; extracted-source and code-block SHA-256; exact extraction rules; line/character counts; callable name and ordered argument names; preserved text identity.

Relationship: authenticates the reference used by every arithmetic observation. Validation: unique implementation fence and source paragraph, pinned identity equality, exact text equality except one Markdown separator LF, expected callable/import shape. State: unread → authenticated → eligible for evaluation; any extraction/identity/shape failure → failed, with no execution. Digests are constants, not regenerated expected values.

## ComparisonCase

Fields: stable case ID; requirement/story/SC IDs; family tags; ordered `criteria`, `alternatives`, `weights`, `types`, `matrix`; expected method-specific named scores/order or reference rejection and product code/path; classification `valid`, `invalid` or `representation`; bounded-domain eligibility; optional relation to a scaled/permuted companion case.

Validation: valid fixtures obey the existing dimensions/input rules and bounded numeric set. Expected numbers are literal or documented analytical expressions independent of product/reference outputs. Invalid fixtures violate a named rule; expected product issues can allow appropriate method-specific codes but must require relevant paths. Cases use copied input objects so neither evaluated function can affect the other's input. Compare before/after values to detect mutation.

Non-finite invalid values are encoded in JSON evidence as explicit tagged values (for example an object with `kind: non-finite` and `value: NaN`, `+Infinity` or `-Infinity`); never emit non-standard JSON numeric NaN/Infinity. Runtime invalid fixtures can hold actual float values. Missing/null/empty-string/zero values remain distinguishable.

## Observation

Fields: case ID, method, source (`reference` or `product`), raw returned value or error class, recorded issues/message where useful, per-alternative score, exact ordered identities, field completeness, input-before/after equality, and observed phase.

Validation: outcomes are captured before assertions, so a mismatch remains visible in a failed report. Valid scores must be finite; output membership is unique and complete; output shape is checked before indexing. Extra product fields remain separate. Expected errors are successful rejection checks only when observed and asserted; unexpected errors remain failures.

## VerificationCheck / EvidenceRun

Check fields: stable check ID, case/input, requirement IDs, expected outcome, observations, comparator result/reason, `passed|failed|unrun` status and evidence level. Run fields: schema version, UTC generation time, Git SHA plus relevant dirty source hashes, reference identities, tool versions, command, exit/result status, report completeness and checks.

State: required checks start unrun; evaluation produces observations; status becomes passed only after relevant assertions and pytest setup/call/teardown succeed. A failure remains failed, missing checks remain unrun. Report emission or a green arithmetic subset cannot mark product/browser gates complete. A truncated/unreadable report is incomplete evidence.

## DifferenceRecord / ReusedEvidence

Difference fields: category, sample behavior, current product behavior, source/test references, policy status and acceptance limitation. Exactly six required categories are in FR-012; O01/O02 final policy remains open.

Reuse fields: original artifact path, named check, original date/environment/command, original source hashes, current hash comparison, relevant scope, artifact availability, decision and rationale. State: candidate → accepted reuse when provenance and scope match, otherwise unrun/needs fresh check. Reused browser presentation never becomes arithmetic proof. Reviewer identity/passwords/tokens and full environment secrets are excluded.
