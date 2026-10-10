# Contract: AHP Run Result Payload

**Field**: `DecisionRun.result`

## Schema

```json
{
  "type": "object",
  "required": ["status", "engine", "weights", "lambda_max", "ci", "cr", "is_consistent"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["ok"]
    },
    "engine": {
      "type": "string",
      "enum": ["ahp"]
    },
    "weights": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["criterion", "weight", "rank"],
        "properties": {
          "criterion": { "type": "string" },
          "weight": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "rank": { "type": "integer", "minimum": 1 }
        }
      }
    },
    "lambda_max": {
      "type": "number"
    },
    "ci": {
      "type": "number",
      "minimum": 0.0
    },
    "cr": {
      "type": "number",
      "minimum": 0.0
    },
    "is_consistent": {
      "type": "boolean"
    }
  }
}
```

## Example Payload

```json
{
  "status": "ok",
  "engine": "ahp",
  "weights": [
    { "criterion": "Quality", "weight": 0.60, "rank": 1 },
    { "criterion": "Cost", "weight": 0.30, "rank": 2 },
    { "criterion": "Time", "weight": 0.10, "rank": 3 }
  ],
  "lambda_max": 3.0092,
  "ci": 0.0046,
  "cr": 0.0079,
  "is_consistent": true
}
```
