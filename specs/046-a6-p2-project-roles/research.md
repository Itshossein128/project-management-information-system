# Research: A6-P2 project roles

## Decision: Local role is the same Role row with a project

Existing roles stay global by leaving `project` empty. A project role sets `project` to that project. Global names stay unique among global roles. A local name is unique inside its project. System protection applies only to global roles whose names are the built-in catalog. A local role cannot reuse a built-in name.

Rationale: One catalog already has permissions, assignment, and tests. A second role table would fork that behavior.

Alternatives considered: A parallel local-role table. Rejected because assignment and effective permissions would need a second path.

## Decision: Assigned custom roles cannot be deleted

Any `ProjectMemberRole` row blocks deletion, including inactive and suspended memberships, and also invited or archived memberships that still hold the link. Delete returns a conflict with the assignment count in the actor's scope and does not remove those links. The user removes or replaces the role first. After the last link is gone, the authorized actor may delete the custom role. System roles stay undeletable.

The check runs again inside a transaction with the role locked. The database also protects the role from cascading assignment deletes.

Global assignment counts include every project. A project manager cannot delete a global role. A project manager can manage only local roles of the project where that person is an active member with member-management authority.

Rationale: This is the customer's option C recorded on 2026-11-05.

Alternatives considered: Cascade-deleting assignments, or deactivating the role in place. Both were rejected by the customer.

## Decision: Permission origin is explicit

The effective boolean remains. Each permission also reports `inherit`, `grant`, or `deny`. Clearing an override deletes the override row and does not create a deny. The form uses the origin, not a missing boolean, to choose inherit.

Inherited access is the union of assigned access roles and the default permissions of the member's selected job titles. An explicit deny wins. An explicit grant adds a permission even when no role or title has it. Removing one role does not remove a permission that another role or title still grants.

Rationale: The current summary reports only a boolean, so the form treats every denied or granted value as an override.

Alternatives considered: Returning null for inherited grants. That cannot represent an inherited denial separately from a missing row once the catalog lists every permission.

## Decision: Several job titles, without replacing roles

A membership keeps its current single title for older readers and gains a set of selected titles. Existing single titles are copied into that set. Selectable titles are active titles of the same project or active titles with no project. Titles of another project are rejected. Changing titles does not clear access roles.

Rationale: A6-P1 decided that several job titles are not the same thing as several access roles, and this phase has to make both usable.

Alternatives considered: Replacing the single title immediately. Older clients would lose the current field.

## Decision: Base history is a dedicated record, not the full audit page

Each role assignment change, override change, role-permission change, and successful role deletion writes one record with the actor, project, subject person, time, and before/after permission or role difference. Authorized project managers can read recent records for their project. The full history screen stays a later phase.

Rationale: The phase asks for a trace and forbids building the finished history product.

Alternatives considered: Relying only on the generic request log. That log does not store the permission difference for these actions.

## Decision: Important edits show impact first

Before replacing a role's permissions, and before delete, the actor sees how many current assignments are in scope. Permission replacement still requires a separate confirmed request. Delete never uses that count to bulk-remove assignments.

Rationale: The customer asked for the effect to be visible before an important change, and for delete not to clear assignments by itself.
