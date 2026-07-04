## 2024-05-24 - Information Exposure in Exception Handling
**Vulnerability:** Raw exception strings (`str(e)`) from `pandas` and other internal libraries were returned directly to the client during Excel file imports.
**Learning:** Broad exception handling returning `str(e)` leaks internal system state and potentially sensitive information to end-users.
**Prevention:** Always log the full exception server-side with `logger.exception()` and return a generic, secure error message to the client.
