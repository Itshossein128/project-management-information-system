## 2025-02-14 - Prevent Information Leakage in API Exceptions
**Vulnerability:** Broad `Exception` handlers in API endpoints (like `import_items`) were catching errors and returning `str(e)` directly to the user in HTTP 400 responses.
**Learning:** This existed because catching `Exception` indiscriminately often bundles system/database/file-system errors into string descriptions that should never reach the client. It's a common pattern to pass `str(e)` out of convenience during initial development.
**Prevention:** Always log the full exception server-side using `logger.exception('...')` and return a safe, generic error message (e.g., "An error occurred") to the client. Avoid `str(e)` in API responses unless the exception is a specific, safe custom exception class.
