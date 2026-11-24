# Stage 2 — A.1 B01 → B06

Each block is one separate specify invocation. B05 is the next active prompt.

# A.1 / B01 — بستن قرارداد داده و نمونه آزمون

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

زیرمرحله جاری: B01 — بستن قرارداد داده و نمونه آزمون
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: روز مرجع کامل و مسئول پذیرش؛ تصمیم‌های باز مجاز به جعل نیستند.
مرحله قبلی در ترتیب: ندارد.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: H04, H05, D05, D07, D08, E17, X01, X02, X03, X04, X05, X06, X07, X08, X09, X10
سهم مشترک با مالک دیگر: E02, Q01. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: مسئول پذیرش و دفتر فنی یک روز واقعی و کامل را انتخاب می‌کنند و برای هر فیلدِ الزام‌شده در 044 و فرم مرجع، سلول/سند منبع، واحد، تبدیل، null/صفر، محل چاپ یا دلیل عدم چاپ و مسیر جزئیات را ثبت می‌کنند. همه ۱۸ بخش broader-daily-sections.md باید تصمیم دامنه داشته باشند.
- قرارداد نسخه‌دار، شناسه روز مرجع، مسئول تصمیم و مسئول پذیرش، نسخه فرم و mapping قابل بازبینی تعریف شود. Q01 در این مرحله قرارداد و mapping دارد؛ اثبات مستقل نهایی با B05 است.
- C01 و C02 مبنای فعلیِ ثبت‌شده‌اند؛ C03 تا C08 پاسخ یا تصمیم مصوب تازه ندارند. راه‌حل پروفایل کاتالوگ در C04 صرفاً پیشنهاد است. C06 حدود fingerprint را مشخص می‌کند، نه PKI. هر تصمیم باید متن پاسخ، مرجع، تصمیم‌گیر و تاریخ داشته باشد؛ فقدان پاسخ را صریح باز نگه دار.
- C09 و C10 را نیز حفظ کن: وضعیت منابع submitted/approved مستقل از خلاصه است؛ پایان A.1 جای پذیرش ارتباطات، گزارش دوره‌ای، آفلاین یا کل عملیات را نمی‌گیرد.
- تصمیم‌ها را می‌توان در چند دور clarification (حداکثر سه سؤال بحرانی در هر دور) روشن کرد؛ برای رعایت سقف سؤال، هیچ تصمیم مادی باقی‌مانده را حدس نزن یا حذف نکن. تا قرارداد مؤثر باز است آمادگی plan/پیاده‌سازی وابسته را اعلام نکن.
پایان قابل آزمون: ۱۰۰٪ فیلدهای الزامی mapping مستقل دارند و C01..C08 به‌علاوه اثر C09/C10 در قرارداد ثبت‌اند؛ هیچ تصمیم باز مؤثر بر خروجی رسمی به‌عنوان حل‌شده نمایش داده نشده است.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B01: qa_passed. Existing specification, regression and handoff baseline. Adopt its current scope and use existing QA evidence. If specify is invoked for a material residual gap, scope that gap against the existing spec.
- Reports: output/a1-requirements-2026-11-22-stage1-b01-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b01-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Use specs/057-a1-b01-data-contract and published contract v1.0.0 (shiraz-file4-v1) as the baseline. Preserve all 128 mappings and 18 sections, idempotent synthetic SIM-A1-001 (1406-03-01 / 2027-05-22), measured zero, unknowns, and GOV-01. C01–C02 are recorded baselines, C03–C08 are ratified, and C09–C10 are preserved boundaries or behaviors. Carry the recorded decisions forward. Employer representative and date are pending B06.

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.01, A.1.02
معیار بسته در کشف مرحله ۱: روز مرجع کامل و هر ۱۸ بخش broader-daily-sections نگاشت نسخه‌دار و قابل بازبینی داشته باشد؛ تصمیم‌های C01 تا C08 ثبت و هیچ ابهام اثرگذار بر خروجی رسمی باز نماند.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b01-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b01-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B01-01 — الزام و منبع معتبر شماره رسمی گزارش و روز پروژه را با C08 ثبت کن. داده ساختگی پذیرفتنی نیست.
- DEF-B01-02 — واحد منطقی گزارش، شناسه و مدت واقعی شیفت و نگاشت هدر/فعالیت/by-date را با C03 ببند.
- DEF-B01-03 — سرجمع نفرات، نفرشیفت و نفرساعت را با پیش‌شرط‌های حضور یکتا و مدت معتبر تعریف کن. B03/B04 مصرف‌کننده‌اند.
- DEF-B01-04 — پروفایل ۳۴/۳۲ و جایگاه عنوان سفارشی/تاریخی را به C04 و تأیید B01 مشروط کن.
- DEF-B01-05 — وضعیت زمین/باد موجود در WeatherLog و پیش‌بینی را با منبع، ضرورت و نحوه نمایش طبق C08 تعیین کن.
- DEF-B01-06 — C01..C08 را تعیین تکلیف کن، C09/C10 را حفظ کن و برای هر ۱۸ بخش جایگاه چاپ، جزئیات یا فاز مالک را ثبت کن.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B01: qa_passed. Acceptance criterion: Independently map every required field and complete reference day; resolve C01-C08 decisions affecting official output.
- Source reports: output/a1-requirements-2026-11-21-stage1-b01-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b01-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Use specs/057-a1-b01-data-contract as the baseline. QA reports 11 passing tests and a versioned fixture contract covering all 18 sections and C01–C08/GOV-01. Preserve SIM-A1-001 as a synthetic fixture. Record any employer decision or real reference-day evidence still needed for official delivery.

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B01 — بستن قرارداد داده و نمونه آزمون

**مربوط به:** H04/H05/D05/D07/D08/E02/E17/X07/Q01. **پیش‌نیاز:** دسترسی به روز مرجع کامل و مسئول پذیرش.

خروجی: یک سند نسخه‌دار شامل روز نماینده، سلول/سند منبع هر فیلد، معنای null/صفر، شیفت و مدت، نفر/نفرشیفت/نفرساعت، ترتیب عناوین و بخش‌ها و دامنه تک‌روز/چندشیته. موارد خارج از چاپ با دلیل و مسیر drill-down معلوم شوند. قاعده داده نباید با سلیقه توسعه‌دهنده یا مقدار ساختگی پر شود.

**پایان قابل آزمون:** همه فیلدهای الزام‌شده در FR044 و روز مرجع نگاشت مستقل داشته باشند. تصمیم‌های C01 تا C08 در سند قرارداد ثبت شوند؛ مورد باز اثرگذار بر خروجی رسمی باقی نماند. پذیرش اولیه A.1 به معنای پذیرش همه زیرسیستم‌های A.8 نیست.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

H04 — مدل شیفت و ساعت شروع/پایان یا مدت واقعی شیفت‌های ۱ تا ۳
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: سطرهای نیروی انسانی و فعالیت شیفت دارند؛ هدر مدل day/night/full دارد. در Excel متن ثابت «ساعات کاری شیفت: ثبت نشده» چاپ می‌شود.
باقیمانده: تثبیت نگاشت هدر/سطر و ثبت مدت یا بازه واقعی هر شیفت؛ نمایش داده واقعی به جای متن ثابت.
پذیرش: سه شیفت مرجع با مدت مشخص، بدون تبدیل خاموش شیفت نامعتبر، در UI/Excel/PDF تطبیق شوند.
حد شاهد: نقص هدر در نمونه خروجی بازتولید شد؛ generated-structure.json
ارجاع: apps/api/core/field_reports/models.py:9؛ apps/api/core/field_reports/shiraz_file4_excel.py:206؛ specs/044-shiraz-excel-parity-pdf/spec.md:181

H05 — شماره رسمی گزارش، شماره صفحه و شماره روز پروژه در مرجع
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: نیازمند تثبیت قرارداد
موجود: فایل مرجع شماره رسمی گزارش دارد؛ فیلد مستقل معادل report_number/project_day_number در DailyReport مشاهده نشد.
باقیمانده: مشخص شود شماره رسمی و روز پروژه در تحویل A.1 الزام هستند یا خیر؛ در صورت الزام مدل و قاعده شماره‌گذاری پیاده شود.
پذیرش: شماره بر اساس قاعده مصوب و مستقل از ID داخلی؛ شماره صفحه در چاپ معتبر باشد.
حد شاهد: بازبینی مدل و سلول‌های واقعی مرجع؛ نمونه AG3=882 و X3=500
ارجاع: apps/api/core/field_reports/models.py:113؛ docs/delivery/R0-scope-and-reports-contract.md:30

D05 — تفکیک صفر واقعی، ثبت‌نشده و اندازه‌گیری‌نشده در حجم فعالیت
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: quantity_measured و قواعد quantity_unset_invalid و نمایش ثبت‌نشده وجود دارند؛ صفر صریح معتبر است.
باقیمانده: رفع تعارض متن قدیمی «صفر ممنوع» با 034/036؛ تطبیق FILE1 و همه viewها با داده legacy ناسازگار.
پذیرش: ۰ و ۰٫۰۰ صفر بمانند؛ null یا not-measured عدد ساختگی نشود؛ حجم نامعلوم از جمع واحدها پنهانی صفر نشود.
حد شاهد: آزمون‌های منتخب unset موفق؛ پوشش همه مسیرهای FILE1/مرورگر ادعا نمی‌شود
ارجاع: apps/api/core/field_reports/daily_report_views.py:332؛ apps/api/core/field_reports/shiraz_file4_excel.py:625؛ specs/036-validation-codes-unset-semantics/spec.md:84

D07 — قاعده نفرساعت و تمایز نفر، نفرشیفت، نفرروز و جمع ردیف‌ها
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: فیلد ساعت و قاعده template و ledger در مسیرهای تخصصی وجود دارد؛ Excel نیروی انسانی نفرشیفت را برچسب می‌زند.
باقیمانده: تثبیت معنای شمارش برای هر خروجی؛ عنوان نفرروز در نوار activity log بدون اثبات حضور یکتا اصلاح شود.
پذیرش: هیچ جمع headcount روی فعالیت‌ها به‌عنوان تعداد افراد یکتا معرفی نشود؛ نفرساعت از مدت واقعی شیفت بیاید.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/models.py:340؛ apps/web/src/app/routes/project-activity-log.tsx:129؛ specs/033-daily-sections-grid/spec.md:196

D08 — کاتالوگ شغل نسخه‌دار، ترتیب پروژه و نگاشت فرم ۳۴/۳۲
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: زیرساخت catalog/template موجود است؛ خروجی FILE4 ابتدا لیست ثابت ۳۴/۳۲ و سپس عنوان‌های اضافه را می‌چیند.
باقیمانده: جداسازی پروفایل فرم شیراز از حقیقت عمومی پروژه؛ رعایت ترتیب و نگاشت عنوان‌های تاریخی/اختصاصی.
پذیرش: تغییر template عنوان یا داده تاریخی را حذف نکند؛ فرم شیراز فقط در پروفایل مصوب ۳۴/۳۲ باشد.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:247؛ specs/033-daily-sections-grid/spec.md:198؛ specs/044-shiraz-excel-parity-pdf/spec.md:182

E17 — دامنه فایل چندشیته تاریخی در مقابل خروجی یک روز
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: نیازمند تثبیت قرارداد
موجود: هر فراخوانی FILE4 یک شیت روزانه می‌سازد؛ مرجع ۱۰۹/۳۶۷ شیت و R0 واژه چندشیته دارد.
باقیمانده: ثبت تصمیم: تک‌روز در A.1 طبق برنامه یا workbook بازه/کل تاریخ؛ بدون فرض خودکار مهاجرت همه شیت‌ها.
پذیرش: دامنه فایل و تعداد شیت در قرارداد خروجی روشن و همان حالت آزموده شود.
حد شاهد: نمونه کنترل یک شیت؛ metadata مرجع واقعی خوانده شد
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:132؛ docs/delivery/R0-scope-and-reports-contract.md:46؛ output/delivery-plan-2026-11-03/delivery-plan.md:107

X01 — آفلاین، صف محلی، retry، حل تعارض و جداسازی هویت
فاز مالک/اثر منبع: A.8؛ سازگاری با A.1 الزامی
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: زیرساخت sync و spec037 و آزمون‌های مستقل وجود دارند؛ به صرف این وجود کامل نامیده نمی‌شود.
باقیمانده: پذیرش اختصاصی operation_id، قطع پیش/پس از commit، refresh/restart، رقابت تأیید، عدم حذف موفق‌ها و تغییر حساب.
پذیرش: هیچ داده/عملیات گم یا تکراری نشود؛ مشتقات پروژه در sync هم readonly؛ اثبات‌های مستقل spec037 ارائه شود.
حد شاهد: تست آفلاین و browser این نوبت اجرا نشده؛ وضعیت «پیاده نشده» به آن نسبت داده نمی‌شود
ارجاع: specs/037-daily-offline-sync/spec.md:104

X02 — درصد اجرا، نفرساعت پیمانکار و QC تخصصی مکانیک/برق
فاز مالک/اثر منبع: A.8؛ خروجی مرتبط A.1
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: مدل‌ها و مسیرهای تخصصی/درصد/بازرسی وجود دارند.
باقیمانده: پذیرش درصد ۰..۱۰۰/null، گزارش خالی، تست فشار و ledger پس از تأیید و داده واقعی واحد.
پذیرش: درصد نامعلوم صفر نشود؛ فشار غیرمثبت رد؛ نفرساعت از مدت واقعی و افراد منبع محاسبه شود.
حد شاهد: درصد/Excel منتخب موفق؛ بقیه گردش تخصصی به طور کامل این نوبت آزموده نشده
ارجاع: specs/038-discipline-sub-reports/spec.md:156

X03 — پیشرفت برنامه‌ای/واقعی و روش‌های وزن‌دهی فیزیکی
فاز مالک/اثر منبع: A.7/A.8
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: ماژول زمان‌بندی/پیشرفت جدا از daily quantities وجود دارد.
باقیمانده: تطبیق WBS و قواعد وزن‌دهی در فاز مربوط؛ مرز نمایش روزانه تعیین شود.
پذیرش: حجم فعالیت روزانه جانشین پیشرفت تجمعی رسمی تلقی نشود.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md:1

X04 — گزارش هفتگی/ماهانه، KPI و کاتالوگ عمومی گزارش‌ها
فاز مالک/اثر منبع: A.10
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: ProjectPeriodReport و کاتالوگ پنج‌گانه جدا هستند؛ مسیر عمومی monthly هنوز از سازنده weekly استفاده می‌کند.
باقیمانده: در A.10 تفکیک معنا، تاریخ/WBS و منابع approved؛ ادعای همه گزارش‌های دوره‌ای ناقص بر اساس یک مسیر عمومی درست نیست.
پذیرش: بازه، شاخص و منبع هر گزارش واقعی آزموده شود؛ A.1 جای پذیرش A.10 را نگیرد.
حد شاهد: کد مسیر عمومی بازبینی شد؛ مسیر تخصصی period_report جداست
ارجاع: docs/delivery/R0-scope-and-reports-contract.md:51؛ apps/api/core/projects/services/report_export_service.py:80

X05 — ذی‌نفعان، جلسات، مکاتبات و گزارش وضعیت ارتباطات
فاز مالک/اثر منبع: A.3.C و گزارش A.10
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: پایه ذی‌نفع/ماتریس/برنامه ارتباطی موجود است؛ اتصال جامع در دامنه پذیرفته‌شده پروژه باقی است.
باقیمانده: تکمیل اتصال صریح stakeholder/meeting/correspondence، مسئول/موعد، workflow و کنترل داده تماس در فاز مربوط.
پذیرش: کارفرما مسیر ثبت تا اقدام باز و گزارش وضعیت فیلترشده را جدا از گزارش روزانه بپذیرد.
حد شاهد: درخواست قبلی کاربر جزو کل تحویل است؛ این ممیزی آن را از کل پروژه حذف نمی‌کند
ارجاع: docs/delivery/R0-scope-and-reports-contract.md:19

X06 — تدارکات روز، RFI/Submittal و پیوند اسناد رسمی
فاز مالک/اثر منبع: A.4/A.9/A.10؛ نمایش روزانه نیازمند قرارداد
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: یادداشت/ارجاع روزانه جایگزین گردش رسمی مکاتبات و تدارکات نیست.
باقیمانده: تعیین اقلام لازم در snapshot چاپی A.1 و اتصال ماژول‌های صاحب داده در فاز مربوط.
پذیرش: شماره/وضعیت سند از منبع رسمی بیاید؛ یک متن آزاد به‌عنوان گزارش کامل تدارکات معرفی نشود.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: docs/delivery/R0-scope-and-reports-contract.md:12؛ docs/delivery/R0-scope-and-reports-contract.md:55

X07 — باد، وضعیت زمین و پیش‌بینی سه روز آینده در فرم واقعی
فاز مالک/اثر منبع: مرتبط؛ دامنه چاپ A.1 باید مشخص شود
وضعیت تاریخی: نیازمند تثبیت قرارداد
موجود: WeatherLog دارای داده باد/زمین است؛ این داده‌ها در هدر فعلی daily/export دیده نشدند؛ فرم واقعی پیش‌بینی سه‌روزه دارد.
باقیمانده: تصمیم صریح درباره ضرورت این فیلدها و منبع قابل اتکا؛ از ساخت سرویس پیش‌بینی بدون نیاز مصوب پرهیز شود.
پذیرش: اگر داخل دامنه شد مقدار/منبع/تاریخ روشن؛ در نبود داده «نامعلوم» و بدون داده ساختگی.
حد شاهد: تفکیک وجود مدل از نبود اتصال به گزارش؛ پیش‌بینی یک مشاهده مرجع است نه تعهد قطعی تازه
ارجاع: apps/api/core/field_reports/models.py:788؛ docs/delivery/R0-scope-and-reports-contract.md:30

X08 — مهاجرت سابقه، نگاشت taxonomy و rollback داده‌های قدیمی
فاز مالک/اثر منبع: A.8/A.12
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: مدل migration trace و الزامات نگهداری شناسه/منبع/تاریخچه در spec032 وجود دارند.
باقیمانده: تمرین مهاجرت با داده واقعی، قرنطینه مقدار نامعلوم، یک نسخه جاری و rollback قابل اثبات.
پذیرش: تمام رکوردها migrated/history/quarantined شمرده شوند؛ سابقه بدون اثر در جمع رسمی قابل ردیابی بماند.
حد شاهد: تمرین مهاجرت و rollback این نوبت اجرا نشده؛ ۳۶۷ شیت به خودی خود تعهد ETL نیست
ارجاع: specs/032-unit-report-source-truth/spec.md:195

X09 — استقرار نهایی کل محصول و آموزش گسترده
فاز مالک/اثر منبع: A.12؛ بسته همان SHA برای A.1 لازم
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: زیرساخت release/راهنما وجود دارد.
باقیمانده: استقرار و آموزش کل محصول در A.12؛ A.1 برای فایل‌های خود نسخه منتشرشده آزموده‌شده و راهنمای محدود می‌خواهد.
پذیرش: آزمون محلی به‌عنوان تأیید production معرفی نشود.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: docs/delivery/R0-scope-and-reports-contract.md:20

X10 — گزارش‌های مستقل دپارتمان و انبار، ورود دسته‌ای و بالانس
فاز مالک/اثر منبع: A.8/A.10؛ سازگاری منبع A.1
وضعیت تاریخی: مرتبط؛ خارج از تحویل مستقیم A.1
موجود: اسناد SPEC09/10 و مسیرهای داده دپارتمان/آزمون گزارش وجود دارند؛ این مسیرها با خلاصه مشتق پروژه یکی نیستند.
باقیمانده: پذیرش مستقل import/export روزانه/هفتگی و بالانس ۸ فیلدی؛ تعیین مسیر قدیمی سازگار با مالکیت شش واحد و جلوگیری از منبع موازی.
پذیرش: رسید/مصرف/مانده و فیلترهای روز/واحد/پیمانکار با مرجع برابر؛ import تکراری یا ردیف نامعتبر داده رسمی را خراب نکند.
حد شاهد: صرفاً ثبت دامنه و مسیرهای موجود؛ آزمون جامع دپارتمان/انبار و بالانس در این نوبت اجرا نشده
ارجاع: apps/api/core/inventory/department_activity_data_views.py:1؛ apps/api/core/sub_reports/tests/test_department_reports.py:1؛ reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md:1؛ reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md:1

رجیستر کامل تصمیم‌های مرحلهٔ ۱ — نقل قول منبع، بدون تصمیم تازه:
## C01 — ورود خام روزانه یا خلاصه مشتق

نیازمندی پایه قدیمی از «تکمیل فرم روزانه» می‌گوید؛ 028/032/037/039 ورود عملیاتی را فقط از صفحات واحد می‌خواهند. **مبنای رفتار فعلی:** خلاصه مشتق و فقط metadata مجاز در سطح پروژه. اصلاحیه نباید این مرز را باز کند. اسناد قدیمی باید با این انتخاب همسو شوند؛ نیازی به ساخت دوباره فرم خام نیست.

## C02 — صفر مجاز یا مقدار صرفاً مثبت

033 FR002/SC004 صفر حجم را نامعتبر می‌نامند؛ 034 FR012 و 036 FR007 صراحتاً صفر و 0.00 را معتبر و از unset متمایز می‌کنند. **مبنای فعلی:** صفر اندازه‌گیری‌شده معتبر؛ null/not-measured نامعلوم. متن و آزمون متناقض قدیمی اصلاح شود؛ صفر همه فیلدها از جمله بتن/فشار به صورت blanket مجاز فرض نمی‌شود.

## C03 — شیفت هدر، شیفت فعالیت و مدت کار

044 سه شیفت با ساعت کار می‌خواهد؛ مدل هدر day/night/full و سطر فعالیت shift_1/2/3 است؛ by-date نیز نگاشت یکسان و صریح سه شیفت ندارد. **تصمیم لازم:** واحد منطقی گزارش، نگاشت نام/کد و منبع مدت یا بازه ساعت واقعی. عدد پیش‌فرض ساختگی مبنای نفرساعت قرار نگیرد.

## C04 — کاتالوگ قابل تنظیم یا شمار ثابت ۳۴/۳۲

033 شمار ثابت را حقیقت عمومی نمی‌پذیرد؛ 044 همان فرم استاندارد را می‌خواهد. **راه‌حل پیشنهادی، هنوز تصمیم جدید مصوب نیست:** کاتالوگ نسخه‌دار و قابل تنظیم پروژه + پروفایل نگاشت فرم شیراز ۳۴/۳۲. انتخاب پروفایل و رفتار عنوان اضافه/تاریخی ثبت شود.

## C05 — یک شیت روزانه یا workbook چندشیته

R0 عبارت «اکسل چندشیته FILE4» دارد، ولی برنامه A.1 یک روز نماینده می‌خواهد و endpoint فعلی یک روز/شیت تولید می‌کند؛ مرجع مجموعه‌ای از روزهاست. **تصمیم لازم:** معیار پذیرش A.1 یک روز است یا export یک بازه/کل تاریخ نیز الزام دارد؟ وجود workbook تاریخی به‌تنهایی تعهد ساخت ETL یا صدور همه ۳۶۷ شیت نیست.

## C06 — «امضای دیجیتال» چه معنایی دارد؟

متن R0 و SC044 تعبیر امضای دیجیتال دارند؛ FR015 دقیقاً fingerprint متادیتا را تعریف کرده و کد همین دامنه محدود را اجرا می‌کند. تغییر quantity هش را تغییر نداد. **بیان مجاز فعلی:** بلوک کنشگرها و fingerprint متادیتا؛ ادعای امضای گواهی‌دار PKI یا تضمین عدم تغییر کل بدنه پشتیبانی نمی‌شود. اگر آن انتظار وجود دارد، باید دامنه الگوریتم/کلید/صحت‌سنجی جدا مشخص شود؛ این ممیزی خودسرانه آن را الزام تازه نکرده است.

## C07 — PDF زیرگزارش تخصصی

SPEC11 اتمیک از PDF زیرگزارش نام می‌برد؛ قرارداد 044 برای FILE5/6 اکسل را الزام کرده و endpoint PDF مستقل واحد مشاهده نشد. **تصمیم لازم:** PDF مستقل هر واحد بخشی از همین تحویل است یا Excel تخصصی کافی است؟ تا پاسخ، قابلیت PDF مستقلِ موجود یا تعهد قطعی A.1 اعلام نمی‌شود.

## C08 — فیلدهای فرم واقعی در برابر فهرست صریح قرارداد

شماره رسمی گزارش/روز پروژه، باد/وضعیت زمین و پیش‌بینی سه روزه در طرح کلی یا فرم واقعی دیده می‌شوند؛ همه در هدر/خروجی روزانه فعلی متصل نیستند. WeatherLog باد و زمین را دارد، پس نبود مدل ادعا نمی‌شود. **تصمیم لازم:** کدام‌یک در نمونه پذیرش A.1 الزامی است و منبعش چیست؟ هیچ شماره، ساعت یا پیش‌بینی جوی نباید ساخته شود.

## C09 — تأیید خلاصه و تأیید همه منابع

032/039 منابع جاری submitted یا approved را واجد شرایط می‌دانند؛ approved شدن خلاصه الزاماً گواه approved بودن تک‌تک واحدها نیست. **بیان فعلی:** وضعیت هر منبع و وضعیت خلاصه مستقل‌اند. اگر تحویل رسمی فقط از همه منابع approved مجاز است، تغییر سیاست/گیت باید صریح تصویب و آزموده شود؛ صرف برچسب «تأییدشده» اجازه چنین استنباطی نمی‌دهد.

## C10 — ارتباطات و گزارش‌های عمومی حذف نشده‌اند

درخواست قبلی کاربر برای ارتباط ذی‌نفع با جلسه/مکاتبه و گردش‌کار یکپارچه در دامنه کل تحویل حفظ شده است. طبق R0 مالک آن A.3.C و گزارش نهایی A.10 است. نقص‌های کاتالوگ عمومی، فیلتر تاریخ/WBS و monthly که weekly را فراخوانی می‌کند در همان مسیر عمومی باقی‌اند؛ مسیر تخصصی ProjectPeriodReport باید جدا سنجیده شود. این یافته‌ها نه نشان تکمیل A.10 است و نه دلیل بازنویسی تمام A.1.

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- D05 | specs/007-daily-report-gaps/spec.md:129 | FR-010
- D05 | specs/007-daily-report-gaps/spec.md:152 | SC-004
- X08 | specs/032-unit-report-source-truth/spec.md:157 | FR-004
- X08 | specs/032-unit-report-source-truth/spec.md:195 | FR-033
- X08 | specs/032-unit-report-source-truth/spec.md:196 | FR-034
- X08 | specs/032-unit-report-source-truth/spec.md:197 | FR-035
- X08 | specs/032-unit-report-source-truth/spec.md:198 | FR-036
- X08 | specs/032-unit-report-source-truth/spec.md:199 | FR-037
- X08 | specs/032-unit-report-source-truth/spec.md:200 | FR-038
- X08 | specs/032-unit-report-source-truth/spec.md:225 | SC-008
- X08 | specs/032-unit-report-source-truth/spec.md:226 | SC-009
- D05 | specs/033-daily-sections-grid/spec.md:187 | FR-002
- H04 | specs/033-daily-sections-grid/spec.md:190 | FR-005
- D07 | specs/033-daily-sections-grid/spec.md:196 | FR-008
- D08 | specs/033-daily-sections-grid/spec.md:198 | FR-010
- D08 | specs/033-daily-sections-grid/spec.md:199 | FR-011
- D05 | specs/033-daily-sections-grid/spec.md:272 | SC-004
- D05 | specs/034-daily-lifecycle-lock/spec.md:97 | FR-011
- D05 | specs/034-daily-lifecycle-lock/spec.md:98 | FR-012
- D05 | specs/034-daily-lifecycle-lock/spec.md:99 | FR-013
- D05 | specs/034-daily-lifecycle-lock/spec.md:118 | SC-004
- D05 | specs/036-validation-codes-unset-semantics/spec.md:84 | FR-006
- D05 | specs/036-validation-codes-unset-semantics/spec.md:85 | FR-007
- D05 | specs/036-validation-codes-unset-semantics/spec.md:86 | FR-008
- D05 | specs/036-validation-codes-unset-semantics/spec.md:87 | FR-009
- D05 | specs/036-validation-codes-unset-semantics/spec.md:88 | FR-010
- D05 | specs/036-validation-codes-unset-semantics/spec.md:89 | FR-011
- D05 | specs/036-validation-codes-unset-semantics/spec.md:90 | FR-012
- D05 | specs/036-validation-codes-unset-semantics/spec.md:109 | SC-002
- D05 | specs/036-validation-codes-unset-semantics/spec.md:110 | SC-003
- X01 | specs/037-daily-offline-sync/spec.md:104 | FR-001
- X01 | specs/037-daily-offline-sync/spec.md:105 | FR-002
- X01 | specs/037-daily-offline-sync/spec.md:106 | FR-003
- X01 | specs/037-daily-offline-sync/spec.md:107 | FR-004
- X01 | specs/037-daily-offline-sync/spec.md:108 | FR-005
- X01 | specs/037-daily-offline-sync/spec.md:109 | FR-006
- X01 | specs/037-daily-offline-sync/spec.md:110 | FR-007
- X01 | specs/037-daily-offline-sync/spec.md:111 | FR-008
- X01 | specs/037-daily-offline-sync/spec.md:112 | FR-009
- X01 | specs/037-daily-offline-sync/spec.md:113 | FR-010
- X01 | specs/037-daily-offline-sync/spec.md:114 | FR-011
- X01 | specs/037-daily-offline-sync/spec.md:115 | FR-012
- X01 | specs/037-daily-offline-sync/spec.md:116 | FR-013
- X01 | specs/037-daily-offline-sync/spec.md:120 | FR-017
- X01 | specs/037-daily-offline-sync/spec.md:121 | FR-018
- X01 | specs/037-daily-offline-sync/spec.md:122 | FR-019
- X01 | specs/037-daily-offline-sync/spec.md:123 | FR-020
- X01 | specs/037-daily-offline-sync/spec.md:124 | FR-021
- X01 | specs/037-daily-offline-sync/spec.md:125 | FR-022
- X01 | specs/037-daily-offline-sync/spec.md:126 | FR-023
- X01 | specs/037-daily-offline-sync/spec.md:127 | FR-024
- X01 | specs/037-daily-offline-sync/spec.md:128 | FR-025
- X01 | specs/037-daily-offline-sync/spec.md:129 | FR-026
- X01 | specs/037-daily-offline-sync/spec.md:130 | FR-027
- X01 | specs/037-daily-offline-sync/spec.md:131 | FR-028
- X01 | specs/037-daily-offline-sync/spec.md:155 | SC-01
- X01 | specs/037-daily-offline-sync/spec.md:156 | SC-02
- X01 | specs/037-daily-offline-sync/spec.md:157 | SC-03
- X01 | specs/037-daily-offline-sync/spec.md:158 | SC-04
- X01 | specs/037-daily-offline-sync/spec.md:159 | SC-05
- X01 | specs/037-daily-offline-sync/spec.md:160 | SC-06
- X01 | specs/037-daily-offline-sync/spec.md:161 | SC-07
- X02 | specs/038-discipline-sub-reports/spec.md:156 | FR-001
- X02 | specs/038-discipline-sub-reports/spec.md:157 | FR-002
- X02 | specs/038-discipline-sub-reports/spec.md:158 | FR-003
- X02 | specs/038-discipline-sub-reports/spec.md:159 | FR-004
- X02 | specs/038-discipline-sub-reports/spec.md:160 | FR-005
- X02 | specs/038-discipline-sub-reports/spec.md:161 | FR-006
- X02 | specs/038-discipline-sub-reports/spec.md:162 | FR-007
- X02 | specs/038-discipline-sub-reports/spec.md:163 | FR-008
- X02 | specs/038-discipline-sub-reports/spec.md:164 | FR-009
- X02 | specs/038-discipline-sub-reports/spec.md:165 | FR-010
- X02 | specs/038-discipline-sub-reports/spec.md:171 | FR-011
- X02 | specs/038-discipline-sub-reports/spec.md:176 | FR-012
- X02 | specs/038-discipline-sub-reports/spec.md:177 | FR-013
- X02 | specs/038-discipline-sub-reports/spec.md:178 | FR-014
- X02 | specs/038-discipline-sub-reports/spec.md:179 | FR-015
- X02 | specs/038-discipline-sub-reports/spec.md:181 | FR-017
- X02 | specs/038-discipline-sub-reports/spec.md:218 | SC-001
- X02 | specs/038-discipline-sub-reports/spec.md:219 | SC-002
- X02 | specs/038-discipline-sub-reports/spec.md:220 | SC-003
- X02 | specs/038-discipline-sub-reports/spec.md:221 | SC-004
- X02 | specs/038-discipline-sub-reports/spec.md:222 | SC-005
- X02 | specs/038-discipline-sub-reports/spec.md:223 | SC-006
- H04 | specs/039-auto-daily-rollup/spec.md:181 | FR-003
- H04 | specs/044-shiraz-excel-parity-pdf/spec.md:181 | FR-003
- D08 | specs/044-shiraz-excel-parity-pdf/spec.md:182 | FR-004
- D08 | specs/044-shiraz-excel-parity-pdf/spec.md:183 | FR-005
- D05 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:63 | FR-DR-010

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):
- US-DR-02 | reports_documentation/atomic-specs/SPEC-01-DAILY-HEADER-WEATHER.md:42 | سهم این مرحله: H04؛ کل گروه‌ها: H03, H04
- US-DR-04 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:15 | سهم این مرحله: D05؛ کل گروه‌ها: D04, D05
- US-DR-05 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:42 | سهم این مرحله: D07, D08؛ کل گروه‌ها: D06, D07, D08
- US-DR-14 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:101 | سهم این مرحله: D05؛ کل گروه‌ها: D05
- US-DR-15 | reports_documentation/atomic-specs/SPEC-04-DAILY-OFFLINE-SYNC.md:15 | سهم این مرحله: X01؛ کل گروه‌ها: X01
- US-DR-16 | reports_documentation/atomic-specs/SPEC-04-DAILY-OFFLINE-SYNC.md:38 | سهم این مرحله: X01؛ کل گروه‌ها: X01
- US-SR-01 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:30 | سهم این مرحله: X02؛ کل گروه‌ها: X02, E10, D01
- US-SR-02 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:53 | سهم این مرحله: X02؛ کل گروه‌ها: X02, E10, D01
- US-SR-03 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:70 | سهم این مرحله: X02؛ کل گروه‌ها: X02, E10, D01
- US-SR-04 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:87 | سهم این مرحله: X02؛ کل گروه‌ها: X02, E10, D01
- US-PR-01 | reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md:23 | سهم این مرحله: X03؛ کل گروه‌ها: X03
- US-PR-02 | reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md:46 | سهم این مرحله: X03؛ کل گروه‌ها: X03
- US-PR-03 | reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md:70 | سهم این مرحله: X03؛ کل گروه‌ها: X03
- US-PR-04 | reports_documentation/atomic-specs/SPEC-08-PERIODIC-REPORTS-ROLLUP.md:25 | سهم این مرحله: X04؛ کل گروه‌ها: X04
- US-PR-05 | reports_documentation/atomic-specs/SPEC-08-PERIODIC-REPORTS-ROLLUP.md:49 | سهم این مرحله: X04؛ کل گروه‌ها: X04
- US-PR-06 | reports_documentation/atomic-specs/SPEC-08-PERIODIC-REPORTS-ROLLUP.md:70 | سهم این مرحله: X04؛ کل گروه‌ها: X04
- US-PR-07 | reports_documentation/atomic-specs/SPEC-08-PERIODIC-REPORTS-ROLLUP.md:87 | سهم این مرحله: X04؛ کل گروه‌ها: X04
- US-DP-01 | reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md:21 | سهم این مرحله: X10؛ کل گروه‌ها: X10
- US-DP-02 | reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md:40 | سهم این مرحله: X10؛ کل گروه‌ها: X10
- US-DP-03 | reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md:57 | سهم این مرحله: X10؛ کل گروه‌ها: X10
- US-WH-01 | reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md:28 | سهم این مرحله: X10؛ کل گروه‌ها: X10, D12
- US-WH-02 | reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md:51 | سهم این مرحله: X10؛ کل گروه‌ها: X10, D12

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```

# A.1 / B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده

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

زیرمرحله جاری: B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01.
مرحله قبلی در ترتیب: B01.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: H06, D01, D02, D03, W01, W02, W03, W04, W05, W06, E15
سهم مشترک با مالک دیگر: X01. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: خلاصه approved حاصل از حداقل دو واحد و چند منبع → ایجاد اصلاحیه با دلیل → رد POST/PATCH/DELETE مستقیم مشتقات → اصلاح واحد منبع و بازسازی مجاز → تأیید نسخه جدید → کنترل جمع و lineage → در شاخه مستقل لغو اصلاحیه و بازگشت دقیق.
- هویت تجمیعی و readonly بودن بر مبنای مالکیت داده در تمام مسیرهای UI، child، batch، offline و legacy حفظ شود؛ metadata مجاز مدیریت با ردیف مشتق خلط نشود.
- مجموعه کامل DailyReportDerivedSource و همه فرزندان به شناسه ردیف‌های مقصد بازنگاشت شوند؛ کپی تک FK کافی نیست. نظر مدیریت، weather/site override مجاز و اطلاعات template/config/aggregation/fingerprint/snapshot مطابق قرارداد نسخه حفظ یا صریح بازتولید شوند.
- فقط نسخه approved جاری در دفتر رسمی جمع شود. مثال ممیزی: دو نسخه پنج‌واحدی باید جمع رسمی ۵ و headcount=۴ بدهند، نه ۱۰ و۸؛ تاریخچه از مسیر مستقل باقی بماند. B04 این سیاست را در فیلترها و جمع کل مصرف می‌کند.
- رقابت دو درخواست اصلاح، یکتایی روز/شیفت مطابق C03، template مؤثر در تاریخ و شش واحد معتبر، منابع روز/پروژه دیگر، draft/rejected/deleted/قدیمی، viewer، نقش غیرمجاز و تفکیک وظایف سناریو داشته باشند. تغییر منبع snapshot approved را پنهانی تغییر ندهد.
پایان قابل آزمون: سناریوهای نقص اصلاحیه/منابع/نظر/override و نسخه تاریخی با assertion صحیح و بدون XFAIL سبز شوند؛ منبع ۲تایی پس از clone همچنان ۲ منبع قابل ردیابی داشته باشد. گیت فنی از پذیرش کارفرما جدا ثبت شود.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B02: qa_passed. Existing specification, regression and handoff baseline. Adopt its current scope and use existing QA evidence. If specify is invoked for a material residual gap, scope that gap against the existing spec.
- Reports: output/a1-requirements-2026-11-22-stage1-b02-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b02-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Use specs/058-a1-b02-version-integrity as the baseline. Carry forward the reported 51 passing cases, including correction and cancellation, concurrent correction, summary ownership, protected derived edits, full provenance remapping, reviewer and weather preservation, and approved-current aggregation. Verify evidence against the target build before reuse.
- DEF-B02-01 — reported resolved in current QA; preserve as regression coverage.
- DEF-B02-02 — reported resolved in current QA; preserve as regression coverage.
- DEF-B02-03 — reported resolved in current QA; preserve as regression coverage.
- DEF-B02-04 — reported resolved in current QA; preserve as regression coverage.
- DEF-B02-05 — reported resolved in current QA; preserve as regression coverage.
- DEF-B02-06 — reported resolved in current QA; preserve as regression coverage.

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.03
معیار بسته در کشف مرحله ۱: فقط نسخه approved جاری در جمع رسمی وارد شود؛ اصلاحیه، منابع، نظر، override و نسخه تاریخی بدون تکرار یا حذف حفظ شوند؛ هیچ ردیف مشتق با API یا UI قابل تألیف مستقیم نباشد.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b02-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b02-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B02-01 — هویت گزارش تجمیعی در نسخه اصلاحی و پس از لغو مطابق قرارداد حفظ شود.
- DEF-B02-02 — رد تغییر مستقیم مشتقات و حفظ داده در تمام مسیرهای تغییر child، batch و legacy به‌عنوان کنترل دفاعی تعریف شود.
- DEF-B02-03 — همه منابع مشتق هر ردیف به همتای همان ردیف در نسخه مقصد منتسب باشند و سابقه قابل ممیزی بماند.
- DEF-B02-04 — نظر مدیریت و override مجاز طبق قواعد حفظ یا بازتولید نسخه ثبت و در چرخه تأیید/لغو قابل مشاهده باشند.
- DEF-B02-05 — جمع رسمی فقط نسخه مصوب جاری را لحاظ کند. B04 همین قاعده را در نتیجه فیلتر و FILE1 مصرف کند.
- DEF-B02-06 — بازسازی خودکار نسخه قدیمی یا بایگانی‌شده رد شود و snapshot و منابع آن نسخه ثابت بمانند. این یافته محلی در Markdown ثبت شده و در JSON و تحویل‌نامه ارائه‌شده نیامده است.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B02: qa_passed. Acceptance criterion: Correction, cancellation, concurrency, unauthorized mutation, lineage, source preservation, and approved-current aggregation pass end-user scenarios.
- Source reports: output/a1-requirements-2026-11-21-stage1-b02-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b02-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Use specs/058-a1-b02-version-integrity as the baseline. Treat DEF-B02-01 through DEF-B02-06 as regression scenarios. Preserve derived-row restrictions, complete lineage, eligible rebuilds, cancel/restore, concurrent correction and approved-current totals.

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده

**مربوط به:** D01/W02/W03/W04/W05/E15. **پیش‌نیاز:** B01 برای قواعد نسخه و منبع؛ بازتولیدهای فعلی آماده‌اند.

1. نسخه اصلاحی هویت تجمیعی خود را حفظ کند. تمام APIهای child و batch/legacy، مستقل از فرض UI، مالکیت ردیف مشتق را اعمال کنند.
2. تمام فرزندان و مجموعه کامل DailyReportDerivedSource با شناسه‌های ردیف نسخه مقصد بازنگاشت شوند؛ فقط کپی فیلد تک‌منبع کافی نیست.
3. نظر مدیریت و overrideهای مجاز و اطلاعات لازم template/aggregation در اصلاح و لغو به درستی حفظ یا طبق قاعده صریح بازتولید شوند؛ هش/snapshot باید به نسخه مربوط بمانند.
4. دفتر عملیاتی فقط نسخه approved جاری را جمع کند؛ تاریخچه در مسیر مستقل قابل مشاهده بماند.

**آزمون تحویل:** approved summary از دو واحد و چند منبع → اصلاحیه → تلاش مستقیم POST/PATCH/DELETE مشتقات (رد) → اصلاح در واحد منبع و بازسازی مجاز → تأیید → کنترل منبع/نظر/override/جمع → لغو سناریوی دوم و بازگشت دقیق. دو درخواست اصلاح همزمان، نقش مشاهده‌گر و پروژه دیگر پوشش داده شوند. آزمون‌های مشاهده نقص بدون XFAIL سبز شوند؛ XFAIL یا xpass را رفع نقص جا نزنیم.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

H06 — یکتایی گزارش جاری، تاریخ منطقی و پوسته گزارش بدون ثبت خام
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: by-date و نسخه جاری، تجمیع روزانه و منع POST گزارش خام وجود دارند.
باقیمانده: تعیین سازگاری مفهوم یک روز با شیفت هدر؛ کنترل رقابت و دسترسی مشاهده‌گر در پذیرش.
پذیرش: تکرار بازکردن تاریخ گزارش موازی نسازد و مشاهده‌گر نیازی به مجوز ویرایش نداشته باشد.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/daily_report_views.py:191؛ apps/api/core/field_reports/daily_report_views.py:197؛ specs/039-auto-daily-rollup/spec.md:179

D01 — گزارش پروژه فقط تجمیعی؛ ورود داده از صفحات واحدها
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: تجمیع و ممنوعیت ایجاد خام وجود دارد؛ قفل ردیف مشتق به is_auto_summary وابسته است.
باقیمانده: رفع گریز اصلاحیه که این پرچم را از دست می‌دهد؛ پوشش تمام مسیرهای مستقیم/قدیمی/batch.
پذیرش: اصلاحیه هم گزارش تجمیعی بماند؛ هیچ ردیف مشتق با API یا UI قابل تألیف مستقیم نباشد.
حد شاهد: نقص اجرایی: اصلاحیه auto_summary=False و PATCH ردیف مشتق 200؛ correction-write-probe.json
ارجاع: apps/api/core/field_reports/daily_report_views.py:618؛ apps/api/core/field_reports/services/correction_service.py:138؛ specs/032-unit-report-source-truth/spec.md:179

D02 — شش واحد معتبر و پیکربندی مؤثر پروژه در تاریخ گزارش
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: buildings/electrical/mechanical/machinery/warehouse/security و قواعد template در تجمیع وجود دارد.
باقیمانده: اعتبارسنجی روی پروژه واقعی و دو نسخه template با تاریخ اثر متفاوت.
پذیرش: واحد الزامی از template همان تاریخ تعیین شود؛ پیش‌فرض ثابت سه‌رشته‌ای معیار نباشد.
حد شاهد: آزمون‌های منتخب completeness موفق؛ همه صفحات شش واحد در این نوبت مرور نشده
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:119؛ specs/032-unit-report-source-truth/spec.md:144

D03 — انتخاب منابع واجد شرایط: جاری، همان پروژه/روز، submitted یا approved
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: فیلتر منابع هم‌پروژه/هم‌روز/جاری و وضعیت SUBMITTED یا APPROVED در موتور هست.
باقیمانده: شفاف‌کردن اینکه approved بودن خلاصه به معنای approved بودن تک‌تک منابع نیست؛ سناریوی واقعی.
پذیرش: draft/rejected/deleted/قدیمی و روز یا پروژه دیگر هیچ contribution و اعتبار تکمیل ندهند.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:41؛ apps/api/core/field_reports/services/daily_report_aggregation.py:53؛ specs/032-unit-report-source-truth/spec.md:176

W01 — گردش draft، submit/review، approve/reject و قفل رسمی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: مراحل، کنشگرها، زمان‌ها، کدهای خطای وضعیت/رد و قفل approved وجود دارند.
باقیمانده: UAT با تهیه‌کننده، ناظر و تأییدکننده واقعی؛ بررسی SoD و همه مسیرهای جایگزین.
پذیرش: حالت نامعتبر رد شود؛ دلیل رد حداقل ۱۰ کاراکتر؛ کاربر ممنوع نتواند تأیید کند.
حد شاهد: آزمون‌های منتخب workflow/status و validation موفق؛ ماتریس کامل نقش‌ها اجرا نشده
ارجاع: apps/api/core/field_reports/services/__init__.py:28؛ apps/api/core/field_reports/daily_report_views.py:332؛ specs/036-validation-codes-unset-semantics/spec.md:79

W02 — اصلاحیه، نسخه‌بندی، دلیل، لغو و بازگشت به نسخه قبلی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: ساخت draft بعدی، دلیل، انتقال فرزندان، تاریخچه و لغو وجود دارند؛ قرارداد قبلی آزمون دارد.
باقیمانده: تکمیل انتقال هویت تجمیعی، مجموعه کامل provenance و متادیتای مالک خلاصه؛ بازآزمایی لغو/تأیید نسخه.
پذیرش: نسخه جدید هیچ داده/منبع معتبر را گم نکند؛ اصلاح همزمان تکراری نشود؛ لغو نسخه approved قبلی را بازگرداند.
حد شاهد: آزمون‌های قدیمی اصلاحیه موفق؛ سه نقص تازه در انتقال معنای خلاصه بازتولید شد
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ specs/035-correction-lineage-cloning/spec.md:89

W03 — قفل داده مشتق پس از اصلاحیه و منع ویرایش مستقیم
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: قفل روی گزارش auto فعال است؛ نسخه اصلاحی ساخته‌شده این پرچم را حفظ نمی‌کند.
باقیمانده: حفظ هویت تجمیعی و قفل‌کردن بر اساس مالکیت داده در تمام child/batch paths؛ اصلاح فقط در واحد منبع.
پذیرش: POST/PATCH/DELETE ردیف مشتق نسخه اصلاحی هم رد شود؛ جزئیات مجاز مدیریت قابل ویرایش بماند.
حد شاهد: نقص اجرایی: PATCH موفق و ذخیره‌شده روی ردیف derived؛ correction-write-probe.json
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ apps/api/core/field_reports/daily_report_views.py:618

W04 — منبع ردیف و مجموعه کامل منابع مقادیر تجمیعی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: DailyReportDerivedSource و drill-down برای خلاصه اصلی موجودند؛ اصلاحیه این رکوردها را کپی/بازنگاشت نمی‌کند.
باقیمانده: بازنگاشت منبع به شناسه ردیف نسخه جدید و حفظ تمام منابع، نه فقط source FK تک‌ردیفی.
پذیرش: جمع دو منبع در هر نسخه هر دو منبع را نشان دهد؛ اصلاح/لغو هیچ منبعی را گم نکند.
حد شاهد: نقص اجرایی: ۲ رکورد provenance در مبدأ و ۰ در نسخه اصلاحی
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ apps/api/core/field_reports/serializers.py:100؛ specs/032-unit-report-source-truth/spec.md:180

W05 — نظر مدیریت، override هوا/تعطیلی و اطلاعات مالک خلاصه در اصلاح
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: بازسازی معمول نظر/override را حفظ می‌کند؛ clone اصلاحیه management_opinion و weather_override را از دست می‌دهد.
باقیمانده: حفظ و تعیین سیاست تمام metadata مالک خلاصه، config/fingerprint/aggregation metadata؛ سازگاری با snapshot نسخه.
پذیرش: اصلاح/لغو/تأیید مجدد نظر و override مجاز را عیناً حفظ کند؛ مقادیر مشتق دوباره دستی نشوند.
حد شاهد: نقص اجرایی نظر و weather_override بازتولید؛ بقیه metadata در کد مشکوک و نیازمند تست دقیق
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ apps/api/core/field_reports/services/daily_report_aggregation.py:559؛ specs/032-unit-report-source-truth/spec.md:184

W06 — نسخه رسمی ثابت و تشخیص تفاوت با منابع جاری
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: snapshot مصوب حفظ و در خروجی مقایسه/هشدار منبع نمایش داده می‌شود؛ زمان ثبت و تأیید جدا هستند.
باقیمانده: تطبیق نسخه دانلودشده با نسخه مصوب و اصلاح‌شده؛ قاعده وضعیت مبنای گزارش رسمی مستند شود.
پذیرش: تغییر منبع بدون اصلاح رسمی محتوای snapshot تأییدشده را پنهانی عوض نکند.
حد شاهد: آزمون‌های منتخب summary_snapshot_comparison موفق
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:593؛ apps/api/core/field_reports/shiraz_file4_excel.py:132؛ apps/api/core/field_reports/pdf.py:117

E15 — نسخه جاری در دفتر رسمی؛ تاریخچه جدا از جمع عملیاتی
فاز مالک/اثر منبع: پشتیبان A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: query وضعیت approved را اعمال می‌کند اما is_current را نه؛ نسخه قدیمی approved هم وارد می‌شود.
باقیمانده: فیلتر نسخه جاری برای دفتر عملیاتی و سیاست نمایش تاریخچه مستقل؛ کنترل پس از اصلاح/لغو.
پذیرش: دو نسخه ۵ واحدی یک فعالیت، جمع رسمی ۵ بدهند نه ۱۰؛ سابقه همچنان قابل دسترس بماند.
حد شاهد: نقص اجرایی: ۲ ردیف، quantity=10 و headcount=8 در برابر ۱ ردیف،۵ و۴
ارجاع: apps/api/core/field_reports/services/activity_log.py:9؛ specs/032-unit-report-source-truth/spec.md:163

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- W01 | specs/007-daily-report-gaps/spec.md:126 | FR-007
- W02 | specs/007-daily-report-gaps/spec.md:127 | FR-008
- W06 | specs/007-daily-report-gaps/spec.md:128 | FR-009
- W03 | specs/007-daily-report-gaps/spec.md:132 | FR-013
- W03 | specs/007-daily-report-gaps/spec.md:150 | SC-002
- D01 | specs/028-auto-daily-report-summary/spec.md:92 | FR-001
- D03 | specs/028-auto-daily-report-summary/spec.md:93 | FR-002
- D01 | specs/028-auto-daily-report-summary/spec.md:94 | FR-003
- H06 | specs/028-auto-daily-report-summary/spec.md:109 | FR-005
- D01 | specs/028-auto-daily-report-summary/spec.md:110 | FR-006
- W05 | specs/028-auto-daily-report-summary/spec.md:113 | FR-009
- H06 | specs/028-auto-daily-report-summary/spec.md:115 | FR-011
- D02 | specs/028-auto-daily-report-summary/spec.md:116 | FR-012
- D01 | specs/028-auto-daily-report-summary/spec.md:134 | SC-001
- D01 | specs/028-auto-daily-report-summary/spec.md:135 | SC-002
- D01 | specs/028-auto-daily-report-summary/spec.md:138 | SC-005
- H06 | specs/028-auto-daily-report-summary/spec.md:140 | SC-007
- H06 | specs/031-site-inactivity-security/spec.md:93 | FR-011
- H06 | specs/031-site-inactivity-security/spec.md:94 | FR-012
- H06 | specs/031-site-inactivity-security/spec.md:117 | SC-005
- D02 | specs/032-unit-report-source-truth/spec.md:144 | FR-001
- D02 | specs/032-unit-report-source-truth/spec.md:156 | FR-003
- D02 | specs/032-unit-report-source-truth/spec.md:158 | FR-005
- H06 | specs/032-unit-report-source-truth/spec.md:162 | FR-006
- H06 | specs/032-unit-report-source-truth/spec.md:163 | FR-007
- D01 | specs/032-unit-report-source-truth/spec.md:164 | FR-008
- H06 | specs/032-unit-report-source-truth/spec.md:165 | FR-009
- W01 | specs/032-unit-report-source-truth/spec.md:166 | FR-010
- W03 | specs/032-unit-report-source-truth/spec.md:167 | FR-011
- W01 | specs/032-unit-report-source-truth/spec.md:168 | FR-012
- W02 | specs/032-unit-report-source-truth/spec.md:169 | FR-013
- D01 | specs/032-unit-report-source-truth/spec.md:176 | FR-017
- D03 | specs/032-unit-report-source-truth/spec.md:177 | FR-018
- D03 | specs/032-unit-report-source-truth/spec.md:178 | FR-019
- D01 | specs/032-unit-report-source-truth/spec.md:179 | FR-020
- W04 | specs/032-unit-report-source-truth/spec.md:180 | FR-021
- W04 | specs/032-unit-report-source-truth/spec.md:181 | FR-022
- W04 | specs/032-unit-report-source-truth/spec.md:182 | FR-023
- W04 | specs/032-unit-report-source-truth/spec.md:183 | FR-024
- W05 | specs/032-unit-report-source-truth/spec.md:184 | FR-025
- D02 | specs/032-unit-report-source-truth/spec.md:185 | FR-026
- D02 | specs/032-unit-report-source-truth/spec.md:186 | FR-027
- D02 | specs/032-unit-report-source-truth/spec.md:187 | FR-028
- D01 | specs/032-unit-report-source-truth/spec.md:191 | FR-029
- D01 | specs/032-unit-report-source-truth/spec.md:192 | FR-030
- D01 | specs/032-unit-report-source-truth/spec.md:193 | FR-031
- D01 | specs/032-unit-report-source-truth/spec.md:194 | FR-032
- D01 | specs/032-unit-report-source-truth/spec.md:218 | SC-001
- D03 | specs/032-unit-report-source-truth/spec.md:220 | SC-003
- W04 | specs/032-unit-report-source-truth/spec.md:221 | SC-004
- W04 | specs/032-unit-report-source-truth/spec.md:222 | SC-005
- D02 | specs/032-unit-report-source-truth/spec.md:223 | SC-006
- D01 | specs/032-unit-report-source-truth/spec.md:224 | SC-007
- W04 | specs/033-daily-sections-grid/spec.md:200 | FR-012
- D03 | specs/033-daily-sections-grid/spec.md:243 | FR-037
- W04 | specs/033-daily-sections-grid/spec.md:244 | FR-038
- W04 | specs/033-daily-sections-grid/spec.md:245 | FR-039
- W05 | specs/033-daily-sections-grid/spec.md:248 | FR-042
- W03 | specs/033-daily-sections-grid/spec.md:249 | FR-043
- W04 | specs/033-daily-sections-grid/spec.md:250 | FR-044
- W04 | specs/033-daily-sections-grid/spec.md:270 | SC-002
- W04 | specs/033-daily-sections-grid/spec.md:273 | SC-005
- W03 | specs/033-daily-sections-grid/spec.md:277 | SC-009
- W02 | specs/034-daily-lifecycle-lock/spec.md:87 | FR-001
- W02 | specs/034-daily-lifecycle-lock/spec.md:88 | FR-002
- W02 | specs/034-daily-lifecycle-lock/spec.md:89 | FR-003
- W02 | specs/034-daily-lifecycle-lock/spec.md:90 | FR-004
- W02 | specs/034-daily-lifecycle-lock/spec.md:91 | FR-005
- W02 | specs/034-daily-lifecycle-lock/spec.md:92 | FR-006
- W02 | specs/034-daily-lifecycle-lock/spec.md:93 | FR-007
- W02 | specs/034-daily-lifecycle-lock/spec.md:94 | FR-008
- W01 | specs/034-daily-lifecycle-lock/spec.md:95 | FR-009
- W01 | specs/034-daily-lifecycle-lock/spec.md:96 | FR-010
- W02 | specs/034-daily-lifecycle-lock/spec.md:115 | SC-001
- W02 | specs/034-daily-lifecycle-lock/spec.md:116 | SC-002
- W01 | specs/034-daily-lifecycle-lock/spec.md:117 | SC-003
- W02 | specs/034-daily-lifecycle-lock/spec.md:119 | SC-005
- W02 | specs/035-correction-lineage-cloning/spec.md:89 | FR-001
- W02 | specs/035-correction-lineage-cloning/spec.md:90 | FR-002
- W02 | specs/035-correction-lineage-cloning/spec.md:96 | FR-003
- W02 | specs/035-correction-lineage-cloning/spec.md:97 | FR-004
- W02 | specs/035-correction-lineage-cloning/spec.md:98 | FR-005
- W02 | specs/035-correction-lineage-cloning/spec.md:99 | FR-006
- W02 | specs/035-correction-lineage-cloning/spec.md:100 | FR-007
- W02 | specs/035-correction-lineage-cloning/spec.md:101 | FR-008
- W02 | specs/035-correction-lineage-cloning/spec.md:102 | FR-009
- W02 | specs/035-correction-lineage-cloning/spec.md:103 | FR-010
- W02 | specs/035-correction-lineage-cloning/spec.md:104 | FR-011
- W02 | specs/035-correction-lineage-cloning/spec.md:118 | SC-001
- W02 | specs/035-correction-lineage-cloning/spec.md:119 | SC-002
- W02 | specs/035-correction-lineage-cloning/spec.md:120 | SC-003
- W02 | specs/035-correction-lineage-cloning/spec.md:121 | SC-004
- W01 | specs/036-validation-codes-unset-semantics/spec.md:79 | FR-001
- W01 | specs/036-validation-codes-unset-semantics/spec.md:80 | FR-002
- W01 | specs/036-validation-codes-unset-semantics/spec.md:81 | FR-003
- W01 | specs/036-validation-codes-unset-semantics/spec.md:82 | FR-004
- W01 | specs/036-validation-codes-unset-semantics/spec.md:83 | FR-005
- W01 | specs/036-validation-codes-unset-semantics/spec.md:108 | SC-001
- W03 | specs/037-daily-offline-sync/spec.md:117 | FR-014
- W04 | specs/037-daily-offline-sync/spec.md:118 | FR-015
- W05 | specs/037-daily-offline-sync/spec.md:119 | FR-016
- D02 | specs/038-discipline-sub-reports/spec.md:180 | FR-016
- D01 | specs/038-discipline-sub-reports/spec.md:184 | FR-018
- W03 | specs/038-discipline-sub-reports/spec.md:186 | FR-020
- D01 | specs/038-discipline-sub-reports/spec.md:224 | SC-007
- H06 | specs/039-auto-daily-rollup/spec.md:179 | FR-001
- H06 | specs/039-auto-daily-rollup/spec.md:180 | FR-002
- D01 | specs/039-auto-daily-rollup/spec.md:182 | FR-004
- W03 | specs/039-auto-daily-rollup/spec.md:185 | FR-007
- W03 | specs/039-auto-daily-rollup/spec.md:186 | FR-008
- W05 | specs/039-auto-daily-rollup/spec.md:191 | FR-013
- D02 | specs/039-auto-daily-rollup/spec.md:192 | FR-014
- D02 | specs/039-auto-daily-rollup/spec.md:193 | FR-015
- D02 | specs/039-auto-daily-rollup/spec.md:194 | FR-016
- H06 | specs/039-auto-daily-rollup/spec.md:211 | SC-001
- H06 | specs/039-auto-daily-rollup/spec.md:212 | SC-002
- W03 | specs/039-auto-daily-rollup/spec.md:214 | SC-004
- D02 | specs/039-auto-daily-rollup/spec.md:217 | SC-007
- W05 | specs/039-auto-daily-rollup/spec.md:218 | SC-008
- W01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:60 | FR-DR-007
- W02 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:61 | FR-DR-008
- W06 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:62 | FR-DR-009

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):
- US-DR-03 | reports_documentation/atomic-specs/SPEC-01-DAILY-HEADER-WEATHER.md:67 | سهم این مرحله: H06؛ کل گروه‌ها: H06
- US-DR-11 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:26 | سهم این مرحله: W01؛ کل گروه‌ها: W01
- US-DR-12 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:53 | سهم این مرحله: W03؛ کل گروه‌ها: W03
- US-DR-13 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:74 | سهم این مرحله: W02, W04, W05؛ کل گروه‌ها: W02, W04, W05
- US-SR-01 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:30 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-SR-02 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:53 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-SR-03 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:70 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-SR-04 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:87 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-AG-01 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:34 | سهم این مرحله: D01, H06؛ کل گروه‌ها: D01, H06
- US-AG-02 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:55 | سهم این مرحله: D03, W04؛ کل گروه‌ها: D03, D04, D06, D11, W04
- US-AG-03 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:78 | سهم این مرحله: W03؛ کل گروه‌ها: W03
- US-AG-04 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:95 | سهم این مرحله: W05؛ کل گروه‌ها: H02, W05
- US-AG-05 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:112 | سهم این مرحله: D02؛ کل گروه‌ها: D02
- US-AG-06 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:129 | سهم این مرحله: E15؛ کل گروه‌ها: E11, E13, E14, E15

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```

# A.1 / B03 — رفع اختلاف خروجی با فرم مرجع

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

زیرمرحله جاری: B03 — رفع اختلاف خروجی با فرم مرجع
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01, B02.
مرحله قبلی در ترتیب: B02.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: H01, H02, H03, D04, D06, D09, D10, D11, D12, D13, D14, D15, D16, D17, E01, E02, E04, E05, E06, E07, E08, E10, E16
سهم مشترک با مالک دیگر: H04, D08, E03, X02, X07. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: کاربر روز عادی، تعطیل، صفر واقعی، ساعت/درصد نامعلوم، سه شیفت واقعی و داده فارسی/انگلیسی طولانی را در FILE4/PDF و خروجی تخصصی مرتبط با فرمِ قرارداد B01 مقایسه می‌کند.
- ساعت واقعی شیفت، هویت/شماره/روز پروژه فقط در صورت الزام مصوب، فیلدهای هوا و ترتیب و جانمایی نیروی مستقیم/غیرمستقیم مطابق قرارداد باشند؛ دامنه تک‌روز/چندشیته E17 اجرا شود. ۳۴/۳۲ فقط طبق تصمیم پروفایل، نه حقیقت ثابت همه پروژه‌ها. عناوین تاریخی/اضافی حذف نشوند.
- legacy equipment با ساعت None در Excel و PDF نامعلوم بماند و صفر صریح ۰ باشد. داده فعالیت/WBS/اکیپ/پیمانکار، مصالح رسید در برابر مصرف/برگشت/ضایعات، بتن و QC، موانع، HSE، بازدید و پیوست به منبع متصل باشند. جزئیات چاپ‌نشده مسیر drill-down و دلیل مصوب داشته باشند.
- FILE5 درصد عددی ۰..۱۰۰ با قالب صحیح و null خالی؛ FILE6 فقط ستون‌های مربوط به برق. PDF مستقل واحد فقط اگر C07 آن را مصوب کرد، در همین مرحله نیازمندی قابل آزمون شود؛ در غیر آن نبود آن با ارجاع تصمیم ثبت شود. تغییر C05/C07 نباید بدون مالک بماند.
- Excel برای A4 با محدوده چاپ/fit، تکرار هدر، wrap، ارتفاع و شکست صفحه خوانا باشد. PDF بیش از ۵۰ ردیف، امضا در انتها، نقش واقعی/زمان محلی خوانا، و واترمارک تمام صفحات غیرمصوب داشته باشد؛ مرحله طی‌نشده کنشگر جعلی نگیرد.
- نام فایل قراردادی، RTL و قلم فارسی، متن چندخطی و متن آغازشونده با =,+,-,@ محفوظ باشند؛ متن کاربر فرمول نشود و فرمول محاسباتی سالم بماند. fingerprint متادیتا به‌عنوان تضمین کل بدنه معرفی نشود.
پایان قابل آزمون: هیچ عدد ساختگی، نقش جعلی، متن بریده، جمع غلط یا خطای فرمول در سناریوهای فوق نباشد. شاهد اصلاح خروجی با گواه تطبیق مستقل B05 یکی تلقی نشود.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B03: qa_passed. Existing specification, regression and handoff baseline. Adopt its current scope and use existing QA evidence. If specify is invoked for a material residual gap, scope that gap against the existing spec.
- Reports: output/a1-requirements-2026-11-22-stage1-b03-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b03-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Use specs/059-a1-b03-reference-parity and contract deliverables. Map the QA aliases by artifact. DEL-01 is single-day Excel and PDF, DEL-02 is discipline Excel, DEL-03 is the date-range workbook, and DEL-04 is standalone discipline PDF. C04 defines 34 indirect / 32 direct slots. Keep B03 technical evidence and send independent numeric, print and download evidence to B05.
- DEF-B03-01 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-02 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-03 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-04 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-05 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-06 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-07 — reported resolved in current QA; preserve as regression coverage.
- DEF-B03-08 — reported resolved in current QA; preserve as regression coverage.

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.02, A.1.03
معیار بسته در کشف مرحله ۱: FILE 4، FILE 5/6 و PDF در سناریوهای روز عادی/تعطیل/صفر/نامعلوم/سه‌شیفت/FA-EN با مرجع برابر باشند و عدد ساختگی، نقش جعلی، متن بریده، جمع غلط یا خطای فرمول نداشته باشند.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b03-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b03-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B03-01 — شروع، پایان و مدت شیفت توافق‌شده با روز مرجع در خروجی مقایسه شود.
- DEF-B03-02 — برای پروفایل مصوب شیراز دو جدول نیروی انسانی مجاور باشند. جایگاه عناوین اضافی را طبق C04 بررسی کن.
- DEF-B03-03 — چاپ A4 در یک صفحه عرض، محدوده چاپ، تکرار هدر و خوانایی متن فارسی بلند بررسی شود.
- DEF-B03-04 — سمت واقعی، نام و زمان محلی کنشگر نمایش داده شود و مرحله طی‌نشده کنشگر یا عنوان ساختگی نگیرد.
- DEF-B03-05 — تجهیز قدیمی با ساعت نامعلوم از ساعت صفر واقعی در Excel/PDF قابل تمایز باشد.
- DEF-B03-06 — برای بچینگ، تراک میکسر، شماره شیت آزمایشگاه و پیوند نتیجه ۲۸روزه، چاپ یا جزئیات را مطابق قرارداد B01 تعیین و بررسی کن.
- DEF-B03-07 — برچسب نوع و شدت حادثه در خروجی فارسی بومی باشد، از جمله معادل‌های Major و safety.
- DEF-B03-08 — پروفایل توافق‌شده در پروژه‌های مختلف و با عنوان سفارشی/تاریخی بدون حذف یا تحمیل شمار ثابت آزموده شود.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B03: qa_passed. Acceptance criterion: Excel/PDF values, fields, labels, roles, unknown semantics, long text, pagination, printing, timezone, and watermark match the agreed reference form.
- Source reports: output/a1-requirements-2026-11-21-stage1-b03-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b03-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Use specs/059-a1-b03-reference-parity as the baseline. Treat DEF-B03-01 through DEF-B03-08 as regression scenarios. Preserve the tested shifts, manpower layout, A4/long print, legal roles and watermarks, unset equipment, concrete QC and Persian HSE display. Real reference-day reconciliation remains a B05 gate.

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B03 — رفع اختلاف خروجی با فرم مرجع

**مربوط به:** H04/D08/D10/D13/D15/E02/E03/E04/E07. **پیش‌نیاز:** B01 و تثبیت رفتار نسخه در B02.

ساعت شیفت از منبع واقعی خوانده شود؛ فیلدهای هدر مصوب، ترتیب نیروی انسانی/ستون‌ها و قالب مرجع تکمیل شود. کاتالوگ عمومی تابع template باشد و ۳۴/۳۲ پروفایل فرم تلقی شود. ساعت تجهیز legacy نامعلوم صفر نشود. فهرست فیلدهای بتن/HSE و نقش‌های امضاکننده طبق قرارداد در چاپ یا جزئیات در دسترس باشد. timezone و تاریخ/ساعت امضا با حساب واقعی بررسی شوند.

چاپ Excel برای A4، محدوده چاپ، fit، تکرار هدر و wrap/ارتفاع تنظیم شود؛ PDF طولانی با امضا در انتها و واترمارک همه صفحات آزموده شود. تغییر ظاهر نباید اعداد یا معنا را عوض کند.

**آزمون تحویل:** روز عادی، روز تعطیل، صفر واقعی، ساعت/درصد نامعلوم، متن فارسی/انگلیسی بلند و بیش از ۵۰ ردیف. هیچ عدد ساختگی، متن بریده، نقش جعلی، جمع اشتباه یا خطای فرمول باقی نماند. تغییر حالت approved/draft و نسخه اصلاحی بررسی شود.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

H01 — هویت گزارش، پروژه، قرارداد، تاریخ شمسی، روز هفته و مسئول تهیه
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: مدل هدر و نمایش/خروجی پروژه، قرارداد، تاریخ و تهیه‌کننده وجود دارد.
باقیمانده: تطبیق مقادیر و عنوان‌ها با روز مرجع و نمایش روی مرورگر.
پذیرش: شناسه پروژه، قرارداد، تاریخ و تهیه‌کننده در صفحه و دو فایل یکسان باشند.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/models.py:113؛ apps/api/core/field_reports/shiraz_file4_excel.py:162؛ apps/api/core/field_reports/pdf.py:117

H02 — آب‌وهوا، دمای اختیاری، اثرات جوی و اعتبارسنجی دما
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: پنج وضعیت پایدار، دامنه دمای -۴۰ تا ۶۰، ترتیب کمینه/بیشینه و یادداشت اثرات در مدل/API/PDF وجود دارد.
باقیمانده: اجرای پذیرش تعاملی دوزبانه؛ حفظ override در اصلاحیه در W05 باز است.
پذیرش: پنج مقدار معتبر پذیرفته؛ مقدار قدیمی/ناشناخته رد؛ متن چندخطی عیناً در PDF حفظ شود.
حد شاهد: آزمون‌های منتخب weather و header در بسته ۶۹تایی موفق؛ مرورگر این نوبت اجرا نشده
ارجاع: apps/api/core/field_reports/models.py:113؛ apps/api/core/field_reports/pdf.py:117؛ specs/030-daily-header-weather/spec.md:87

H03 — فعال/تعطیل بودن کارگاه و دلیل استاندارد تعطیلی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: دلایل پنج‌گانه، الزام دلیل در تعطیلی، نمایش PDF و کنترل مجوز by-date در کد وجود دارند.
باقیمانده: اخطار فعالیت مثبت در روز تعطیل و تأیید/انصراف آن در مرورگر دوباره بررسی شود.
پذیرش: تعطیلی بدون دلیل ثبت نشود؛ فعال‌شدن دلیل قبلی نسازد؛ انصراف از اخطار چیزی ثبت نکند.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/daily_report_views.py:197؛ apps/api/core/field_reports/pdf.py:117؛ specs/031-site-inactivity-security/spec.md:83

D04 — فعالیت اجراشده با WBS، پیمانکار، اکیپ، محل، حجم و واحد
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: فیلدهای فعالیت شامل شیفت، قطعه/بلوک/طبقه، پیمانکار و اکیپ جدا و مقادیر کارکرد در مدل و خروجی هستند.
باقیمانده: تطبیق همه ستون‌ها با روز مرجع؛ آزمون مرورگری شناسه‌های پروژه دیگر و WBS مجاز.
پذیرش: پیمانکار جای اکیپ ننشیند؛ WBS و پیمانکار نامعتبر یا پروژه دیگر رد شوند.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/models.py:46؛ apps/api/core/field_reports/shiraz_file4_excel.py:625؛ specs/033-daily-sections-grid/spec.md:186

D06 — نیروی انسانی مستقیم/غیرمستقیم، پیمانکار، شیفت، مرخصی و اضافه‌کاری
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: مدل و تجمیع دسته، شغل، پیمانکار و شمارش شیفت‌ها را نگه می‌دارند؛ SUM در Excel وجود دارد.
باقیمانده: تطبیق مقادیر واقعی، مرخصی اختیاری و عنوان واحد شمارش؛ عدم فرض نفر یکتا.
پذیرش: یک عنوان نزد دو پیمانکار در داده منبع جدا بماند؛ جمع هر ستون با مرجع برابر شود.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/models.py:340؛ apps/api/core/field_reports/services/daily_report_aggregation.py:559؛ apps/api/core/field_reports/shiraz_file4_excel.py:247

D09 — ماشین‌آلات: هویت یکتا، پنج وضعیت، ساعات و دلیل توقف
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: مدل و تجمیع وضعیت/ساعت/هویت و قواعد توقف و سقف ۲۴ ساعت وجود دارد.
باقیمانده: کنترل روز واقعی، دو واحد گزارش‌دهنده یک تجهیز و خطاهای دوزبانه در UI.
پذیرش: تجهیز با شناسه پایدار یک‌بار شمرده شود؛ توقف بدون دلیل و زمان بیش از ۲۴ ساعت رد شود.
حد شاهد: آزمون‌های منتخب machinery_derivation در بسته ۶۹تایی موفق
ارجاع: apps/api/core/field_reports/models.py:636؛ apps/api/core/field_reports/services/daily_report_aggregation.py:559؛ specs/033-daily-sections-grid/spec.md:204

D10 — ساعت نامعلوم ماشین‌آلات در خروجی legacy
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: مسیر تجمیعی جدید nullable را حفظ می‌کند؛ شاخه equipment قدیمی در Excel مقدار None را ۰ می‌نویسد؛ PDF خط تیره می‌دهد.
باقیمانده: همسان‌سازی معنای null/صفر در شاخه legacy یا تعیین بازنشستگی رسمی آن بدون تغییر تاریخچه.
پذیرش: None در هر دو فایل نامعلوم باشد؛ صفر صریح عدد ۰ بماند.
حد شاهد: نقص اجرایی strict XFAIL؛ کنترل مستقل صفر صریح موفق
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:614؛ apps/api/core/field_reports/pdf.py:212

D11 — مصالح وارده واقعی در جدول اصلی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: تمایز رسید واقعی و ردیف عمومی و نمایش دریافت در جدول اصلی وجود دارد.
باقیمانده: تطبیق نوع سند، واحد و مقدار روی روز مرجع.
پذیرش: مصرف/برگشت/ضایعات به‌عنوان رسید واقعی نمایش داده نشوند.
حد شاهد: آزمون‌های منتخب material reconciliation موفق
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:1193؛ apps/api/core/field_reports/shiraz_file4_excel.py:417؛ specs/033-daily-sections-grid/spec.md:213

D12 — مصرف، برگشت، ضایعات و مغایرت با سند معین انبار
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: جزئیات و reconciliation دارای match/mismatch/insufficient-data با مرجع سند انبار وجود دارند.
باقیمانده: آزمون گردش کامل سند واقعی و پیوند قابل مشاهده از گزارش؛ بازطراحی کل انبار در A.1 نیست.
پذیرش: مقایسه با سند ارجاع‌شده باشد؛ مانده تاریخی کلی جانشین سند نشود.
حد شاهد: آزمون‌های منتخب سندمحور موفق؛ پذیرش گردش واقعی اجرا نشده
ارجاع: apps/api/core/field_reports/daily_report_views.py:542؛ apps/api/core/field_reports/daily_report_views.py:548؛ specs/033-daily-sections-grid/spec.md:216

D13 — بتن‌ریزی و جزئیات نمونه‌برداری/کیفیت
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: داده تخصصی بتن و QC در کد هست؛ Excel/PDF روزانه فقط بخشی از اطلاعات پایه را چاپ می‌کنند.
باقیمانده: تعیین ستون‌های چاپی الزامی و مسیر drill-down برای بچینگ، کامیون، نمونه، آزمایش و محل دقیق؛ سپس تطبیق.
پذیرش: حجم و محل برابر مرجع؛ هر نمونه‌برداری با نتیجه/بازرسی مربوط قابل ردیابی باشد.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:476؛ apps/api/core/field_reports/pdf.py:250؛ specs/033-daily-sections-grid/spec.md:222

D14 — فعالیت عمومی، موانع و دستورکار با مسئول و موعد
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: ردیف‌های ساخت‌یافته عمومی، مسائل، مسئول و سررسید و ترتیب/منبع در مدل و تجمیع هستند.
باقیمانده: تطبیق متن چندخطی و ترتیب در خروجی؛ آزمون عدم تبدیل یادداشت ساده به مسئله.
پذیرش: ردیف ساخت‌یافته در بازسازی به متن قالب‌بندی‌شده تبدیل نشود؛ مالک و موعد مانع محفوظ باشد.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:699؛ apps/api/core/field_reports/shiraz_file4_excel.py:716؛ specs/033-daily-sections-grid/spec.md:228

D15 — حوادث HSE، شدت، اقدام فوری و پیگیری
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: حادثه و شدت و مسیر پیگیری در کد وجود دارد؛ نمایش Excel از جمله Major انگلیسی است.
باقیمانده: هماهنگ‌سازی واژگان فارسی/انگلیسی خروجی و اثبات ایجاد اعلان/پیگیری واقعی در سناریو.
پذیرش: شدت و اقدام فوری از منبع بیایند؛ کار پیگیری و مسئول/موعد قابل مشاهده باشد.
حد شاهد: بازبینی مستقیم؛ وجود مسیر اعلان معادل تحویل واقعی اعلان نیست
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:723؛ specs/033-daily-sections-grid/spec.md:231

D16 — بازدیدها و جلسات روزانه ساخت‌یافته
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: ردیف بازدید با منبع و تاریخ/ترتیب و انتقال به خلاصه موجود است.
باقیمانده: تطبیق بازدید روز مرجع؛ اتصال کامل مدیریت جلسات/مصوبات در A.3.C جداست.
پذیرش: انتقال چند واحد ترتیب و منبع را حفظ کند؛ متن جلسه با مصوبه رسمی خلط نشود.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:723؛ specs/033-daily-sections-grid/spec.md:229

D17 — عکس و پیوست فعالیت، محدودیت نوع/اندازه و انتساب پروژه
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: قواعد JPEG/PNG تا ۱۰MB و ارتباط منبع/فعالیت و پیوند بخش‌ها در پیاده‌سازی وجود دارد.
باقیمانده: تست upload واقعی و پروژه دیگر، MIME جعلی، تاریخ ثبت و بازیابی از هر بخش در مرورگر.
پذیرش: ZIP/EXE/فایل جعلی یا بزرگ رد؛ فایل پروژه دیگر متصل نشود؛ گالری بزرگ چاپی الزام خودکار نیست.
حد شاهد: بازبینی کد؛ ذخیره‌سازی و مرورگر پیوست این نوبت اجرا نشده
ارجاع: apps/api/core/sub_reports/services/attachments.py:28؛ apps/api/core/field_reports/serializers.py:1439؛ specs/033-daily-sections-grid/spec.md:236

E01 — دانلود FILE4 با RTL، فونت فارسی و بخش‌های اصلی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: سازنده Excel، endpoint مجاز و بخش‌های اصلی فعال هستند؛ فایل کنترل تولید شد.
باقیمانده: تطبیق کامل با مرجع مستقل و اصلاح اختلاف‌های E02 تا E04.
پذیرش: xlsx سالم، فارسی خوانا و همه بخش‌های مورد توافق با مقدار درست دانلود شوند.
حد شاهد: آزمون‌های منتخب FILE4 موفق؛ این وضعیت معادل برابری کامل فرم نیست
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:124؛ apps/api/core/field_reports/daily_report_views.py:435

E02 — انطباق چیدمان و فیلدهای FILE4 با فرم واقعی شیراز
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: بخش‌های اصلی موجودند؛ خروجی فعلی جدول‌های روی‌هم دارد، فرم واقعی نیروی مستقیم/غیرمستقیم را کنار هم می‌چیند.
باقیمانده: تعیین و اجرای معیار برابری ساختاری/چاپی؛ ساعت شیفت و شماره رسمی، عنوان‌ها و ترتیب ستون‌ها روشن شوند.
پذیرش: بازبین با مقایسه کنارهم محل و مقدار هر فیلد مصوب را بدون نگاشت مبهم پیدا کند.
حد شاهد: مقایسه ساختار workbook مرجع با خروجی کنترل؛ تطبیق عددی یک روز کامل انجام نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:162؛ apps/api/core/field_reports/shiraz_file4_excel.py:247؛ docs/delivery/R0-scope-and-reports-contract.md:30

E04 — چاپ Excel و PDF برای متن بلند و بیش از ۵۰ ردیف
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: PDF صفحه‌بندی دارد؛ Excel عرض ستون را محدود می‌کند اما print area/fit/repeat headers و ارتفاع پویا تنظیم نشده‌اند.
باقیمانده: تنظیم چاپ، شکست صفحه، تکرار عنوان و wrap/ارتفاع؛ بازبینی بصری همه صفحات و امضاها.
پذیرش: هیچ متن/عدد بریده نشود؛ عنوان‌ها در صفحات بعد خوانا و امضا آخرین صفحه باشد.
حد شاهد: ساختار نمونه Excel فاقد print area/orientation؛ PDF بلند مستقل بصری این نوبت بررسی نشده
ارجاع: apps/api/core/field_reports/shiraz_file4_excel.py:763؛ apps/api/core/field_reports/pdf.py:83

E05 — PDF روزانه، نام فایل و محتوای بخش‌ها
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: PDF فارسی با هدر، فعالیت، منابع، یادداشت و نظر مدیریت و نام قراردادی تولید می‌شود.
باقیمانده: تطبیق ارقام و فیلدهای الزامی با Excel و مرجع؛ جزئیات بتن و شیفت طبق قرارداد.
پذیرش: نام daily-report-{date}-{shift}.pdf و محتوای نسخه یکسان باشد.
حد شاهد: آزمون‌های منتخب PDF summary parity موفق؛ برابر بودن با مرجع واقعی هنوز اثبات نشده
ارجاع: apps/api/core/field_reports/pdf.py:83؛ apps/api/core/field_reports/daily_report_views.py:423؛ specs/044-shiraz-excel-parity-pdf/spec.md:189

E06 — واترمارک تمام صفحات پیش‌نویس و حذف آن از نسخه مصوب
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: وضعیت غیرapproved واترمارک و approved حذف آن دارد.
باقیمانده: بازبینی بصری PDF چندصفحه‌ای برای هر حالت و نسخه اصلاحی.
پذیرش: تمام صفحات غیرمصوب نشانه پیش‌نویس داشته باشند؛ نسخه مصوب نشان پیش‌نویس نداشته باشد.
حد شاهد: آزمون‌های منتخب watermark/signatures موفق؛ بررسی بصری مستقل همه حالت‌ها انجام نشده
ارجاع: apps/api/core/field_reports/pdf.py:298؛ specs/044-shiraz-excel-parity-pdf/spec.md:190

E07 — سه جای امضای واقعی، سمت کنشگر و زمان محلی خوانا
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: نام کنشگر و زمان در سه جای امضای آخر فایل هست؛ سمت/نقش واقعی در خروجی چاپ نشده.
باقیمانده: افزودن نقش مصوب/واقعی؛ بررسی تقویم/منطقه زمانی و مسیر تأیید مستقیم بدون ساخت ناظر جعلی.
پذیرش: کنشگر واقعی همراه سمت و زمان قابل فهم؛ مرحله طی‌نشده نام یا امضای ساختگی نگیرد.
حد شاهد: نام/زمان در آزمون‌های منتخب؛ نبود نقش از کد؛ اشکال منطقه زمانی بازتولید نشده
ارجاع: apps/api/core/field_reports/pdf.py:338؛ specs/044-shiraz-excel-parity-pdf/spec.md:192

E08 — شناسه صحت مبتنی بر متادیتا و حدود ادعای امضای دیجیتال
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: fingerprint قطعی از شناسه/lineage/روز/شیفت/وضعیت/کنش تأیید چاپ می‌شود.
باقیمانده: در تحویل صریحاً متادیتایی بودن هش توضیح داده شود؛ اگر امضای کل محتوا/PKI خواسته شود قرارداد جدید لازم است.
پذیرش: metadata برابر هش برابر دهد؛ این نشان به‌عنوان اثبات عدم تغییر همه مقادیر یا امضای گواهی‌دار معرفی نشود.
حد شاهد: آزمون مشخصه موفق: تغییر quantity هش را عوض نکرد؛ تغییر status عوض کرد؛ این خود نقض FR015 نیست
ارجاع: apps/api/core/field_reports/pdf.py:316؛ specs/044-shiraz-excel-parity-pdf/spec.md:196

E10 — FILE5 ابنیه و FILE6 برق با درصد عددی و ستون‌های تخصصی
فاز مالک/اثر منبع: مرتبط با A.1؛ ورود داده در A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: هر دو Excel تخصصی و دکمه/endpoint واحد وجود دارند؛ درصد عددی 0.0%، درصد نامعلوم خالی؛ برق فاقد قطعه/درصد است.
باقیمانده: تطبیق تخصصی با فایل واقعی و کنترل مسیر دسترسی؛ تعیین ابهام PDF زیرگزارش.
پذیرش: ابنیه درصد ۰ تا ۱۰۰ به فرمت درصد صحیح؛ برق ستون ابنیه اضافه نداشته باشد.
حد شاهد: آزمون‌های منتخب subreport Excel موفق؛ گردش واقعی مرورگری اجرا نشده
ارجاع: apps/api/core/sub_reports/shiraz_subreport_excel.py:1؛ specs/044-shiraz-excel-parity-pdf/spec.md:185

E16 — امنیت محتوای سلول‌های Excel و متن فارسی/چندخطی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: literalize_cell در خروجی‌های Excel برای جلوگیری از فرمول‌شدن متن وجود دارد.
باقیمانده: حفظ پوشش متن‌های شروع‌شونده با =,+,-,@ و فارسی/انگلیسی در نمونه پذیرش.
پذیرش: ورودی کاربر به‌عنوان متن ذخیره شود؛ فرمول‌های محاسباتی داخلی سالم بمانند.
حد شاهد: آزمون‌های منتخب export موفق؛ ارزیابی امنیت جامع کل محصول انجام نشده
ارجاع: apps/api/core/field_reports/excel_safety.py:1؛ apps/api/core/field_reports/shiraz_file4_excel.py:124

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- H01 | specs/007-daily-report-gaps/spec.md:120 | FR-001
- D04 | specs/007-daily-report-gaps/spec.md:121 | FR-002
- D06 | specs/007-daily-report-gaps/spec.md:122 | FR-003
- D09 | specs/007-daily-report-gaps/spec.md:123 | FR-004
- D12 | specs/007-daily-report-gaps/spec.md:124 | FR-005
- D14 | specs/007-daily-report-gaps/spec.md:125 | FR-006
- D12 | specs/007-daily-report-gaps/spec.md:131 | FR-012
- D12 | specs/007-daily-report-gaps/spec.md:151 | SC-003
- D12 | specs/007-daily-report-gaps/spec.md:153 | SC-005
- E02 | specs/028-auto-daily-report-summary/spec.md:95 | FR-004
- D06 | specs/028-auto-daily-report-summary/spec.md:111 | FR-007
- D04 | specs/028-auto-daily-report-summary/spec.md:112 | FR-008
- E02 | specs/028-auto-daily-report-summary/spec.md:136 | SC-003
- D06 | specs/028-auto-daily-report-summary/spec.md:137 | SC-004
- H02 | specs/030-daily-header-weather/spec.md:87 | FR-001
- H02 | specs/030-daily-header-weather/spec.md:88 | FR-002
- H02 | specs/030-daily-header-weather/spec.md:89 | FR-003
- H02 | specs/030-daily-header-weather/spec.md:90 | FR-004
- H02 | specs/030-daily-header-weather/spec.md:91 | FR-005
- H02 | specs/030-daily-header-weather/spec.md:92 | FR-006
- H02 | specs/030-daily-header-weather/spec.md:93 | FR-007
- H02 | specs/030-daily-header-weather/spec.md:94 | FR-008
- H02 | specs/030-daily-header-weather/spec.md:95 | FR-009
- H02 | specs/030-daily-header-weather/spec.md:96 | FR-010
- H02 | specs/030-daily-header-weather/spec.md:97 | FR-011
- H02 | specs/030-daily-header-weather/spec.md:98 | FR-012
- H02 | specs/030-daily-header-weather/spec.md:99 | FR-013
- H02 | specs/030-daily-header-weather/spec.md:100 | FR-014
- H02 | specs/030-daily-header-weather/spec.md:101 | FR-015
- H02 | specs/030-daily-header-weather/spec.md:102 | FR-016
- H02 | specs/030-daily-header-weather/spec.md:103 | FR-017
- H02 | specs/030-daily-header-weather/spec.md:137 | SC-001
- H02 | specs/030-daily-header-weather/spec.md:138 | SC-002
- H02 | specs/030-daily-header-weather/spec.md:139 | SC-003
- H02 | specs/030-daily-header-weather/spec.md:140 | SC-004
- H02 | specs/030-daily-header-weather/spec.md:141 | SC-005
- H02 | specs/030-daily-header-weather/spec.md:142 | SC-006
- H03 | specs/031-site-inactivity-security/spec.md:83 | FR-001
- H03 | specs/031-site-inactivity-security/spec.md:84 | FR-002
- H03 | specs/031-site-inactivity-security/spec.md:85 | FR-003
- H03 | specs/031-site-inactivity-security/spec.md:86 | FR-004
- H03 | specs/031-site-inactivity-security/spec.md:87 | FR-005
- H03 | specs/031-site-inactivity-security/spec.md:88 | FR-006
- H03 | specs/031-site-inactivity-security/spec.md:89 | FR-007
- H03 | specs/031-site-inactivity-security/spec.md:90 | FR-008
- H03 | specs/031-site-inactivity-security/spec.md:91 | FR-009
- H03 | specs/031-site-inactivity-security/spec.md:92 | FR-010
- H03 | specs/031-site-inactivity-security/spec.md:113 | SC-001
- H03 | specs/031-site-inactivity-security/spec.md:114 | SC-002
- H03 | specs/031-site-inactivity-security/spec.md:115 | SC-003
- H03 | specs/031-site-inactivity-security/spec.md:116 | SC-004
- H03 | specs/031-site-inactivity-security/spec.md:118 | SC-006
- D04 | specs/033-daily-sections-grid/spec.md:186 | FR-001
- D04 | specs/033-daily-sections-grid/spec.md:188 | FR-003
- D04 | specs/033-daily-sections-grid/spec.md:189 | FR-004
- D06 | specs/033-daily-sections-grid/spec.md:194 | FR-006
- D06 | specs/033-daily-sections-grid/spec.md:195 | FR-007
- D06 | specs/033-daily-sections-grid/spec.md:197 | FR-009
- D09 | specs/033-daily-sections-grid/spec.md:204 | FR-013
- D09 | specs/033-daily-sections-grid/spec.md:205 | FR-014
- D09 | specs/033-daily-sections-grid/spec.md:206 | FR-015
- D09 | specs/033-daily-sections-grid/spec.md:207 | FR-016
- D09 | specs/033-daily-sections-grid/spec.md:208 | FR-017
- D09 | specs/033-daily-sections-grid/spec.md:209 | FR-018
- D12 | specs/033-daily-sections-grid/spec.md:213 | FR-019
- D11 | specs/033-daily-sections-grid/spec.md:214 | FR-020
- D11 | specs/033-daily-sections-grid/spec.md:215 | FR-021
- D12 | specs/033-daily-sections-grid/spec.md:216 | FR-022
- D12 | specs/033-daily-sections-grid/spec.md:217 | FR-023
- D12 | specs/033-daily-sections-grid/spec.md:218 | FR-024
- D13 | specs/033-daily-sections-grid/spec.md:222 | FR-025
- D13 | specs/033-daily-sections-grid/spec.md:223 | FR-026
- D13 | specs/033-daily-sections-grid/spec.md:224 | FR-027
- D14 | specs/033-daily-sections-grid/spec.md:228 | FR-028
- D16 | specs/033-daily-sections-grid/spec.md:229 | FR-029
- D14 | specs/033-daily-sections-grid/spec.md:230 | FR-030
- D15 | specs/033-daily-sections-grid/spec.md:231 | FR-031
- D14 | specs/033-daily-sections-grid/spec.md:232 | FR-032
- D17 | specs/033-daily-sections-grid/spec.md:236 | FR-033
- D17 | specs/033-daily-sections-grid/spec.md:237 | FR-034
- D17 | specs/033-daily-sections-grid/spec.md:238 | FR-035
- D17 | specs/033-daily-sections-grid/spec.md:239 | FR-036
- D10 | specs/033-daily-sections-grid/spec.md:246 | FR-040
- D14 | specs/033-daily-sections-grid/spec.md:247 | FR-041
- D16 | specs/033-daily-sections-grid/spec.md:251 | FR-045
- D09 | specs/033-daily-sections-grid/spec.md:274 | SC-006
- D12 | specs/033-daily-sections-grid/spec.md:275 | SC-007
- D14 | specs/033-daily-sections-grid/spec.md:276 | SC-008
- D06 | specs/039-auto-daily-rollup/spec.md:183 | FR-005
- D06 | specs/039-auto-daily-rollup/spec.md:184 | FR-006
- H02 | specs/039-auto-daily-rollup/spec.md:190 | FR-012
- D11 | specs/039-auto-daily-rollup/spec.md:195 | FR-017
- D06 | specs/039-auto-daily-rollup/spec.md:213 | SC-003
- E01 | specs/044-shiraz-excel-parity-pdf/spec.md:179 | FR-001
- E01 | specs/044-shiraz-excel-parity-pdf/spec.md:180 | FR-002
- E02 | specs/044-shiraz-excel-parity-pdf/spec.md:184 | FR-006
- E10 | specs/044-shiraz-excel-parity-pdf/spec.md:185 | FR-007
- E10 | specs/044-shiraz-excel-parity-pdf/spec.md:186 | FR-008
- E10 | specs/044-shiraz-excel-parity-pdf/spec.md:187 | FR-009
- E05 | specs/044-shiraz-excel-parity-pdf/spec.md:189 | FR-011
- E06 | specs/044-shiraz-excel-parity-pdf/spec.md:190 | FR-012
- E06 | specs/044-shiraz-excel-parity-pdf/spec.md:191 | FR-013
- E07 | specs/044-shiraz-excel-parity-pdf/spec.md:192 | FR-014
- E08 | specs/044-shiraz-excel-parity-pdf/spec.md:196 | FR-015
- E07 | specs/044-shiraz-excel-parity-pdf/spec.md:221 | SC-003
- E10 | specs/044-shiraz-excel-parity-pdf/spec.md:223 | SC-005
- H01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:54 | FR-DR-001
- D04 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:55 | FR-DR-002
- D06 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:56 | FR-DR-003
- D09 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:57 | FR-DR-004
- D12 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:58 | FR-DR-005
- D14 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:59 | FR-DR-006

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):
- US-DR-01 | reports_documentation/atomic-specs/SPEC-01-DAILY-HEADER-WEATHER.md:15 | سهم این مرحله: H02؛ کل گروه‌ها: H02
- US-DR-02 | reports_documentation/atomic-specs/SPEC-01-DAILY-HEADER-WEATHER.md:42 | سهم این مرحله: H03؛ کل گروه‌ها: H03, H04
- US-DR-04 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:15 | سهم این مرحله: D04؛ کل گروه‌ها: D04, D05
- US-DR-05 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:42 | سهم این مرحله: D06؛ کل گروه‌ها: D06, D07, D08
- US-DR-06 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:66 | سهم این مرحله: D09, D10؛ کل گروه‌ها: D09, D10
- US-DR-07 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:91 | سهم این مرحله: D11, D12؛ کل گروه‌ها: D11, D12
- US-DR-08 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:112 | سهم این مرحله: D13؛ کل گروه‌ها: D13
- US-DR-09 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:129 | سهم این مرحله: D14, D15؛ کل گروه‌ها: D14, D15
- US-DR-10 | reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md:146 | سهم این مرحله: D17؛ کل گروه‌ها: D17
- US-SR-01 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:30 | سهم این مرحله: E10؛ کل گروه‌ها: X02, E10, D01
- US-SR-02 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:53 | سهم این مرحله: E10؛ کل گروه‌ها: X02, E10, D01
- US-SR-03 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:70 | سهم این مرحله: E10؛ کل گروه‌ها: X02, E10, D01
- US-SR-04 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:87 | سهم این مرحله: E10؛ کل گروه‌ها: X02, E10, D01
- US-AG-02 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:55 | سهم این مرحله: D04, D06, D11؛ کل گروه‌ها: D03, D04, D06, D11, W04
- US-AG-04 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:95 | سهم این مرحله: H02؛ کل گروه‌ها: H02, W05
- US-WH-01 | reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md:28 | سهم این مرحله: D12؛ کل گروه‌ها: X10, D12
- US-WH-02 | reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md:51 | سهم این مرحله: D12؛ کل گروه‌ها: X10, D12
- US-EX-01 | reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md:26 | سهم این مرحله: E01, E02, E04؛ کل گروه‌ها: E01, E02, E03, E04
- US-EX-02 | reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md:43 | سهم این مرحله: E10؛ کل گروه‌ها: E10
- US-EX-03 | reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md:60 | سهم این مرحله: E05, E06, E07, E08؛ کل گروه‌ها: E05, E06, E07, E08

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```

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

# A.1 / B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما

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

زیرمرحله جاری: B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01, B02, B03, B04, B05.
مرحله قبلی در ترتیب: B05.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: E09, Q03, Q04, Q05
سهم مشترک با مالک دیگر: ندارد. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: تهیه‌کننده، ناظر و کارفرما از مسیر قابل دسترسی همان release/SHA آزموده‌شده، فایل روز مرجع را دانلود می‌کنند، سناریوهای پذیرش را اجرا کرده و نتیجه اولیه را صریح ثبت می‌کنند.
- بسته شامل شناسه release/SHA و محیط/URL، تاریخ شواهد، ورودی و expected مستقل، فایل‌های نهایی با checksum، راهنمای نقش‌ها و مسیرهای واقعی، نقشه تصمیم کاربر، سناریو و نتیجه باشد. لینک شکسته صفر؛ راهنما دامنه واقعی fingerprint و وضعیت مستقل منابع را توضیح دهد.
- API و مرورگر روی همان نسخه: دسکتاپ/موبایل × فارسی/انگلیسی، تهیه‌کننده/ناظر/تأییدکننده/viewer مجاز، نقش غیرمجاز و پروژه دیگر؛ از ثبت واحد تا تجمیع، اصلاح، لغو، تاریخچه و دانلود. ID مستقیم، مسیر جایگزین، دانلود و پیوست تابع دسترسی منبع/پروژه باشند؛ SoD با قرارداد A.6 بازآزمایی شود.
- B05 را برای فایل واقعاً دانلودشده از نسخه هدف معتبر کن؛ SHA و checksum نامنطبق یا تغییر مؤثر پس از آزمون مستلزم بررسی دوباره است. صرف CI یا سرویس فعال یا آزمون محلی، استقرار production را ثابت نمی‌کند.
- B01..B05 باید handoff بسته داشته باشند؛ همه۶۱ گروه،۳۷۰ بند و۴۲ داستان را طبق disposition و مرز قرارداد مرور کن، نه اینکه خارج‌دامنه‌ها را پیاده‌شده یا پذیرفته‌شده حساب کنی. پرونده انتقال به A.3.C/A.4/A.7/A.8/A.9/A.10/A.12 حفظ شود.
- سه وضعیت مستقل گزارش شوند: آمادگی فنی، نسخه قابل دسترسی آزموده‌شده، و پذیرش اولیه کارفرما. هیچ عامل یا تستی به‌جای کارفرما امضا نکند. نبود کارفرما/محیط واقعی/داده لازم نتیجه pending با مسئول و شاهد لازم دارد.
پایان A.1 تنها با بسته‌شدن نقص اجرایی مؤثر، گواه مستقل عدد/فرمول/چاپ، تصمیم‌های دامنه مؤثر، صفر خطای باز رسمی و صورت‌جلسه پذیرش اولیه صریح کارفرما قابل اعلام است.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B06: qa_failed. Specify after B05 in the sequence. Release acceptance requires the B05 evidence and same-candidate clearance of B01–B05.
- Reports: output/a1-requirements-2026-11-22-stage1-b06-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b06-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Specify a frozen release manifest and sample hashes, independent B05 evidence, role/access guide, and a walkthrough with explicit employer disposition, identity, date and release. B01–B04 reported passes supersede the blanket upstream QA claim within their tested scopes. B05 remains open. Require candidate-bound clearance for B01–B05. Record authorized access-control verification by role, project and download surface, desktop and 390×844 mobile in FA RTL and EN LTR across 18 sections, and reconcile the decision tree with deployed permissions. Keep acceptance pending until the employer records it.
- DEF-B06-01 — Missing frozen Phase A.1 release package with commit SHA, independent inputs/expected fixtures, final sample exports, and verified SHA-256 checksums
- DEF-B06-02 — Hard dependency block: upstream delivery packages B01 through B05 have open blocker defects
- DEF-B06-03 — Missing explicit employer review and sign-off protocol
- DEF-B06-04 — Unverified live cross-project isolation matrix and negative security tests for direct ID download endpoints
- DEF-B06-05 — Incomplete mobile responsive and bilingual (FA/EN) verification evidence across all 18 daily report sections
- DEF-B06-06 — Decision tree in docs/decision-tree/ lacks final verification against deployed authorization gates and export routes

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.04
معیار بسته در کشف مرحله ۱: یک release/SHA و فایل‌های checksum‌دار با راهنمای نقش و سناریو ارائه شود؛ آزمون API و مرورگر در دسکتاپ/موبایل و FA/EN انجام و سه وضعیت فنی، نسخه قابل دسترسی آزموده‌شده و پذیرش صریح کارفرما جدا ثبت شوند.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b06-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b06-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B06-01 — آرشیو منجمد با release/SHA، ورودی، expected، فایل‌ها، راهنمای نقش و SHA-256 تحویل شود.
- DEF-B06-02 — بسته‌شدن B01..B05 و تعیین تکلیف شواهد نقص‌های باز قبل از اعلام آمادگی ثبت شود.
- DEF-B06-03 — نتیجه صریح کارفرما روی همان نسخه، همراه با تاریخ، نقش، اختلاف و وضعیت pending/accepted/rejected ثبت شود.
- DEF-B06-04 — برای E09 معیار دفاعی رد دسترسی و دانلود میان پروژه‌ها را با نقش‌ها و داده آزمون مجاز روی نسخه هدف مشخص کن.
- DEF-B06-05 — گردش واقعی نقش‌ها روی دسکتاپ/موبایل و FA/EN را با وضعیت و شواهد هر یک از ۱۸ بخش مرتبط ثبت کن.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B06: qa_failed. Acceptance criterion: Fixed release/SHA, guide, inputs/expected values, checksums, role/device/language/cross-project tests, and explicit employer review are recorded.
- Source reports: output/a1-requirements-2026-11-21-stage1-b06-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b06-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Require a frozen release/SHA with inputs, expected values, outputs, checksums and role guide. Require authenticated desktop and 390×844 mobile evidence in Persian RTL and English LTR across all 18 sections, including scoped permission-denial checks on the candidate and verification against docs/decision-tree/. Require named employer disposition (accepted, rejected or conditional), date and feedback. Record technical QA separately. B01–B03 have reported technical passes, with same-release verification still due. B04/B05 remain failed. Require evidence before checking off A.1.01–A.1.04 at http://localhost:5173/delivery-plan. The Stage 1 live visit redirected to login, so authenticated status remains unverified.
- DEF-B06-01 — Missing frozen Phase A.1 release package with commit SHA, independent inputs/expected fixtures, final sample exports, and verified SHA-256 checksums
- DEF-B06-02 — Hard dependency block: upstream delivery packages B01 through B05 have open blocker defects
- DEF-B06-03 — Missing explicit employer review and sign-off protocol
- DEF-B06-04 — Unverified live cross-project isolation matrix and negative security tests for direct ID download endpoints
- DEF-B06-05 — Incomplete mobile responsive and bilingual (FA/EN) verification evidence across all 18 daily report sections
- DEF-B06-06 — Decision tree in docs/decision-tree/ lacks final verification against deployed authorization gates and export routes

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما

**مربوط به:** E09/Q03/Q04/Q05. **پیش‌نیاز:** B01 تا B05 بسته شده باشند.

یک release/SHA مشخص، مسیر دسترسی، ورودی/expected، راهنمای نقش‌ها، فایل‌های نمونه با checksum و سناریوهای پذیرش ارائه شود. API و مرورگر روی همان نسخه، دسکتاپ/موبایل و فارسی/انگلیسی، نقش مجاز/غیرمجاز و پروژه دیگر آزموده شوند. تهیه‌کننده/ناظر/کارفرما همان نسخه را دانلود کنند و تفاوت منبع submitted با approved و حدود fingerprint توضیح داده شود.

**معیار پایان A.1:** نقص‌های اجرایی اثرگذار بسته؛ گواه مستقل عدد/فرمول/چاپ موجود؛ همه تصمیم‌های دامنه اثرگذار ثبت‌شده؛ هیچ خطای باز تأثیرگذار بر گزارش رسمی؛ نتیجه مرور کارفرما و پذیرش اولیه صریح ثبت شود. قبولی اتوماتیک تست‌ها به جای صورت‌جلسه کارفرما نیست.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

E09 — مجوز مشاهده و دانلود و جلوگیری از نشت بین پروژه‌ها
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: endpointهای خروجی و عضویت/مجوز view_reports وجود دارند و تست منتخب دارند.
باقیمانده: ماتریس کامل نقش مجاز/غیرمجاز/کاربر پروژه دیگر در API و مرورگر روی همان نسخه تحویل.
پذیرش: کاربر غیرمجاز نتواند با ID مستقیم گزارش یا فایل را بگیرد؛ viewer مجاز بتواند دانلود کند.
حد شاهد: بخشی از آزمون مجوز در بسته‌های موفق؛ پوشش منفی کامل و استقرار زنده اثبات نشده
ارجاع: apps/api/core/field_reports/daily_report_views.py:423؛ apps/api/core/field_reports/daily_report_views.py:435؛ specs/044-shiraz-excel-parity-pdf/spec.md:188

Q03 — پذیرش مرورگری دسکتاپ/موبایل و فارسی/انگلیسی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: UI و سناریوهای E2E/گزارش‌های قبلی وجود دارند.
باقیمانده: اجرای تازه از ثبت واحد تا تجمیع، اصلاح، مشاهده نسخه و دانلود با نقش‌های واقعی و اندازه موبایل.
پذیرش: مسیرهای لازم بدون خطای UI، داده گمشده و دورزدن مجوز در هر دو زبان کامل شوند.
حد شاهد: گزارش‌های قدیمی صرفاً تاریخی؛ در این ممیزی اجرای تازه مرورگر انجام نشده
ارجاع: specs/007-daily-report-gaps/spec.md:130؛ specs/033-daily-sections-grid/verification-report.md:1

Q04 — راهنمای مسیرها و درخت تصمیم مطابق رفتار واقعی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: سندهای مسیر کاربر و تصمیم‌گیری برای دانلودها وجود دارند.
باقیمانده: تطبیق همه لینک‌ها و gateهای نقش با نسخه نهایی و حذف ادعای امضای گواهی‌دار اثبات‌نشده.
پذیرش: هر اقدام خروجی از مسیر واقعی و مجوز درست به فایل صحیح برسد؛ لینک شکسته صفر.
حد شاهد: وجود docs بررسی شده؛ ممیزی کامل همه لینک‌ها این نوبت انجام نشده
ارجاع: specs/044-shiraz-excel-parity-pdf/spec.md:201؛ docs/decision-tree/README.md:1

Q05 — بسته تحویل همان نسخه، راهنمای آزمون و صورت‌جلسه پذیرش
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: زیرساخت برنامه و اسناد تحویل وجود دارد؛ کد و تست هم بخش عمده موجودند.
باقیمانده: ثبت SHA انتشار، فایل‌ها و checksum، ورودی/expected، لاگ بازحساب و صفحات PDF و اجرای آزمون کارفرما.
پذیرش: کارفرما دقیقاً فایل و نسخه آزموده‌شده را دانلود و نتیجه پذیرش اولیه را صریح ثبت کند.
حد شاهد: استقرار، فایل دانلودی تولید و صورت‌جلسه کارفرما در این ممیزی احراز/ایجاد نشده
ارجاع: output/delivery-plan-2026-11-03/delivery-plan.md:113؛ docs/delivery/R0-scope-and-reports-contract.md:22

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- Q03 | specs/007-daily-report-gaps/spec.md:130 | FR-011
- Q03 | specs/007-daily-report-gaps/spec.md:149 | SC-001
- E09 | specs/028-auto-daily-report-summary/spec.md:114 | FR-010
- Q03 | specs/030-daily-header-weather/spec.md:143 | SC-007
- Q03 | specs/031-site-inactivity-security/spec.md:119 | SC-007
- Q03 | specs/032-unit-report-source-truth/spec.md:155 | FR-002
- E09 | specs/032-unit-report-source-truth/spec.md:170 | FR-014
- E09 | specs/032-unit-report-source-truth/spec.md:171 | FR-015
- E09 | specs/032-unit-report-source-truth/spec.md:172 | FR-016
- E09 | specs/032-unit-report-source-truth/spec.md:219 | SC-002
- Q03 | specs/032-unit-report-source-truth/spec.md:227 | SC-010
- Q03 | specs/033-daily-sections-grid/spec.md:269 | SC-001
- E09 | specs/033-daily-sections-grid/spec.md:271 | SC-003
- Q03 | specs/033-daily-sections-grid/spec.md:278 | SC-010
- Q03 | specs/034-daily-lifecycle-lock/spec.md:100 | FR-014
- E09 | specs/035-correction-lineage-cloning/spec.md:105 | FR-012
- E09 | specs/035-correction-lineage-cloning/spec.md:122 | SC-005
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:91 | FR-013
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:92 | FR-014
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:93 | FR-015
- E09 | specs/036-validation-codes-unset-semantics/spec.md:94 | FR-016
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:111 | SC-004
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:112 | SC-005
- Q03 | specs/038-discipline-sub-reports/spec.md:185 | FR-019
- Q03 | specs/038-discipline-sub-reports/spec.md:225 | SC-008
- E09 | specs/044-shiraz-excel-parity-pdf/spec.md:188 | FR-010
- Q04 | specs/044-shiraz-excel-parity-pdf/spec.md:201 | FR-020
- Q04 | specs/044-shiraz-excel-parity-pdf/spec.md:224 | SC-006
- Q03 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:64 | FR-DR-011

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```
