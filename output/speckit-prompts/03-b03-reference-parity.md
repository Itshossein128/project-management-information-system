# A.1 / B03 — رفع اختلاف خروجی با فرم مرجع

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
