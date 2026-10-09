---
trigger: always_on
description: Standard operating rules for building and incrementally extending the application Decision Tree in docs/decision-tree/.
---

# Decision Tree Documentation Rules

This repository maintains a comprehensive state machine and decision tree in `docs/decision-tree/`. It maps every single route, UI interaction, permission gate, and state transition in the application.

## 1. Directory & File Hierarchy

1. **Root Directory**: `docs/decision-tree/`
2. **Directory per Decision**:
   - Every decision MUST have its own directory.
   - For any subsequent decision possible from that resulting state, create a **nested subdirectory** inside that decision's directory.
3. **Permission Protection Rule**:
   - If a decision or route is protected by a permission, role, or authorization check:
     - The directory title **MUST be wrapped in square brackets `[]`** (e.g., `[navigate-hr-hub]`, `[navigate-roles]`, `[create-project]`, `[approve-daily-report]`).
     - If the decision does not require special permissions (or is public/authenticated user standard), the directory title is **NOT** wrapped in brackets (e.g., `submit-valid-credentials`, `navigate-register`).
4. **Markdown File in Each Directory**:
   - Inside every decision directory, create a `README.md` detailing:
     - **Title**: Clean descriptive heading of the decision.
     - **Current Route / Screen**: URL pathname and UI component.
     - **Action / Trigger**: Exact user interaction (input entered, button clicked, link navigated).
     - **Required Permissions**: Explicitly list all backend permission codenames, Django groups, or frontend role checks required (e.g., `IsHrOrAdmin`, `view_wbs`, `edit_project`, or `None (Public)`).
     - **Desired Result**: Network request sent, state transition, UI change, or route navigation.
     - **Resulting Route / Screen**: Where the user ends up after taking the decision.
     - **Next Decisions**: Bulleted list of links to child directories representing all valid subsequent decisions.

## 2. Incremental Completion Protocol

Whenever instructed to expand, update, or verify the decision tree:
1. Inspect the routes in `apps/web/src/app/routes.ts`, `apps/web/src/app/routes/business-setup.routes.ts`, and component actions.
2. Inspect backend viewset permissions in `apps/api/core/` (e.g. `authentication/permissions.py`, `permissions/constants.py`, and endpoint `get_permissions()`).
3. Traverse unexplored leaf directories in `docs/decision-tree/` and add the child decision directories with their `README.md` files.
4. Ensure directory names use kebab-case: `[<permission-protected-action>]` or `<unprotected-action>`.
5. Keep `docs/decision-tree/README.md` updated with the overall state graph index and progress status.
