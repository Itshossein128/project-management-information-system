## 2025-05-24 - Do Not Leak Raw Exception Error Messages to End Users
**Vulnerability:** Raw exception messages leaked to the user.
**Learning:** Returning `str(e)` in an API error response exposes potential inner workings of the application (e.g. details about the server, database or libraries being used) which is a security risk.
**Prevention:** Always log exceptions securely using `logger.exception('...')` on the backend, and present a generic sanitized error message to the user such as "An error occurred".
