# Contract: WBS templates (copy-on-write)

## Existing surfaces (reuse)

- Template CRUD / list under project-templates / settings templates UI  
- `apply_template_to_project(template, project, force=..., user=...)`  
- Project create wizard may apply a template  

## Immutability rule

After apply, project `WBS` rows are **not** FK-synced to `ProjectTemplateWBS`. Editing template name/codes/children MUST leave previously applied project trees unchanged.

## Apply

- Default: refuse if project already has WBS (`force=false`).  
- `force=true`: **explicit** replace only — must not run silently; must respect delete-dependency policy (refuse replace if any existing node would violate FR-WBS-006, or soft-delete only safe nodes after confirmation). Prefer soft-delete over hard `DELETE` for alignment with 002.

## Tests (implement time)

1. Apply template → project has N nodes.  
2. Mutate template root name/code.  
3. Re-fetch project WBS → still previous name/code.  
4. Optional: force replace blocked when costs exist on project WBS.  
