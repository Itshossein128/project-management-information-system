# API Contract: Measurement Method Configuration & Approval

## Endpoints

### 1. `GET /api/v1/projects/{project_pk}/activities/{activity_id}/measurement/`
Retrieves or auto-creates draft measurement definition for the activity.

#### Response 200 OK
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "activity_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "method": "quantity_based",
  "status": "draft",
  "total_quantity": 1500.0,
  "unit_id": "8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e",
  "milestones": [],
  "evidence_rules": "",
  "pending_change_reason": "",
  "current_version_id": null,
  "approved_at": null,
  "approved_by": null,
  "versions": []
}
```

---

### 2. `PATCH /api/v1/projects/{project_pk}/activities/{activity_id}/measurement/`
Updates draft measurement fields. Locked once approved (`measurement_locked`).

#### Request Body
```json
{
  "method": "weighted_milestones",
  "milestones": [
    {"name": "Earthwork excavation", "weight": 0.25},
    {"name": "Lean concrete blinding", "weight": 0.15},
    {"name": "Reinforcement steel fixing", "weight": 0.35},
    {"name": "Concrete casting and curing", "weight": 0.25}
  ]
}
```

---

### 3. `POST /api/v1/projects/{project_pk}/activities/{activity_id}/measurement/approve/`
Validates basis and freezes snapshot as immutable `ActivityMeasurementVersion`.

#### Validation Rules
1. `quantity_based`: `total_quantity > 0` and `unit_id != null`. Error if missing: `incomplete_measurement_basis`.
2. `weighted_milestones`: at least 1 milestone; weights must sum to 1.0 (100%) within `±0.01%`. Error if missing or unbalanced: `incomplete_measurement_basis`.
3. `evidence_based`: non-empty `evidence_rules`. Error if missing: `incomplete_measurement_basis`.
4. If already approved, return 409 Conflict: `measurement_already_approved`.

#### Error Response: Incomplete Basis (`incomplete_measurement_basis`)
```json
{
  "error": {
    "code": "incomplete_measurement_basis",
    "message": "مجموع وزن milestoneها باید برابر ۱ باشد."
  }
}
```
