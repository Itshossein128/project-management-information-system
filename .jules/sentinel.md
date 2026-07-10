## 2024-06-26 - Exception Information Leakage
**Vulnerability:** API endpoints were returning raw stringified exceptions (`str(e)`) to the client during file imports and processing.
**Learning:** Returning `str(e)` directly from libraries like `pandas` can expose sensitive internal path information, stack traces, and system details to users.
**Prevention:** Catch exceptions, log the full details server-side using `logger.exception()`, and return a generic, user-friendly error message to the client. Validate expected edge cases explicitly (like `ValueError`) to return helpful validation messages without exposing internals.
## 2024-05-24 - Redact sensitive fields in AuditLogMiddleware
**Vulnerability:** Unredacted sensitive data like passwords could be logged in plaintext into `audit_log` via `AuditLogMiddleware`.
**Learning:** `AuditLogMiddleware` serialized complete request body data (`changes`) without obfuscating sensitive fields, leaking plaintext passwords from auth routes.
**Prevention:** Implement a recursive data redaction layer before audit logging that actively strips or masks keys typically associated with sensitive information (e.g. password, token, secret).
