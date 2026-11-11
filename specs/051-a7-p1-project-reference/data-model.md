# Data Model: A.7-P1 Reference Project

No new tables and no migration. Existing rows stay valid.

## Project.contract_type

- Stored as text, maximum 60 characters, blank allowed.
- On create, blank or the `code` of an active `ManagedContractType`.
- On update, the same rule, except the value already stored on that project may be saved again even when it is not in the catalog.
- Unknown new values are rejected and the project row is not created or changed.
- This field is not the contract record's `contract_type` / `contract_type_ref`.

## OrganizationUnit

- Unchanged. Create and update stay limited to superuser and groups `admin`, `hr`, and `business-setup`.
- Authenticated users may read.
- A unit may still be chosen as `Project.owning_unit`.

## ManagedContractType

- Unchanged catalog. The project field stores the catalog `code`, not the row id.

## Unit

- Unchanged columns: `id`, `unit_name`, `unit_symbol`.
- Create is added on the existing list route for the same writers as organization units.
- `unit_name` is required after trimming.
- A second unit whose name matches an existing name, ignoring letter case, is rejected. Uniqueness is enforced in validation because the table has no unique constraint and this phase does not migrate it.

## Project status

- Unchanged `ProjectStatus` choices and transition constraints.
- No status catalog table is added.

## Reference scenario identity

- Project code `A7P1-REF` is reserved for the automated scenario in the test database.
- The scenario also stores an owning unit, an active contract type, six charter sections, and three nested work packages.

## Schedule reference files

- `real-data/plan.mpp` is not a model and is not modified.
- Authored examples live under this feature's `evidence/fixtures/` and are not imported by this phase.
