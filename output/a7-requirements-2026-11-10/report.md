# نیازمندی‌ها و بسته تحویل A.7

تاریخ ممیزی: ۱۹ آبان ۱۴۰۵ / 2026-11-10. موضوع A.7 در برنامه تحویل: **پروژه، اطلاعات پایه و ورود گروهی**.

**نتیجه:** پایه‌های ثبت پروژه، چرخه عمر، WBS، قالب‌ها و واردسازی وجود دارند و بخش مهمی از آزمون‌های محلی موفق‌اند. A.7 هنوز برای اعلام «تحویل کامل» مدرک کافی ندارد؛ علاوه بر پذیرش روی پروژه واقعی، چند نقص مشخص در واردسازی باید اصلاح شوند. تعداد اقلام این فهرست، درصد پیشرفت یا برآورد نفرساعت نیست.

این گزارش وضعیت نسخه محلی را بررسی می‌کند؛ هیچ استقرار یا پذیرش کارفرما در این بررسی انجام نشده است. عنوان «موجود و آزموده محلی» به معنای وجود قابلیت و موفقیت آزمون‌های منتخب است، نه آزموده شدن تمام حالت‌ها یا تأیید محیط تحویل.

## مبنا و مرز دامنه

- گفته کارفرما: سند اصلی `document (5).docx`، بخش برنامه‌ریزی؛ متن استخراج‌شده در پیوست منابع آمده است. اسناد FR-PRJ، FR-WBS و FR-SCH بازنویسی نیازمندی‌ها هستند و در خود فایل‌ها وضعیت «پیش‌نویس» دارند؛ تأیید مستقل همه جزئیات آن‌ها از عنوان سند استنتاج نشده است.
- مرز A.7: سند R.0.01 و برنامه تحویل اصلاح‌شده. ورودی پایه MSP XML، MPP یا P6 XER است. **ورود مستقل WBS از CSV/Excel، بازنویسی preview، همگام‌سازی زنده P6 و پشتیبانی همه فیلدهای Microsoft Project تعهد پایه نیستند.** ورود XLSX جداول پویا که از قبل وجود دارد، قابلیت جداگانه‌ای است.
- پروژه، WBS، نمونه واقعی و ایمنی ورود هسته A.7 هستند. زمان‌بندی تفصیلی/خط مبنا و اطلاعات مرجع با عنوان «مرتبط» جدا آمده‌اند تا در تحویل از دست نروند؛ این عنوان به‌خودی‌خود به معنی انتقال کل دامنه مالی، پیشرفت، منابع انسانی یا گزارش‌های A.10 به A.7 نیست.
- تاریخ‌های برنامه قدیمی و نمای فعلی برنامه تحویل یکسان نیستند؛ این ممیزی تعهد زمانی تازه ایجاد نمی‌کند.

## چه چیزهایی قبلاً ساخته شده‌اند و می‌توان برای تست ارائه کرد؟

۱. ثبت و ویرایش پروژه، کد یکتا و فیلدهای اصلی، ایجاد پیش‌نویس، ارسال/رد/تصویب و شرط فعال‌سازی.
۲. برگه آغاز پروژه و درخواست تغییر اطلاعات مصوب.
۳. چرخه تعلیق، خاتمه، بایگانی، خروج از بایگانی و بازگردانی وضعیت با دلیل، مجوز و سابقه.
۴. WBS چندسطحی، مشخصات و مسئول بسته کاری، جابه‌جایی، کنترل حلقه و حذف دستی گره وابسته.
۵. قالب پروژه/WBS با کپی مستقل، بدون تغییر خودکار پروژه‌های قبلی.
۶. فعالیت، تقویم، روابط، نسخه برنامه، قفل خط مبنا و درخواست تغییر زمان؛ کنترل‌های CRUD آن‌ها پایه موجود هستند.
۷. انتخاب XML/MPP/XER، preview، انتخاب افزودن/جایگزینی، job، پیشرفت و وضعیت نهایی، کنترل اندازه و خطاهای فایل.

این‌ها قابلیت‌های موجود برای نمایش و UAT هستند. موارد واردسازی که در بخش بعد آمده‌اند باید پیش از وعده تحویل کامل رفع شوند.

## اصلاحات لازم پیش از تحویل A.7

**اولویت ضروری ـ جلوگیری از تخریب و نگاشت نادرست**

- جایگزینی برنامه باید حفاظت حذف گره وابسته و تاریخچه مصوب را رعایت کند. در آزمایش، سربرگ خط مبنای قفل‌شده باقی ماند اما دو ردیف آن صفر شد؛ خود فعالیت‌های قدیمی حتی به شکل حذف منطقی هم باقی نماندند.
- فقط‌خواندنی بودن بایگانی باید مسیر واردسازی را هم پوشش دهد؛ API با فایل معتبر برای عضو غیرمدیر سیستم پاسخ 202 داد.
- والدهای P6 باید از شناسه والد واقعی گرفته شوند؛ در نمونه دوشاخه، فرزند P زیر Q قرار گرفت. مسیر fallback فعالیت بی‌والد نیز نباید آن را بی‌هشدار به بسته نامرتبط وصل کند.
- واردسازی باید همان قواعد مهم صحت داده را اعمال کند: دور، تاریخ ناممکن، والد نامعتبر، عمق و روابط. نمونه XML با دو رابطه دوری و پایان پیش از شروع ثبت شد و هشدار آن‌ها نداشت.
- واحد تأخیر MSP و نوع رابطه باید با فرمت مرجع تطبیق شوند. مقدار LinkLag برابر ۴۸۰۰ در نمونه بدون تبدیل به lag_days=4800 رسید؛ این عدد نباید به‌عنوان تعداد روز تحویل شود.
- مدت، نقطه عطف و تقویم باید به مقصد درست نگاشت شوند. مدت صفر MSP به None و در P6 به ۱ روز تبدیل شد؛ is_milestone در فعالیت‌های وارداتی false ماند.

**مشاهده روی فایل واقعی کارفرما:** plan.mpp در پایگاه آزمایشی وارد شد: ۶ گره WBS، ۷۴ فعالیت و ۷۹ رابطه در نتیجه importer. parser فایل ۸۳ پیوند پیش‌نیازی داشت؛ ۴ مورد به‌علت پیش‌نیاز ناموجود منتقل نشدند و هشدار گرفتند. دو هشدار دیگر برای مدت صفر شروع/پایان بود. علت و تصمیم درباره ۴ رابطه باید با کارشناس کنترل پروژه روشن شود؛ حذف این موارد خودکار پذیرفته‌شده فرض نمی‌شود.

**اولویت تکمیل کیفیت و تجربه تحویل**

- تکرار ورود نباید بی‌توضیح خط مبنای جاری تازه و خالی بسازد. در نمونه، بار دوم صفر WBS/فعالیت/رابطه ساخت ولی تعداد baseline به دو رسید.
- پیش‌نمایش و نتیجه نهایی باید تعداد ورودی، ایجادشده، تکراری و کنارگذاشته، روابط واقعی و متن هشدارها را برای تطبیق نشان دهند. UI فعلی شمار روابط و متن هشدارهای نهایی را ارائه نمی‌کند.
- انتساب ایجادکننده به WBS وارداتی، فارسی/انگلیسی، خطا و بازیابی، کنترل drop هنگام پردازش، صفحه‌کلید و موبایل تکمیل/آزموده شود.
- سیاست نگهداری فایل job و محدودیت منابع پردازش، و محیط واقعی MPXJ/JRE و worker اثبات شود. timeout thread به‌تنهایی اثبات آزاد شدن منابع نیست.
- مجوز نویسنده اطلاعات مرجع با A.6 و تست‌ها همسو شود. یک تست موجود صرف is_staff را کافی می‌داند ولی API فعلی 403 می‌دهد؛ این تعارض به‌تنهایی اثبات خطای سیاست دسترسی نیست.

## کارفرما در پایان A.7 چه تحویل بگیرد و چه تست کند؟

### بسته A.7.01 ـ پروژه و ورودی مرجع

فایل واقعی با نسخه/hash، ساختار مورد انتظار، نگاشت فیلدها و فهرست ارقام کنترل شامل WBS، فعالیت، رابطه، نقاط عطف، تاریخ‌ها و هشدارهای مورد انتظار. شمارش مشتق‌شده از parser همان سامانه، کنترل مستقل کارفرما محسوب نمی‌شود.

### بسته A.7.02 ـ پروژه و داده واردشده سالم

پروژه واقعی با مشخصات و برگه آغاز، وضعیت درست، WBS صحیح و فعالیت‌های متصل. فرمت‌های پذیرفته‌شده با همان preview موجود کار کنند. فیلد خارج از پشتیبانی یا ردیف منتقل‌نشده باید با علت اعلام شود؛ افت داده خاموش پذیرفته نیست.

### بسته A.7.03 ـ کنترل ایمنی و چرخه عمر

شواهد ورود تکراری، جایگزینی روی پروژه خالی و وابسته، حفظ نسخه‌های قبلی، رد فایل خراب/بزرگ/مخرب، محدودیت نقش و پروژه، بایگانی و بازگردانی. پاسخ ارسالی نامعلوم، خطا یا لغو نباید موفقیت فرضی بسازد. پیش‌نیاز A.6 در نقش‌ها و محرمانگی دوباره مصرف و کنترل شود.

### بسته A.7.04 ـ تست کامل توسط کارفرما

نسخه قابل شناسایی در محیط تحویل، حساب‌های نقش‌های لازم، راهنمای کوتاه و سناریوی «ایجاد → تصویب → WBS/قالب → preview → ورود → کنترل جمع‌ها → ورود دوباره → جایگزینی ایمن → بایگانی/بازیابی». نتیجه واقعی هر گام، نقص باز و پاسخ کارفرما طبق روال داخلی ثبت شود؛ نبود مدرک در مخزن معادل اثبات انجام نشدن پذیرش نیست.

## فهرست قابل ردیابی نیازمندی‌ها

در ادامه هر قلم، وضعیت فعلی، کار لازم برای پذیرش و مسیر منبع آمده است. شناسه‌های P/W/M/S/I/D شناسه ممیزی‌اند و جای شناسه قرارداد را نمی‌گیرند.

### پروژه

**P01 — ثبت مشخصات کامل پروژه**

- مرجع نیازمندی: FR-PRJ-001؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. فرم ایجاد و تنظیمات، API و فیلدهای هویت، هدف، محدوده، خروجی‌ها، کارفرما، مدیر، تاریخ‌ها، قرارداد، ارز، مبلغ و واحد مالک موجودند.
- تحویل/تست: یک پروژه واقعی با تمام فیلدها ذخیره و پس از بازگشایی تطبیق شود.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [PROJECT_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/serializers.py:170>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**P02 — کد یکتای پروژه**

- مرجع نیازمندی: FR-PRJ-007؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. یکتایی کد در مدل و آزمون‌های پروژه برقرار است.
- تحویل/تست: کد تکراری با پیام قابل فهم رد شود؛ پروژه نیمه‌کاره ایجاد نشود.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [PROJECT_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/serializers.py:170>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**P03 — پیش‌نویس، ارسال و چرخه وضعیت**

- مرجع نیازمندی: FR-PRJ-002/003؛ 008 FR-002/008/010؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. چرخه پیش‌نویس، انتظار تصویب، فعال، تعلیق، خاتمه و بایگانی و مسیرهای مجاز وجود دارد.
- تحویل/تست: ایجاد به‌صورت پیش‌نویس، ارسال، رد، تصویب، تعلیق و خاتمه با نقش مجاز طی شود.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [LIFECYCLE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/lifecycle_service.py:30>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**P04 — شرط فعال‌سازی و تصویب بودجه**

- مرجع نیازمندی: FR-PRJ-003؛ SC-PRJ-002؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. نبود مدیر، محدوده یا مبلغ مانع فعال‌سازی است؛ تصویب پروژه مهر تصویب بودجه را ثبت می‌کند.
- تحویل/تست: هر سه نقص جداگانه و هم‌زمان نمایش داده شوند؛ صرف وارد کردن مبلغ پروژه را فعال نکند.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [LIFECYCLE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/lifecycle_service.py:30>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**P05 — جلوگیری از تعهد یا خط مبنای قطعی پیش از تصویب**

- مرجع نیازمندی: FR-PRJ-004؛ دامنه: مرتبط با A.7.
- وضعیت: **موجود و آزموده محلی**. گیت تعهد الزام‌آور و قفل خط مبنا در آزمون‌ها کنترل شده؛ snapshot وارداتی به‌خودی‌خود مصوب و قفل‌شده نیست.
- تحویل/تست: در پیش‌نویس/انتظار تصویب و تعلیق، مسیرهای ایجاد قطعی مسدود باشند؛ تفاوت نسخه وارداتی و مصوب روشن باشد.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [BASELINE](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/baseline_service.py:1>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**P06 — برگه آغاز پروژه**

- مرجع نیازمندی: FR-PRJ-005؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. توجیه، معیار موفقیت، محدودیت، فرضیات، ذی‌نفعان کلیدی و اختیار مدیر قابل ذخیره‌اند.
- تحویل/تست: هر شش بخش ثبت و از جزئیات پروژه دوباره دیده شود.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [CHARTER](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/charter_service.py:1>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**P07 — تغییر کنترل‌شده اطلاعات مصوب**

- مرجع نیازمندی: FR-PRJ-006؛ SC-PRJ-003؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. درخواست تغییر پروژه و حفاظت تاریخ‌ها، مبلغ، کارفرما و محدوده موجود است.
- تحویل/تست: ویرایش مستقیم رد شود؛ تصویب درخواست مقدار را تغییر دهد و رد/لغو آن مقدار را ثابت نگه دارد.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [PRJCR](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/change_request_service.py:1>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**P08 — فقط‌خواندنی بودن پروژه بایگانی‌شده**

- مرجع نیازمندی: 008 FR-009؛ قاعده مرزی FR-PRJ؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. تنظیمات و برگه آغاز کنترل دارند؛ با فایل XML معتبر، API واردسازی برای عضو غیرمدیر سیستم روی پروژه بایگانی‌شده پاسخ 202 داد. این مسیر محدودیت فقط‌خواندنی را رعایت نمی‌کند.
- تحویل/تست: کاربر غیرمدیر سیستم نتواند از هیچ مسیر، از جمله واردسازی، داده پروژه بایگانی‌شده را تغییر دهد.
- شواهد: [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [LIFECYCLE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/lifecycle_service.py:30>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**P09 — خروج از بایگانی با مقصد و مجوز صحیح**

- مرجع نیازمندی: FR-RPA-001–006/014؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. پیش‌نمایش، دلیل، مقصد ثابت از وضعیت قبلی، اختیار مدیر سیستم و راه رفع نقص در کد و آزمون‌های منتخب وجود دارند.
- تحویل/تست: فعال/تعلیق/خاتمه به مقصد درست بازگردند؛ کاربر فاقد اختیار و تأیید کهنه رد شود.
- شواهد: [RESTORE](</home/hossein/Desktop/projects/building-management/specs/008-project-registration/restore-project-archive/spec.md:132>)، [LIFECYCLE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/lifecycle_service.py:30>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**P10 — حفظ سوابق، تکرار ایمن و پیگیری بازگردانی**

- مرجع نیازمندی: FR-RPA-007–013؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. سابقه اقدام، حفظ داده، rollback، تکرار دقیق و پیگیری نتیجه در آزمون‌های منتخب بررسی شده‌اند؛ کل هم‌زمانی/مرورگر در این ممیزی بازاجرا نشد.
- تحویل/تست: داده‌ها، تأییدهای قبلی و خط مبنا ثابت بمانند؛ دوبار کلیک یا قطع پاسخ موفقیت دوم نسازد؛ فارسی/انگلیسی در مرورگر بررسی شود.
- شواهد: [RESTORE](</home/hossein/Desktop/projects/building-management/specs/008-project-registration/restore-project-archive/spec.md:132>)، [LIFECYCLE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/lifecycle_service.py:30>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**P11 — ازسرگیری تعلیق و بازگردانی خاتمه**

- مرجع نیازمندی: FR-UPS-001–015؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. دو مسیر مستقل با منشأ رخداد، مقصد ثابت، اختیار، تأیید، دلیل و سابقه موجودند؛ آزمون‌های منتخب backend اجرا شده‌اند.
- تحویل/تست: تعلیق با مجوز پروژه و بازگردانی خاتمه فقط با اختیار مدیر سیستم؛ حفظ داده، تأیید تازه، تکرار و هماهنگی نماها آزموده شود.
- شواهد: [UNDO](</home/hossein/Desktop/projects/building-management/specs/026-undo-project-status/spec.md:106>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

### WBS

**W01 — درخت چندسطحی و تفکیک دامنه**

- مرجع نیازمندی: FR-WBS-001/003؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. درخت و بسته کاری از فعالیت و CBS مجزا است.
- تحویل/تست: حداقل سه سطح واقعی ایجاد و ارتباط پروژه، والد و بسته کاری قابل مشاهده باشد.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [WBS_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/wbs/services.py:100>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)، [SOURCE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/stakeholder-document-5.txt:86>)

**W02 — مشخصات و مسئول بسته کاری**

- مرجع نیازمندی: FR-WBS-002/004؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. کد، عنوان، شرح، والد، سطح، مسئول، معیار پذیرش، وضعیت و وزن‌ها پشتیبانی می‌شوند.
- تحویل/تست: مسئول و معیار تکمیل یک بسته ثبت، بازگشایی و به فعالیت/بودجه مرتبط شوند؛ بودجه تفصیلی تعهد مستقل A.7 نیست.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [WBS_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/wbs/services.py:100>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**W03 — کد یکتا، والد معتبر و ممنوعیت دور**

- مرجع نیازمندی: FR-WBS-005؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. مسیر دستی ایجاد و جابه‌جایی کنترل و آزمون دارد؛ سلامت ورودی گروهی جدا بررسی می‌شود.
- تحویل/تست: کد تکراری، والد پروژه دیگر و انتقال گره زیر فرزند خودش رد شود.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [WBS_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/wbs/services.py:100>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**W04 — محافظت از گره وابسته**

- مرجع نیازمندی: FR-WBS-006؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. حذف دستی هزینه/پیشرفت/سند/فرزند/فعالیت را کنترل می‌کند؛ واردسازی replace همان مسیر را استفاده نمی‌کند.
- تحویل/تست: این حفاظت در حذف دستی، اعمال قالب و جایگزینی وارداتی برقرار باشد و تاریخچه حفظ شود.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [WBS_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/wbs/services.py:100>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**W05 — قالب مستقل و قابل استفاده مجدد**

- مرجع نیازمندی: FR-WBS-007؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. کپی قالب به پروژه و عدم تغییر خودکار پروژه با ویرایش قالب آزموده شد.
- تحویل/تست: قالب روی پروژه جدید اعمال شود؛ ویرایش قالب پروژه قبلی را تغییر ندهد؛ جایگزینی قالب وابسته ایمن باشد.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [TEMPLATE](</home/hossein/Desktop/projects/building-management/apps/api/core/project_templates/services.py:1>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**W06 — جابه‌جایی، مسیر و کدگذاری مجدد**

- مرجع نیازمندی: 004 SC-004 و edge cases؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. سرویس جابه‌جایی درخت و بازتولید کد وجود دارد.
- تحویل/تست: والد، عمق، ترتیب و کدهای وابسته بعد از جابه‌جایی تطبیق شوند.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [WBS_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/wbs/services.py:100>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**W07 — عمق، وزن‌ها و هشدار ساختار خالی**

- مرجع نیازمندی: 004 edge cases؛ 029 edge cases؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. کنترل دستی و هشدارهای UI وجود دارند؛ MSP برای max_depth هشدار/skip دارد و مسیر P6 همان کنترل صریح را ندارد.
- تحویل/تست: درخت خالی و وزن نامعتبر هشدار بدهد؛ ردیف بیش از عمق مجاز در هر فرمت توضیح و در شمارش کنترل لحاظ شود.
- شواهد: [WBS](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/04-ساختار شکست کار WBS.md:44>)، [WBS_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/wbs/services.py:100>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)

### اطلاعات پایه

**M01 — واحد سازمانی و واحد مالک پروژه**

- مرجع نیازمندی: FR-DATA-003؛ FR-PRJ-001؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. کاتالوگ و اتصال owning_unit موجود است؛ یک آزمون موجود برای is_staff تنها انتظار 201 دارد اما 403 می‌گیرد.
- تحویل/تست: نقش نویسنده مرجع با A.6 هماهنگ شود؛ تست و توضیح مجوز همسو شوند؛ واحد تازه در ثبت پروژه انتخاب شود.
- شواهد: [DATA](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/02-مدل داده مرکزی.md:52>)، [REF](</home/hossein/Desktop/projects/building-management/apps/api/core/master_data/ref_views.py:1>)، [PROJECT_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/serializers.py:170>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**M02 — نوع قرارداد و واحد اندازه‌گیری قابل مدیریت**

- مرجع نیازمندی: FR-DATA-003؛ SC-DATA-004؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. کاتالوگ نوع قرارداد، API خواندن واحد و صفحه انتخاب وجود دارد؛ مدیریت واحد از admin است و نوع قرارداد پروژه هنوز متن ذخیره می‌شود.
- تحویل/تست: مسیر مدیریت مرجع برای کاربر مسئول روشن شود؛ مقادیر حیاتی در API اعتبارسنجی و با کاتالوگ همسو باشند.
- شواهد: [DATA](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/02-مدل داده مرکزی.md:52>)، [REF](</home/hossein/Desktop/projects/building-management/apps/api/core/master_data/ref_views.py:1>)، [PROJECT_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/serializers.py:170>)

**M03 — وضعیت‌های مرجع و چرخه مجاز**

- مرجع نیازمندی: FR-DATA-003 در برابر FR-PRJ-002؛ دامنه: مرتبط با A.7.
- وضعیت: **نیازمند اثبات تحویل**. وضعیت پروژه از enum و قواعد چرخه عمر می‌آید؛ تغییر دلخواه فهرست وضعیت‌ها از UI اثبات نشد.
- تحویل/تست: تفسیر مرجع قابل مدیریت با چرخه وضعیت مصوب روشن شود؛ وضعیت دلخواه بدون تعریف انتقال به A.7 افزوده نشود.
- شواهد: [DATA](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/02-مدل داده مرکزی.md:52>)، [PRJ](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/03-ثبت پروژه و آغاز کار.md:46>)، [PROJECT_CODE](</home/hossein/Desktop/projects/building-management/apps/api/core/projects/serializers.py:170>)

**M04 — جداول و فیلدهای پویا و Excel آنها**

- مرجع نیازمندی: قابلیت موجود وابسته به اطلاعات پایه؛ دامنه: مرتبط با A.7.
- وضعیت: **نیازمند اثبات تحویل**. ورود XLSX ردیف‌های جداول پویا با خطای سطری موجود است؛ جایگزین import تخصصی WBS نیست.
- تحویل/تست: اگر در جریان واقعی A.7 استفاده می‌شود، قالب، ردیف خطادار و مجوز آن آزموده شود؛ انتقال مستقل WBS از Excel تعهد جدید است.
- شواهد: [DYNAMIC](</home/hossein/Desktop/projects/building-management/apps/api/core/business_meta/data_views.py:147>)، [CORRECTION](</home/hossein/Desktop/projects/building-management/output/delivery-plan-2026-11-03/reviewer-corrections.md:11>)

### زمان‌بندی مرتبط

**S01 — فعالیت متصل به بسته با مدت و تقویم**

- مرجع نیازمندی: FR-SCH-001؛ دامنه: مرتبط با A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. CRUD فعالیت و تقویم موجود و آزموده‌اند؛ واردسازی همه فیلدهای Activity را پر نمی‌کند.
- تحویل/تست: فعالیت وارداتی با بسته صحیح، مدت، نقطه عطف، تقویم و مسئول قابل کنترل باشد؛ فیلد پشتیبانی‌نشده صریح اعلام شود.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [ACT](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/activity_service.py:1>)، [CAL](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/calendar_service.py:1>)، [SHARED](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/shared_import.py:3>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**S02 — روابط و تأخیر بین فعالیت‌ها**

- مرجع نیازمندی: FR-SCH-002؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. CRUD انواع FS/SS/FF/SF را کنترل می‌کند؛ واحد lag در مسیر MSP و ورود گروهی نیازمند اصلاح است.
- تحویل/تست: نوع و تأخیر روابط با منبع در واحد روز/ساعت توافق‌شده برابر باشد؛ پیش‌نیاز ناموجود گزارش شود.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [REL](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/relation_service.py:29>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**S03 — تاریخ ناممکن، دور و فعالیت بی‌والد**

- مرجع نیازمندی: FR-SCH-003؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. CRUD کنترل دارد؛ import مستقیم bulk_create و fallback والد، همان کنترل‌ها را طی نمی‌کند.
- تحویل/تست: دور، پایان پیش از شروع و والد نامعتبر پیش از ثبت رد یا با هشدار قابل تطبیق و تصمیم صریح مدیریت شوند.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [REL](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/relation_service.py:29>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**S04 — تفکیک تاریخ برنامه‌ای، واقعی و پیش‌بینی**

- مرجع نیازمندی: FR-SCH-004؛ دامنه: مرتبط با A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. مدل و API این فیلدها را دارند؛ parser وارداتی عمدتاً start/finish برنامه‌ای را می‌گیرد.
- تحویل/تست: برنامه جاری، مصوب، واقعی و پیش‌بینی قاطی نشوند؛ محدوده داده‌های منتقل‌شده از فایل به‌روشنی اعلام شود.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [ACT](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/activity_service.py:1>)، [MSP](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:81>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [SHARED](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/shared_import.py:3>)

**S05 — نسخه مصوب و قفل‌شده با حفظ تاریخچه**

- مرجع نیازمندی: FR-SCH-005؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. قفل و نسخه‌گذاری موجود و آزموده است؛ replace می‌تواند با حذف Activity ردیف snapshot تاریخی را حذف کند.
- تحویل/تست: واردسازی روی پروژه دارای مبنای مصوب تاریخچه را از بین نبرد؛ نسخه جدید فقط طبق سیاست مصوب جاری شود.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [BASELINE](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/baseline_service.py:1>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**S06 — درخواست تغییر زمان و نسخه جدید**

- مرجع نیازمندی: FR-SCH-006؛ دامنه: مرتبط با A.7.
- وضعیت: **موجود و آزموده محلی**. ثبت علت، اثر، تصمیم و تولید نسخه جدید در سرویس و آزمون منتخب وجود دارد.
- تحویل/تست: تغییر زمان مصوب با حفظ نسخه قبل و اثر نقاط عطف/هزینه/قرارداد ثبت شود؛ تغییر پروژه با تغییر برنامه یکی تلقی نشود.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [SCHED_CR](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/change_request_service.py:1>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**S07 — گزارش نقاط عطف، تأخیر و پیش‌بینی پایان**

- مرجع نیازمندی: FR-SCH-007؛ SC-SCH-003؛ دامنه: مرتبط با A.7.
- وضعیت: **موجود و آزموده محلی**. سرویس گزارش وضعیت و آزمون backend موجود است؛ ممیزی رابط و داده واقعی آن انجام نشد.
- تحویل/تست: پس از import نمونه، تاریخ‌های چهارگانه و نقطه عطف در گانت/گزارش صحیح باشند؛ کاتالوگ گزارش‌های نهایی A.10 باقی می‌ماند.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [STATUS](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/status_report_service.py:1>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**S08 — اعتبار مسیر بحرانی**

- مرجع نیازمندی: FR-SCH-008؛ دامنه: مرتبط با A.7.
- وضعیت: **موجود و آزموده محلی**. گیت اعتبار مدت/روابط و آزمون backend موجود است.
- تحویل/تست: داده ناقص نتیجه معتبر جلوه نکند؛ ورود فایل با فیلدهای ناقص باید نامعتبر/غیرقابل محاسبه نشان دهد.
- شواهد: [SCH](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/05-برنامه زمان‌بندی و خط مبنا.md:47>)، [CRITICAL](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/critical_path_validity.py:1>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

### ورود گروهی

**I01 — پذیرش MPP، MSP XML و P6 XER**

- مرجع نیازمندی: 029 FR-001/002/022؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. سه فرمت و مسیرهای parser و تبدیل موجودند؛ آزمون‌های نمونه موجود پاس شدند.
- تحویل/تست: نمونه قابل خواندن هر فرمت قبول و فایل ناخوانا با راهکار روشن رد شود؛ پشتیبانی همه سال‌های MSP ادعا نشود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [R0](</home/hossein/Desktop/projects/building-management/docs/delivery/R0-scope-and-reports-contract.md:18>)، [MSP](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:81>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I02 — جریان انتخاب، پیش‌نمایش، تأیید، پیشرفت و نتیجه**

- مرجع نیازمندی: 029 FR-003؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. wizard سه‌مرحله‌ای و append/replace موجود است؛ نتیجه نهایی همه جزئیات مورد نیاز را نشان نمی‌دهد.
- تحویل/تست: فایل واقعی از بارگذاری تا مشاهده WBS و جمع‌ها در مرورگر طی شود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [UI](</home/hossein/Desktop/projects/building-management/apps/web/src/components/wbs/msp-import-wizard.tsx:30>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)

**I03 — یکسان بودن تفسیر پیش‌نمایش و ثبت**

- مرجع نیازمندی: 029 FR-004؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. هر دو از parser مشترک استفاده می‌کنند اما preview جزئیات روابط/همه فیلدها را نشان نمی‌دهد و نگاشت P6 آسیب‌پذیر است.
- تحویل/تست: شمارش، والدها، شناسه‌ها و هشدارهای preview با ثبت نهایی و ارقام کنترل یکسان باشند.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [PREVIEW](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:185>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**I04 — حفظ کامل داده‌های پشتیبانی‌شده فایل**

- مرجع نیازمندی: 029 FR-005؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. برخی مدت/درصد/slack فقط در BaselineActivity می‌مانند؛ duration_days، milestone و تقویم Activity کامل نگاشت نمی‌شوند.
- تحویل/تست: فهرست فیلدهای پشتیبانی‌شده مشخص شود و انتقال هرکدام در مقصد مصرف داده آزموده شود؛ افت داده خاموش ممنوع.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [SHARED](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/shared_import.py:3>)، [MSP](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:81>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**I05 — Summary به WBS و برگ/نقطه عطف به فعالیت**

- مرجع نیازمندی: 029 FR-006؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. اصل مدل موجود است؛ انتخاب parent در P6 به آخرین والد یک سطح وابسته است و fallback در MSP/P6 والد دلخواه می‌دهد.
- تحویل/تست: WBS چندشاخه با والد واقعی برابر باشد؛ فعالیت بی‌والد به بسته نامرتبط متصل نشود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**I06 — افزودن و برخورد با کدهای تکراری**

- مرجع نیازمندی: 029 FR-007؛ A.7.03؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. کد تکراری با هشدار کنار گذاشته می‌شود؛ تکرار import نسخه baseline تازه حتی با صفر ردیف جدید می‌سازد.
- تحویل/تست: ورود تکراری داده و رابطه تکراری نسازد؛ ردیف skipped و اثر روی baseline روشن و کنترل شود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [SHARED](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/shared_import.py:3>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**I07 — جایگزینی ایمن**

- مرجع نیازمندی: 029 FR-007/010؛ FR-WBS-006؛ FR-CORE-007؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. replace در importer مستقیماً relations، activities و WBS را حذف می‌کند و مسیر حفاظت حذف دستی را دور می‌زند.
- تحویل/تست: با وابستگی به هزینه، پیشرفت، سند یا مبنای قفل‌شده مسدود یا مسیر نسخه‌دار ایمن اجرا شود؛ هیچ سابقه مصوب حذف نشود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**I08 — پیش‌نمایش بدون تغییر دائمی**

- مرجع نیازمندی: 029 US1/3؛ FR-003/004؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. پیش‌نمایش parser/build_preview اجرا می‌کند و داده دامنه ایجاد نمی‌کند.
- تحویل/تست: باز کردن preview و لغو آن شمار رکوردهای پروژه را تغییر ندهد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [PREVIEW](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:185>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I09 — Job و پیشرفت پس‌زمینه**

- مرجع نیازمندی: 029 FR-007/011؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. job، وضعیت pending/running/done/failed و progress وجود دارد؛ آزمون محلی eager است.
- تحویل/تست: در محیط تحویل worker واقعی اجرا شود؛ موفقیت و خطا به وضعیت نهایی برسند و واردسازی بعدی ممکن باشد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [TASK](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/tasks.py:40>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I10 — شمارش‌ها و گزارش هشدار قابل تطبیق**

- مرجع نیازمندی: 029 FR-007/016؛ A.7.01/04؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. backend شمار WBS/فعالیت/رابطه و warnings می‌دهد؛ UI نتیجه فقط WBS، فعالیت و تعداد هشدار را نشان می‌دهد؛ bulk relation count پیش از درج واقعی زیاد می‌شود.
- تحویل/تست: تعداد ورودی، ایجاد، تکراری، کنارگذاشته و روابط واقعی با علت هر مغایرت و متن هشدارها نمایش داده شود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [PREVIEW](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:185>)، [SHARED](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/shared_import.py:3>)، [UI](</home/hossein/Desktop/projects/building-management/apps/web/src/components/wbs/msp-import-wizard.tsx:30>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

**I11 — عضویت، edit_wbs و جداسازی پروژه‌ها**

- مرجع نیازمندی: 029 FR-007/018؛ FR-CORE-009؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. مجوز preview/start و محدودسازی status به project_id وجود دارد؛ تست‌های unauthorized و cross-project پاس شدند.
- تحویل/تست: کاربر غیرمجاز preview/start/result پروژه دیگر را نبیند؛ کنترل وضعیت بایگانی جداگانه P08 است.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I12 — سقف ۵۰ مگابایت و اصالت فایل**

- مرجع نیازمندی: 029 FR-008/009؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. اعتبارسنجی اندازه، نوع و محتوای فایل و آزمون‌های خرابی/تغییر پسوند وجود دارد.
- تحویل/تست: فایل بزرگ، خالی یا فایل با پسوند جعلی رد شود و داده پروژه ثابت بماند.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I13 — خطاهای متمایز و قابل اقدام**

- مرجع نیازمندی: 029 FR-010/013/022؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. کدهای خراب، رمزدار، پشتیبانی‌نشده، نوع نامعتبر، بزرگ و timeout در تبدیل/API موجودند.
- تحویل/تست: هر نوع خطا پیام و راه اصلاح مناسب بدهد؛ فایل رمزدار دور زده نشود.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [CONVERT](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/mpp_convert.py:62>)، [IMPORT_API](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/views.py:88>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I14 — اتمی بودن خطا و امکان تلاش بعدی**

- مرجع نیازمندی: 029 FR-010/011؛ دامنه: هسته A.7.
- وضعیت: **موجود و آزموده محلی**. اجرای دامنه transaction.atomic دارد و شکست تبدیل قبل از mutation آزموده شده؛ آزمون همه انواع شکست در تحویل لازم است.
- تحویل/تست: شکست قبل و میانه import هیچ داده نیمه‌کاره نگذارد؛ attempt بعدی به نتیجه برسد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [TASK](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/tasks.py:40>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I15 — زبان فعال و راه بازیابی خطا**

- مرجع نیازمندی: 029 FR-012/016؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. بخش قابل توجهی از متن wizard فارسی ثابت و برخی warnings انگلیسی parser است.
- تحویل/تست: کمک، هشدار، نتیجه و خطا در فارسی و انگلیسی مطابق زبان فعال باشد؛ انتخاب فایل دیگر/تلاش مجدد روشن باشد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [UI](</home/hossein/Desktop/projects/building-management/apps/web/src/components/wbs/msp-import-wizard.tsx:30>)، [MSP](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:81>)، [P6](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/p6_import.py:77>)

**I16 — نمایش پردازش و جلوگیری از ارسال دوباره**

- مرجع نیازمندی: 029 FR-015؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. دکمه و input هنگام پردازش غیرفعال‌اند؛ مسیر drag/drop همان guard را صریح اعمال نمی‌کند.
- تحویل/تست: در زمان preview/submit، کلیک، انتخاب و drop فایل دوم هیچ درخواست یا تغییر فایل ناخواسته نسازد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [UI](</home/hossein/Desktop/projects/building-management/apps/web/src/components/wbs/msp-import-wizard.tsx:30>)

**I17 — صفحه‌کلید، RTL/LTR و موبایل**

- مرجع نیازمندی: 029 FR-017؛ SC-008؛ دامنه: هسته A.7.
- وضعیت: **نیازمند اثبات تحویل**. کنترل‌های UI و فایل‌های تست وجود دارند؛ در این ممیزی سفر مرورگری تازه اجرا نشد.
- تحویل/تست: ورود موفق و بازیابی خطا با صفحه‌کلید در هر دو زبان و عرض موبایل قابل انجام باشد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [UI](</home/hossein/Desktop/projects/building-management/apps/web/src/components/wbs/msp-import-wizard.tsx:30>)

**I18 — ردیابی اقدام و نتیجه واردسازی**

- مرجع نیازمندی: 029 FR-014؛ FR-CORE-003/014؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. job کاربر/نام فایل/حالت/نتیجه را نگه می‌دارد؛ WBS ایجادشده مستقیماً created_by/updated_by نمی‌گیرد.
- تحویل/تست: کاربر، زمان، پروژه، فایل، حالت و نتیجه قابل پیگیری و انتساب گره‌ها روشن باشد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [EXEC](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/msp_import.py:221>)، [TASK](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/tasks.py:40>)، [CORE](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/01-دامنه، اصول و واژه‌نامه.md:54>)

**I19 — نگهداری و پاک‌سازی فایل‌ها**

- مرجع نیازمندی: 029 FR-019؛ دامنه: پیش‌نیاز و کنترل تحویل.
- وضعیت: **ناقص / نیازمند اصلاح**. فایل موقت تبدیل cleanup دارد؛ file_data در job می‌ماند و سیاست پاک‌سازی اجرایی آن در مسیر بررسی‌شده یافت نشد.
- تحویل/تست: قاعده نگهداری فایل اصلی/مشتق/نتیجه مشخص و اعمال شود؛ دسترسی بین پروژه‌ها بسته بماند.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [CONVERT](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/mpp_convert.py:62>)، [TASK](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/tasks.py:40>)

**I20 — حد زمان و منابع پردازش**

- مرجع نیازمندی: 029 FR-020؛ SC-006؛ دامنه: پیش‌نیاز و کنترل تحویل.
- وضعیت: **ناقص / نیازمند اصلاح**. timeout تبدیل وجود دارد؛ thread داخلی JPype پس از timeout قابل توقف صریح نیست و سقف منابع/بار هم‌زمان اثبات نشده.
- تحویل/تست: فایل سنگین/خراب در حد مشخص تمام شود؛ منابع آزاد و worker برای کار بعدی سالم بماند.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [CONVERT](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/mpp_convert.py:62>)

**I21 — مجموعه نمونه سازگاری و برابری MPP/XML**

- مرجع نیازمندی: 029 FR-021؛ SC-002/003/005؛ دامنه: هسته A.7.
- وضعیت: **ناقص / نیازمند اصلاح**. fixture معتبر جفت و موارد خراب وجود دارند و تست‌ها پاس شدند؛ آزمون equivalence فعلی فقط subset preview را مقایسه می‌کند.
- تحویل/تست: تاریخ، مدت، milestone، درصد، hierarchy، رابطه/lag و هشدارها با داده ذخیره‌شده مقایسه شوند؛ ۹۵٪ فقط برای corpus اعلام‌شده معنی دارد.
- شواهد: [MPP](</home/hossein/Desktop/projects/building-management/specs/029-native-mpp-import/spec.md:138>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**I22 — فایل واقعی کارفرما و ارقام کنترل**

- مرجع نیازمندی: A.7.01/02؛ R.0.01؛ دامنه: هسته A.7.
- وضعیت: **نیازمند اثبات تحویل**. plan.mpp محلی تبدیل و در پایگاه آزمون وارد شد: ۶ WBS، ۷۴ فعالیت و ۷۹ رابطه در نتیجه importer؛ parser منبع ۸۳ پیوند داشت و ۴ پیش‌نیاز ناموجود هشدار گرفت. دو هشدار مدت صفر نیز وجود داشت؛ این تطبیق هنوز کنترل مستقل کارفرما نیست.
- تحویل/تست: WBS، برگ‌ها، روابط، مقادیر مهم و هشدارهای مورد انتظار پیش از import ثبت و پس از آن تطبیق شوند.
- شواهد: [R0](</home/hossein/Desktop/projects/building-management/docs/delivery/R0-scope-and-reports-contract.md:18>)، [PLAN](</home/hossein/Desktop/projects/building-management/output/delivery-plan-2026-11-03/delivery-plan.md:86>)، [PROBE](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)

### تحویل

**D01 — ماتریس نمونه، نگاشت و اختلاف‌ها**

- مرجع نیازمندی: A.7.01؛ دامنه: پیش‌نیاز و کنترل تحویل.
- وضعیت: **مدرک یا خروجی یافت نشد**. بسته کامل مخصوص A.7 با ارقام کنترل مورد تأیید کارفرما در منابع بررسی‌شده یافت نشد؛ این ممیزی جای آن نیست.
- تحویل/تست: فایل مرجع با hash، نسخه، نگاشت و انتظار هر هشدار ضمیمه شود.
- شواهد: [PLAN](</home/hossein/Desktop/projects/building-management/output/delivery-plan-2026-11-03/delivery-plan.md:86>)، [R0](</home/hossein/Desktop/projects/building-management/docs/delivery/R0-scope-and-reports-contract.md:18>)

**D02 — آمادگی محیط واقعی تبدیل و worker**

- مرجع نیازمندی: A.7.02؛ 029 FR-020؛ دامنه: پیش‌نیاز و کنترل تحویل.
- وضعیت: **نیازمند اثبات تحویل**. تبدیل fixture در محیط محلی پاس شد؛ کانتینر/میزبان تحویل، worker و broker این ممیزی نشده‌اند.
- تحویل/تست: همان نسخه در محیط تحویل با MPXJ/JRE و worker واقعی، فایل کارفرما را پردازش کند.
- شواهد: [PLAN](</home/hossein/Desktop/projects/building-management/output/delivery-plan-2026-11-03/delivery-plan.md:86>)، [CONVERT](</home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/mpp_convert.py:62>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)

**D03 — آزمون مرورگری یک پروژه مرجع**

- مرجع نیازمندی: A.7.04؛ SC-PRJ/WBS/SCH/MPP؛ دامنه: پیش‌نیاز و کنترل تحویل.
- وضعیت: **مدرک یا خروجی یافت نشد**. شواهد قدیمی و تست‌های مرورگر وجود دارند؛ بسته پذیرش تازه و یکپارچه A.7 روی نمونه کارفرما یافت نشد.
- تحویل/تست: ایجاد → تصویب → WBS/قالب → preview → import → کنترل جمع‌ها → تکرار/جایگزینی → بایگانی/بازیابی با نقش‌ها ثبت شود.
- شواهد: [PLAN](</home/hossein/Desktop/projects/building-management/output/delivery-plan-2026-11-03/delivery-plan.md:86>)، [TEST](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)، [EXTRA](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)

**D04 — نسخه تحویلی، راهنمای تست و نتیجه پذیرش**

- مرجع نیازمندی: معیار پذیرش A.7؛ FR-CORE-002/008/009؛ دامنه: پیش‌نیاز و کنترل تحویل.
- وضعیت: **مدرک یا خروجی یافت نشد**. این گزارش فهرست و آزمون پیشنهادی می‌دهد؛ صورت‌جلسه پذیرش و اثبات استقرار محسوب نمی‌شود.
- تحویل/تست: commit، محیط، حساب نقش‌ها، راهنمای کوتاه، نتیجه هر سناریو، نقص‌های باز و پاسخ کارفرما طبق روال داخلی ثبت شود.
- شواهد: [PLAN](</home/hossein/Desktop/projects/building-management/output/delivery-plan-2026-11-03/delivery-plan.md:86>)، [R0](</home/hossein/Desktop/projects/building-management/docs/delivery/R0-scope-and-reports-contract.md:18>)، [CORE](</home/hossein/Desktop/projects/building-management/docs/طرح اولیه و نیازمندی‌های سیستم (System Requirements)/راهنمای پیاده‌سازی Velora (Velora Implementation Specs)/01-دامنه، اصول و واژه‌نامه.md:54>)

## روش و حدود شواهد

- graphify موجود با ۲۷٬۸۹۸ گره برای یافتن مسیرها query شد؛ گراف بازسازی نشد. نتیجه گراف، راهنمای مراجعه به فایل اصلی است و به‌تنهایی مدرک رفتار runtime نیست. واژه‌های گراف: schedule، wbs، msp، import، calendar، baseline، فعالیت.
- LM Studio محلی با مدل text-embedding-qwen3-embedding-0.6b فعال و ایندکس hybrid تازه شد: ۲٬۴۶۳ سند، ۱۶٬۹۷۰ قطعه، ۱٬۴۶۶ embedding جدید و وضعیت fresh. درخواست اصلی و queryهای هدفمند در پیوست محفوظ‌اند. context عمومی A.7 نتایج معنایی کم‌ربط و هشدار نیاز به بررسی عامل داد؛ دامنه با سند R0/برنامه اصلاح‌شده و متن منابع اصلی رفع ابهام شد، نه با رتبه بازیابی.
- آزمون‌های موجود اصلی: **۱۹۴ موفق**. آزمون‌های موجود تکمیلی: **۱۰۲ موفق و یک شکست**؛ شکست، اختلاف انتظار مجوز is_staff در ایجاد واحد سازمانی است. یک شکست اولیه دیگر متعلق به آماده‌سازی probe ممیزی بود که وضعیت archive را بدون context لازم تنظیم می‌کرد؛ اصلاح شد و نقص محصول شمرده نمی‌شود.
- اجرای probe مشاهده‌گر: نتیجه JSON مرجع است. پاس شدن خود probe فقط یعنی ثبت مشاهدات انجام شد؛ نشانه پاس شدن معیارهای پذیرش محصول نیست.
- پایگاه آزمون جدا به نام test_velora_a7_audit_20261110 استفاده شد. داده اصلی و کد محصول تغییر نکردند. مرورگر، production، CI، broker/worker واقعی و دانلود بایت اسناد بیرونی در این ممیزی آزموده نشدند.
- شواهد قدیمی archive/status-undo در مخزن موجودند؛ در وضعیت فعلی فقط دامنه آزمون‌های انتخاب‌شده دوباره اجرا شد. همه سناریوهای هم‌زمانی و مرورگری آن گزارش‌ها به نتیجه امروز تعمیم داده نشده‌اند.

## پیوست‌ها

- [فهرست ساخت‌یافته ۵۶ قلم](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/requirements.json>)
- [آزمون‌های اصلی](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/focused-tests.log>)
- [آزمون‌های تکمیلی و اختلاف مجوز مرجع](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/additional-tests.log>)
- [مشاهدات واردسازی و نمونه واقعی](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import-probe-observations.json>)
- [روش بازتولید مشاهدات](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/import_probes.py>)
- [هویت و تازگی knowledge](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/knowledge-status.json>)
- [context درخواست اصلی](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/knowledge-context.md>)
- [مسیرهای graphify](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/graph-query.txt>)
- [متن استخراج‌شده سند اصلی](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/evidence/stakeholder-document-5.txt>)

نسخه کد بررسی‌شده: `b4ec9b963586c8222f8ff3f08f5f877b5da309f7`. این ممیزی هیچ تاریخ تحویل یا پذیرش تازه‌ای را تصویب نمی‌کند.
