# API Contract: Standardized Daily Weather and Temperature

## 1. Scope and conventions

Base path:

```text
/api/v1/projects/{project_id}/daily-reports/
```

Existing authentication, project membership, permission checks, report lifecycle rules, and automatic-summary creation behavior remain unchanged. This contract defines only weather, temperature, weather-impact note, aggregation, and PDF behavior.

Requests send `Accept-Language: fa|en`. Field names, weather values, and stable error codes never change with locale; human messages may be localized.

## 2. Shared weather values

The only valid non-empty weather values are:

```json
["clear", "cloudy", "rainy", "snowy", "stormy"]
```

Presentation order and meaning:

| Value | Persian | English |
|-------|---------|---------|
| `clear` | آفتابی / صاف | Clear / sunny |
| `cloudy` | ابری | Cloudy |
| `rainy` | بارانی | Rainy |
| `snowy` | برفی | Snowy |
| `stormy` | طوفانی / گرد و غبار | Stormy / dust |

`sunny`, `partly_cloudy`, `foggy`, and unknown values are invalid for new writes. Historical/offline data is normalized before it reaches the current write contract.

## 3. Read daily-report detail

```http
GET /api/v1/projects/{project_id}/daily-reports/{report_id}/
```

Relevant response fields:

```json
{
  "report_id": "uuid",
  "report_date": "1405/07/30",
  "weather_condition": "stormy",
  "weather_condition_label": "طوفانی / گرد و غبار",
  "temp_min": "-2.5",
  "temp_max": "8.0",
  "weather_impact_notes": "بارش و وزش باد موجب توقف جرثقیل شد.",
  "weather_override": false,
  "aggregation": {
    "weather_source": "derived"
  }
}
```

Contract rules:

- `weather_condition` is one approved value or `null` where the existing report allows no observation.
- `weather_condition_label` is a server display convenience and is `null` when weather is `null`; bilingual clients localize from the stable `weather_condition` value and MUST NOT depend on this label as their only translation source.
- Temperatures are decimal strings or `null`.
- `weather_impact_notes` is a string; the empty representation is `""`.
- Multi-line and mixed Persian/English text is returned without silent truncation or character loss.

## 4. Update daily-report header

```http
PATCH /api/v1/projects/{project_id}/daily-reports/{report_id}/
Content-Type: application/json
```

Relevant partial payload:

```json
{
  "weather_condition": "rainy",
  "temp_min": "4.5",
  "temp_max": "11.0",
  "weather_impact_notes": "بارندگی دسترسی به جبهه شمالی را محدود کرد."
}
```

Any subset may be sent. Validation uses the candidate object produced by merging supplied values with the current stored report.

Rules:

- `weather_condition`: one approved value or `null` when existing optionality permits clearing it.
- `temp_min`, `temp_max`: decimal values from `-40` through `60`, inclusive, or `null`.
- When both candidate temperatures are non-null, `temp_max >= temp_min`.
- Sending `null` for one temperature intentionally clears it.
- `weather_impact_notes`: optional plain-text string; `""` clears it.
- A successful response uses the daily-report detail representation so the client can replace local state with authoritative values.

No new daily-report POST or PUT behavior is introduced by this feature.

## 5. Validation errors

### Retired or unknown weather

```http
HTTP/1.1 400 Bad Request
```

```json
{
  "error": {
    "code": "invalid_choice",
    "message": "weather_condition: ...",
    "details": {
      "weather_condition": ["... is not a valid choice."]
    }
  }
}
```

The exact localized message is not a stable contract. The error must remain field-specific.

### Temperature outside the allowed range

```http
HTTP/1.1 400 Bad Request
```

```json
{
  "error": {
    "code": "min_value",
    "message": "temp_min: ...",
    "details": {
      "temp_min": ["..."]
    }
  }
}
```

The standard bound code may be `min_value` or `max_value` according to the violated boundary. The corresponding temperature field must appear in `details`.

### Maximum below minimum

```http
HTTP/1.1 400 Bad Request
```

```json
{
  "error": {
    "code": "temp_max_must_be_gte_temp_min",
    "message": "Maximum temperature must be greater than or equal to minimum temperature.",
    "details": {
      "temp_max": ["Maximum temperature must be greater than or equal to minimum temperature."]
    }
  }
}
```

Required invariants:

- Top-level `error.code` is exactly `temp_max_must_be_gte_temp_min`.
- The field key is exactly `temp_max`.
- The message may be Persian or English; field and code do not change.
- The same result applies when only one submitted field makes the candidate pair invalid against its stored peer.

## 6. Derived summary weather

Eligible contributing specialty reports retain the existing eligibility rules. For their nonblank approved weather values:

```text
stormy > snowy > rainy > cloudy > clear
```

- The highest severity becomes the daily-report weather when `weather_override=false`.
- An approved explicit value remains unchanged when `weather_override=true`.
- Blank values do not contribute.
- Unknown values do not contribute and are reported by data-integrity verification.
- If no approved contribution remains and no override exists, derived weather is `null`; a stale previous derived value is not retained.
- Rebuild never overwrites `weather_impact_notes`.

## 7. Shared compatibility surfaces

Because the backend weather enum is shared:

- Standalone weather-log writes accept the same five weather values and reject retired/unknown values.
- Specialty-report writes accept the same five values when nonblank and reject retired/unknown values.
- This feature adds no weather-impact note field to either surface.
- Daily-report temperature and note contracts remain scoped to the daily-report header.

## 8. Corrections, sync, and offline replay

- A daily-report correction/version copy carries weather, both temperatures, weather-impact notes, and the existing weather override.
- Header sync comparison includes these fields so concurrent edits are reported rather than silently overwritten.
- Pending offline values from the retired vocabulary are normalized by the client data upgrade before replay.
- New or external clients that submit retired values receive the normal invalid-choice response.
- Invalid temperatures are rejected before persistence even if browser validation is bypassed.

## 9. Official PDF

```http
GET /api/v1/projects/{project_id}/daily-reports/{report_id}/pdf/
```

Successful response:

- HTTP `200`
- `Content-Type: application/pdf`
- Existing attachment filename convention

The header table always includes:

```text
توضیحات و اثرات شرایط جوی
```

If notes exist, the cell reproduces the saved plain text with readable wrapping and line breaks. If notes are empty, the row remains present with an empty cell; no dash or fabricated prose is inserted as user content.
