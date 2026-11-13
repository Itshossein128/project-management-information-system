# Traceability Matrix: Schedule Import Safety and History (A.7-P2)

**Phase**: `A.7-P2` (`specs/052-a7-p2-import-safety`)  
**Owned Audit IDs**: `P08`, `W04`, `S05`, `I06`, `I07`, `I08`, `I11`, `I14`, `I18`  
**Contract Reference**: [`contracts/import-safety.md`](./contracts/import-safety.md)  
**Verification & Handoff**: [`evidence/verification.md`](./evidence/verification.md), [`handoff.md`](./handoff.md)

| Audit ID | Title (`requirements.json`) | Spec Mapping (`spec.md`) | Owning Code & Tests | Verification Evidence |
| --- | --- | --- | --- | --- |
| `P08` | آرشیو فقط‌خواندنی در تمام مسیرها از جمله ورود زمان‌بندی | `US4`, `FR-009` | `apps/api/core/schedule/services/import_safety.py`, `apps/api/core/schedule/views.py`, `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (49 passed) and P1–P4 combined recheck (93 passed). |
| `W04` | یکتایی کد WBS در سطح پروژه بدون دورزدن از طریق نرمال‌سازی یا ورود فایل | `US3`, `FR-007` | `apps/api/core/projects/models.py`, `apps/api/core/schedule/services/import_safety.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (normalized uniqueness & collision guard). |
| `S05` | خط مبنا، نسخه‌بندی و قفل تغییر مستقیم پس از تصویب | `US2`, `FR-004`, `FR-005` | `apps/api/core/schedule/services/import_safety.py`, `apps/api/core/schedule/models.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (locked/approved baseline guard `baseline_replace_forbidden`, no empty baseline on repeat append). |
| `I06` | تفکیک شفاف دو حالت «افزودن/به‌روزرسانی» و «جایگزینی ایمن» | `US1`, `US2`, `FR-001`–`FR-005` | `apps/api/core/schedule/services/import_safety.py`, `apps/api/core/schedule/services/msp_import.py`, `p6_import.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (`append` vs `replace` semantics & soft-delete replacement on unprotected projects). |
| `I07` | اتمیک بودن کامل ورود و عدم ایجاد داده ناقص در خطا | `US3`, `FR-006`, `FR-007` | `apps/api/core/schedule/services/import_safety.py`, `msp_import.py`, `p6_import.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (mid-write rollback leaves zero partial WBS/activities/relations). |
| `I08` | جلوگیری از تکرار در ورود مجدد همان فایل | `US1`, `FR-002`, `FR-003` | `apps/api/core/schedule/services/msp_import.py`, `p6_import.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (`nothing_changed = true`, zero duplicate WBS/activities/relations). |
| `I11` | قفل هم‌زمانی ورود در سطح پروژه برای MSP و P6 | `US4`, `FR-008` | `apps/api/core/schedule/services/import_safety.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (cross-pipeline project lock & in-flight job replay). |
| `I14` | تاریخچه کامل عملیات ورود و ممیزی در سطح پروژه | `US5`, `FR-011`, `FR-012` | `apps/api/core/schedule/models.py`, `apps/api/core/schedule/views.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (unified MSP/P6 import history & actor attribution). |
| `I18` | بازسنجی مجوز و وضعیت پروژه در زمان اجرای واقعی پردازنده پس‌زمینه | `US4`, `FR-009`, `FR-010` | `apps/api/core/schedule/services/import_safety.py`, `apps/api/core/schedule/tasks.py`, `test_a7_p2_import_safety.py` | Verified in `evidence/verification.md` (apply-time permission & active-status re-validation). |
