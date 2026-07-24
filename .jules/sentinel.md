## 2024-06-26 - Exception Information Leakage
**Vulnerability:** API endpoints were returning raw stringified exceptions (`str(e)`) to the client during file imports and processing.
**Learning:** Returning `str(e)` directly from libraries like `pandas` can expose sensitive internal path information, stack traces, and system details to users.
**Prevention:** Catch exceptions, log the full details server-side using `logger.exception()`, and return a generic, user-friendly error message to the client. Validate expected edge cases explicitly (like `ValueError`) to return helpful validation messages without exposing internals.
## 2024-05-24 - Redact sensitive fields in AuditLogMiddleware
**Vulnerability:** Unredacted sensitive data like passwords could be logged in plaintext into `audit_log` via `AuditLogMiddleware`.
**Learning:** `AuditLogMiddleware` serialized complete request body data (`changes`) without obfuscating sensitive fields, leaking plaintext passwords from auth routes.
**Prevention:** Implement a recursive data redaction layer before audit logging that actively strips or masks keys typically associated with sensitive information (e.g. password, token, secret).
## 2026-07-10 - Prevent XXE and Billion Laughs Vulnerabilities\n**Vulnerability:** Found standard `xml.etree.ElementTree` used to parse user-uploaded MSP XML files without mitigations.\n**Learning:** The built-in XML parser is vulnerable to Entity Expansion and XXE attacks. Even Python 3.12 defaults are susceptible to Billion Laughs.\n**Prevention:** Always use `defusedxml` (e.g., `defusedxml.ElementTree`) when parsing XML from untrusted user inputs, and ensure any `DefusedXmlException` is caught and masked with a generic error message so internals aren't leaked.
## 2024-05-24 - [Path Traversal in File Uploads]
**Vulnerability:** The document upload service was passing unsanitized client-provided filenames directly to AWS S3 key construction in `apps/api/core/documents/services/upload_service.py`. While the core prefix included a UUID mitigating direct overwrites, extracting paths or persisting malicious names in the database posed a risk for downstream consumers.
**Learning:** Overly aggressive validation (like raising an error if `..` is present) can break valid filenames (e.g. `draft..v1.pdf`). It is safer to rely on `os.path.basename` to extract the file correctly while discarding the path.
**Prevention:** Always sanitize `file_obj.name` using `os.path.basename` (after converting backslashes if necessary for cross-platform robustness) before using or returning it in the upload pipeline.

## 2024-05-24 - Fail Securely in HTTP Responses
**Vulnerability:** Found `ValueError` exceptions being cast to string and returned directly in 400 Bad Request responses within `apps/api/core/storage/views.py`.
**Learning:** Returning `str(exc)` can leak sensitive internal information, stack traces, or validation details that an attacker could use to probe the system. This violates the principle of failing securely.
**Prevention:** Always catch exceptions, log the full details server-side using `logger.exception(...)` so debugging information is preserved internally, and return generic, safe messages like `'Invalid request.'` to the client. Keep any specific safe messages (like `'Not found.'` mapped to 404) explicitly checked, rather than relying on dynamic error strings.

## 2024-07-19 - Explicitly Reject Path Traversal Attempts
**Vulnerability:** Document upload logic in `apps/api/core/documents/services/upload_service.py` relied solely on silent sanitization (`os.path.basename`) when processing client-provided filenames.
**Learning:** While `os.path.basename` sanitizes the filename, explicitly failing and rejecting payloads containing path traversal characters (`..`, `/`, `\`) provides stronger defense-in-depth and is a preferred security posture over silently modifying malicious input. Note that this supersedes previous learnings about just using `os.path.basename` due to the explicit requirement to explicitly reject such inputs.
**Prevention:** Always add explicit checks to reject malicious filenames (e.g. by raising `ValidationError`) early in the pipeline before performing any file operations or relying on silent sanitization functions.
## 2024-07-23 - Prevent Exception Information Leakage in APIs
**Vulnerability:** Found an API endpoint (`apps/api/core/inventory/views.py`) returning a raw exception string (`str(e)`) inside a generic 400 response.
**Learning:** Returning `str(e)` directly to clients leaks internal implementation details, such as file paths or module internals, exposing the application to reconnaissance attacks.
**Prevention:** Instead of stringifying generic exceptions in JSON responses, explicitly catch the expected errors, log them using `logger.exception()` to preserve debugging information server-side, and return a safe, generic error message (like "Invalid request.") to the client.
