
## 2024-05-18 - Prevented Information Leakage in API Views
**Vulnerability:** Raw exception details (`str(e)`) were being leaked to the client in REST API responses in `apps/api/core/inventory/views.py` and `apps/api/core/business_meta/data_views.py`.
**Learning:** Returning unhandled exception messages directly to the client can expose sensitive internal information (stack traces, database structure, etc.). This pattern exists because it is easy to write, but it violates the fail securely principle.
**Prevention:** Always catch exceptions using a standard logger (`logger.exception()`) to keep the detailed trace server-side and return a generic, sanitized error message to the client.
