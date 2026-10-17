# UI Contract: Contractor Stakeholder Select

## Shared control

- Component intent: **ContractorSelect** (or equivalent) — searchable optional, **non-creatable**.
- Options: `fetchStakeholders(projectId)` filtered `role=contractor&status=active` (shared helper).
- Value: stakeholder UUID string; label: stakeholder `name` (optionally append organization when useful).
- Empty list: short message that contractors are managed on ذینفعان; link/nav hint allowed; no free-text fallback.
- Do not use `CreatableSelect` Add path for this field.

## ذینفعان page

- Create/edit exposes **role** (missing in current add form). Include option value `contractor`, label پیمانکار / “Contractor”.
- Status control already available or add if missing so inactive removes from pickers.
- After create/update of a contractor, invalidate stakeholder/contractor query keys used by pickers.

## Department activity (P1)

- Modal field `#container-departmentActivityContractor` / `departmentActivityContractor`: replace `Input` with ContractorSelect.
- Sticky-field behavior preserved if already present.
- List column shows snapshot name; filter uses select of contractors (or searchable select), not free-text only.

## Daily report / labor (P2)

- Activity grid پیمانکار column and labor-camp پیمانکار: options from same contractor helper (not `/contracts/`).
- Persist `contractor_ref` (+ name snapshot fields per API contract).

## Project settings / create wizard (P2)

- پیمانکار party field uses same ContractorSelect; optional clear.

## Locales

- fa/en strings for: role option پیمانکار/Contractor, empty-state guidance, validation “select a contractor” / “register on stakeholders first”.
- Stable option value remains `contractor`.

## Accessibility

- Keyboard open/select/close; associated label; error text linked to control; RTL/LTR with existing form patterns.
