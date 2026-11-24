# Stage 1.1 Discovery — Phase A.1

## Selection

- Selected phase: **A.1 — گزارش روزانه و خروجی‌ها**.
- Selection rule: R.0, A.6 and A.7 are fully implemented; A.1 is the first declared phase with remaining tasks.
- User context: “start A.1, نهایی‌کردن قواعد اطلاعات روزانه. Previews feature is accepted and completed”. The implemented preview/export status was not treated as final employer acceptance.

## Remaining requirements

| ID | Requirement | Acceptance focus |
|---|---|---|
| A.1.01 | نهایی‌کردن قواعد اطلاعات روزانه | Versioned field contract, reference-day fixture, units/conversions, null/zero and provenance decisions. |
| A.1.02 | تطبیق تمام بخش‌های گزارش با روز مرجع | Full daily-report section parity, lifecycle, lineage, source preservation and browser/API evidence. |
| A.1.03 | رفع اختلاف ارقام و نمایش خروجی‌ها | Independent numeric/formula reconciliation, Excel/PDF parity, complete filtered totals and read-only preview. |
| A.1.04 | ارائه نمونه نهایی و تأیید اولیه گزارش | Frozen sample/SHA, checksums, role/language/device/cross-project evidence and traceable employer sign-off. |

## Evidence and boundaries

- Primary phase source: `apps/web/src/app/data/delivery-plan.ts:161-205`.
- Schedule cross-check: `output/delivery-plan-2026-11-03/schedule.json`.
- Knowledge context was refreshed semantically on 2026-11-24 and returned fresh hybrid retrieval.
- Graphify query covered daily-report rules, previews, totals, corrections, and related tests; graph results are discovery evidence, not runtime acceptance proof.
- Downstream QA must fan out only the four remaining IDs above and must verify end-user browser behavior, negative permissions, bilingual rendering, persistence/reload, and absence of console/5xx failures.
