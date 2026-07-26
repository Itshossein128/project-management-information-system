# Project Templates Endpoints

This document describes the API endpoints for managing project templates.
Project templates are used to pre-populate projects with a Work Breakdown Structure (WBS), activities, and roles.

## Endpoints

### 1. Project Templates List
- **URL**: `/api/v1/project-templates/`
- **Method**: `GET`
- **Description**: Retrieves a list of all available project templates. Can be filtered by `project_type` (e.g., residential, road) and `is_system` (boolean).
- **Access**: Authenticated users.

### 2. Create Project Template
- **URL**: `/api/v1/project-templates/`
- **Method**: `POST`
- **Description**: Creates a new project template.
- **Access**: Authenticated users.

### 3. Retrieve Project Template Detail
- **URL**: `/api/v1/project-templates/<uuid:pk>/`
- **Method**: `GET`
- **Description**: Retrieves detailed information about a specific project template, including its full WBS tree and roles.
- **Access**: Authenticated users.

### 4. Update Project Template (Partial)
- **URL**: `/api/v1/project-templates/<uuid:pk>/`
- **Method**: `PATCH`
- **Description**: Updates specific fields of a project template. System templates cannot be edited.
- **Access**: Authenticated users.

### 5. Delete Project Template
- **URL**: `/api/v1/project-templates/<uuid:pk>/`
- **Method**: `DELETE`
- **Description**: Deletes a project template. System templates cannot be deleted.
- **Access**: Authenticated users.

### 6. Apply Template to Project
- **URL**: `/api/v1/project-templates/<uuid:pk>/apply/<uuid:project_id>/`
- **Method**: `POST`
- **Description**: Applies the selected template's WBS, activities, and roles to a target project. Use `?force=true` to overwrite existing WBS nodes.
- **Access**: Authenticated users.

### 7. Save Project as Template
- **URL**: `/api/v1/projects/<uuid:project_pk>/save-as-template/`
- **Method**: `POST`
- **Description**: Creates a new project template based on an existing project's WBS structure. System templates can only be created by admins.
- **Access**: Authenticated users with `edit_wbs` permission on the project.
