# WBS (Work Breakdown Structure) Endpoints

Routes are nested under a project: `/api/v1/projects/{project_pk}/`

## Permissions

| Action | Permission |
|--------|------------|
| View | `view_schedule` + `IsProjectMember` |
| Create / Edit / Move / Delete | `edit_schedule` |

## Endpoints

### 1. WBS Tree Management

The WBS is managed as a hierarchical tree (using `django-treebeard` under the hood).

*   **URL:** `/wbs/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: Returns the entire WBS for the project structured as a nested JSON tree.
    *   `POST`: Creates a new WBS node. Requires specifying `parent_id` (unless it's the root node).

*   **URL:** `/wbs/flat/`
*   **Method:** `GET`
*   **Description:** Returns the WBS nodes as a flat list (useful for dropdowns).

*   **URL:** `/wbs/{wbs_id}/`
*   **Methods:** `PATCH`, `DELETE`
*   **Description:** Update a WBS node's properties (name, code) or delete it. Deleting a node typically cascades or prevents deletion if it has children/activities.

*   **URL:** `/wbs/{wbs_id}/move/`
*   **Method:** `POST`
*   **Description:** Move a WBS node in the hierarchy.
    *   **Body:** `target_id` (UUID of the new parent or sibling), `position` (e.g., `first-child`, `last-child`, `left`, `right`).
