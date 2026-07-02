## 2025-02-14 - Prevent Raw Exception Leakage to Clients
**Vulnerability:** Raw exception traces (`str(e)`) were being returned directly in JSON API responses when processing file uploads/imports.
**Learning:** Returning `str(e)` in an HTTP response allows internal system, schema, and environment details to leak to an attacker, failing the "fail securely" principle.
**Prevention:** Always log the exception safely on the backend with `logger.exception("...")` and return a safe, generic error message (e.g., "Failed to read file", "An error occurred").
