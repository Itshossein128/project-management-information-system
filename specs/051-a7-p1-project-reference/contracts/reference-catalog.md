# Contract: Organization reference catalog

## Organization units and contract types

Unchanged routes:

- `GET/POST /api/v1/organization-units/`
- `PATCH /api/v1/organization-units/{id}/`
- `GET/POST /api/v1/contract-types/`

Write permission remains superuser or group `admin`, `hr`, or `business-setup`. A staff user who is in none of those groups receives 403 and no row is created. Any authenticated user may list.

## Measurement units

- `GET /api/v1/measurement-units/` — any authenticated user. Response items: `id`, `unit_name`, `unit_symbol`.
- `POST /api/v1/measurement-units/` — same writers as organization units.

Request body:

- `unit_name` (required, trimmed, non-empty)
- `unit_symbol` (optional)

Responses:

- `201` with the created unit.
- `400` when the name is blank or matches an existing name ignoring case.
- `403` for an authenticated user who is not an allowed writer.

## Project contract type

`POST /api/v1/projects/` and `PATCH /api/v1/projects/{id}/` accept `contract_type`.

- Empty string is stored as empty.
- Any other new or changed value must equal an active managed contract type `code`.
- `PATCH` may resend the project's current value even when that value is not in the catalog.
- A rejected value returns `400` and does not create or change the project.
- `owning_unit` remains an optional organization-unit id.

## Project status

Clients cannot add a status. Status changes continue through the existing project action routes from specs 008 and 026.
