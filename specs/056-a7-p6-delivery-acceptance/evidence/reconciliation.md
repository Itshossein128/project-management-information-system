# تطبیق فایل‌های مرجع A.7

نسخه: `2090da13f90756e9512070ffcd4feb87dcf5fd7a`. مرجع ماشینی: `reconciliation.json`.

فایل plan.mpp تغییر نکرده است: ۸۰ وظیفه = ۶ خلاصه + ۷۴ برگ. دو برگ بدون والد شروع/پایان طبق تصمیم ثبت‌شده حذف می‌شوند. از ۸۳ پیوند خام، چهار پیش‌نیاز خلاصه و هفت پیوند وابسته به برگ‌های حذف‌شده کنار گذاشته می‌شوند؛ خروجی ۶ WBS، ۷۲ فعالیت و ۷۲ رابطه است. اولین ورود یک خط مبنای کاری می‌سازد؛ این نسخه تصویب قطعی نیست. ورود افزایشی مجدد هیچ ردیف یا خط مبنای اضافی نمی‌سازد.

## real_data_plan_mpp

مسیر: `real-data/plan.mpp`؛ اندازه: 777216 بایت.
SHA-256: `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`
پیش‌نمایش: {'wbs_count': 6, 'activity_count': 72, 'relation_count': 72, 'warning_count': 9}؛ ذخیره: {'wbs_count': 6, 'activity_count': 72, 'relation_count': 72}.
هشدارها: activity_without_parent, predecessor_is_summary, calendar_not_applied.

## valid_msp_xml

مسیر: `specs/051-a7-p1-project-reference/evidence/fixtures/branch.xml`؛ اندازه: 781 بایت.
SHA-256: `fddc1cacb4eb608c80f0ded9390f3317b31b02e4a52976ebb36808f5c085a6c2`
پیش‌نمایش: {'wbs_count': 1, 'activity_count': 2, 'relation_count': 0}؛ ذخیره: {'wbs_count': 1, 'activity_count': 2, 'relation_count': 0}.
هشدارها: calendar_not_applied.

## valid_p6_xer

مسیر: `specs/051-a7-p1-project-reference/evidence/fixtures/branch.xer`؛ اندازه: 263 بایت.
SHA-256: `a7cae14d13b93abe4c966d48be227deae9935a488dffb06ed71974e155f40469`
پیش‌نمایش: {'wbs_count': 3, 'activity_count': 2, 'relation_count': 0}؛ ذخیره: {'wbs_count': 3, 'activity_count': 2, 'relation_count': 0}.
هشدارها: calendar_not_applied.

## valid_p6_xml

مسیر: `apps/api/core/schedule/tests/fixtures/mpp/duration-test9.xml`؛ اندازه: 58666 بایت.
SHA-256: `8c8dc05c56e3d8b7f69bc45bed2c6756e56116d6c1aff35d10fc8d05e6b375d4`
پیش‌نمایش: {'wbs_count': 0, 'activity_count': 0, 'relation_count': 0}؛ ذخیره: {'wbs_count': 0, 'activity_count': 0, 'relation_count': 0}.
هشدارها: calendar_not_applied, duration_not_whole_days, activity_without_parent, empty_import.

شناسه تاریخی valid_p6_xml نام‌گذاری نادرست دارد: فایل duration-test9.xml در واقع MSPDI است. مدت‌های کسری و فعالیت‌های بدون والد قابل درج نیستند، بنابراین خروجی صحیح صفر/صفر/صفر و هشدار empty_import است. فایل را نمونه موفق P6 XML یا خروجی ۱/۵/۰ معرفی نمی‌کنیم. آزمون منفی جایگزینی خالی، حفظ داده قبلی را جداگانه اثبات می‌کند.

تقویم منبع با هشدار calendar_not_applied همراه است؛ مدت/lag بر مبنای ۴۸۰ دقیقه روز کاری تبدیل می‌شوند. فیلدهای پشتیبانی‌شده و محدودیت‌ها در راهنمای P3 و آزمون برابری MPP/XML ثبت شده‌اند.
