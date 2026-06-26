## 2024-06-26 - Exception Information Leakage
**Vulnerability:** API endpoints were returning raw stringified exceptions (`str(e)`) to the client during file imports and processing.
**Learning:** Returning `str(e)` directly from libraries like `pandas` can expose sensitive internal path information, stack traces, and system details to users.
**Prevention:** Catch exceptions, log the full details server-side using `logger.exception()`, and return a generic, user-friendly error message to the client. Validate expected edge cases explicitly (like `ValueError`) to return helpful validation messages without exposing internals.
