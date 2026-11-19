# A.1 / B01 — بستن قرارداد داده و نمونه آزمون

```text
/speckit-specify

این درخواست فقط نگارش specification برای همین زیرمرحله است. طبق قالب فعال SpecKit یک feature specification و checklist کیفیت مستقل تولید کن و سپس متوقف شو؛ plan، tasks، analyze، implement، تست محصول، استقرار و اجرای مرحله بعد مجاز نشده‌اند. خروجی حاضرِ Stage 2 صرفاً ورودی specify است.

ورودی workflow اصلی (عین متن):
Generate ordered speckit-specify prompts for Phase A.1 work packages B01 through B06 from /home/hossein/Desktop/projects/building-management/output/a1-requirements-2026-11-18

ریشه پروژه: /home/hossein/Desktop/projects/building-management
منبع مرحلهٔ ۱: /home/hossein/Desktop/projects/building-management/output/a1-requirements-2026-11-18
پیش از تفسیر، knowledge/agent-instructions.md و راهنمای پروژه را رعایت کن. منابع اصلی زیر را بخوان: README.md، remaining-work.md، scope-decisions.md، requirements-and-delivery.md، requirements.json، source-clauses.json/md، atomic-stories.json، atomic-coverage.md، broader-daily-sections.md، employer-summary.md و evidence/README.md در پوشه منبع. coverage.json همین بسته نگاشت مالکیت است؛ الزام تازه یا تأیید کارفرما نیست. برای هر گروه، بندهای منبع و معیارهای کامل داستان‌های مرتبط را هم بخوان؛ شناسه FR/SC به‌تنهایی یکتا نیست و باید با مسیر و خط همراه باشد.

قواعد نگارش:
- چه چیزی و چرا، نقش‌ها، ارزش کاربر، دامنه/غیردامنه، سناریوهای Given/When/Then و شکست/لبه، نیازمندی‌های قابل آزمون، معیارهای موفقیت قابل اندازه‌گیری، وابستگی و تصمیم‌های باز را در spec بنویس. فناوری/ساختار کد را راه‌حل اجباری نکن. نام API/مدل در شواهد فقط نشانی رفتار فعلی است.
- شناسه‌های H/D/W/E/Q/X و C و US و path:line بندها را به FR/SC و سناریوهای spec وصل کن؛ برای هر بند disposition صریحِ حفظ رفتار، رفع شکاف، تصمیم شرطی یا ارجاع فاز دیگر بده. نگاشت داستان به گروه به معنی اجرای تمام سناریوهای آن نیست؛ اختلاف‌ها را در سطح معیار بررسی کن.
- مبنای ممیزی f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a در 2026-11-18 است؛ وضعیت کد امروز از این متن استنباط نشود. ۱۶۲ تست موجود و۲ کنترل موفق و۶ strict XFAIL تاریخی‌اند؛ XFAIL شاهد نقص است. نبود شاهد با نبود قابلیت یکی نیست. اگر نقص در کد روز رفع شده، الزام حفظ رفتار و اثبات باقیمانده را ثبت کن، بازنویسی نکن.
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
