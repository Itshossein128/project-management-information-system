# Risk App Endpoints

This document describes the API endpoints and routes available in the `risk` app (`apps/api/core/risk/urls.py`).

## `/barriers/`

This endpoint handles operations on the collection of barrier logs for a specific project.

*   **`GET`**: Lists all project barriers. Supports filtering via query parameters (e.g., status, category, impact_schedule, impact_cost, date_from, date_to).
*   **`POST`**: Creates a new barrier log. Automatically associates the new barrier with the current active project and sets its type to `EventType.BARRIER`.

## `/barriers/<uuid:pk>/`

This endpoint handles operations on a specific, existing barrier log identified by its UUID (`pk`).

*   **`GET`**: Retrieves the details of the specific barrier log.
*   **`PATCH`**: Partially updates the specific barrier log. It includes validation to ensure that if the barrier's status is changed to "resolved", a resolution date is provided.
*   **`DELETE`**: Soft-deletes the specific barrier log.