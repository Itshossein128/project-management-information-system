# Sprint 6 Section 1 — Security Audit Report

## XML parsing

| Location | Parser | User input? | Action |
|----------|--------|-------------|--------|
| `schedule/services/msp_import.py` | `defusedxml.ElementTree` | Yes | Hardened — catches `DefusedXmlException`, `DTDForbidden` |
| `.jules/sentinel.md` | Documentation only | N/A | No change |
| Frontend `JSON.parse` | N/A | N/A | Unrelated |

No stdlib `xml.etree.ElementTree` usage in application code.

## SQL injection

Searched for `cursor.execute`, `connection.cursor()`, `.raw(`, `.extra(` across all Python files.

**Result: clean** — ORM-only data access.

## File upload validation

Central validator: `common/validators.py`

Applied to:
- MSP import (`schedule/views.py`)
- Document presign (`storage/views.py`)
- Dynamic rows Excel import (`business_meta/data_views.py`)
- Department activity import (`inventory/department_activity_data_views.py`)
- Legacy items import (`inventory/views.py`)

## Rate limiting

Auth endpoints use `django-ratelimit`:
- Login: 10/m per IP
- Token refresh: 30/m per IP
- Forgot/reset password: 5/m per IP

Traefik edge login limit retained as defense-in-depth.
