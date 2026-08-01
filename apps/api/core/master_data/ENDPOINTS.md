# Master Data Endpoints

This document describes the API endpoints for Master Data. Currently, Master Data relies on generic viewsets or is accessed indirectly through other modules (e.g. Roles in projects).
Master data contains base entities such as Roles, Project Members, and other system-wide definitions.

## Endpoints

Master Data models and logic are primarily used as ForeignKeys by other apps (e.g., `projects.urls` mapping to `RoleListView` or `UserLookupView`). Specific endpoints directly exposing master data entities would be documented here. Currently, user lookup and global roles are exposed through `config/urls.py` routing into `projects.role_urls.py` and `projects.member_views.py`.

### 1. User Lookup
- **URL**: `/api/v1/users/lookup/`
- **Method**: `GET`
- **Description**: Lookup users for assignment (e.g., adding project members).
- **Access**: Authenticated users.
