# A.1 / B05 — تطبیق مستقل عدد، فرمول و چاپ

```text
/speckit-specify

این درخواست فقط نگارش specification برای همین زیرمرحله است. طبق قالب فعال SpecKit یک feature specification و checklist کیفیت مستقل تولید کن و سپس متوقف شو؛ plan، tasks، analyze، implement، تست محصول، استقرار و اجرای مرحله بعد مجاز نشده‌اند. خروجی حاضرِ Stage 2 صرفاً ورودی specify است.

ورودی workflow اصلی (عین متن):
Go for the next step to deliver the application, based on A.1 phase in http://localhost:5173/delivery-plan

ریشه پروژه: /home/hossein/Desktop/projects/building-management
منبع مرحلهٔ ۱: /home/hossein/Desktop/projects/building-management/output/a1-requirements-2026-11-18
پیش از تفسیر، knowledge/agent-instructions.md و راهنمای پروژه را رعایت کن. منابع اصلی زیر را بخوان: README.md، remaining-work.md، scope-decisions.md، requirements-and-delivery.md، requirements.json، source-clauses.json/md، atomic-stories.json، atomic-coverage.md، broader-daily-sections.md، employer-summary.md و evidence/README.md در پوشه منبع. coverage.json همین بسته نگاشت مالکیت است؛ الزام تازه یا تأیید کارفرما نیست. برای هر گروه، بندهای منبع و معیارهای کامل داستان‌های مرتبط را هم بخوان؛ شناسه FR/SC به‌تنهایی یکتا نیست و باید با مسیر و خط همراه باشد.

قواعد نگارش:
- چه چیزی و چرا، نقش‌ها، ارزش کاربر، دامنه/غیردامنه، سناریوهای Given/When/Then و شکست/لبه، نیازمندی‌های قابل آزمون، معیارهای موفقیت قابل اندازه‌گیری، وابستگی و تصمیم‌های باز را در spec بنویس. فناوری/ساختار کد را راه‌حل اجباری نکن. نام API/مدل در شواهد فقط نشانی رفتار فعلی است.
- شناسه‌های H/D/W/E/Q/X و C و US و path:line بندها را به FR/SC و سناریوهای spec وصل کن؛ برای هر بند disposition صریحِ حفظ رفتار، رفع شکاف، تصمیم شرطی یا ارجاع فاز دیگر بده. نگاشت داستان به گروه به معنی اجرای تمام سناریوهای آن نیست؛ اختلاف‌ها را در سطح معیار بررسی کن.
- مبنای ممیزی f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a در 2026-11-18 است؛ وضعیت کد امروز از این متن استنباط نشود. ۱۶۲ تست موجود و۲ کنترل موفق و۶ strict XFAIL تاریخی‌اند؛ XFAIL شاهد نقص است. نبود شاهد با نبود قابلیت یکی نیست. اگر نقص در کد روز رفع شده، الزام حفظ رفتار و اثبات باقیمانده را ثبت کن، بازنویسی نکن. وضعیت‌ها و تصمیم‌های نقل‌شده از ممیزی پایه تاریخی‌اند؛ برای رفتار جاری، قرارداد نسخه‌دار و شواهد تاریخ‌دار پایین را بررسی کن.
- تصمیم باز را به کارفرما نسبت نده؛ پیشنهاد، تصمیم مصوب و رفتار مشاهده‌شده جدا باشند. C01..C10 را با متن منبع حفظ کن؛ اثرگذاری تصمیم باید پیش از کار وابسته رفع شود. برای پنهان‌کردن ابهام مادی default نساز. حداکثر۳ سؤال بحرانی هر دور؛ باقی موارد در رجیستر باز باقی بمانند.
- هسته روزانه، موتور تجمیع، صفحات واحد، workflow و خروجی‌های موجود را بی‌دلیل از نو تعریف نکن. کل عملیات/آفلاین/منابع A.8، ارتباطات A.3.C، گزارش‌های دوره‌ای A.10 و استقرار/آموزش جامع A.12 در مالک خود باقی‌اند؛ اثر خراب‌کننده آن‌ها بر A.1 قابل چشم‌پوشی نیست. قرارداد دامنه B01 هر توسعه شرطی را به مالک مشخص می‌رساند.
- پیش از ایجاد feature، مسیر/شماره آزاد را با وضعیت واقعی specs انتخاب کن؛ مسیر اشغال‌شده را بازنویسی نکن. شناسه B بسته ثابت است و feature-number نیست. یک feature در هر فراخوانی؛ شماره از پیش تحمیل نشده است.
- خروجی specify: مسیر واقعی spec/checklist، traceability، نتیجه بررسی کیفیت، تصمیم‌های باز و آمادگی واقعی clarify/plan. تولید spec گواه پیاده‌سازی، release یا پذیرش نیست.

زیرمرحله جاری: B05 — تطبیق مستقل عدد، فرمول و چاپ
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01, B02, B03, B04.
مرحله قبلی در ترتیب: B04.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: E03, Q01, Q02
سهم مشترک با مالک دیگر: E04, E05. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: بازبین مستقل با روز مرجعِ B01، ارقام، برچسب‌ها، فرمول‌ها و صفحات چاپی خروجی‌های release نامزد را با مرجع و با یکدیگر تطبیق می‌دهد.
- expected از سند/سلول کنترل‌شده مستقل تهیه شود؛ استفاده از همان builder یا موتور aggregation برای ساخت expected ممنوع است. برای هر بخش source/unit/conversion/expected/actual/delta ثبت شود؛ generated-sample مصنوعی ممیزی golden واقعی نیست.
- FILE4 در Excel یا نرم‌افزار مستقل سازگار واقعاً بازحساب شود؛ نام/نسخه موتور، لاگ recalc، مقدار cache، خطاهای #REF/#VALUE/#NAME و محاسبه روی ردیف خالی ثبت شوند. وجود SUM در XML یا صرف بازکردن فایل گواه recalc نیست.
- PDF و Excel و FILE1/FILE5/FILE6 مرتبط، با روز مرجع و با هم بررسی عددی/معنایی و بصری شوند؛ تمام صفحات معمول و طولانی screenshot داشته باشند و source approved/correction درست باشد.
- سرعت دانلود همان نسخه روی داده معمول ۱۵–۳۰ فعالیت و۲۰ ردیف منابع اندازه‌گیری شود؛ معیار زیر۳ثانیه منبع و معیارهای زمان/موفقیت کاربر از بندهای SC مرتبط با زمینه سنجش ثبت شوند. مدت pytest جای سنجش کاربر نیست.
پایان قابل آزمون: mapping، expected مستقل، اختلاف قبل/بعد، فایل نهایی، تصاویر صفحات، لاگ بازحساب و checksum فراهم باشد. اختلاف مؤثر بر گزارش رسمی صفر؛ اختلاف حل‌نشده مانع پذیرش و به B02/B03/B04 برگردد. محیط/مرجع موجود نبود نتیجه blocked/unverified ثبت شود، نه موفق.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B05: qa_failed. Next active specification. Use the existing passed packages as baselines and scope the residual independent reconciliation work.
- Reports: output/a1-requirements-2026-11-22-stage1-b05-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b05-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Specify independent source-to-expected calculations, unit/rounding rules, cached-value checks on candidate Excel files and standalone recalculation. Record formula, value, rendering and print comparisons by cell and page with SHA-256 and discrepancy decisions. Measure end-to-end SC-002 under 3.0 seconds for representative FILE 4 and PDF downloads (15–30 activities and 20 resource/equipment rows) on the candidate. Recheck the historical missing-cache observation on fresh exports; generated-sample.xlsx is synthetic historical evidence. Define closure evidence for A.1.02 and A.1.03. B01–B04 are reported passes with candidate validation required.
- DEF-B05-01 — Missing cached values for formula cells in exported Excel and lack of standalone recalculation tests
- DEF-B05-02 — Missing real-world download latency benchmark (<3.0s) for standard site daily reports (SC-002)
- DEF-B05-03 — Expected test assertions generated from internal models/aggregators rather than independent calculation oracle (Q01)
- DEF-B05-04 — Lack of visual regression and page-by-page screenshot diff logs across PDF, Excel print layout, and employer reference form
- DEF-B05-05 — Delivery plan tasks A.1.02 and A.1.03 remain in 'remaining' status

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.02, A.1.03
معیار بسته در کشف مرحله ۱: برای روز مرجع، mapping و expected مستقل، اختلاف قبل/بعد، بازحساب بدون #REF/#VALUE/#NAME، تصاویر چاپی، لاگ و checksum ثبت شود؛ اختلاف مؤثر حل‌نشده نتیجه را blocked/unverified کند.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b05-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b05-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B05-01 — بازحساب مستقل و مقایسه مقدار/فرمول را ثبت کن. نبود cache نمونه تاریخی و خطاهای بازحساب جداگانه گزارش شوند. الزام انتشار cache فقط با شواهد قرارداد.
- DEF-B05-02 — SC-002 را برای دانلود Excel/PDF زیر ۳ ثانیه روی نسخه هدف با ۱۵ تا ۳۰ فعالیت و ۲۰ ردیف تجهیزات اندازه‌گیری کن.
- DEF-B05-03 — expected و قواعد گردکردن/واحد را از داده مرجع مستقل از builder و aggregate تولید کن.
- DEF-B05-04 — نقشه سلول/صفحه، اختلاف قبل/بعد، تصاویر خوانا، لاگ بازحساب و checksum را برای Excel/PDF و مرجع نگه دار.
- DEF-B05-05 — پیش‌نیازهای B02/B03/B04 را با شواهد همان نسخه راستی‌آزمایی کن. اختلاف مؤثر باز نتیجه را blocked/unverified نگه دارد.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B05: qa_failed. Acceptance criterion: Independent expected values, recalculation logs, mapping, checksums, screenshots, discrepancy decisions, and measured download time prove Excel/PDF parity.
- Source reports: output/a1-requirements-2026-11-21-stage1-b05-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b05-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Specify an independently computed expected dataset and reconcile cells, formulas and rendered output. Record before/after cached values and standalone recalculation results, page-by-page print comparisons, SHA-256 and unresolved discrepancies. Measure SC-002 on the target release with representative data and record whether download is under 3.0 seconds. The upstream blocker finding requires current evidence for B02–B04. B02/B03 have reported technical passes, and B04 remains failed.
- DEF-B05-01 — Missing cached values for formula cells in exported Excel and lack of standalone recalculation tests
- DEF-B05-02 — Missing real-world download latency benchmark (<3.0s) for standard site daily reports (SC-002)
- DEF-B05-03 — Expected test assertions generated from internal models/aggregators rather than independent calculation oracle (Q01)
- DEF-B05-04 — Lack of visual regression and page-by-page screenshot diff logs across PDF, Excel print layout, and employer reference form
- DEF-B05-05 — Unresolved blocking defects in upstream prerequisites B02, B03, and B04

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B05 — تطبیق مستقل عدد، فرمول و چاپ

**مربوط به:** Q01/E03/E04/E05/Q02. **پیش‌نیاز:** B02 تا B04 سبز.

روز مرجع کامل از داده کنترل‌شده مستقل ساخته شود؛ expected از خود builder یا همان موتور aggregation تولید نشود. هر بخش به منبع/واحد/تبدیل وصل شود. Excel در نرم‌افزار مستقل بازحساب و خطاها/مقادیر cache ثبت شوند. PDF و Excel کنار مرجع و کنار هم از نظر ارقام، برچسب و چاپ بررسی شوند. سرعت دانلود روی نسخه هدف و داده معمول اندازه‌گیری شود.

**خروجی:** mapping، expected مستقل، اختلاف قبل/بعد، فایل‌های نهایی، screenshot صفحات، لاگ recalc و checksum؛ هر اختلاف باز دارای تصمیم/رفع صریح باشد. تولید یک فایل مصنوعی یا assertion روی وجود متن، جای این مرحله را نمی‌گیرد.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

E03 — فرمول‌های بومی جمع و بازحساب در نرم‌افزار مستقل
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: فرمول SUM و جمع کل در xlsx نوشته می‌شوند و تست ساختار دارند.
باقیمانده: بازحساب واقعی با Excel یا موتور سازگار و کنترل مقادیر cache/خطا؛ صرف نوشتن فرمول کافی نیست.
پذیرش: جمع کنترل‌شده برابر مرجع و بدون #REF/#VALUE/#NAME باشد؛ فرمول بر داده خالی صفر ساختگی نسازد.
حد شاهد: وجود فرمول در آزمون تأیید؛ recalc مستقل این نوبت اجرا نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:247؛ specs/044-shiraz-excel-parity-pdf/spec.md:219

Q01 — روز مرجع کامل و نگاشت مستقل همه داده‌ها
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: فایل‌های واقعی در real-data ثبت شده‌اند؛ آزمون‌های واحد و sample کنترل موجودند.
باقیمانده: انتخاب یک روز کامل با ارقام کنترل‌شده تمام بخش‌ها و ساخت expected مستقل از builder/aggregation.
پذیرش: برای هر مقدار خروجی، سلول یا سند منبع، واحد، تبدیل و انتظار ثبت شود؛ اختلاف باز صفر.
حد شاهد: گواه تطبیق مستقل کامل یک روز و پذیرش کارفرما در بررسی حاضر احراز نشد؛ نبودش در کل دنیا ادعا نمی‌شود
ارجاع: docs/delivery/R0-scope-and-reports-contract.md:30؛ output/delivery-plan-2026-11-03/delivery-plan.md:107

Q02 — معیار سرعت دانلود و زمان انجام کار توسط کاربر
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: تولید فایل در آزمون کار می‌کند؛ معیار ۳ ثانیه دانلود و معیارهای usability در specs وجود دارند.
باقیمانده: اندازه‌گیری روی همان release و روز معمول ۱۵–۳۰ فعالیت و ۲۰ ردیف منابع؛ تجربه کاربران فارسی/انگلیسی.
پذیرش: دانلود معمول زیر ۳ ثانیه طبق معیار توافق‌شده؛ نرخ موفقیت/زمان کاربر با شاهد ثبت شود.
حد شاهد: سنجش کارایی/کاربر این نوبت اجرا نشده؛ زمان pytest معیار دانلود نیست
ارجاع: specs/044-shiraz-excel-parity-pdf/spec.md:220؛ specs/028-auto-daily-report-summary/spec.md:139

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- Q02 | specs/007-daily-report-gaps/spec.md:154 | SC-006
- Q02 | specs/028-auto-daily-report-summary/spec.md:139 | SC-006
- E03 | specs/044-shiraz-excel-parity-pdf/spec.md:219 | SC-001
- Q02 | specs/044-shiraz-excel-parity-pdf/spec.md:220 | SC-002
- Q01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:76 | SC-DR-001
- Q01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:77 | SC-DR-002
- Q01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:78 | SC-DR-003
- Q01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:79 | SC-DR-004

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):
- US-EX-01 | reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md:26 | سهم این مرحله: E03؛ کل گروه‌ها: E01, E02, E03, E04

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```
