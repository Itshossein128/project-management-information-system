# UI Contract: MSP/P6 Import Wizard (MPP support)

**Surface**: Existing modal `MspImportWizard` opened from project WBS (`بارگذاری از MSP / P6` / equivalent).

**Locales**: Persian (RTL) and English (LTR). All new strings in locale files; permission codes stay language-independent.

## 1. Accepted formats

| Format | Extension | Client route |
|--------|-----------|--------------|
| Microsoft Project (native) | `.mpp` | MSP preview/import APIs |
| Microsoft Project XML | `.xml` | MSP preview/import APIs |
| Primavera P6 | `.xer` | P6 preview/import APIs |

- File input `accept` includes `.mpp`, `.xml`, `.xer` (and existing XML MIME types as today).
- Drag-and-drop uses the same acceptance rules.
- Help text lists accepted formats clearly; **must not** say binary `.mpp` is unsupported.
- Users should not need to understand that MPP is converted internally to XML.

## 2. Steps (unchanged structure)

1. **Upload** — select/drop file; show filename + size; Cancel / Preview.
2. **Preview** — tree + warnings; append vs replace; Back / Import.
3. **Progress / result** — progress bar; success summary (WBS, activities; relationships when API returns them); or fatal error; link to WBS when done.

Preview remains a **mandatory** checkpoint before import.

## 3. Processing state (MPP and slow previews)

While preview (or import start) is in flight:
- Show meaningful “preparing / processing” feedback (not a blank stalled modal).
- Disable duplicate Preview/Import submissions.
- Keep the selected **filename** visible.
- On settle: either advance to preview/progress or show fatal error with recovery.

Wizard must not remain indefinitely in an ambiguous processing state (server timeout surfaces as `processing_timeout`).

## 4. Warnings vs errors

| Kind | Presentation |
|------|----------------|
| Non-blocking `warnings[]` from preview/result | Distinct warning styling (existing warning banner pattern) |
| Fatal validation/processing errors | Destructive/error styling + recovery actions |

Recovery actions (as appropriate to `error.code`):
- Choose another file (reset to step 1 / clear file).
- Guidance to remove password / export unprotected XML.
- Guidance that this MPP cannot be processed — try XML/XER.
- Retry when `processing_timeout` / `conversion_failed` may be transient.

## 5. Permissions

- Entry control to open wizard remains `edit_wbs` (UX only).
- API enforces authorization; on 403 show localized denial.

## 6. Accessibility

- Keyboard: file control label, Preview, Back, Import, Close, recovery actions reachable in all steps.
- RTL/LTR: layout and text direction remain usable; no clipped primary actions.
- Focus not trapped incorrectly when processing ends in error.

## 7. Empty / rejection client pre-check

Client may reject obviously wrong extensions before upload for snappy UX, but **must allow `.mpp`**. Server remains source of truth for content validation.
