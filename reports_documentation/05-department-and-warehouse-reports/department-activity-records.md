# Contract: Department Activity Records (Warehouse Fields)

**Feature**: `001-warehouse-report-fields`  
**Base path**: `/api/v1/projects/{project_id}/department-activity-records/`  
**Auth**: JWT + project membership / permissions (unchanged)

## Resource: DepartmentActivityRecord

### Shared response fields

| Field | Type | Always present |
|-------|------|----------------|
| id | string/uuid | yes |
| project_id | string/uuid | yes |
| department | enum string | yes |
| date | `YYYY-MM-DD` | yes |
| location | string | yes (may be `""`) |
| activity_description | string | yes (may be `""`) |
| contractor | string | yes (may be `""`) |
| unit | string | yes (may be `""`) |
| description | string | yes (may be `""`) |
| material_type | string | yes (may be `""`) |
| quantity_in | number/string decimal | yes (default `0`) |
| quantity_out | number/string decimal | yes (default `0`) |
| consumption_location | string | yes (may be `""`) |
| supplier | string | yes (may be `""`) |
| created_at | ISO datetime | yes |
| updated_at | ISO datetime | yes |

Decimal fields serialize as JSON numbers or decimal strings consistent with existing DRF decimal handling in this codebase—clients must accept either; web types use `string | number` if needed for precision.

---

## POST `/` — Create

### Warehouse body (`department: "warehouse"`)

```json
{
  "department": "warehouse",
  "date": "2026-10-01",
  "material_type": "سیمان",
  "quantity_in": "10.000",
  "unit": "ton",
  "quantity_out": "2.500",
  "consumption_location": "بلوک A",
  "supplier": "شرکت تامین",
  "description": "optional"
}
```

**Success**: `201` with full record; generic fields stored as `""`.

**Validation errors** (`400`):

| Condition | Field keys (typical) |
|-----------|----------------------|
| Missing material_type / unit / consumption_location / supplier / date | respective field |
| Both quantities ≤ 0 | `quantity_in` and/or non-field / shared message |
| Negative quantity | `quantity_in` or `quantity_out` |
| Generic-only fields sent | ignored/cleared; not required |

### Non-warehouse body (unchanged)

```json
{
  "department": "buildings",
  "date": "2026-10-01",
  "location": "Site A",
  "activity_description": "Pouring",
  "contractor": "Acme",
  "unit": "m3",
  "description": ""
}
```

Warehouse fields cleared to `""` / `0` on save.

---

## GET `/` — List

### Query parameters

**Shared**: `department` (required for department pages), `page`, `page_size`, `search`, `ordering`, `date_from`, `date_to`, `unit`

**Generic filters** (non-warehouse): `location`, `activity_description`, `contractor`

**Warehouse filters** (additive): `material_type`, `consumption_location`, `supplier`

**Warehouse search**: matches `material_type`, `consumption_location`, `supplier`, `unit`, `description` (and may include quantity string forms optionally—minimum is the text fields above)

**Warehouse ordering** (additive): `material_type`, `-material_type`, `quantity_in`, `-quantity_in`, `quantity_out`, `-quantity_out`, `consumption_location`, `-consumption_location`, `supplier`, `-supplier` plus existing date/unit/created_at fields

---

## GET/PATCH/PUT/DELETE `/{id}/`

Unchanged verbs. Update validation same as create based on record `department` (or payload department if allowed—prefer immutable department; if department change is currently allowed, re-validate under target department and clear opposite field set).

---

## GET `export/?department=warehouse`

Returns `.xlsx` with header row (English keys for stability; Persian aliases accepted on import):

`date, material_type, quantity_in, unit, quantity_out, consumption_location, supplier, description`

Non-warehouse export headers remain the existing generic set (with/without `unit` per security).

---

## POST `import/?department=warehouse`

Multipart Excel upload. Required warehouse columns (aliases allowed):

| Canonical | Aliases (examples) |
|-----------|--------------------|
| date | تاریخ, Date |
| material_type | نوع مصالح, Material Type |
| quantity_in | ورودی, Inbound, In |
| unit | واحد, Unit |
| quantity_out | خروجی, Outbound, Out |
| consumption_location | محل مصرف, Consumption Location |
| supplier | تامین‌کننده, تامین کننده, Supplier |
| description | توضیحات, Notes (optional) |

**Response shape**: unchanged `{ created: number, errors: [{ row, errors }] }` (or existing project format).

---

## GET `reports/daily/` and `reports/weekly/`

Query: `department` required. For `warehouse`, PDF table columns:

Date | Material type | In | Unit | Out | Consumption location | Supplier | Description

Generic departments keep prior PDF columns.
