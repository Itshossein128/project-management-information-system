## 2024-05-24 - [Information Leakage via Exception Handling]
**Vulnerability:** Raw exception strings (`str(e)`) were being returned directly in API error responses (e.g., in file import endpoints), potentially exposing sensitive internal system details or stack traces to the client.
**Learning:** Broad exception blocks (`except Exception as e:`) combined with returning the exception message to the user is a common pattern that leads to information leakage.
**Prevention:** Always log the full exception server-side using `logger.exception(...)` and return a generic, safe error message to the client instead of exposing raw error details.
