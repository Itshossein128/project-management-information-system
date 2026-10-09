---
name: decision-tree
description: Systematically build, validate, and incrementally extend the user decision tree and state machine in docs/decision-tree/.
---

# Decision Tree Management Skill

This skill guides the creation, expansion, and verification of the decision tree state machine located in `docs/decision-tree/`.

## Purpose & Scope
The goal of `docs/decision-tree/` is to map every possible decision a user can make, starting from opening the app for the very first time (unauthenticated at the login form), and navigating through all features and states of the system.

## Tree Structure Specifications

1. **Path Representation**:
   - Every node in the decision tree is a directory.
   - Root starts at `docs/decision-tree/login/` (representing the initial entry state: Login Form).
   - Each transition/action taken by the user creates a nested subdirectory within the current state directory.

2. **Directory Naming Conventions**:
   - Use kebab-case for directory names (e.g. `submit-valid-credentials`, `navigate-register`).
   - **Permission-protected decisions MUST have their directory name wrapped in square brackets `[]`**:
     - Example: `[navigate-hr-hub]` (requires `IsHrOrAdmin`)
     - Example: `[navigate-roles]` (requires `IsHrOrAdmin`)
     - Example: `[navigate-templates]` (requires `admin`, `hr`, or `business-setup`)
     - Example: `[approve-project]` (requires `approve_project` permission)
     - Example: `[delete-project]` (requires `edit_project` or `admin`)
   - Unprotected / standard decisions must not have brackets:
     - Example: `submit-valid-credentials`
     - Example: `navigate-register`
     - Example: `select-project`

3. **File Requirements**:
   - Inside every directory, create `README.md` following this standard template:

```markdown
# Decision: <Title>

## Context & Screen
- **Route**: `<path>` (e.g. `/login`, `/projects`, `/projects/:projectId/overview`)
- **Component**: `<Component>` (e.g. `Login`, `ProjectListPage`)
- **Initial State**: Describe the state prior to taking this decision.

## Action Taken
- **Trigger**: Exact interaction (button click, form submission, link click, keyboard event).
- **Inputs**: Values provided by the user (if any).

## Authorization & Permissions
- **Required Permissions**: List permissions (e.g. `None (Public)`, `IsAuthenticated`, or specific codename like `view_costs`, `edit_wbs`).
- **Required Roles / Groups**: (e.g. `admin`, `hr`, `project_manager`).

## Desired Result
- **API Call**: (e.g. `POST /api/v1/auth/login/`)
- **State Change**: Auth token stored, cache invalidated, redux/react state changed.
- **Navigation**: Redirected to `<path>`.
- **UI Feedback**: Error alert, toast notification, or loaded page.

## Subsequent Decisions
List and link all valid next decisions available from this new state:
- [Decision 1](decision-1-dir/)
- [[Protected Decision 2]](%5Bprotected-decision-2-dir%5D/)
```

## Incremental Expansion Strategy
1. **Find Terminal / Leaf Nodes**:
   Check which subdirectories in `docs/decision-tree/` do not yet have their children documented.
2. **Consult Source Code**:
   - Examine frontend routes (`apps/web/src/app/routes.ts`, `routeVars.ts`, and component views).
   - Check backend permission classes (`apps/api/core/authentication/permissions.py`, `permissions/constants.py`).
3. **Generate Child Directories**:
   Create the next round of decision subdirectories with accurate permissions and desired results.
4. **Update Root Index**:
   Update `docs/decision-tree/README.md` with the updated tree diagram and summary.
