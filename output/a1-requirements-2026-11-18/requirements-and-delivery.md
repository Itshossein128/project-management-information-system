# ممیزی نیازمندی‌ها و باقیمانده تحویل A.1 ولورا

تاریخ بررسی: ۱۸ نوامبر ۲۰۲۶ / ۲۷ آبان ۱۴۰۵. مبنای کد: `f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a` روی develop.

## نتیجه قابل اتکا

**A.1 در این وضعیت آماده اعلام «تحویل کامل» نیست.** بخش عمده سازوکار گزارش روزانه و خروجی‌ها ساخته شده است، اما شش نقص اجرایی با سناریوی مستقل بازتولید شد؛ همچنین برابری کامل یک روز واقعی، بازحساب مستقل Excel و پذیرش کارفرما هنوز در این بررسی احراز نشده‌اند. این ممیزی برای شناسایی و تعیین کار است؛ کد محصول اصلاح یا منتشر نشده است.

۱۶۲ آزمون موجود در دو بسته منتخب موفق شدند؛ دو آزمون کنترل مستقل هم موفق بودند. شش آزمون مستقل با `strict XFAIL` انتظار برآورده‌نشده را بازتولید کردند. XFAIL در اینجا **شاهد نقص باز است، نه قبولی گیت تحویل**. موفقیت آزمون‌های منتخب، کل محصول یا تمام بندهای اسناد را تأیید نمی‌کند.

## دامنه و روش

مبنای مستقیم A.1 طبق سند R0 و برنامه تفصیلی، تطبیق/تحویل اولیه گزارش روزانه FILE4 و PDF روی یک روز کامل و کنترل‌شده است. FILE1 و FILE5/6 و موتور واحدها به این خروجی وابسته‌اند و در فهرست دیده می‌شوند؛ پذیرش جامع عملیات، آفلاین و منابع در A.8 و گزارش‌های دوره‌ای در A.10 باقی می‌ماند. نقص وابستگی اگر خروجی A.1 را خراب کند باید پیش از پذیرش A.1 رفع شود.

در این گزارش «کامل» یعنی بستن نیازمندی‌های مستقیم A.1 و سازگاری وابستگی‌های مؤثر آن؛ به معنی پایان تمام اسناد مربوط به کل سیستم گزارش‌دهی نیست. توسعه ارتباطات ذی‌نفع/جلسه/مکاتبه همچنان جزو تحویل کل پروژه است و در A.3.C/A.10 ردیابی می‌شود.

از graphify برای یافتن ارتباط‌ها و vocabulary واقعی `daily report excel pdf export formula approval rollup shiraz گزارش روزانه` استفاده شد. نتایج traversal محدود/بریده هستند و صرف رتبه یا وجود edge گواه الزام یا صحت اجرا نیست. سپس منابع اصلی و کد مستقیماً خوانده شدند.

ایندکس knowledge قدیمی بود. سرویس embedding محلی LM Studio روی loopback راه‌اندازی/در دسترس قرار گرفت؛ دسترسی Python به loopback از proxy محیط جدا شد و `index --semantic` بدون سرویس بیرونی اجرا شد. نتیجه: hybrid تازه برای همین commit، ۲۵۹۱ سند، ۱۸۱۸۳ chunk، مدل `text-embedding-qwen3-embedding-0.6b` با ۱۰۲۴ بُعد و ۷۸۰ embedding جدید. پرسش اصلی عیناً حفظ شد؛ بازیابی اولیه عمومی بود و با جستجوهای هدفمند daily/exports/operations و مراجعه مستقیم تکمیل شد. شاخص retrieval به‌عنوان تصمیم کارفرما تفسیر نشده است.

اسناد R0، برنامه تحویل و specهای 007، 028، 030 تا 039 مرتبط و 044، نیازمندی پایه روزانه، اسناد اتمیک، کد جاری، دو workbook واقعی و آزمون‌های منتخب مبنای این فهرست‌اند. اسناد پیش‌نویس و طرح کلی به عنوان نیاز/طرح علامت خورده‌اند؛ محتوای سند پیوست دستور اجرایی تلقی نشده است. فایل‌های مرجع دست‌نخورده‌اند.

## چگونه وضعیت‌ها خوانده شوند

- **پیاده‌سازی موجود:** مسیر/مدل/خروجی آن در کد فعلی مشاهده شده؛ محدودیت آزمون کنار هر مورد آمده؛ این عنوان معادل پذیرش کارفرما نیست.
- **ناقص:** بخشی موجود و نقص اثبات‌شده یا کار پذیرش/تطبیق باقی است. «ناقص» الزاماً به معنی نبود backend نیست.
- **نیازمند تثبیت قرارداد:** اسناد/فرم‌ها دامنه یکسانی ندارند؛ تصمیم دقیق باید پیش از پیاده‌سازی ثبت شود.
- **مرتبط؛ خارج از تحویل مستقیم A.1:** برای پوشش کامل نیازها فهرست شده؛ فاز مالک و الزام سازگاری آن مشخص است.

واحد شمارش فهرست، گروه نیازمندی بدون تکرار است. هر گروه چند بند همپوشان را پوشش می‌دهد؛ تعداد گروه‌ها درصد پیشرفت نیست. رجیستر بندهای اصلی، متن الزام را جدا نگه می‌دارد؛ وضعیت یک گروه نباید به معنای اجرای جداگانه و موفق همه آزمون‌های بندهای زیرمجموعه آن خوانده شود.

## نقص‌های اجرایی بازتولیدشده

1. **صفر ساختگی ساعت تجهیز legacy:** productive_hours=None در شاخه قدیمی Excel به ۰ تبدیل می‌شود؛ PDF نامعلوم را خط تیره نشان می‌دهد. شاخه ماشین‌آلات تجمیعی جدید این اشکال را به همان شکل ندارد. کنترل مستقل نشان داد صفر واقعی باید همچنان ۰ بماند.
2. **دو بار شمردن نسخه مصوب قدیمی و جدید در دفتر فعالیت:** با دو نسخه approved یک فعالیت، query دو ردیف/۱۰ واحد/۸ نفر می‌دهد؛ انتظار جاری یک ردیف/۵ واحد/۴ نفر است. تاریخچه باید حفظ شود ولی وارد جمع رسمی جاری نشود.
3. **جمع نوار خلاصه فقط برای صفحه فعلی:** برای ۵۱ ردیف، API count=51 و results=50 می‌دهد؛ UI جمع ۵۰ را به عنوان خلاصه نشان می‌دهد. aggregate تمام نتیجه فیلتر در API نیست.
4. **گریز از قفل مشتقات با اصلاحیه:** خلاصه تولیدشده is_auto_summary=True است ولی clone اصلاحی False می‌شود؛ PATCH مستقیم ردیف derived پاسخ ۲۰۰ داده و تغییر را ذخیره کرد.
5. **گم‌شدن منبع‌های کامل در اصلاحیه:** مبدأ دو رکورد DailyReportDerivedSource دارد و نسخه جدید صفر؛ کپی FK یک منبع در بعضی فرزندان جای مجموعه منابع را نمی‌گیرد.
6. **گم‌شدن نظر مدیریت و علامت override هوا در اصلاحیه:** متن مدیریت به خالی و weather_override از True به False برمی‌گردد. سایر metadata حذف‌شده در constructor نیازمند آزمون دقیق‌اند؛ بازتولید این ممیزی فقط همین دو مورد را قطعی می‌کند.

شواهد عددی و آزمون قابل تکرار در [evidence](evidence/) هستند. نمونه‌های generated-sample مصنوعی و صرفاً کنترل سازنده‌اند؛ به عنوان روز واقعی، golden یا نمونه آماده پذیرش معرفی نمی‌شوند.

## فهرست نیازمندی‌ها و وضعیت فعلی

تعداد گروه‌های ردیابی‌شده: **61**. متن **370 بند FR/SC** از اسناد اصلی در [رجیستر بندها](source-clauses.csv) و [نسخه JSON](source-clauses.json) حفظ شده است. بندهای همپوشان دوباره به عنوان کار مستقل جمع زده نشده‌اند. [فهرست قابل پردازش](requirements.json) و [CSV نیازمندی‌ها](requirements.csv) برای پیگیری در دسترس‌اند.

### H01 — هویت گزارش، پروژه، قرارداد، تاریخ شمسی، روز هفته و مسئول تهیه

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** مدل هدر و نمایش/خروجی پروژه، قرارداد، تاریخ و تهیه‌کننده وجود دارد.

**باقیمانده:** تطبیق مقادیر و عنوان‌ها با روز مرجع و نمایش روی مرورگر.

**انتظار قابل آزمون:** شناسه پروژه، قرارداد، تاریخ و تهیه‌کننده در صفحه و دو فایل یکسان باشند.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:113](../../apps/api/core/field_reports/models.py#L113)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:162](../../apps/api/core/field_reports/shiraz_file4_excel.py#L162)؛ [apps/api/core/field_reports/pdf.py:117](../../apps/api/core/field_reports/pdf.py#L117)

### H02 — آب‌وهوا، دمای اختیاری، اثرات جوی و اعتبارسنجی دما

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** پنج وضعیت پایدار، دامنه دمای -۴۰ تا ۶۰، ترتیب کمینه/بیشینه و یادداشت اثرات در مدل/API/PDF وجود دارد.

**باقیمانده:** اجرای پذیرش تعاملی دوزبانه؛ حفظ override در اصلاحیه در W05 باز است.

**انتظار قابل آزمون:** پنج مقدار معتبر پذیرفته؛ مقدار قدیمی/ناشناخته رد؛ متن چندخطی عیناً در PDF حفظ شود.

**حد اثبات فعلی:** آزمون‌های منتخب weather و header در بسته ۶۹تایی موفق؛ مرورگر این نوبت اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:113](../../apps/api/core/field_reports/models.py#L113)؛ [apps/api/core/field_reports/pdf.py:117](../../apps/api/core/field_reports/pdf.py#L117)؛ [specs/030-daily-header-weather/spec.md:87](../../specs/030-daily-header-weather/spec.md#L87)

### H03 — فعال/تعطیل بودن کارگاه و دلیل استاندارد تعطیلی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** دلایل پنج‌گانه، الزام دلیل در تعطیلی، نمایش PDF و کنترل مجوز by-date در کد وجود دارند.

**باقیمانده:** اخطار فعالیت مثبت در روز تعطیل و تأیید/انصراف آن در مرورگر دوباره بررسی شود.

**انتظار قابل آزمون:** تعطیلی بدون دلیل ثبت نشود؛ فعال‌شدن دلیل قبلی نسازد؛ انصراف از اخطار چیزی ثبت نکند.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/daily_report_views.py:197](../../apps/api/core/field_reports/daily_report_views.py#L197)؛ [apps/api/core/field_reports/pdf.py:117](../../apps/api/core/field_reports/pdf.py#L117)؛ [specs/031-site-inactivity-security/spec.md:83](../../specs/031-site-inactivity-security/spec.md#L83)

### H04 — مدل شیفت و ساعت شروع/پایان یا مدت واقعی شیفت‌های ۱ تا ۳

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** سطرهای نیروی انسانی و فعالیت شیفت دارند؛ هدر مدل day/night/full دارد. در Excel متن ثابت «ساعات کاری شیفت: ثبت نشده» چاپ می‌شود.

**باقیمانده:** تثبیت نگاشت هدر/سطر و ثبت مدت یا بازه واقعی هر شیفت؛ نمایش داده واقعی به جای متن ثابت.

**انتظار قابل آزمون:** سه شیفت مرجع با مدت مشخص، بدون تبدیل خاموش شیفت نامعتبر، در UI/Excel/PDF تطبیق شوند.

**حد اثبات فعلی:** نقص هدر در نمونه خروجی بازتولید شد؛ generated-structure.json

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:9](../../apps/api/core/field_reports/models.py#L9)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:206](../../apps/api/core/field_reports/shiraz_file4_excel.py#L206)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:181](../../specs/044-shiraz-excel-parity-pdf/spec.md#L181)

### H05 — شماره رسمی گزارش، شماره صفحه و شماره روز پروژه در مرجع

**وضعیت:** نیازمند تثبیت قرارداد · **فاز مالک/اثر:** A.1

**آنچه موجود است:** فایل مرجع شماره رسمی گزارش دارد؛ فیلد مستقل معادل report_number/project_day_number در DailyReport مشاهده نشد.

**باقیمانده:** مشخص شود شماره رسمی و روز پروژه در تحویل A.1 الزام هستند یا خیر؛ در صورت الزام مدل و قاعده شماره‌گذاری پیاده شود.

**انتظار قابل آزمون:** شماره بر اساس قاعده مصوب و مستقل از ID داخلی؛ شماره صفحه در چاپ معتبر باشد.

**حد اثبات فعلی:** بازبینی مدل و سلول‌های واقعی مرجع؛ نمونه AG3=882 و X3=500

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:113](../../apps/api/core/field_reports/models.py#L113)؛ [docs/delivery/R0-scope-and-reports-contract.md:30](../../docs/delivery/R0-scope-and-reports-contract.md#L30)

### H06 — یکتایی گزارش جاری، تاریخ منطقی و پوسته گزارش بدون ثبت خام

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** by-date و نسخه جاری، تجمیع روزانه و منع POST گزارش خام وجود دارند.

**باقیمانده:** تعیین سازگاری مفهوم یک روز با شیفت هدر؛ کنترل رقابت و دسترسی مشاهده‌گر در پذیرش.

**انتظار قابل آزمون:** تکرار بازکردن تاریخ گزارش موازی نسازد و مشاهده‌گر نیازی به مجوز ویرایش نداشته باشد.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/daily_report_views.py:191](../../apps/api/core/field_reports/daily_report_views.py#L191)؛ [apps/api/core/field_reports/daily_report_views.py:197](../../apps/api/core/field_reports/daily_report_views.py#L197)؛ [specs/039-auto-daily-rollup/spec.md:179](../../specs/039-auto-daily-rollup/spec.md#L179)

### D01 — گزارش پروژه فقط تجمیعی؛ ورود داده از صفحات واحدها

**وضعیت:** ناقص · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** تجمیع و ممنوعیت ایجاد خام وجود دارد؛ قفل ردیف مشتق به is_auto_summary وابسته است.

**باقیمانده:** رفع گریز اصلاحیه که این پرچم را از دست می‌دهد؛ پوشش تمام مسیرهای مستقیم/قدیمی/batch.

**انتظار قابل آزمون:** اصلاحیه هم گزارش تجمیعی بماند؛ هیچ ردیف مشتق با API یا UI قابل تألیف مستقیم نباشد.

**حد اثبات فعلی:** نقص اجرایی: اصلاحیه auto_summary=False و PATCH ردیف مشتق 200؛ correction-write-probe.json

**شواهد مستقیم:** [apps/api/core/field_reports/daily_report_views.py:618](../../apps/api/core/field_reports/daily_report_views.py#L618)؛ [apps/api/core/field_reports/services/correction_service.py:138](../../apps/api/core/field_reports/services/correction_service.py#L138)؛ [specs/032-unit-report-source-truth/spec.md:179](../../specs/032-unit-report-source-truth/spec.md#L179)

### D02 — شش واحد معتبر و پیکربندی مؤثر پروژه در تاریخ گزارش

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** buildings/electrical/mechanical/machinery/warehouse/security و قواعد template در تجمیع وجود دارد.

**باقیمانده:** اعتبارسنجی روی پروژه واقعی و دو نسخه template با تاریخ اثر متفاوت.

**انتظار قابل آزمون:** واحد الزامی از template همان تاریخ تعیین شود؛ پیش‌فرض ثابت سه‌رشته‌ای معیار نباشد.

**حد اثبات فعلی:** آزمون‌های منتخب completeness موفق؛ همه صفحات شش واحد در این نوبت مرور نشده

**شواهد مستقیم:** [apps/api/core/field_reports/services/daily_report_aggregation.py:119](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L119)؛ [specs/032-unit-report-source-truth/spec.md:144](../../specs/032-unit-report-source-truth/spec.md#L144)

### D03 — انتخاب منابع واجد شرایط: جاری، همان پروژه/روز، submitted یا approved

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** فیلتر منابع هم‌پروژه/هم‌روز/جاری و وضعیت SUBMITTED یا APPROVED در موتور هست.

**باقیمانده:** شفاف‌کردن اینکه approved بودن خلاصه به معنای approved بودن تک‌تک منابع نیست؛ سناریوی واقعی.

**انتظار قابل آزمون:** draft/rejected/deleted/قدیمی و روز یا پروژه دیگر هیچ contribution و اعتبار تکمیل ندهند.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/services/daily_report_aggregation.py:41](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L41)؛ [apps/api/core/field_reports/services/daily_report_aggregation.py:53](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L53)؛ [specs/032-unit-report-source-truth/spec.md:176](../../specs/032-unit-report-source-truth/spec.md#L176)

### D04 — فعالیت اجراشده با WBS، پیمانکار، اکیپ، محل، حجم و واحد

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** فیلدهای فعالیت شامل شیفت، قطعه/بلوک/طبقه، پیمانکار و اکیپ جدا و مقادیر کارکرد در مدل و خروجی هستند.

**باقیمانده:** تطبیق همه ستون‌ها با روز مرجع؛ آزمون مرورگری شناسه‌های پروژه دیگر و WBS مجاز.

**انتظار قابل آزمون:** پیمانکار جای اکیپ ننشیند؛ WBS و پیمانکار نامعتبر یا پروژه دیگر رد شوند.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:46](../../apps/api/core/field_reports/models.py#L46)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:625](../../apps/api/core/field_reports/shiraz_file4_excel.py#L625)؛ [specs/033-daily-sections-grid/spec.md:186](../../specs/033-daily-sections-grid/spec.md#L186)

### D05 — تفکیک صفر واقعی، ثبت‌نشده و اندازه‌گیری‌نشده در حجم فعالیت

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** quantity_measured و قواعد quantity_unset_invalid و نمایش ثبت‌نشده وجود دارند؛ صفر صریح معتبر است.

**باقیمانده:** رفع تعارض متن قدیمی «صفر ممنوع» با 034/036؛ تطبیق FILE1 و همه viewها با داده legacy ناسازگار.

**انتظار قابل آزمون:** ۰ و ۰٫۰۰ صفر بمانند؛ null یا not-measured عدد ساختگی نشود؛ حجم نامعلوم از جمع واحدها پنهانی صفر نشود.

**حد اثبات فعلی:** آزمون‌های منتخب unset موفق؛ پوشش همه مسیرهای FILE1/مرورگر ادعا نمی‌شود

**شواهد مستقیم:** [apps/api/core/field_reports/daily_report_views.py:332](../../apps/api/core/field_reports/daily_report_views.py#L332)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:625](../../apps/api/core/field_reports/shiraz_file4_excel.py#L625)؛ [specs/036-validation-codes-unset-semantics/spec.md:84](../../specs/036-validation-codes-unset-semantics/spec.md#L84)

### D06 — نیروی انسانی مستقیم/غیرمستقیم، پیمانکار، شیفت، مرخصی و اضافه‌کاری

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** مدل و تجمیع دسته، شغل، پیمانکار و شمارش شیفت‌ها را نگه می‌دارند؛ SUM در Excel وجود دارد.

**باقیمانده:** تطبیق مقادیر واقعی، مرخصی اختیاری و عنوان واحد شمارش؛ عدم فرض نفر یکتا.

**انتظار قابل آزمون:** یک عنوان نزد دو پیمانکار در داده منبع جدا بماند؛ جمع هر ستون با مرجع برابر شود.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:340](../../apps/api/core/field_reports/models.py#L340)؛ [apps/api/core/field_reports/services/daily_report_aggregation.py:559](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L559)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:247](../../apps/api/core/field_reports/shiraz_file4_excel.py#L247)

### D07 — قاعده نفرساعت و تمایز نفر، نفرشیفت، نفرروز و جمع ردیف‌ها

**وضعیت:** ناقص · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** فیلد ساعت و قاعده template و ledger در مسیرهای تخصصی وجود دارد؛ Excel نیروی انسانی نفرشیفت را برچسب می‌زند.

**باقیمانده:** تثبیت معنای شمارش برای هر خروجی؛ عنوان نفرروز در نوار activity log بدون اثبات حضور یکتا اصلاح شود.

**انتظار قابل آزمون:** هیچ جمع headcount روی فعالیت‌ها به‌عنوان تعداد افراد یکتا معرفی نشود؛ نفرساعت از مدت واقعی شیفت بیاید.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:340](../../apps/api/core/field_reports/models.py#L340)؛ [apps/web/src/app/routes/project-activity-log.tsx:129](../../apps/web/src/app/routes/project-activity-log.tsx#L129)؛ [specs/033-daily-sections-grid/spec.md:196](../../specs/033-daily-sections-grid/spec.md#L196)

### D08 — کاتالوگ شغل نسخه‌دار، ترتیب پروژه و نگاشت فرم ۳۴/۳۲

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** زیرساخت catalog/template موجود است؛ خروجی FILE4 ابتدا لیست ثابت ۳۴/۳۲ و سپس عنوان‌های اضافه را می‌چیند.

**باقیمانده:** جداسازی پروفایل فرم شیراز از حقیقت عمومی پروژه؛ رعایت ترتیب و نگاشت عنوان‌های تاریخی/اختصاصی.

**انتظار قابل آزمون:** تغییر template عنوان یا داده تاریخی را حذف نکند؛ فرم شیراز فقط در پروفایل مصوب ۳۴/۳۲ باشد.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:247](../../apps/api/core/field_reports/shiraz_file4_excel.py#L247)؛ [specs/033-daily-sections-grid/spec.md:198](../../specs/033-daily-sections-grid/spec.md#L198)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:182](../../specs/044-shiraz-excel-parity-pdf/spec.md#L182)

### D09 — ماشین‌آلات: هویت یکتا، پنج وضعیت، ساعات و دلیل توقف

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** مدل و تجمیع وضعیت/ساعت/هویت و قواعد توقف و سقف ۲۴ ساعت وجود دارد.

**باقیمانده:** کنترل روز واقعی، دو واحد گزارش‌دهنده یک تجهیز و خطاهای دوزبانه در UI.

**انتظار قابل آزمون:** تجهیز با شناسه پایدار یک‌بار شمرده شود؛ توقف بدون دلیل و زمان بیش از ۲۴ ساعت رد شود.

**حد اثبات فعلی:** آزمون‌های منتخب machinery_derivation در بسته ۶۹تایی موفق

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:636](../../apps/api/core/field_reports/models.py#L636)؛ [apps/api/core/field_reports/services/daily_report_aggregation.py:559](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L559)؛ [specs/033-daily-sections-grid/spec.md:204](../../specs/033-daily-sections-grid/spec.md#L204)

### D10 — ساعت نامعلوم ماشین‌آلات در خروجی legacy

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** مسیر تجمیعی جدید nullable را حفظ می‌کند؛ شاخه equipment قدیمی در Excel مقدار None را ۰ می‌نویسد؛ PDF خط تیره می‌دهد.

**باقیمانده:** همسان‌سازی معنای null/صفر در شاخه legacy یا تعیین بازنشستگی رسمی آن بدون تغییر تاریخچه.

**انتظار قابل آزمون:** None در هر دو فایل نامعلوم باشد؛ صفر صریح عدد ۰ بماند.

**حد اثبات فعلی:** نقص اجرایی strict XFAIL؛ کنترل مستقل صفر صریح موفق

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:614](../../apps/api/core/field_reports/shiraz_file4_excel.py#L614)؛ [apps/api/core/field_reports/pdf.py:212](../../apps/api/core/field_reports/pdf.py#L212)

### D11 — مصالح وارده واقعی در جدول اصلی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** تمایز رسید واقعی و ردیف عمومی و نمایش دریافت در جدول اصلی وجود دارد.

**باقیمانده:** تطبیق نوع سند، واحد و مقدار روی روز مرجع.

**انتظار قابل آزمون:** مصرف/برگشت/ضایعات به‌عنوان رسید واقعی نمایش داده نشوند.

**حد اثبات فعلی:** آزمون‌های منتخب material reconciliation موفق

**شواهد مستقیم:** [apps/api/core/field_reports/services/daily_report_aggregation.py:1193](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L1193)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:417](../../apps/api/core/field_reports/shiraz_file4_excel.py#L417)؛ [specs/033-daily-sections-grid/spec.md:213](../../specs/033-daily-sections-grid/spec.md#L213)

### D12 — مصرف، برگشت، ضایعات و مغایرت با سند معین انبار

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** جزئیات و reconciliation دارای match/mismatch/insufficient-data با مرجع سند انبار وجود دارند.

**باقیمانده:** آزمون گردش کامل سند واقعی و پیوند قابل مشاهده از گزارش؛ بازطراحی کل انبار در A.1 نیست.

**انتظار قابل آزمون:** مقایسه با سند ارجاع‌شده باشد؛ مانده تاریخی کلی جانشین سند نشود.

**حد اثبات فعلی:** آزمون‌های منتخب سندمحور موفق؛ پذیرش گردش واقعی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/daily_report_views.py:542](../../apps/api/core/field_reports/daily_report_views.py#L542)؛ [apps/api/core/field_reports/daily_report_views.py:548](../../apps/api/core/field_reports/daily_report_views.py#L548)؛ [specs/033-daily-sections-grid/spec.md:216](../../specs/033-daily-sections-grid/spec.md#L216)

### D13 — بتن‌ریزی و جزئیات نمونه‌برداری/کیفیت

**وضعیت:** ناقص · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** داده تخصصی بتن و QC در کد هست؛ Excel/PDF روزانه فقط بخشی از اطلاعات پایه را چاپ می‌کنند.

**باقیمانده:** تعیین ستون‌های چاپی الزامی و مسیر drill-down برای بچینگ، کامیون، نمونه، آزمایش و محل دقیق؛ سپس تطبیق.

**انتظار قابل آزمون:** حجم و محل برابر مرجع؛ هر نمونه‌برداری با نتیجه/بازرسی مربوط قابل ردیابی باشد.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:476](../../apps/api/core/field_reports/shiraz_file4_excel.py#L476)؛ [apps/api/core/field_reports/pdf.py:250](../../apps/api/core/field_reports/pdf.py#L250)؛ [specs/033-daily-sections-grid/spec.md:222](../../specs/033-daily-sections-grid/spec.md#L222)

### D14 — فعالیت عمومی، موانع و دستورکار با مسئول و موعد

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** ردیف‌های ساخت‌یافته عمومی، مسائل، مسئول و سررسید و ترتیب/منبع در مدل و تجمیع هستند.

**باقیمانده:** تطبیق متن چندخطی و ترتیب در خروجی؛ آزمون عدم تبدیل یادداشت ساده به مسئله.

**انتظار قابل آزمون:** ردیف ساخت‌یافته در بازسازی به متن قالب‌بندی‌شده تبدیل نشود؛ مالک و موعد مانع محفوظ باشد.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:699](../../apps/api/core/field_reports/shiraz_file4_excel.py#L699)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:716](../../apps/api/core/field_reports/shiraz_file4_excel.py#L716)؛ [specs/033-daily-sections-grid/spec.md:228](../../specs/033-daily-sections-grid/spec.md#L228)

### D15 — حوادث HSE، شدت، اقدام فوری و پیگیری

**وضعیت:** ناقص · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** حادثه و شدت و مسیر پیگیری در کد وجود دارد؛ نمایش Excel از جمله Major انگلیسی است.

**باقیمانده:** هماهنگ‌سازی واژگان فارسی/انگلیسی خروجی و اثبات ایجاد اعلان/پیگیری واقعی در سناریو.

**انتظار قابل آزمون:** شدت و اقدام فوری از منبع بیایند؛ کار پیگیری و مسئول/موعد قابل مشاهده باشد.

**حد اثبات فعلی:** بازبینی مستقیم؛ وجود مسیر اعلان معادل تحویل واقعی اعلان نیست

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:723](../../apps/api/core/field_reports/shiraz_file4_excel.py#L723)؛ [specs/033-daily-sections-grid/spec.md:231](../../specs/033-daily-sections-grid/spec.md#L231)

### D16 — بازدیدها و جلسات روزانه ساخت‌یافته

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** ردیف بازدید با منبع و تاریخ/ترتیب و انتقال به خلاصه موجود است.

**باقیمانده:** تطبیق بازدید روز مرجع؛ اتصال کامل مدیریت جلسات/مصوبات در A.3.C جداست.

**انتظار قابل آزمون:** انتقال چند واحد ترتیب و منبع را حفظ کند؛ متن جلسه با مصوبه رسمی خلط نشود.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:723](../../apps/api/core/field_reports/shiraz_file4_excel.py#L723)؛ [specs/033-daily-sections-grid/spec.md:229](../../specs/033-daily-sections-grid/spec.md#L229)

### D17 — عکس و پیوست فعالیت، محدودیت نوع/اندازه و انتساب پروژه

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** وابستگی A.1 / عملیات A.8

**آنچه موجود است:** قواعد JPEG/PNG تا ۱۰MB و ارتباط منبع/فعالیت و پیوند بخش‌ها در پیاده‌سازی وجود دارد.

**باقیمانده:** تست upload واقعی و پروژه دیگر، MIME جعلی، تاریخ ثبت و بازیابی از هر بخش در مرورگر.

**انتظار قابل آزمون:** ZIP/EXE/فایل جعلی یا بزرگ رد؛ فایل پروژه دیگر متصل نشود؛ گالری بزرگ چاپی الزام خودکار نیست.

**حد اثبات فعلی:** بازبینی کد؛ ذخیره‌سازی و مرورگر پیوست این نوبت اجرا نشده

**شواهد مستقیم:** [apps/api/core/sub_reports/services/attachments.py:28](../../apps/api/core/sub_reports/services/attachments.py#L28)؛ [apps/api/core/field_reports/serializers.py:1439](../../apps/api/core/field_reports/serializers.py#L1439)؛ [specs/033-daily-sections-grid/spec.md:236](../../specs/033-daily-sections-grid/spec.md#L236)

### W01 — گردش draft، submit/review، approve/reject و قفل رسمی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** مراحل، کنشگرها، زمان‌ها، کدهای خطای وضعیت/رد و قفل approved وجود دارند.

**باقیمانده:** UAT با تهیه‌کننده، ناظر و تأییدکننده واقعی؛ بررسی SoD و همه مسیرهای جایگزین.

**انتظار قابل آزمون:** حالت نامعتبر رد شود؛ دلیل رد حداقل ۱۰ کاراکتر؛ کاربر ممنوع نتواند تأیید کند.

**حد اثبات فعلی:** آزمون‌های منتخب workflow/status و validation موفق؛ ماتریس کامل نقش‌ها اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/services/__init__.py:28](../../apps/api/core/field_reports/services/__init__.py#L28)؛ [apps/api/core/field_reports/daily_report_views.py:332](../../apps/api/core/field_reports/daily_report_views.py#L332)؛ [specs/036-validation-codes-unset-semantics/spec.md:79](../../specs/036-validation-codes-unset-semantics/spec.md#L79)

### W02 — اصلاحیه، نسخه‌بندی، دلیل، لغو و بازگشت به نسخه قبلی

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** ساخت draft بعدی، دلیل، انتقال فرزندان، تاریخچه و لغو وجود دارند؛ قرارداد قبلی آزمون دارد.

**باقیمانده:** تکمیل انتقال هویت تجمیعی، مجموعه کامل provenance و متادیتای مالک خلاصه؛ بازآزمایی لغو/تأیید نسخه.

**انتظار قابل آزمون:** نسخه جدید هیچ داده/منبع معتبر را گم نکند؛ اصلاح همزمان تکراری نشود؛ لغو نسخه approved قبلی را بازگرداند.

**حد اثبات فعلی:** آزمون‌های قدیمی اصلاحیه موفق؛ سه نقص تازه در انتقال معنای خلاصه بازتولید شد

**شواهد مستقیم:** [apps/api/core/field_reports/services/correction_service.py:138](../../apps/api/core/field_reports/services/correction_service.py#L138)؛ [specs/035-correction-lineage-cloning/spec.md:89](../../specs/035-correction-lineage-cloning/spec.md#L89)

### W03 — قفل داده مشتق پس از اصلاحیه و منع ویرایش مستقیم

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** قفل روی گزارش auto فعال است؛ نسخه اصلاحی ساخته‌شده این پرچم را حفظ نمی‌کند.

**باقیمانده:** حفظ هویت تجمیعی و قفل‌کردن بر اساس مالکیت داده در تمام child/batch paths؛ اصلاح فقط در واحد منبع.

**انتظار قابل آزمون:** POST/PATCH/DELETE ردیف مشتق نسخه اصلاحی هم رد شود؛ جزئیات مجاز مدیریت قابل ویرایش بماند.

**حد اثبات فعلی:** نقص اجرایی: PATCH موفق و ذخیره‌شده روی ردیف derived؛ correction-write-probe.json

**شواهد مستقیم:** [apps/api/core/field_reports/services/correction_service.py:138](../../apps/api/core/field_reports/services/correction_service.py#L138)؛ [apps/api/core/field_reports/daily_report_views.py:618](../../apps/api/core/field_reports/daily_report_views.py#L618)

### W04 — منبع ردیف و مجموعه کامل منابع مقادیر تجمیعی

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** DailyReportDerivedSource و drill-down برای خلاصه اصلی موجودند؛ اصلاحیه این رکوردها را کپی/بازنگاشت نمی‌کند.

**باقیمانده:** بازنگاشت منبع به شناسه ردیف نسخه جدید و حفظ تمام منابع، نه فقط source FK تک‌ردیفی.

**انتظار قابل آزمون:** جمع دو منبع در هر نسخه هر دو منبع را نشان دهد؛ اصلاح/لغو هیچ منبعی را گم نکند.

**حد اثبات فعلی:** نقص اجرایی: ۲ رکورد provenance در مبدأ و ۰ در نسخه اصلاحی

**شواهد مستقیم:** [apps/api/core/field_reports/services/correction_service.py:138](../../apps/api/core/field_reports/services/correction_service.py#L138)؛ [apps/api/core/field_reports/serializers.py:100](../../apps/api/core/field_reports/serializers.py#L100)؛ [specs/032-unit-report-source-truth/spec.md:180](../../specs/032-unit-report-source-truth/spec.md#L180)

### W05 — نظر مدیریت، override هوا/تعطیلی و اطلاعات مالک خلاصه در اصلاح

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** بازسازی معمول نظر/override را حفظ می‌کند؛ clone اصلاحیه management_opinion و weather_override را از دست می‌دهد.

**باقیمانده:** حفظ و تعیین سیاست تمام metadata مالک خلاصه، config/fingerprint/aggregation metadata؛ سازگاری با snapshot نسخه.

**انتظار قابل آزمون:** اصلاح/لغو/تأیید مجدد نظر و override مجاز را عیناً حفظ کند؛ مقادیر مشتق دوباره دستی نشوند.

**حد اثبات فعلی:** نقص اجرایی نظر و weather_override بازتولید؛ بقیه metadata در کد مشکوک و نیازمند تست دقیق

**شواهد مستقیم:** [apps/api/core/field_reports/services/correction_service.py:138](../../apps/api/core/field_reports/services/correction_service.py#L138)؛ [apps/api/core/field_reports/services/daily_report_aggregation.py:559](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L559)؛ [specs/032-unit-report-source-truth/spec.md:184](../../specs/032-unit-report-source-truth/spec.md#L184)

### W06 — نسخه رسمی ثابت و تشخیص تفاوت با منابع جاری

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** snapshot مصوب حفظ و در خروجی مقایسه/هشدار منبع نمایش داده می‌شود؛ زمان ثبت و تأیید جدا هستند.

**باقیمانده:** تطبیق نسخه دانلودشده با نسخه مصوب و اصلاح‌شده؛ قاعده وضعیت مبنای گزارش رسمی مستند شود.

**انتظار قابل آزمون:** تغییر منبع بدون اصلاح رسمی محتوای snapshot تأییدشده را پنهانی عوض نکند.

**حد اثبات فعلی:** آزمون‌های منتخب summary_snapshot_comparison موفق

**شواهد مستقیم:** [apps/api/core/field_reports/services/daily_report_aggregation.py:593](../../apps/api/core/field_reports/services/daily_report_aggregation.py#L593)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:132](../../apps/api/core/field_reports/shiraz_file4_excel.py#L132)؛ [apps/api/core/field_reports/pdf.py:117](../../apps/api/core/field_reports/pdf.py#L117)

### E01 — دانلود FILE4 با RTL، فونت فارسی و بخش‌های اصلی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** سازنده Excel، endpoint مجاز و بخش‌های اصلی فعال هستند؛ فایل کنترل تولید شد.

**باقیمانده:** تطبیق کامل با مرجع مستقل و اصلاح اختلاف‌های E02 تا E04.

**انتظار قابل آزمون:** xlsx سالم، فارسی خوانا و همه بخش‌های مورد توافق با مقدار درست دانلود شوند.

**حد اثبات فعلی:** آزمون‌های منتخب FILE4 موفق؛ این وضعیت معادل برابری کامل فرم نیست

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:124](../../apps/api/core/field_reports/shiraz_file4_excel.py#L124)؛ [apps/api/core/field_reports/daily_report_views.py:435](../../apps/api/core/field_reports/daily_report_views.py#L435)

### E02 — انطباق چیدمان و فیلدهای FILE4 با فرم واقعی شیراز

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** بخش‌های اصلی موجودند؛ خروجی فعلی جدول‌های روی‌هم دارد، فرم واقعی نیروی مستقیم/غیرمستقیم را کنار هم می‌چیند.

**باقیمانده:** تعیین و اجرای معیار برابری ساختاری/چاپی؛ ساعت شیفت و شماره رسمی، عنوان‌ها و ترتیب ستون‌ها روشن شوند.

**انتظار قابل آزمون:** بازبین با مقایسه کنارهم محل و مقدار هر فیلد مصوب را بدون نگاشت مبهم پیدا کند.

**حد اثبات فعلی:** مقایسه ساختار workbook مرجع با خروجی کنترل؛ تطبیق عددی یک روز کامل انجام نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:162](../../apps/api/core/field_reports/shiraz_file4_excel.py#L162)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:247](../../apps/api/core/field_reports/shiraz_file4_excel.py#L247)؛ [docs/delivery/R0-scope-and-reports-contract.md:30](../../docs/delivery/R0-scope-and-reports-contract.md#L30)

### E03 — فرمول‌های بومی جمع و بازحساب در نرم‌افزار مستقل

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** فرمول SUM و جمع کل در xlsx نوشته می‌شوند و تست ساختار دارند.

**باقیمانده:** بازحساب واقعی با Excel یا موتور سازگار و کنترل مقادیر cache/خطا؛ صرف نوشتن فرمول کافی نیست.

**انتظار قابل آزمون:** جمع کنترل‌شده برابر مرجع و بدون #REF/#VALUE/#NAME باشد؛ فرمول بر داده خالی صفر ساختگی نسازد.

**حد اثبات فعلی:** وجود فرمول در آزمون تأیید؛ recalc مستقل این نوبت اجرا نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:247](../../apps/api/core/field_reports/shiraz_file4_excel.py#L247)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:219](../../specs/044-shiraz-excel-parity-pdf/spec.md#L219)

### E04 — چاپ Excel و PDF برای متن بلند و بیش از ۵۰ ردیف

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** PDF صفحه‌بندی دارد؛ Excel عرض ستون را محدود می‌کند اما print area/fit/repeat headers و ارتفاع پویا تنظیم نشده‌اند.

**باقیمانده:** تنظیم چاپ، شکست صفحه، تکرار عنوان و wrap/ارتفاع؛ بازبینی بصری همه صفحات و امضاها.

**انتظار قابل آزمون:** هیچ متن/عدد بریده نشود؛ عنوان‌ها در صفحات بعد خوانا و امضا آخرین صفحه باشد.

**حد اثبات فعلی:** ساختار نمونه Excel فاقد print area/orientation؛ PDF بلند مستقل بصری این نوبت بررسی نشده

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:763](../../apps/api/core/field_reports/shiraz_file4_excel.py#L763)؛ [apps/api/core/field_reports/pdf.py:83](../../apps/api/core/field_reports/pdf.py#L83)

### E05 — PDF روزانه، نام فایل و محتوای بخش‌ها

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** PDF فارسی با هدر، فعالیت، منابع، یادداشت و نظر مدیریت و نام قراردادی تولید می‌شود.

**باقیمانده:** تطبیق ارقام و فیلدهای الزامی با Excel و مرجع؛ جزئیات بتن و شیفت طبق قرارداد.

**انتظار قابل آزمون:** نام daily-report-{date}-{shift}.pdf و محتوای نسخه یکسان باشد.

**حد اثبات فعلی:** آزمون‌های منتخب PDF summary parity موفق؛ برابر بودن با مرجع واقعی هنوز اثبات نشده

**شواهد مستقیم:** [apps/api/core/field_reports/pdf.py:83](../../apps/api/core/field_reports/pdf.py#L83)؛ [apps/api/core/field_reports/daily_report_views.py:423](../../apps/api/core/field_reports/daily_report_views.py#L423)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:189](../../specs/044-shiraz-excel-parity-pdf/spec.md#L189)

### E06 — واترمارک تمام صفحات پیش‌نویس و حذف آن از نسخه مصوب

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** وضعیت غیرapproved واترمارک و approved حذف آن دارد.

**باقیمانده:** بازبینی بصری PDF چندصفحه‌ای برای هر حالت و نسخه اصلاحی.

**انتظار قابل آزمون:** تمام صفحات غیرمصوب نشانه پیش‌نویس داشته باشند؛ نسخه مصوب نشان پیش‌نویس نداشته باشد.

**حد اثبات فعلی:** آزمون‌های منتخب watermark/signatures موفق؛ بررسی بصری مستقل همه حالت‌ها انجام نشده

**شواهد مستقیم:** [apps/api/core/field_reports/pdf.py:298](../../apps/api/core/field_reports/pdf.py#L298)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:190](../../specs/044-shiraz-excel-parity-pdf/spec.md#L190)

### E07 — سه جای امضای واقعی، سمت کنشگر و زمان محلی خوانا

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** نام کنشگر و زمان در سه جای امضای آخر فایل هست؛ سمت/نقش واقعی در خروجی چاپ نشده.

**باقیمانده:** افزودن نقش مصوب/واقعی؛ بررسی تقویم/منطقه زمانی و مسیر تأیید مستقیم بدون ساخت ناظر جعلی.

**انتظار قابل آزمون:** کنشگر واقعی همراه سمت و زمان قابل فهم؛ مرحله طی‌نشده نام یا امضای ساختگی نگیرد.

**حد اثبات فعلی:** نام/زمان در آزمون‌های منتخب؛ نبود نقش از کد؛ اشکال منطقه زمانی بازتولید نشده

**شواهد مستقیم:** [apps/api/core/field_reports/pdf.py:338](../../apps/api/core/field_reports/pdf.py#L338)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:192](../../specs/044-shiraz-excel-parity-pdf/spec.md#L192)

### E08 — شناسه صحت مبتنی بر متادیتا و حدود ادعای امضای دیجیتال

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** fingerprint قطعی از شناسه/lineage/روز/شیفت/وضعیت/کنش تأیید چاپ می‌شود.

**باقیمانده:** در تحویل صریحاً متادیتایی بودن هش توضیح داده شود؛ اگر امضای کل محتوا/PKI خواسته شود قرارداد جدید لازم است.

**انتظار قابل آزمون:** metadata برابر هش برابر دهد؛ این نشان به‌عنوان اثبات عدم تغییر همه مقادیر یا امضای گواهی‌دار معرفی نشود.

**حد اثبات فعلی:** آزمون مشخصه موفق: تغییر quantity هش را عوض نکرد؛ تغییر status عوض کرد؛ این خود نقض FR015 نیست

**شواهد مستقیم:** [apps/api/core/field_reports/pdf.py:316](../../apps/api/core/field_reports/pdf.py#L316)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:196](../../specs/044-shiraz-excel-parity-pdf/spec.md#L196)

### E09 — مجوز مشاهده و دانلود و جلوگیری از نشت بین پروژه‌ها

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** endpointهای خروجی و عضویت/مجوز view_reports وجود دارند و تست منتخب دارند.

**باقیمانده:** ماتریس کامل نقش مجاز/غیرمجاز/کاربر پروژه دیگر در API و مرورگر روی همان نسخه تحویل.

**انتظار قابل آزمون:** کاربر غیرمجاز نتواند با ID مستقیم گزارش یا فایل را بگیرد؛ viewer مجاز بتواند دانلود کند.

**حد اثبات فعلی:** بخشی از آزمون مجوز در بسته‌های موفق؛ پوشش منفی کامل و استقرار زنده اثبات نشده

**شواهد مستقیم:** [apps/api/core/field_reports/daily_report_views.py:423](../../apps/api/core/field_reports/daily_report_views.py#L423)؛ [apps/api/core/field_reports/daily_report_views.py:435](../../apps/api/core/field_reports/daily_report_views.py#L435)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:188](../../specs/044-shiraz-excel-parity-pdf/spec.md#L188)

### E10 — FILE5 ابنیه و FILE6 برق با درصد عددی و ستون‌های تخصصی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** مرتبط با A.1؛ ورود داده در A.8

**آنچه موجود است:** هر دو Excel تخصصی و دکمه/endpoint واحد وجود دارند؛ درصد عددی 0.0%، درصد نامعلوم خالی؛ برق فاقد قطعه/درصد است.

**باقیمانده:** تطبیق تخصصی با فایل واقعی و کنترل مسیر دسترسی؛ تعیین ابهام PDF زیرگزارش.

**انتظار قابل آزمون:** ابنیه درصد ۰ تا ۱۰۰ به فرمت درصد صحیح؛ برق ستون ابنیه اضافه نداشته باشد.

**حد اثبات فعلی:** آزمون‌های منتخب subreport Excel موفق؛ گردش واقعی مرورگری اجرا نشده

**شواهد مستقیم:** [apps/api/core/sub_reports/shiraz_subreport_excel.py:1](../../apps/api/core/sub_reports/shiraz_subreport_excel.py#L1)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:185](../../specs/044-shiraz-excel-parity-pdf/spec.md#L185)

### E11 — دفتر فعالیت‌ها و FILE1 با تمام نتیجه فیلتر

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** پشتیبان A.1 / عملیات A.8

**آنچه موجود است:** API دفتر فعالیت و خروجی Excel کامل queryset فیلترشده وجود دارند.

**باقیمانده:** رفع نسخه‌های تاریخی و جمع کل در E14/E15؛ تثبیت معیار measured/نامعلوم در داده legacy.

**انتظار قابل آزمون:** تمام ردیف‌های نتیجه فیلتر، مستقل از صفحه، با همان ستون‌ها صادر شوند.

**حد اثبات فعلی:** آزمون‌های منتخب FILE1 موفق؛ نقص‌های دامنه نتیجه جدا بازتولید شده

**شواهد مستقیم:** [apps/api/core/field_reports/report_views.py:89](../../apps/api/core/field_reports/report_views.py#L89)؛ [apps/api/core/field_reports/shiraz_file1_excel.py:1](../../apps/api/core/field_reports/shiraz_file1_excel.py#L1)

### E12 — فیلترهای کامل فهرست گزارش روزانه و URL

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** فهرست روزانه date_from/date_to/status/page دارد؛ discipline/contractor/block در UI و queryset این مسیر مشاهده نشد.

**باقیمانده:** پیاده‌سازی/تثبیت معنای سه فیلتر مفقود برای یک خلاصه چندواحدی؛ اتصال UI/API/URL و دانلود.

**انتظار قابل آزمون:** URL اشتراکی تمام فیلترهای FR016 را با نتیجه یکسان بازسازد.

**حد اثبات فعلی:** نقص با بازبینی UI و backend؛ سناریوی مرورگر اجرا نشده

**شواهد مستقیم:** [apps/web/src/app/routes/daily-reports-list.tsx:91](../../apps/web/src/app/routes/daily-reports-list.tsx#L91)؛ [apps/api/core/field_reports/daily_report_views.py:153](../../apps/api/core/field_reports/daily_report_views.py#L153)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:197](../../specs/044-shiraz-excel-parity-pdf/spec.md#L197)

### E13 — فیلتر چندبعدی دفتر فعالیت و بازگردانی URL

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** پشتیبان A.1 / عملیات A.8

**آنچه موجود است:** date/disc/parcel/zone/block/subcontractor/page در URL و query وجود دارند.

**باقیمانده:** UAT لینک مشترک، refresh، بازگشت مرورگر و یکسانی download؛ replace:true می‌تواند تاریخچه را محدود کند.

**انتظار قابل آزمون:** دو عضو مجاز با URL یکسان ورودی‌ها، صفحه و مجموعه نتیجه یکسان ببینند.

**حد اثبات فعلی:** وجود پیاده‌سازی؛ ریسک history مشاهده کدی است و نقص اجرایی اثبات‌شده نامیده نمی‌شود

**شواهد مستقیم:** [apps/web/src/app/routes/project-activity-log.tsx:1](../../apps/web/src/app/routes/project-activity-log.tsx#L1)؛ [specs/044-shiraz-excel-parity-pdf/spec.md:198](../../specs/044-shiraz-excel-parity-pdf/spec.md#L198)

### E14 — جمع کل دفتر فعالیت روی تمام نتیجه فیلتر، جدا به تفکیک واحد

**وضعیت:** ناقص · **فاز مالک/اثر:** پشتیبان A.1 / عملیات A.8

**آنچه موجود است:** UI جمع headcount و quantity را از data.results همان صفحه می‌گیرد؛ API aggregate کل نمی‌دهد.

**باقیمانده:** محاسبه کل سمت سرور با همان فیلتر و قواعد null/measured؛ اصلاح عنوان نفرروز مطابق D07.

**انتظار قابل آزمون:** برای ۵۱ ردیف و صفحه ۵۰تایی جمع کل ۵۱ باشد و با خروجی کل برابر؛ m2 با m3 جمع نشود.

**حد اثبات فعلی:** نقص اجرایی: count=51، results=50 و جمع صفحه=50؛ pagination-probe.json

**شواهد مستقیم:** [apps/web/src/app/routes/project-activity-log.tsx:129](../../apps/web/src/app/routes/project-activity-log.tsx#L129)؛ [apps/api/core/field_reports/report_views.py:89](../../apps/api/core/field_reports/report_views.py#L89)

### E15 — نسخه جاری در دفتر رسمی؛ تاریخچه جدا از جمع عملیاتی

**وضعیت:** ناقص · **فاز مالک/اثر:** پشتیبان A.1 / عملیات A.8

**آنچه موجود است:** query وضعیت approved را اعمال می‌کند اما is_current را نه؛ نسخه قدیمی approved هم وارد می‌شود.

**باقیمانده:** فیلتر نسخه جاری برای دفتر عملیاتی و سیاست نمایش تاریخچه مستقل؛ کنترل پس از اصلاح/لغو.

**انتظار قابل آزمون:** دو نسخه ۵ واحدی یک فعالیت، جمع رسمی ۵ بدهند نه ۱۰؛ سابقه همچنان قابل دسترس بماند.

**حد اثبات فعلی:** نقص اجرایی: ۲ ردیف، quantity=10 و headcount=8 در برابر ۱ ردیف،۵ و۴

**شواهد مستقیم:** [apps/api/core/field_reports/services/activity_log.py:9](../../apps/api/core/field_reports/services/activity_log.py#L9)؛ [specs/032-unit-report-source-truth/spec.md:163](../../specs/032-unit-report-source-truth/spec.md#L163)

### E16 — امنیت محتوای سلول‌های Excel و متن فارسی/چندخطی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** literalize_cell در خروجی‌های Excel برای جلوگیری از فرمول‌شدن متن وجود دارد.

**باقیمانده:** حفظ پوشش متن‌های شروع‌شونده با =,+,-,@ و فارسی/انگلیسی در نمونه پذیرش.

**انتظار قابل آزمون:** ورودی کاربر به‌عنوان متن ذخیره شود؛ فرمول‌های محاسباتی داخلی سالم بمانند.

**حد اثبات فعلی:** آزمون‌های منتخب export موفق؛ ارزیابی امنیت جامع کل محصول انجام نشده

**شواهد مستقیم:** [apps/api/core/field_reports/excel_safety.py:1](../../apps/api/core/field_reports/excel_safety.py#L1)؛ [apps/api/core/field_reports/shiraz_file4_excel.py:124](../../apps/api/core/field_reports/shiraz_file4_excel.py#L124)

### E17 — دامنه فایل چندشیته تاریخی در مقابل خروجی یک روز

**وضعیت:** نیازمند تثبیت قرارداد · **فاز مالک/اثر:** A.1

**آنچه موجود است:** هر فراخوانی FILE4 یک شیت روزانه می‌سازد؛ مرجع ۱۰۹/۳۶۷ شیت و R0 واژه چندشیته دارد.

**باقیمانده:** ثبت تصمیم: تک‌روز در A.1 طبق برنامه یا workbook بازه/کل تاریخ؛ بدون فرض خودکار مهاجرت همه شیت‌ها.

**انتظار قابل آزمون:** دامنه فایل و تعداد شیت در قرارداد خروجی روشن و همان حالت آزموده شود.

**حد اثبات فعلی:** نمونه کنترل یک شیت؛ metadata مرجع واقعی خوانده شد

**شواهد مستقیم:** [apps/api/core/field_reports/shiraz_file4_excel.py:132](../../apps/api/core/field_reports/shiraz_file4_excel.py#L132)؛ [docs/delivery/R0-scope-and-reports-contract.md:46](../../docs/delivery/R0-scope-and-reports-contract.md#L46)؛ [output/delivery-plan-2026-11-03/delivery-plan.md:107](../delivery-plan-2026-11-03/delivery-plan.md#L107)

### Q01 — روز مرجع کامل و نگاشت مستقل همه داده‌ها

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** فایل‌های واقعی در real-data ثبت شده‌اند؛ آزمون‌های واحد و sample کنترل موجودند.

**باقیمانده:** انتخاب یک روز کامل با ارقام کنترل‌شده تمام بخش‌ها و ساخت expected مستقل از builder/aggregation.

**انتظار قابل آزمون:** برای هر مقدار خروجی، سلول یا سند منبع، واحد، تبدیل و انتظار ثبت شود؛ اختلاف باز صفر.

**حد اثبات فعلی:** گواه تطبیق مستقل کامل یک روز و پذیرش کارفرما در بررسی حاضر احراز نشد؛ نبودش در کل دنیا ادعا نمی‌شود

**شواهد مستقیم:** [docs/delivery/R0-scope-and-reports-contract.md:30](../../docs/delivery/R0-scope-and-reports-contract.md#L30)؛ [output/delivery-plan-2026-11-03/delivery-plan.md:107](../delivery-plan-2026-11-03/delivery-plan.md#L107)

### Q02 — معیار سرعت دانلود و زمان انجام کار توسط کاربر

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** تولید فایل در آزمون کار می‌کند؛ معیار ۳ ثانیه دانلود و معیارهای usability در specs وجود دارند.

**باقیمانده:** اندازه‌گیری روی همان release و روز معمول ۱۵–۳۰ فعالیت و ۲۰ ردیف منابع؛ تجربه کاربران فارسی/انگلیسی.

**انتظار قابل آزمون:** دانلود معمول زیر ۳ ثانیه طبق معیار توافق‌شده؛ نرخ موفقیت/زمان کاربر با شاهد ثبت شود.

**حد اثبات فعلی:** سنجش کارایی/کاربر این نوبت اجرا نشده؛ زمان pytest معیار دانلود نیست

**شواهد مستقیم:** [specs/044-shiraz-excel-parity-pdf/spec.md:220](../../specs/044-shiraz-excel-parity-pdf/spec.md#L220)؛ [specs/028-auto-daily-report-summary/spec.md:139](../../specs/028-auto-daily-report-summary/spec.md#L139)

### Q03 — پذیرش مرورگری دسکتاپ/موبایل و فارسی/انگلیسی

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** UI و سناریوهای E2E/گزارش‌های قبلی وجود دارند.

**باقیمانده:** اجرای تازه از ثبت واحد تا تجمیع، اصلاح، مشاهده نسخه و دانلود با نقش‌های واقعی و اندازه موبایل.

**انتظار قابل آزمون:** مسیرهای لازم بدون خطای UI، داده گمشده و دورزدن مجوز در هر دو زبان کامل شوند.

**حد اثبات فعلی:** گزارش‌های قدیمی صرفاً تاریخی؛ در این ممیزی اجرای تازه مرورگر انجام نشده

**شواهد مستقیم:** [specs/007-daily-report-gaps/spec.md:130](../../specs/007-daily-report-gaps/spec.md#L130)؛ [specs/033-daily-sections-grid/verification-report.md:1](../../specs/033-daily-sections-grid/verification-report.md#L1)

### Q04 — راهنمای مسیرها و درخت تصمیم مطابق رفتار واقعی

**وضعیت:** پیاده‌سازی موجود · **فاز مالک/اثر:** A.1

**آنچه موجود است:** سندهای مسیر کاربر و تصمیم‌گیری برای دانلودها وجود دارند.

**باقیمانده:** تطبیق همه لینک‌ها و gateهای نقش با نسخه نهایی و حذف ادعای امضای گواهی‌دار اثبات‌نشده.

**انتظار قابل آزمون:** هر اقدام خروجی از مسیر واقعی و مجوز درست به فایل صحیح برسد؛ لینک شکسته صفر.

**حد اثبات فعلی:** وجود docs بررسی شده؛ ممیزی کامل همه لینک‌ها این نوبت انجام نشده

**شواهد مستقیم:** [specs/044-shiraz-excel-parity-pdf/spec.md:201](../../specs/044-shiraz-excel-parity-pdf/spec.md#L201)؛ [docs/decision-tree/README.md:1](../../docs/decision-tree/README.md#L1)

### Q05 — بسته تحویل همان نسخه، راهنمای آزمون و صورت‌جلسه پذیرش

**وضعیت:** ناقص · **فاز مالک/اثر:** A.1

**آنچه موجود است:** زیرساخت برنامه و اسناد تحویل وجود دارد؛ کد و تست هم بخش عمده موجودند.

**باقیمانده:** ثبت SHA انتشار، فایل‌ها و checksum، ورودی/expected، لاگ بازحساب و صفحات PDF و اجرای آزمون کارفرما.

**انتظار قابل آزمون:** کارفرما دقیقاً فایل و نسخه آزموده‌شده را دانلود و نتیجه پذیرش اولیه را صریح ثبت کند.

**حد اثبات فعلی:** استقرار، فایل دانلودی تولید و صورت‌جلسه کارفرما در این ممیزی احراز/ایجاد نشده

**شواهد مستقیم:** [output/delivery-plan-2026-11-03/delivery-plan.md:113](../delivery-plan-2026-11-03/delivery-plan.md#L113)؛ [docs/delivery/R0-scope-and-reports-contract.md:22](../../docs/delivery/R0-scope-and-reports-contract.md#L22)

### X01 — آفلاین، صف محلی، retry، حل تعارض و جداسازی هویت

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.8؛ سازگاری با A.1 الزامی

**آنچه موجود است:** زیرساخت sync و spec037 و آزمون‌های مستقل وجود دارند؛ به صرف این وجود کامل نامیده نمی‌شود.

**باقیمانده:** پذیرش اختصاصی operation_id، قطع پیش/پس از commit، refresh/restart، رقابت تأیید، عدم حذف موفق‌ها و تغییر حساب.

**انتظار قابل آزمون:** هیچ داده/عملیات گم یا تکراری نشود؛ مشتقات پروژه در sync هم readonly؛ اثبات‌های مستقل spec037 ارائه شود.

**حد اثبات فعلی:** تست آفلاین و browser این نوبت اجرا نشده؛ وضعیت «پیاده نشده» به آن نسبت داده نمی‌شود

**شواهد مستقیم:** [specs/037-daily-offline-sync/spec.md:104](../../specs/037-daily-offline-sync/spec.md#L104)

### X02 — درصد اجرا، نفرساعت پیمانکار و QC تخصصی مکانیک/برق

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.8؛ خروجی مرتبط A.1

**آنچه موجود است:** مدل‌ها و مسیرهای تخصصی/درصد/بازرسی وجود دارند.

**باقیمانده:** پذیرش درصد ۰..۱۰۰/null، گزارش خالی، تست فشار و ledger پس از تأیید و داده واقعی واحد.

**انتظار قابل آزمون:** درصد نامعلوم صفر نشود؛ فشار غیرمثبت رد؛ نفرساعت از مدت واقعی و افراد منبع محاسبه شود.

**حد اثبات فعلی:** درصد/Excel منتخب موفق؛ بقیه گردش تخصصی به طور کامل این نوبت آزموده نشده

**شواهد مستقیم:** [specs/038-discipline-sub-reports/spec.md:156](../../specs/038-discipline-sub-reports/spec.md#L156)

### X03 — پیشرفت برنامه‌ای/واقعی و روش‌های وزن‌دهی فیزیکی

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.7/A.8

**آنچه موجود است:** ماژول زمان‌بندی/پیشرفت جدا از daily quantities وجود دارد.

**باقیمانده:** تطبیق WBS و قواعد وزن‌دهی در فاز مربوط؛ مرز نمایش روزانه تعیین شود.

**انتظار قابل آزمون:** حجم فعالیت روزانه جانشین پیشرفت تجمعی رسمی تلقی نشود.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md:1](../../reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md#L1)

### X04 — گزارش هفتگی/ماهانه، KPI و کاتالوگ عمومی گزارش‌ها

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.10

**آنچه موجود است:** ProjectPeriodReport و کاتالوگ پنج‌گانه جدا هستند؛ مسیر عمومی monthly هنوز از سازنده weekly استفاده می‌کند.

**باقیمانده:** در A.10 تفکیک معنا، تاریخ/WBS و منابع approved؛ ادعای همه گزارش‌های دوره‌ای ناقص بر اساس یک مسیر عمومی درست نیست.

**انتظار قابل آزمون:** بازه، شاخص و منبع هر گزارش واقعی آزموده شود؛ A.1 جای پذیرش A.10 را نگیرد.

**حد اثبات فعلی:** کد مسیر عمومی بازبینی شد؛ مسیر تخصصی period_report جداست

**شواهد مستقیم:** [docs/delivery/R0-scope-and-reports-contract.md:51](../../docs/delivery/R0-scope-and-reports-contract.md#L51)؛ [apps/api/core/projects/services/report_export_service.py:80](../../apps/api/core/projects/services/report_export_service.py#L80)

### X05 — ذی‌نفعان، جلسات، مکاتبات و گزارش وضعیت ارتباطات

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.3.C و گزارش A.10

**آنچه موجود است:** پایه ذی‌نفع/ماتریس/برنامه ارتباطی موجود است؛ اتصال جامع در دامنه پذیرفته‌شده پروژه باقی است.

**باقیمانده:** تکمیل اتصال صریح stakeholder/meeting/correspondence، مسئول/موعد، workflow و کنترل داده تماس در فاز مربوط.

**انتظار قابل آزمون:** کارفرما مسیر ثبت تا اقدام باز و گزارش وضعیت فیلترشده را جدا از گزارش روزانه بپذیرد.

**حد اثبات فعلی:** درخواست قبلی کاربر جزو کل تحویل است؛ این ممیزی آن را از کل پروژه حذف نمی‌کند

**شواهد مستقیم:** [docs/delivery/R0-scope-and-reports-contract.md:19](../../docs/delivery/R0-scope-and-reports-contract.md#L19)

### X06 — تدارکات روز، RFI/Submittal و پیوند اسناد رسمی

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.4/A.9/A.10؛ نمایش روزانه نیازمند قرارداد

**آنچه موجود است:** یادداشت/ارجاع روزانه جایگزین گردش رسمی مکاتبات و تدارکات نیست.

**باقیمانده:** تعیین اقلام لازم در snapshot چاپی A.1 و اتصال ماژول‌های صاحب داده در فاز مربوط.

**انتظار قابل آزمون:** شماره/وضعیت سند از منبع رسمی بیاید؛ یک متن آزاد به‌عنوان گزارش کامل تدارکات معرفی نشود.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [docs/delivery/R0-scope-and-reports-contract.md:12](../../docs/delivery/R0-scope-and-reports-contract.md#L12)؛ [docs/delivery/R0-scope-and-reports-contract.md:55](../../docs/delivery/R0-scope-and-reports-contract.md#L55)

### X07 — باد، وضعیت زمین و پیش‌بینی سه روز آینده در فرم واقعی

**وضعیت:** نیازمند تثبیت قرارداد · **فاز مالک/اثر:** مرتبط؛ دامنه چاپ A.1 باید مشخص شود

**آنچه موجود است:** WeatherLog دارای داده باد/زمین است؛ این داده‌ها در هدر فعلی daily/export دیده نشدند؛ فرم واقعی پیش‌بینی سه‌روزه دارد.

**باقیمانده:** تصمیم صریح درباره ضرورت این فیلدها و منبع قابل اتکا؛ از ساخت سرویس پیش‌بینی بدون نیاز مصوب پرهیز شود.

**انتظار قابل آزمون:** اگر داخل دامنه شد مقدار/منبع/تاریخ روشن؛ در نبود داده «نامعلوم» و بدون داده ساختگی.

**حد اثبات فعلی:** تفکیک وجود مدل از نبود اتصال به گزارش؛ پیش‌بینی یک مشاهده مرجع است نه تعهد قطعی تازه

**شواهد مستقیم:** [apps/api/core/field_reports/models.py:788](../../apps/api/core/field_reports/models.py#L788)؛ [docs/delivery/R0-scope-and-reports-contract.md:30](../../docs/delivery/R0-scope-and-reports-contract.md#L30)

### X08 — مهاجرت سابقه، نگاشت taxonomy و rollback داده‌های قدیمی

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.8/A.12

**آنچه موجود است:** مدل migration trace و الزامات نگهداری شناسه/منبع/تاریخچه در spec032 وجود دارند.

**باقیمانده:** تمرین مهاجرت با داده واقعی، قرنطینه مقدار نامعلوم، یک نسخه جاری و rollback قابل اثبات.

**انتظار قابل آزمون:** تمام رکوردها migrated/history/quarantined شمرده شوند؛ سابقه بدون اثر در جمع رسمی قابل ردیابی بماند.

**حد اثبات فعلی:** تمرین مهاجرت و rollback این نوبت اجرا نشده؛ ۳۶۷ شیت به خودی خود تعهد ETL نیست

**شواهد مستقیم:** [specs/032-unit-report-source-truth/spec.md:195](../../specs/032-unit-report-source-truth/spec.md#L195)

### X09 — استقرار نهایی کل محصول و آموزش گسترده

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.12؛ بسته همان SHA برای A.1 لازم

**آنچه موجود است:** زیرساخت release/راهنما وجود دارد.

**باقیمانده:** استقرار و آموزش کل محصول در A.12؛ A.1 برای فایل‌های خود نسخه منتشرشده آزموده‌شده و راهنمای محدود می‌خواهد.

**انتظار قابل آزمون:** آزمون محلی به‌عنوان تأیید production معرفی نشود.

**حد اثبات فعلی:** بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده

**شواهد مستقیم:** [docs/delivery/R0-scope-and-reports-contract.md:20](../../docs/delivery/R0-scope-and-reports-contract.md#L20)

### X10 — گزارش‌های مستقل دپارتمان و انبار، ورود دسته‌ای و بالانس

**وضعیت:** مرتبط؛ خارج از تحویل مستقیم A.1 · **فاز مالک/اثر:** A.8/A.10؛ سازگاری منبع A.1

**آنچه موجود است:** اسناد SPEC09/10 و مسیرهای داده دپارتمان/آزمون گزارش وجود دارند؛ این مسیرها با خلاصه مشتق پروژه یکی نیستند.

**باقیمانده:** پذیرش مستقل import/export روزانه/هفتگی و بالانس ۸ فیلدی؛ تعیین مسیر قدیمی سازگار با مالکیت شش واحد و جلوگیری از منبع موازی.

**انتظار قابل آزمون:** رسید/مصرف/مانده و فیلترهای روز/واحد/پیمانکار با مرجع برابر؛ import تکراری یا ردیف نامعتبر داده رسمی را خراب نکند.

**حد اثبات فعلی:** صرفاً ثبت دامنه و مسیرهای موجود؛ آزمون جامع دپارتمان/انبار و بالانس در این نوبت اجرا نشده

**شواهد مستقیم:** [apps/api/core/inventory/department_activity_data_views.py:1](../../apps/api/core/inventory/department_activity_data_views.py#L1)؛ [apps/api/core/sub_reports/tests/test_department_reports.py:1](../../apps/api/core/sub_reports/tests/test_department_reports.py#L1)؛ [reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md:1](../../reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md#L1)؛ [reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md:1](../../reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md#L1)

## آنچه پیاده‌سازی آن در مسیر فعلی مشاهده نشد

این موارد اجزای مفقود در یک قابلیت موجودند، نه لزوماً ماژول کاملاً غایب:

- منبع و نمایش واقعی ساعت سه شیفت در هدر FILE4؛ اکنون متن ثابت چاپ می‌شود (H04).
- فیلتر discipline/contractor/block در مسیر فهرست روزانه (E12).
- aggregate کل نتیجه فیلتر در API دفتر فعالیت (E14).
- بازنگاشت کامل provenance و حفظ هویت تجمیعی/نظر/override در clone اصلاحیه (W03 تا W05).
- چاپ نقش واقعی در سه جای امضا و تنظیمات کامل چاپ Excel (E07/E04).
- شماره رسمی گزارش/روز پروژه در مدل daily و PDF مستقل زیرگزارش مشاهده نشدند؛ الزام آن‌ها هنوز تصمیم دامنه است، نه کار قطعی تازه (H05/C07).

فقدان گواه بازحساب، تطبیق روز واقعی یا صورت‌جلسه، «فقدان مدرک پذیرش» است و به تنهایی به معنی نبود کد آن قابلیت نیست.

## ادامه کار و مراجع مکمل

[برنامه شش بسته کاری و آزمون پایان هر بسته](remaining-work.md)، [ده تصمیم/تعارض ثبت‌شده](scope-decisions.md)، [پوشش ۱۸ بخش طرح جامع](broader-daily-sections.md)، [رجیستر کامل بندهای اصلی](source-clauses.md)، [خلاصه قابل ارائه به کارفرما](employer-summary.md) و [روش/حدود آزمون و manifest](evidence/README.md).

## حدود این نتیجه

این ممیزی به snapshot کد و مجموعه منابع ذکرشده مربوط است؛ ادعای کشف تمام نیازهای شفاهی ثبت‌نشده یا همه عیب‌های ممکن را ندارد. build/typecheck/full-suite، UAT مرورگر، recalc واقعی Excel، اندازه‌گیری شبکه، production و تمرین مهاجرت/rollback در این نوبت اجرا نشده‌اند. گزارش‌های آزمون قبلی شواهد تاریخی‌اند. متن «پیاده‌سازی موجود» گواه انتشار یا پذیرش نیست. برای اعلام پایان A.1 بسته‌های B01 تا B06 باید با شاهد بسته شوند.
