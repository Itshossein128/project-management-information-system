# پرامپت‌های Stage 2 برای A.1

این بسته فقط ورودی‌های `/speckit-specify` را تولید می‌کند. هیچ feature، branch، کد محصول یا پذیرش اجرایی ایجاد نشده است.

`granularity: "multi"`؛ شش بسته به ترتیب زیر، هرکدام یک فراخوانی specify. تصمیم بر چندمرحله‌ای بودن بر اساس کوپلینگ قرارداد داده، نسخه/منابع، خروجی، فیلتر/جمع، تطبیق مستقل و پذیرش است؛ تعداد فایل به‌تنهایی ملاک نیست.

## ترتیب استفاده

1. [B01 — بستن قرارداد داده و نمونه آزمون](01-b01-data-contract.md)
2. [B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده](02-b02-version-integrity.md)
3. [B03 — رفع اختلاف خروجی با فرم مرجع](03-b03-reference-parity.md)
4. [B04 — فیلترها، مجموعه نتیجه و جمع قابل اتکا](04-b04-filters-totals.md)
5. [B05 — تطبیق مستقل عدد، فرمول و چاپ](05-b05-independent-reconciliation.md)
6. [B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما](06-b06-delivery-acceptance.md)

متن داخل بلوک هر فایل را کامل وارد کنید. پس از تولید spec و checklist متوقف شوید. clarify برای تصمیم‌های باز مرحله بعد است؛ اجرای plan/tasks/implement یا کل چرخه با این بسته درخواست نشده است. برای specification بعدی وابستگی‌ها را صریح ثبت کنید؛ برای اجرای کار وابسته، قرارداد و handoff معتبر قبلی لازم است. مراحل را هم‌زمان روی feature pointer مشترک اجرا نکنید. شماره feature هنگام فراخوانی با وضعیت واقعی مخزن انتخاب می‌شود.

وابستگی سخت B04 به B01/B02 است؛ قرارگیری آن پس از B03 ترتیب انتخاب‌شده برای اجرای متوالی است. B05 به خروجی اصلاح‌شده B02..B04 و B06 به بسته‌شدن B01..B05 وابسته است.

## مرز دامنه و پوشش

[coverage.json](coverage.json) ماتریس کامل است: ۶۱/۶۱ گروه، ۳۷۰/۳۷۰ بند منبع، ۴۲/۴۲ داستان اتمیک و ۱۰/۱۰ تصمیم C01..C10. برای هر گروه یک مالک اصلی و سهم مراحل دیگر ثبت شده؛ بندها با path:line:id یکتا شده‌اند. متن اصلی بندها و متن کامل داستان‌ها حفظ شده است. همه معیارهای داستان در specify باید جدا ارزیابی شوند؛ نسبت‌دادن داستان به گروه گواه اجرای سناریو نیست.

پوشش ۱۰۰٪ یعنی هیچ قلمی بی‌ردیابی نیست؛ به معنی پیاده‌سازی یا پذیرش ۱۰۰٪ نیست. قابلیت موجود حفظ و شکاف بسته می‌شود؛ X01..X10 جز X07 دامنه بیرونی/سازگاری دارند و با نام فاز مالک منتقل می‌شوند، نه حذف یا اعلام تکمیل. X07 و H05/E17 و PDF مستقل واحد و پروفایل فرم تابع تصمیم B01 هستند. C09/C10 افزون بر C01..C08 حفظ شده‌اند. متن تصمیم‌های قدیمی برای ردیابی حفظ شده است. وضعیت جاری را از قرارداد B01 بخوانید.

ممیزی پایه در 2026-11-18 روی f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a بوده؛ آزمون‌های آن در Stage 2 تکرار نشده‌اند. فایل‌های generated-sample مصنوعی‌اند. منابع اصلی مستقیماً مبنای ماتریس‌اند.

## بررسی بازتولیدپذیر

از ریشه مخزن اجرا کنید:

```bash
python3 output/a1-requirements-2026-11-18/speckit-prompts/validate_coverage.py
```

اعتبارسنجی، برابری دقیق ورودی‌ها/نگاشت‌ها، مالک یکتا، لینک مرحله، DAG، حفظ متن، fingerprint منابع و یکسان‌بودن فایل‌های تولیدی در هر دو مسیر را کنترل می‌کند. این بررسی تست محصول نیست.

نسخه دوم همین فایل‌ها در `output/speckit-prompts/` قرار دارد. [all-prompts.md](all-prompts.md) نسخه تجمیعی برای مرور است؛ هر بلوک باید جدا و به ترتیب استفاده شود.

## تحویل‌نامه و QA مرحلهٔ اول

چهار قلم رسمی A.1.01 تا A.1.04، شش معیار پذیرش بسته و ۳۶ یافته QA در ماتریس و پرامپت‌های مربوط نگاشت شده‌اند. DEF-B02-06 فقط در Markdown محلی آمده است. اختلاف معنای DEF-B04-06 در گزارش محلی و تحویل‌نامه ثبت شده و هر دو سناریو پوشش دارند. مسیر و SHA-256 گزارش‌های Markdown و JSON ثبت شده‌اند. خلاصه کشف و معیارهای بازبینی هر یافته در ماتریس آمده‌اند تا پرامپت‌ها با یک checkout که گزارش‌های محلی را ندارد هم قابل استفاده باشند.

## Stage 1 update — 2026-11-22

**Next active prompt: [B05](05-b05-independent-reconciliation.md).** B01–B04 have package-specific technical QA passes and existing specifications. Their prompts serve as regression and handoff baselines. B05 has five open findings and B06 has six. Run B06 after B05 and require candidate-bound evidence for B01–B05 before release acceptance. The B06 report's blanket upstream blocker conflicts with the B01–B04 package results. The matrix retains both source claims and their reconciliation. The delivery-plan source still lists A.1.01–A.1.04 as remaining.

The November 22 reports and supplied workflow handoff were available. The separate `state.memory.stage1_audit_snapshot` field was unavailable. The knowledge index was stale. Stage 1 reported a login redirect at the local delivery-plan route. The matrix validates prompt traceability and file integrity. Product QA and employer disposition remain outside the evidence produced in Stage 2.
