# Risk & Barriers Module Endpoints

This document describes the API endpoints exposed by the `risk` module located in `apps/api/core/risk/`.

All endpoints here inherit from `ProjectScopedViewSet`, meaning they require a project context (either globally or via URL depending on the router configuration) and apply project-level permissions (`view_reports` and `edit_reports`).

## 1. Barriers (`/barriers/`)

Handles CRUD operations for project barriers (events that specifically block or hinder progress).

*   **`GET /barriers/`**: Lists barrier logs. Results are heavily filtered to only include events where `event_type='barrier'`. Query parameters support filtering by `status`, `category`, `impact_schedule`, `impact_cost`, `date_from`, and `date_to`.
*   **`POST /barriers/`**: Creates a new barrier log. The backend forces the `event_type` to `BARRIER` automatically upon creation.
*   **`GET /barriers/<uuid:pk>/`**: Retrieves the details of a specific barrier log.
*   **`PATCH /barriers/<uuid:pk>/`**: Partially updates a barrier log. Contains custom validation to ensure that if a barrier's status is changed to `resolved`, a `resolved_date` must be provided.
*   **`DELETE /barriers/<uuid:pk>/`**: Soft-deletes a specific barrier log.

## 2. Risk Events (`/risk-events/`)

Handles CRUD operations for general project risk and delay events.

*   **`GET /risk-events/`**: Lists risk/delay events. Supports query parameters to filter by `event_type`, `severity`, `status`, date ranges, and a generic text `search` (matching description, responsible party, or category).
*   **`POST /risk-events/`**: Creates a new risk or delay event.
*   **`GET /risk-events/<uuid:pk>/`**: Retrieves the details of a specific risk/delay event.
*   **`PATCH /risk-events/<uuid:pk>/`**: Partially updates a risk/delay event. Ensures validation rules, like requiring a resolution date for resolved items, and that related entities (daily reports, correspondences) belong to the same project.
*   **`DELETE /risk-events/<uuid:pk>/`**: Soft-deletes a specific risk/delay event.

## 3. Risk Matrix (`/risk-events/matrix/`)

Provides an aggregated view of active risk events for dashboard reporting.

*   **`GET /risk-events/matrix/`**: Returns a data structure mapping open risk events (excluding resolved statuses) into a 2D matrix of "Probability vs. Severity".
    *   Probability is grouped into predefined buckets (0-20, 21-40, etc.).
    *   Severity is sorted from Low to Critical.
    *   The payload returns `total_open` and an array representing the `matrix` cells.
