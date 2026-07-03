## 2024-05-24 - Do not leak error details via `str(e)`
**Vulnerability:** Found `Exception as e:` blocks returning `str(e)` directly to the API client in `apps/api/core/inventory/views.py`. This is an information disclosure vulnerability (Medium Priority), as it might leak internal stack traces or database/system details.
**Learning:** Raw exception strings should never be passed to client responses.
**Prevention:** Always log the full exception server-side using `logger.exception()` and return generic, safe error messages to the client.
