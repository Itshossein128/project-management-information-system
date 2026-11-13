# Traceability Matrix: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Phase**: `A.7-P6` (`specs/056-a7-p6-delivery-acceptance`)  
**Direct Audit IDs**: `D03`, `D04`  
**Integrated Scope**: All 56 audit items (`P01`–`P11`, `W01`–`W07`, `M01`–`M04`, `S01`–`S08`, `I01`–`I22`, `D01`–`D04`) from `output/a7-requirements-2026-11-10/requirements.json`  
**Machine-Readable Disposition Ledger**: `specs/056-a7-p6-delivery-acceptance/evidence/audit-disposition.json`  
**Stage**: Integrated Technical Verification Complete (`تأیید فنی` across all 56 items; Human Employer Acceptance `pending`)

## 1. Predecessor Gate Summary (`051`–`055`)

| Phase | Feature Directory | Owned Audit IDs | Handoff & Evidence Artifacts | Predecessor Gate Status (Verified 2026-11-13) |
| --- | --- | --- | --- | --- |
| `A.7-P1` | `specs/051-a7-p1-project-reference` | `P01`–`P07`, `P09`–`P11`, `W01`–`W03`, `W05`, `W06`, `M01`–`M04`, `D01` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md`, `contracts/schedule-reference.md` | **Verified**: 108 P1 tests + P6 positive/negative/browser acceptance suites passed; `complete`/`undo-complete` and `archive`/`restore` browser clicks verified in `e2e/tests/a7-p6-delivery-acceptance.spec.ts`. |
| `A.7-P2` | `specs/052-a7-p2-import-safety` | `P08`, `W04`, `S05`, `I06`–`I08`, `I11`, `I14`, `I18` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md`, `contracts/import-safety.md` | **Verified**: Standalone `traceability.md` backfilled (`T003`); all 9 safety items verified across P2 + P6 regression & acceptance suites. |
| `A.7-P3` | `specs/053-a7-p3-import-fidelity` | `W07`, `S01`–`S04`, `S06`–`S08`, `I01`, `I03`–`I05`, `I12`, `I13`, `I21`, `I22` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md`, `contracts/import-fidelity.md` | **Verified (`T034` resolved)**: Standalone `traceability.md` backfilled (`T004`); `real-data/plan.mpp` (`6` WBS, `72` activities, `72` relations) and XML/XER fixtures reconciled in `evidence/reconciliation.json`. |
| `A.7-P4` | `specs/054-a7-p4-import-experience` | `I02`, `I10`, `I15`–`I17` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md` | **Verified**: 93 backend tests + `pnpm typecheck` + Playwright retry and P6 bilingual/responsive/keyboard/account-switch browser tests passed. |
| `A.7-P5` | `specs/055-a7-p5-import-operations` | `I09`, `I19`, `I20`, `D02` | `spec.md`, `handoff.md`, `tasks.md`, `traceability.md`, `evidence/verification.md`, `evidence/reproduction.md` | **Verified (`T049` Closed 2026-11-13)**: Acceptance image (`sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`, product schedule SHA-256 `eb2a29edcb92f01711d8a3594c41c26e05b078601258a9ce45ebd4ebe635abb1`, P5 schedule-tree SHA-256 `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`) passed the 13-group matrix, broker outage recovery, two-importer duplicate delivery, 110 host pytest tests, and 4/4 browser retry tests in both implementer and independent second-operator runs. |

---

## 2. Direct A.7-P6 Audit Items (`D03`, `D04`)

| Audit ID | Title (`requirements.json`) | P6 Spec Mapping | Verification & Package Deliverable | Current Disposition |
| --- | --- | --- | --- | --- |
| `D03` | سناریوهای پذیرش انتها-به-انتها با داده واقعی | `US2`, `US3`, `US4`, `FR-003`–`FR-007`, `SC-002`–`SC-004` | `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py` (`POS-01`–`POS-10`, `NEG-01`–`NEG-14`), `e2e/tests/a7-p6-delivery-acceptance.spec.ts` (`OPS-01`–`OPS-03`), `evidence/scenarios.json`, `evidence/reconciliation.json`. | `تأیید فنی` |
| `D04` | بسته تحویل و چک‌لیست پذیرش کارفرما | `US1`, `US5`, `FR-001`, `FR-002`, `FR-008`–`FR-010`, `SC-001`, `SC-005`, `SC-006` | `guide.md`, `evidence/package.json`, `evidence/audit-disposition.json`, `evidence/accounts.md`, `evidence/defects.md`, `evidence/minutes.md`, `evidence/validate_package.py`. | `تأیید فنی` |

---

## 3. Integrated 56-Item Master Audit Disposition Matrix (`P01`–`D04`)

### 3.1 Project Lifecycle, Charter, Change Control & Archive (`P01`–`P11`)

| Audit ID | Title | Owning Phase | Employer Summary Bucket | Current Candidate Evidence Reference | Disposition |
| --- | --- | --- | --- | --- | --- |
| `P01` | ثبت مشخصات کامل پروژه | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-01`) | `تأیید فنی` |
| `P02` | کد یکتای پروژه | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-01`) | `تأیید فنی` |
| `P03` | پیش‌نویس، ارسال و چرخه وضعیت | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-02`, `POS-10`) | `تأیید فنی` |
| `P04` | تفکیک ثبت‌کننده و تصویب‌کننده | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-02`) | `تأیید فنی` |
| `P05` | گیت‌های فعال‌سازی پروژه | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-02`) | `تأیید فنی` |
| `P06` | منشور پروژه و استخراج اولیه | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-01`) | `تأیید فنی` |
| `P07` | بازگردانی کنترل‌شده از تعلیق و خاتمه | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-10`), `a7-p6-delivery-acceptance.spec.ts` | `تأیید فنی` |
| `P08` | بایگانی فقط‌خواندنی واقعی | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-14`) | `تأیید فنی` |
| `P09` | بازیابی کنترل‌شده از بایگانی | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-10`), `a7-p6-delivery-acceptance.spec.ts` | `تأیید فنی` |
| `P10` | درخواست تغییر روی فیلدهای مصوب | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-03`) | `تأیید فنی` |
| `P11` | هم‌ترازی دسترسی پروژه با ماتریس A.6 | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-11`–`NEG-13`) | `تأیید فنی` |

### 3.2 WBS Hierarchy, Validation & Templates (`W01`–`W07`)

| Audit ID | Title | Owning Phase | Employer Summary Bucket | Current Candidate Evidence Reference | Disposition |
| --- | --- | --- | --- | --- | --- |
| `W01` | درخت WBS چندسطحی | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-04`) | `تأیید فنی` |
| `W02` | کد، عنوان، سطح، ترتیب، وزن، مسئول و معیار تکمیل | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-04`) | `تأیید فنی` |
| `W03` | جابه‌جایی، تغییر والد و ترتیب بدون چرخه | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-02`, `NEG-03`) | `تأیید فنی` |
| `W04` | یکتایی کد WBS در تمام مسیرها | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-01`) | `تأیید فنی` |
| `W05` | قواعد وزن WBS و فعالیت‌های برگ | `A.7-P1` (`051`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-04`) | `تأیید فنی` |
| `W06` | کپی مستقل الگوی WBS به پروژه | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-04`) | `تأیید فنی` |
| `W07` | نگاشت والد-فرزندی WBS در ورود زمان‌بندی | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`, `POS-07`) | `تأیید فنی` |

### 3.3 Organizational Reference Data & Templates (`M01`–`M04`)

| Audit ID | Title | Owning Phase | Employer Summary Bucket | Current Candidate Evidence Reference | Disposition |
| --- | --- | --- | --- | --- | --- |
| `M01` | مدیریت داده‌های مرجع سازمانی موردنیاز پروژه و زمان‌بندی | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-01`) | `تأیید فنی` |
| `M02` | اتصال واقعی فرم پروژه و زمان‌بندی به داده‌های مرجع | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-01`) | `تأیید فنی` |
| `M03` | تعیین تکلیف وضعیت‌های پروژه به‌عنوان چرخه کنترل‌شده یا داده مرجع | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `guide.md` | `تأیید فنی` |
| `M04` | کتابخانه الگوهای WBS و زمان‌بندی | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-04`) | `تأیید فنی` |

### 3.4 Schedule Dates, Milestones, Dependencies, Baseline & Critical Path (`S01`–`S08`)

| Audit ID | Title | Owning Phase | Employer Summary Bucket | Current Candidate Evidence Reference | Disposition |
| --- | --- | --- | --- | --- | --- |
| `S01` | نگهداری و نمایش ۴ تاریخ کلیدی فعالیت | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-09`) | `تأیید فنی` |
| `S02` | پشتیبانی کامل مایلستون و مدت صفر | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`, `NEG-04`) | `تأیید فنی` |
| `S03` | روابط پیش‌نیازی/پس‌نیازی، Lag/Lead و تشخیص حلقه | `A.7-P3` (`053`) | `قبلاً موجود و تأییدشده روی نسخه حاضر` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`, `NEG-03`) | `تأیید فنی` |
| `S04` | تقویم کاری پروژه و هم‌راستایی محاسبه مدت/Lag | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`) | `تأیید فنی` |
| `S05` | خط مبنا، نسخه‌بندی و قفل تغییر مستقیم پس از تصویب | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-07`, `POS-08`) | `تأیید فنی` |
| `S06` | دروازه اعتبار مسیر بحرانی و محاسبه شناوری | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-09`) | `تأیید فنی` |
| `S07` | گزارش تأخیر فعالیت‌ها نسبت به خط مبنای مصوب | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-09`) | `تأیید فنی` |
| `S08` | هم‌راستایی نماهای جدول، گانت، WBS و خلاصه زمان‌بندی | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-09`) | `تأیید فنی` |

### 3.5 MSP & Primavera P6 Import Pipeline (`I01`–`I22`)

| Audit ID | Title | Owning Phase | Employer Summary Bucket | Current Candidate Evidence Reference | Disposition |
| --- | --- | --- | --- | --- | --- |
| `I01` | پشتیبانی صادقانه و کامل فرمت‌های ورود زمان‌بندی در دامنه مصوب | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `evidence/reconciliation.json` | `تأیید فنی` |
| `I02` | اعتبارسنجی اولیه فایل، حجم، پسوند، امضا و فایل‌های معیوب یا رمزدار | `A.7-P4` (`054`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/054-a7-p4-import-experience/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-06`) | `تأیید فنی` |
| `I03` | تطبیق کامل شمارش و نگاشت روی فایل واقعی `real-data/plan.mpp` | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `evidence/reconciliation.json`, `test_a7_p6_delivery_acceptance.py` (`POS-06`) | `تأیید فنی` |
| `I04` | تعیین تکلیف فعالیت‌های مدت صفر و ردیف‌های بدون والد در ورود فایل | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`) | `تأیید فنی` |
| `I05` | تعیین تکلیف روابط پیش‌نیاز به فعالیت خلاصه | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`) | `تأیید فنی` |
| `I06` | تفکیک شفاف دو حالت «افزودن/به‌روزرسانی» و «جایگزینی ایمن» | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`, `POS-08`) | `تأیید فنی` |
| `I07` | اتمیک بودن کامل ورود و عدم ایجاد داده ناقص در خطا | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-03`, `NEG-06`) | `تأیید فنی` |
| `I08` | جلوگیری از تکرار در ورود مجدد همان فایل | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-07`) | `تأیید فنی` |
| `I09` | اجرای واقعی صف و پردازنده پس‌زمینه برای ورود زمان‌بندی | `A.7-P5` (`055`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/055-a7-p5-import-operations/evidence/reproduction.md`, `independent-complete-matrix.json` (`OPS-04`) | `تأیید فنی` |
| `I10` | بازیابی وضعیت ورود پس از قطع ارتباط، بستن صفحه یا خطای موقت | `A.7-P4` (`054`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/054-a7-p4-import-experience/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-08`), `a7-p6-delivery-acceptance.spec.ts` | `تأیید فنی` |
| `I11` | قفل هم‌زمانی ورود در سطح پروژه برای MSP و P6 | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-09`) | `تأیید فنی` |
| `I12` | یکسان‌سازی کامل خط لوله‌های پیش‌نمایش، ورود مستقیم، ورود ناهمگام و خط فرمان | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `evidence/reconciliation.json` | `تأیید فنی` |
| `I13` | گزارش ساختاریافته، دقیق و قابل فهم هشدارها و خطاهای ردیفی | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-06`, `NEG-05`) | `تأیید فنی` |
| `I14` | تاریخچه کامل عملیات ورود و ممیزی در سطح پروژه | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p2_import_safety.py` | `تأیید فنی` |
| `I15` | تجربه کاربری انتخاب مجدد فایل، لغو، تلاش مجدد و صفحه‌بندی پیش‌نمایش | `A.7-P4` (`054`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/054-a7-p4-import-experience/traceability.md`, `a7-p6-delivery-acceptance.spec.ts` (`NEG-07`, `OPS-01`) | `تأیید فنی` |
| `I16` | جلوگیری از ارسال تکراری و Drag/Drop در حین ورود فعال | `A.7-P4` (`054`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/054-a7-p4-import-experience/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-09`) | `تأیید فنی` |
| `I17` | بومی‌سازی کامل فارسی/انگلیسی، راست‌به‌چپ، واکنش‌گرایی و دسترس‌پذیری صفحه‌کلید | `A.7-P4` (`054`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/054-a7-p4-import-experience/traceability.md`, `a7-p6-delivery-acceptance.spec.ts` (`OPS-01`–`OPS-03`) | `تأیید فنی` |
| `I18` | بازسنجی مجوز و وضعیت پروژه در زمان اجرای واقعی پردازنده پس‌زمینه | `A.7-P2` (`052`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/052-a7-p2-import-safety/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`NEG-10`) | `تأیید فنی` |
| `I19` | محدودیت زمان، حافظه و ایزوله‌سازی فرآیند تجزیه فایل‌های سنگین یا معیوب | `A.7-P5` (`055`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/055-a7-p5-import-operations/evidence/reproduction.md`, `independent-complete-matrix.json` (`OPS-04`) | `تأیید فنی` |
| `I20` | سیاست نگهداری، پاک‌سازی فایل خام آپلودشده و فایل‌های موقت | `A.7-P5` (`055`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/055-a7-p5-import-operations/evidence/reproduction.md`, `independent-complete-matrix.json` (`OPS-04`) | `تأیید فنی` |
| `I21` | حفظ شناسه منبع و پشتیبانی به‌روزرسانی افزایشی از فایل زمان‌بندی | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p6_delivery_acceptance.py` (`POS-07`) | `تأیید فنی` |
| `I22` | تبدیل دقیق واحدهای مدت و Lag از دقیقه به روز کاری بر اساس تقویم | `A.7-P3` (`053`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/053-a7-p3-import-fidelity/traceability.md`, `test_a7_p3_import_fidelity.py` | `تأیید فنی` |

### 3.6 Acceptance Data, Infrastructure & Delivery Package (`D01`–`D04`)

| Audit ID | Title | Owning Phase | Employer Summary Bucket | Current Candidate Evidence Reference | Disposition |
| --- | --- | --- | --- | --- | --- |
| `D01` | مجموعه داده مرجع و فایل‌های نمونه معتبر و معیوب برای پذیرش | `A.7-P1` (`051`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/051-a7-p1-project-reference/traceability.md`, `evidence/reconciliation.json` | `تأیید فنی` |
| `D02` | محیط اجرای پذیرش تکرارپذیر با سرویس‌های واقعی | `A.7-P5` (`055`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/055-a7-p5-import-operations/evidence/reproduction.md`, `independent-complete-matrix.json` (`OPS-04`) | `تأیید فنی` |
| `D03` | سناریوهای پذیرش انتها-به-انتها با داده واقعی | `A.7-P6` (`056`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/056-a7-p6-delivery-acceptance/evidence/scenarios.json`, `test_a7_p6_delivery_acceptance.py`, `a7-p6-delivery-acceptance.spec.ts` | `تأیید فنی` |
| `D04` | بسته تحویل و چک‌لیست پذیرش کارفرما | `A.7-P6` (`056`) | `در A.7 اصلاح/تکمیل شد` + `قابل تست توسط کارفرما` | `specs/056-a7-p6-delivery-acceptance/guide.md`, `evidence/package.json`, `evidence/minutes.md`, `evidence/validate_package.py` | `تأیید فنی` |
