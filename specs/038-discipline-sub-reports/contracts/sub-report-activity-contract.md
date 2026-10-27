# Contract: Unit Report Activity Section API

## Endpoints

- `GET /api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/activities/`
- `POST /api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/activities/`
- `PATCH /api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/activities/{row_id}/`
- `DELETE /api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/activities/{row_id}/`

## Request Payload (POST / PATCH)

```json
{
  "shift": "shift_1",
  "crew_name": "A-Team Crew",
  "foreman_count": 2,
  "worker_count": 6,
  "shift_hours": "8.00",
  "activity_ref": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "activity_description": "Piping installation in zone B",
  "contractor_ref": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
  "quantity": "45.0000",
  "unit": "متر طول",
  "execution_percentage": "15.50",
  "is_hydrostatic_tested": true,
  "test_pressure_bar": "6.50",
  "test_duration_minutes": 120,
  "test_outcome": "PASSED",
  "tested_segment": "Riser R-2, Level 3 to 4",
  "notes": "Testing witnessed by QC engineer"
}
```

## Validation Rules & Error Responses

### 1. Invalid Execution Percentage Range
When `execution_percentage` is less than 0.00 or greater than 100.00:
- **HTTP Status**: 400 Bad Request
- **Response**:
```json
{
  "execution_percentage": [
    {
      "code": "percent_must_be_between_0_and_100",
      "message": "درصد پیشرفت باید بین ۰ تا ۱۰۰ باشد / Execution percentage must be between 0.00 and 100.00"
    }
  ]
}
```

### 2. Invalid Test Pressure Value
When `is_hydrostatic_tested` is true, but `test_pressure_bar` is missing or `<= 0`:
- **HTTP Status**: 400 Bad Request
- **Response**:
```json
{
  "test_pressure_bar": [
    {
      "code": "invalid_test_pressure_value",
      "message": "فشار آزمون باید عددی مثبت باشد / Test pressure must be a positive number"
    }
  ]
}
```
