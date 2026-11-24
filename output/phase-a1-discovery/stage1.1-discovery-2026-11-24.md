# Stage 1.1 Discovery — A.1

Inspected on 2026-11-24. The first phase in declared delivery-plan order that is not fully implemented is **A.1**. Only its four `remaining` tasks are in scope for downstream QA fan-out.

## Remaining requirements

- **A.1.01 — نهایی‌کردن قواعد اطلاعات روزانه**
  - Acceptance: قاعده null/صفر، شیفت، شمارش نفر و منبع هر بخش ثبت شود.
- **A.1.02 — تطبیق تمام بخش‌های گزارش با روز مرجع**
  - Acceptance: اقلام، واحدها، ارقام و فرمول‌ها با مرجع مستقل مقایسه و Excel بازحساب شود.
- **A.1.03 — رفع اختلاف ارقام و نمایش خروجی‌ها**
  - Acceptance: ساعت نامعلوم ماشین‌آلات صفر قطعی جلوه نکند و تست دقیق اضافه شود.
- **A.1.04 — ارائه نمونه نهایی و تأیید اولیه گزارش**
  - Acceptance: فایل و نسخه و نتیجه بازبینی ارقام و صفحه‌بندی نگهداری شود.

## Phase acceptance

یک روز کامل با ارقام کنترل‌شده، Excel مستقل بازحساب‌شده، PDF خوانا و تأیید اولیه لازم است؛ بستن کل دامنه گزارش‌ها پس از A.10 انجام می‌شود.

## Evidence

- `apps/web/src/app/data/delivery-plan.ts:161-206`
- `output/delivery-plan-2026-11-03/schedule.json`
- `output/a1-requirements-2026-11-18/requirements.json`
- `output/a1-requirements-2026-11-18/remaining-work.md`
- `graphify-out/graph.json`
- `knowledge/agent-instructions.md`

## Inspection notes

The generic employer extractor returned stale A.6 context, so it was excluded from A.1 conclusions. Completed A.1-B04 and historical QA artifacts are not included in the remaining-task fan-out scope.
