# IPCAS Scope Map

Maps the **engineering blueprint** to the **current monorepo implementation**. Use this to avoid naming and feature mismatches during development.

## Terminology

| Blueprint | Code (monorepo) | Notes |
|-----------|-----------------|-------|
| Project | `Business` | Same tenant scope; do not rename without API versioning |
| `project_members` | `UserBusinessAssignment` | Includes wage/tools/dates |
| `project_positions` | `BusinessJobPosition` | Per-business job titles |
| `daily_reports` | `DepartmentActivityRecord` | **Not equivalent** — use "department activity log" in UI/docs |
| Materials ledger | `Item`, `DynamicTableRow`, `SpaceMaterialRequest` | Fragmented; none match blueprint Module 11 |

## Module status (summary)

| Module | Status |
|--------|--------|
| 1 Project Foundation | Partial — `Business` CRUD only |
| 2 WBS & Activities | Not started |
| 3 Schedule | Not started |
| 4 Daily Field Report | Partial, misaligned — department logs |
| 5–8 Progress, Cost, Cash, IPCs | Not started |
| 9 HR | Partial — users, assignments |
| 10–17 Equipment, Materials, Procurement, etc. | Not started or misaligned |
| 18 Access Control | Partial — JWT + Django Groups |

## Stack alignment

| Blueprint | Monorepo |
|-----------|----------|
| PostgreSQL | Yes — required via `DATABASE_URL` |
| Redis, S3, message bus | Not yet |
| Microservices | Single Django monolith (acceptable for now) |
| Offline PWA | Not yet |

## API paths

Blueprint uses `/projects`; implementation uses `/api/businesses/`. Generate TypeScript types from live OpenAPI at `/api/schema/`, not from blueprint paths.

## Warehouse naming

Route `/businesses/:id/warehouse` is a **department activity log**, not stock inventory (Module 11).

## Auth gaps (known)

- Password reset completion returns 501
- Token refresh exists on API; frontend `restoreSession` is stub
- `usePermission()` defined but unused in web UI

See full blueprint: [IPCAS_Engineering_Blueprint.md](./IPCAS_Engineering_Blueprint.md)
