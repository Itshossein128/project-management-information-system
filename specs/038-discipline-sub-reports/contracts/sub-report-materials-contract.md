# Contract: Mechanical Materials Section API

## Endpoints

- `GET /api/v1/projects/{project_id}/units/mechanical/daily-reports/{report_id}/materials/`
- `POST /api/v1/projects/{project_id}/units/mechanical/daily-reports/{report_id}/materials/`
- `PATCH /api/v1/projects/{project_id}/units/mechanical/daily-reports/{report_id}/materials/{row_id}/`
- `DELETE /api/v1/projects/{project_id}/units/mechanical/daily-reports/{report_id}/materials/{row_id}/`

## Request Payload (POST / PATCH)

```json
{
  "transaction_type": "consumption",
  "material_description": "لوله ۵ لایه",
  "quantity": "25.0000",
  "unit": "متر طول",
  "consumption_location": "طبقه ۴ - بلوک B",
  "notes": "نصب لوله‌کشی کلکتور گرمایشی"
}
```

## Quick-Pick Catalog Suggestions (Frontend UI)
For `unit === 'mechanical'`:
1. `لوله ۵ لایه` (unit: `متر طول`)
2. `لوله پلیکا / فاضلابی` (unit: `شاخه`)
3. `اتصالات جوشی گاز` (unit: `عدد`)
4. `عایق الاستومری حرارتی/برودتی` (unit: `متر مربع`)
5. `لوله گالوانیزه` (unit: `شاخه`)
