# UAT Checklist (SC-005): Dashboards, Roles & Reports

**Purpose**: Primary operational acceptance for PM, site, finance, and project controls before release.  
**Feature**: [spec.md](../spec.md)

## Project manager

- [ ] Open project dashboard pack and see schedule / risk / contract-oriented figures (or inactive where modules off)
- [ ] Click a figure → drill shows source rows with approval status and last updated
- [ ] Cannot finally approve a material change request they alone created (`sod_self_approve`)

## Site

- [ ] Site specialist / supervisor can open dashboard with `view_dashboard` where granted
- [ ] Viewer-like site users cannot perform approve actions from dashboard UI

## Finance

- [ ] Finance dashboard/pack shows budget/cash/IPC-related figures for member projects only
- [ ] Portfolio dashboard omits projects where finance user is not a member
- [ ] IPC self-approve blocked; second finance user can approve

## Project controls

- [ ] Controls / planning pack shows progress / EVM-oriented figures
- [ ] Standard weekly/monthly report export includes extraction date and filters
- [ ] Approved-only report excludes draft figures from totals

## Sign-off

| Role | Tester | Date | Pass |
|------|--------|------|------|
| PM | | | |
| Site | | | |
| Finance | | | |
| Controls | | | |
