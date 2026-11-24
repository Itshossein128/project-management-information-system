# A.1 / B04 — فیلترها، مجموعه نتیجه و جمع قابل اتکا

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

زیرمرحله جاری: B04 — فیلترها، مجموعه نتیجه و جمع قابل اتکا
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01, B02.
مرحله قبلی در ترتیب: B03.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: E11, E12, E13, E14
سهم مشترک با مالک دیگر: E15, D07, D05. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: دو عضو مجاز با یک URL یکسان، فیلتر روزانه و دفتر فعالیت را اعمال می‌کنند؛ refresh، بازگشت مرورگر، تعویض صفحه و دانلود کامل Excel همان مجموعه منطقی را بازسازی کند.
- فهرست روزانه date/status و discipline/contractor/block و همه فیلترهای الزام‌شده FR016 را طبق معنای ثبت‌شده برای خلاصه چندواحدی بپذیرد. روشن کن تطبیق همزمان پیمانکار/واحد/بلوک باید روی همان ردیف منبع باشد یا عضویت در خلاصه؛ این انتخاب را از خود اختراع نکن و در صورت فقدان به B01 برگردان.
- دفتر فعالیت date/disc/parcel/zone/block/subcontractor و سایر ابعاد الزام‌شده منبع را در UI/URL/API/Excel هم‌معنا اعمال کند؛ شناسه پروژه دیگر مجاز نشود. تاریخچه مستقلِ B02 وارد مجموع عملیاتی نشود.
- جمع کل با کل نتیجه فیلترشده محاسبه شود؛ quantity به تفکیک واحد و measured بودن باشد، m2 وm3 جمع نشوند و null/not-measured پنهانی صفر نشوند. عنوان شمارش مطابق D07؛ headcount فعالیت‌ها تعداد افراد یکتا نیست.
- fixture حداقل ۵۱ ردیف، page_size=50، دو واحد اندازه‌گیری، مقدار نامعلوم، دو نسخه approved و دو پیمانکار با شغل هم‌نام داشته باشد. count=51 و جمع کامل ۵۱ در مثال واحدِ کنترل‌شده، مستقل از صفحه باقی بماند؛ Excel همه نتیجه را بدهد.
- معیار اتمیک US-EX-04 برای فیلتر زیر یک ثانیه روی داده/محیط مستند، و بازیابی فیلتر برای عضو مجاز دیگر ردیابی شود؛ اگر با قرارداد جاری تعارض دارد حل مصوب ثبت شود، نه حذف خاموش.
پایان قابل آزمون: صفحه، aggregate، URL و خروجی یک دامنه داده داشته باشند؛ سهم E15 با گیت B02 بازآزمایی شود.

در تحویل‌نامه، DEF-B04-06 به ناوبری URL اشاره می‌کند؛ در جدول و JSON محلی همین شناسه به ورود نسخه تاریخی اشاره دارد. هر دو سناریو لازم‌اند. ناوبری ذیل DEF-B04-03 و ریسک نسخه تاریخی با B02 پوشش داده شود. جدول محلی برای شرح DEF-B04-02/04/05 مبناست و مقادیر اندازه‌گیری‌نشده و واحدها ذیل DEF-B04-02 آزموده شوند.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B04: qa_passed. Existing specification, regression and handoff baseline. Adopt its current scope and use existing QA evidence. If specify is invoked for a material residual gap, scope that gap against the existing spec.
- Reports: output/a1-requirements-2026-11-22-stage1-b04-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b04-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Use specs/060-a1-b04-filters-totals as the baseline. Under FR-001 one eligible source activity row must satisfy all selected discipline, contractor and block dimensions. Include a split-row exclusion case. Preserve all-results FILE 1 and totals across pagination, role/project scope, bilingual URL restoration and zero versus unset. Reconcile any older DEF-B04-06 variants by scenario and target evidence.
- DEF-B04-01 — reported resolved in current QA; preserve as regression coverage.
- DEF-B04-02 — reported resolved in current QA; preserve as regression coverage.
- DEF-B04-03 — reported resolved in current QA; preserve as regression coverage.
- DEF-B04-04 — reported resolved in current QA; preserve as regression coverage.
- DEF-B04-05 — reported resolved in current QA; preserve as regression coverage.

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.03
معیار بسته در کشف مرحله ۱: صفحه، aggregate، URL، pagination و Excel export از یک دامنه داده استفاده کنند؛ فیلترهای الزامی کامل و project-isolated باشند؛ جمع ۵۱ ردیف مستقل از صفحه ۵۰تایی، ۵۱ بماند.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b04-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b04-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B04-01 — روی داده ۵۱ ردیفی، تغییر صفحه ۵۰/۱، جمع کل را تغییر ندهد.
- DEF-B04-02 — پاسخ فهرست امکان نمایش جمع تمام نتایج فیلترشده را مستقل از صفحه بدهد و واحدها و null/zero را تفکیک کند.
- DEF-B04-03 — فیلتر دیسیپلین، پیمانکار و بلوک همراه با دیگر ابعاد مصوب در UI/API/URL هم‌معنا باشند. reload، لینک و back/forward پوشش داده شوند.
- DEF-B04-04 — جمع نفرات سطرها با برچسب منطبق بر D07 نمایش داده شود.
- DEF-B04-05 — FILE1 و فهرست بر دامنه یکسان فیلترشده و مجاز منطبق باشند.
- DEF-B04-06 — ریسک گزارش‌شده را با قرارداد B02 بررسی کن. فیلتر عملیاتی نباید نسخه تاریخی را دوباره وارد نتیجه یا جمع کند.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B04: qa_failed. Acceptance criterion: API, UI, URL, Excel, pagination, and totals represent one complete filtered queryset with correct units and unset semantics.
- Source reports: output/a1-requirements-2026-11-21-stage1-b04-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b04-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Use specs/060-a1-b04-filters-totals as the baseline. The 51-row fixture must yield the same full totals on both pages and the same logical rows in FILE1. Require server-wide aggregates for the authorized filtered set, discipline/block/contractor filters with clear multi-unit matching, separate measured zero from unknown, and label raw row sums without man-days or unique-person claims.
- DEF-B04-01 — Client-side aggregation on page slice instead of whole queryset
- DEF-B04-02 — Missing whole-queryset totals/aggregates payload in ActivityLogView API
- DEF-B04-03 — Missing discipline, block, and contractor filters on Daily Reports list
- DEF-B04-04 — Collapsing unset/unmeasured quantities into numeric zero
- DEF-B04-05 — Misleading man-days labeling for raw headcount row sum

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B04 — فیلترها، مجموعه نتیجه و جمع قابل اتکا

**مربوط به:** E11/E12/E13/E14/E15/D07. **پیش‌نیاز:** سیاست نسخه جاری از B02.

فیلترهای discipline/contractor/block در فهرست روزانه با معنای روشن برای خلاصه چندواحدی و همان معنای API/UI/URL تکمیل شوند. دفتر فعالیت aggregate کل queryset فیلترشده را از سرور بگیرد؛ quantity بر اساس واحد و measured بودن محاسبه شود؛ مقدار نامعلوم از صفر متمایز باشد. عنوان headcount مطابق معیار مصوب باشد؛ جمع ردیف‌ها به افراد یکتا تبدیل لفظی نشود.

**آزمون تحویل:** ۵۱ ردیف با page_size=50، چند واحد اندازه‌گیری، یک مقدار نامعلوم، دو نسخه approved و دو پیمانکار هم‌نامِ شغل. URL مشترک نزد عضو مجاز دیگر، refresh و بازگشت مرورگر، نتیجه فهرست و Excel کامل، همگی یک مجموعه منطقی بدهند. جمع کل با تغییر صفحه عوض نشود.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

E11 — دفتر فعالیت‌ها و FILE1 با تمام نتیجه فیلتر
فاز مالک/اثر منبع: پشتیبان A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: API دفتر فعالیت و خروجی Excel کامل queryset فیلترشده وجود دارند.
باقیمانده: رفع نسخه‌های تاریخی و جمع کل در E14/E15؛ تثبیت معیار measured/نامعلوم در داده legacy.
پذیرش: تمام ردیف‌های نتیجه فیلتر، مستقل از صفحه، با همان ستون‌ها صادر شوند.
حد شاهد: آزمون‌های منتخب FILE1 موفق؛ نقص‌های دامنه نتیجه جدا بازتولید شده
ارجاع: apps/api/core/field_reports/report_views.py:89؛ apps/api/core/field_reports/shiraz_file1_excel.py:1

E12 — فیلترهای کامل فهرست گزارش روزانه و URL
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: فهرست روزانه date_from/date_to/status/page دارد؛ discipline/contractor/block در UI و queryset این مسیر مشاهده نشد.
باقیمانده: پیاده‌سازی/تثبیت معنای سه فیلتر مفقود برای یک خلاصه چندواحدی؛ اتصال UI/API/URL و دانلود.
پذیرش: URL اشتراکی تمام فیلترهای FR016 را با نتیجه یکسان بازسازد.
حد شاهد: نقص با بازبینی UI و backend؛ سناریوی مرورگر اجرا نشده
ارجاع: apps/web/src/app/routes/daily-reports-list.tsx:91؛ apps/api/core/field_reports/daily_report_views.py:153؛ specs/044-shiraz-excel-parity-pdf/spec.md:197

E13 — فیلتر چندبعدی دفتر فعالیت و بازگردانی URL
فاز مالک/اثر منبع: پشتیبان A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: date/disc/parcel/zone/block/subcontractor/page در URL و query وجود دارند.
باقیمانده: UAT لینک مشترک، refresh، بازگشت مرورگر و یکسانی download؛ replace:true می‌تواند تاریخچه را محدود کند.
پذیرش: دو عضو مجاز با URL یکسان ورودی‌ها، صفحه و مجموعه نتیجه یکسان ببینند.
حد شاهد: وجود پیاده‌سازی؛ ریسک history مشاهده کدی است و نقص اجرایی اثبات‌شده نامیده نمی‌شود
ارجاع: apps/web/src/app/routes/project-activity-log.tsx:1؛ specs/044-shiraz-excel-parity-pdf/spec.md:198

E14 — جمع کل دفتر فعالیت روی تمام نتیجه فیلتر، جدا به تفکیک واحد
فاز مالک/اثر منبع: پشتیبان A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: UI جمع headcount و quantity را از data.results همان صفحه می‌گیرد؛ API aggregate کل نمی‌دهد.
باقیمانده: محاسبه کل سمت سرور با همان فیلتر و قواعد null/measured؛ اصلاح عنوان نفرروز مطابق D07.
پذیرش: برای ۵۱ ردیف و صفحه ۵۰تایی جمع کل ۵۱ باشد و با خروجی کل برابر؛ m2 با m3 جمع نشود.
حد شاهد: نقص اجرایی: count=51، results=50 و جمع صفحه=50؛ pagination-probe.json
ارجاع: apps/web/src/app/routes/project-activity-log.tsx:129؛ apps/api/core/field_reports/report_views.py:89

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- E11 | specs/039-auto-daily-rollup/spec.md:187 | FR-009
- E13 | specs/039-auto-daily-rollup/spec.md:188 | FR-010
- E11 | specs/039-auto-daily-rollup/spec.md:189 | FR-011
- E11 | specs/039-auto-daily-rollup/spec.md:215 | SC-005
- E13 | specs/039-auto-daily-rollup/spec.md:216 | SC-006
- E12 | specs/044-shiraz-excel-parity-pdf/spec.md:197 | FR-016
- E13 | specs/044-shiraz-excel-parity-pdf/spec.md:198 | FR-017
- E11 | specs/044-shiraz-excel-parity-pdf/spec.md:199 | FR-018
- E14 | specs/044-shiraz-excel-parity-pdf/spec.md:200 | FR-019
- E13 | specs/044-shiraz-excel-parity-pdf/spec.md:222 | SC-004

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):
- US-AG-06 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:129 | سهم این مرحله: E11, E13, E14؛ کل گروه‌ها: E11, E13, E14, E15
- US-EX-04 | reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md:79 | سهم این مرحله: E12, E13, E14؛ کل گروه‌ها: E12, E13, E14

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```
