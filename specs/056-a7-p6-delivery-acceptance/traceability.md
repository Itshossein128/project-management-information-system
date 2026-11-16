# ردیابی نهایی A.7

نسخه منبع: `2090da13f90756e9512070ffcd4feb87dcf5fd7a`. عنوان و معیار هر ردیف عین ممیزی اصلی است. تصمیم انسانی تمام موارد pending است.

M04 تعیین تکلیف دامنه شرطی است؛ آزمون عمومی Excel ادعا نشده است.

## P01 — ثبت مشخصات کامل پروژه

مرجع: FR-PRJ-001؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

یک پروژه واقعی با تمام فیلدها ذخیره و پس از بازگشایی تطبیق شود.

شواهد: `apps/api/core/projects/tests/test_a7_p1_reference_project.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P02 — کد یکتای پروژه

مرجع: FR-PRJ-007؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

کد تکراری با پیام قابل فهم رد شود؛ پروژه نیمه‌کاره ایجاد نشود.

شواهد: `apps/api/core/schedule/tests/test_a7_neg01_duplicate_codes.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P03 — پیش‌نویس، ارسال و چرخه وضعیت

مرجع: FR-PRJ-002/003؛ 008 FR-002/008/010؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

ایجاد به‌صورت پیش‌نویس، ارسال، رد، تصویب، تعلیق و خاتمه با نقش مجاز طی شود.

شواهد: `apps/api/core/projects/tests/test_project_registration_lifecycle.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P04 — شرط فعال‌سازی و تصویب بودجه

مرجع: FR-PRJ-003؛ SC-PRJ-002؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

هر سه نقص جداگانه و هم‌زمان نمایش داده شوند؛ صرف وارد کردن مبلغ پروژه را فعال نکند.

شواهد: `apps/api/core/projects/tests/test_project_activation_feedback.py`, `apps/api/core/projects/tests/test_project_registration_gates.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P05 — جلوگیری از تعهد یا خط مبنای قطعی پیش از تصویب

مرجع: FR-PRJ-004؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

در پیش‌نویس/انتظار تصویب و تعلیق، مسیرهای ایجاد قطعی مسدود باشند؛ تفاوت نسخه وارداتی و مصوب روشن باشد.

شواهد: `apps/api/core/projects/tests/test_project_registration_gates.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P06 — برگه آغاز پروژه

مرجع: FR-PRJ-005؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

هر شش بخش ثبت و از جزئیات پروژه دوباره دیده شود.

شواهد: `apps/api/core/projects/tests/test_project_registration_charter.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P07 — تغییر کنترل‌شده اطلاعات مصوب

مرجع: FR-PRJ-006؛ SC-PRJ-003؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

ویرایش مستقیم رد شود؛ تصویب درخواست مقدار را تغییر دهد و رد/لغو آن مقدار را ثابت نگه دارد.

شواهد: `apps/api/core/projects/tests/test_project_registration_change_request.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P08 — فقط‌خواندنی بودن پروژه بایگانی‌شده

مرجع: 008 FR-009؛ قاعده مرزی FR-PRJ؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

کاربر غیرمدیر سیستم نتواند از هیچ مسیر، از جمله واردسازی، داده پروژه بایگانی‌شده را تغییر دهد.

شواهد: `apps/api/core/schedule/tests/test_a7_p2_import_safety.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P09 — خروج از بایگانی با مقصد و مجوز صحیح

مرجع: FR-RPA-001–006/014؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

فعال/تعلیق/خاتمه به مقصد درست بازگردند؛ کاربر فاقد اختیار و تأیید کهنه رد شود.

شواهد: `apps/api/core/projects/tests/test_project_archive_restore.py`, `apps/api/core/projects/tests/test_project_archive_restore_permissions.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P10 — حفظ سوابق، تکرار ایمن و پیگیری بازگردانی

مرجع: FR-RPA-007–013؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

داده‌ها، تأییدهای قبلی و خط مبنا ثابت بمانند؛ دوبار کلیک یا قطع پاسخ موفقیت دوم نسازد؛ فارسی/انگلیسی در مرورگر بررسی شود.

شواهد: `apps/api/core/projects/tests/test_project_archive_restore_preservation.py`, `apps/api/core/projects/tests/test_project_archive_restore_retries.py`, `apps/api/core/projects/tests/test_project_archive_restore_concurrency.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## P11 — ازسرگیری تعلیق و بازگردانی خاتمه

مرجع: FR-UPS-001–015؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

تعلیق با مجوز پروژه و بازگردانی خاتمه فقط با اختیار مدیر سیستم؛ حفظ داده، تأیید تازه، تکرار و هماهنگی نماها آزموده شود.

شواهد: `apps/api/core/projects/tests/test_project_status_undo.py`, `apps/api/core/projects/tests/test_project_status_undo_permissions.py`, `apps/api/core/projects/tests/test_project_status_undo_concurrency.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W01 — درخت چندسطحی و تفکیک دامنه

مرجع: FR-WBS-001/003؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

حداقل سه سطح واقعی ایجاد و ارتباط پروژه، والد و بسته کاری قابل مشاهده باشد.

شواهد: `apps/api/core/wbs/tests/test_wbs_structure_fields.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W02 — مشخصات و مسئول بسته کاری

مرجع: FR-WBS-002/004؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

مسئول و معیار تکمیل یک بسته ثبت، بازگشایی و به فعالیت/بودجه مرتبط شوند؛ بودجه تفصیلی تعهد مستقل A.7 نیست.

شواهد: `apps/api/core/wbs/tests/test_wbs_structure_fields.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W03 — کد یکتا، والد معتبر و ممنوعیت دور

مرجع: FR-WBS-005؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

کد تکراری، والد پروژه دیگر و انتقال گره زیر فرزند خودش رد شود.

شواهد: `apps/api/core/wbs/tests/test_wbs_cycle_move.py`, `apps/api/core/schedule/tests/test_a7_neg01_duplicate_codes.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W04 — محافظت از گره وابسته

مرجع: FR-WBS-006؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

این حفاظت در حذف دستی، اعمال قالب و جایگزینی وارداتی برقرار باشد و تاریخچه حفظ شود.

شواهد: `apps/api/core/wbs/tests/test_wbs_delete_guards.py`, `apps/api/core/project_templates/tests/test_wbs_template_immutability.py`, `apps/api/core/schedule/tests/test_a7_p2_import_safety.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W05 — قالب مستقل و قابل استفاده مجدد

مرجع: FR-WBS-007؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

قالب روی پروژه جدید اعمال شود؛ ویرایش قالب پروژه قبلی را تغییر ندهد؛ جایگزینی قالب وابسته ایمن باشد.

شواهد: `apps/api/core/project_templates/tests/test_wbs_template_immutability.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W06 — جابه‌جایی، مسیر و کدگذاری مجدد

مرجع: 004 SC-004 و edge cases؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

والد، عمق، ترتیب و کدهای وابسته بعد از جابه‌جایی تطبیق شوند.

شواهد: `apps/api/core/wbs/tests/test_tree_ordering.py`, `apps/api/core/wbs/tests/test_services.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## W07 — عمق، وزن‌ها و هشدار ساختار خالی

مرجع: 004 edge cases؛ 029 edge cases؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

درخت خالی و وزن نامعتبر هشدار بدهد؛ ردیف بیش از عمق مجاز در هر فرمت توضیح و در شمارش کنترل لحاظ شود.

شواهد: `apps/api/core/wbs/tests/test_services.py`, `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## M01 — واحد سازمانی و واحد مالک پروژه

مرجع: FR-DATA-003؛ FR-PRJ-001؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

نقش نویسنده مرجع با A.6 هماهنگ شود؛ تست و توضیح مجوز همسو شوند؛ واحد تازه در ثبت پروژه انتخاب شود.

شواهد: `apps/api/core/projects/tests/test_central_data_owning_unit.py`, `apps/api/core/projects/tests/test_a7_p1_reference_project.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## M02 — نوع قرارداد و واحد اندازه‌گیری قابل مدیریت

مرجع: FR-DATA-003؛ SC-DATA-004؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

مسیر مدیریت مرجع برای کاربر مسئول روشن شود؛ مقادیر حیاتی در API اعتبارسنجی و با کاتالوگ همسو باشند.

شواهد: `apps/api/core/projects/tests/test_a7_p1_reference_project.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## M03 — وضعیت‌های مرجع و چرخه مجاز

مرجع: FR-DATA-003 در برابر FR-PRJ-002؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

تفسیر مرجع قابل مدیریت با چرخه وضعیت مصوب روشن شود؛ وضعیت دلخواه بدون تعریف انتقال به A.7 افزوده نشود.

وضعیت‌های پروژه چرخه ثابت و انتقال‌های مصوب دارند؛ کاتالوگ مرجع مجوز ساخت وضعیت دلخواه برای پروژه نمی‌دهد.

شواهد: `apps/api/core/projects/tests/test_project_registration_lifecycle.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## M04 — جداول و فیلدهای پویا و Excel آنها

مرجع: قابلیت موجود وابسته به اطلاعات پایه؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

اگر در جریان واقعی A.7 استفاده می‌شود، قالب، ردیف خطادار و مجوز آن آزموده شود؛ انتقال مستقل WBS از Excel تعهد جدید است.

شرط استفاده در جریان واقعی A.7 برقرار نیست؛ ورود مستقل WBS از Excel و آزمون عمومی جداول پویا خارج از دامنه این تحویل‌اند. این ردیف تعیین تکلیف دامنه است و ادعای آزمون Excel ندارد.

شواهد: `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S01 — فعالیت متصل به بسته با مدت و تقویم

مرجع: FR-SCH-001؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

فعالیت وارداتی با بسته صحیح، مدت، نقطه عطف، تقویم و مسئول قابل کنترل باشد؛ فیلد پشتیبانی‌نشده صریح اعلام شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S02 — روابط و تأخیر بین فعالیت‌ها

مرجع: FR-SCH-002؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

نوع و تأخیر روابط با منبع در واحد روز/ساعت توافق‌شده برابر باشد؛ پیش‌نیاز ناموجود گزارش شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `apps/api/core/schedule/tests/test_relations.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S03 — تاریخ ناممکن، دور و فعالیت بی‌والد

مرجع: FR-SCH-003؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

دور، پایان پیش از شروع و والد نامعتبر پیش از ثبت رد یا با هشدار قابل تطبیق و تصمیم صریح مدیریت شوند.

شواهد: `apps/api/core/schedule/tests/test_a7_cycle_cancel_acceptance.py`, `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S04 — تفکیک تاریخ برنامه‌ای، واقعی و پیش‌بینی

مرجع: FR-SCH-004؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

برنامه جاری، مصوب، واقعی و پیش‌بینی قاطی نشوند؛ محدوده داده‌های منتقل‌شده از فایل به‌روشنی اعلام شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S05 — نسخه مصوب و قفل‌شده با حفظ تاریخچه

مرجع: FR-SCH-005؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

واردسازی روی پروژه دارای مبنای مصوب تاریخچه را از بین نبرد؛ نسخه جدید فقط طبق سیاست مصوب جاری شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p2_import_safety.py`, `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S06 — درخواست تغییر زمان و نسخه جدید

مرجع: FR-SCH-006؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

تغییر زمان مصوب با حفظ نسخه قبل و اثر نقاط عطف/هزینه/قرارداد ثبت شود؛ تغییر پروژه با تغییر برنامه یکی تلقی نشود.

شواهد: `apps/api/core/schedule/tests/test_schedule_change_request.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S07 — گزارش نقاط عطف، تأخیر و پیش‌بینی پایان

مرجع: FR-SCH-007؛ SC-SCH-003؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

پس از import نمونه، تاریخ‌های چهارگانه و نقطه عطف در گانت/گزارش صحیح باشند؛ کاتالوگ گزارش‌های نهایی A.10 باقی می‌ماند.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `apps/api/core/schedule/tests/test_gantt.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## S08 — اعتبار مسیر بحرانی

مرجع: FR-SCH-008؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

داده ناقص نتیجه معتبر جلوه نکند؛ ورود فایل با فیلدهای ناقص باید نامعتبر/غیرقابل محاسبه نشان دهد.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I01 — پذیرش MPP، MSP XML و P6 XER

مرجع: 029 FR-001/002/022؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

نمونه قابل خواندن هر فرمت قبول و فایل ناخوانا با راهکار روشن رد شود؛ پشتیبانی همه سال‌های MSP ادعا نشود.

شواهد: `apps/api/core/schedule/tests/test_mpp_import.py`, `apps/api/core/schedule/tests/test_msp_import.py`, `apps/api/core/schedule/tests/test_p6_import.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I02 — جریان انتخاب، پیش‌نمایش، تأیید، پیشرفت و نتیجه

مرجع: 029 FR-003؛ مالک: A.7-P4؛ نتیجه: تأیید فنی.

فایل واقعی از بارگذاری تا مشاهده WBS و جمع‌ها در مرورگر طی شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I03 — یکسان بودن تفسیر پیش‌نمایش و ثبت

مرجع: 029 FR-004؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

شمارش، والدها، شناسه‌ها و هشدارهای preview با ثبت نهایی و ارقام کنترل یکسان باشند.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I04 — حفظ کامل داده‌های پشتیبانی‌شده فایل

مرجع: 029 FR-005؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

فهرست فیلدهای پشتیبانی‌شده مشخص شود و انتقال هرکدام در مقصد مصرف داده آزموده شود؛ افت داده خاموش ممنوع.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I05 — Summary به WBS و برگ/نقطه عطف به فعالیت

مرجع: 029 FR-006؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

WBS چندشاخه با والد واقعی برابر باشد؛ فعالیت بی‌والد به بسته نامرتبط متصل نشود.

شواهد: `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I06 — افزودن و برخورد با کدهای تکراری

مرجع: 029 FR-007؛ A.7.03؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

ورود تکراری داده و رابطه تکراری نسازد؛ ردیف skipped و اثر روی baseline روشن و کنترل شود.

شواهد: `apps/api/core/schedule/tests/test_a7_neg01_duplicate_codes.py`, `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I07 — جایگزینی ایمن

مرجع: 029 FR-007/010؛ FR-WBS-006؛ FR-CORE-007؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

با وابستگی به هزینه، پیشرفت، سند یا مبنای قفل‌شده مسدود یا مسیر نسخه‌دار ایمن اجرا شود؛ هیچ سابقه مصوب حذف نشود.

شواهد: `apps/api/core/schedule/tests/test_a7_p2_import_safety.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I08 — پیش‌نمایش بدون تغییر دائمی

مرجع: 029 US1/3؛ FR-003/004؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

باز کردن preview و لغو آن شمار رکوردهای پروژه را تغییر ندهد.

شواهد: `apps/api/core/schedule/tests/test_a7_cycle_cancel_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I09 — Job و پیشرفت پس‌زمینه

مرجع: 029 FR-007/011؛ مالک: A.7-P5؛ نتیجه: تأیید فنی.

در محیط تحویل worker واقعی اجرا شود؛ موفقیت و خطا به وضعیت نهایی برسند و واردسازی بعدی ممکن باشد.

شواهد: `apps/api/core/schedule/tests/test_a7_p5_runtime_preflight.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`, `specs/055-a7-p5-import-operations/evidence/runtime/manifest.json`, `specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml`

## I10 — شمارش‌ها و گزارش هشدار قابل تطبیق

مرجع: 029 FR-007/016؛ A.7.01/04؛ مالک: A.7-P4؛ نتیجه: تأیید فنی.

تعداد ورودی، ایجاد، تکراری، کنارگذاشته و روابط واقعی با علت هر مغایرت و متن هشدارها نمایش داده شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I11 — عضویت، edit_wbs و جداسازی پروژه‌ها

مرجع: 029 FR-007/018؛ FR-CORE-009؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

کاربر غیرمجاز preview/start/result پروژه دیگر را نبیند؛ کنترل وضعیت بایگانی جداگانه P08 است.

شواهد: `apps/api/core/schedule/tests/test_a7_cross_project_schedule_isolation.py`, `apps/api/core/schedule/tests/test_a7_viewer_readonly_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I12 — سقف ۵۰ مگابایت و اصالت فایل

مرجع: 029 FR-008/009؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

فایل بزرگ، خالی یا فایل با پسوند جعلی رد شود و داده پروژه ثابت بماند.

شواهد: `apps/api/core/common/tests/test_validators.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I13 — خطاهای متمایز و قابل اقدام

مرجع: 029 FR-010/013/022؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

هر نوع خطا پیام و راه اصلاح مناسب بدهد؛ فایل رمزدار دور زده نشود.

شواهد: `apps/api/core/schedule/tests/test_mpp_import.py`, `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I14 — اتمی بودن خطا و امکان تلاش بعدی

مرجع: 029 FR-010/011؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

شکست قبل و میانه import هیچ داده نیمه‌کاره نگذارد؛ attempt بعدی به نتیجه برسد.

شواهد: `apps/api/core/schedule/tests/test_a7_p2_import_safety.py`, `apps/api/core/schedule/tests/test_a7_p5_recovery.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`, `specs/055-a7-p5-import-operations/evidence/runtime/manifest.json`, `specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml`

## I15 — زبان فعال و راه بازیابی خطا

مرجع: 029 FR-012/016؛ مالک: A.7-P4؛ نتیجه: تأیید فنی.

کمک، هشدار، نتیجه و خطا در فارسی و انگلیسی مطابق زبان فعال باشد؛ انتخاب فایل دیگر/تلاش مجدد روشن باشد.

شواهد: `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I16 — نمایش پردازش و جلوگیری از ارسال دوباره

مرجع: 029 FR-015؛ مالک: A.7-P4؛ نتیجه: تأیید فنی.

در زمان preview/submit، کلیک، انتخاب و drop فایل دوم هیچ درخواست یا تغییر فایل ناخواسته نسازد.

شواهد: `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I17 — صفحه‌کلید، RTL/LTR و موبایل

مرجع: 029 FR-017؛ SC-008؛ مالک: A.7-P4؛ نتیجه: تأیید فنی.

ورود موفق و بازیابی خطا با صفحه‌کلید در هر دو زبان و عرض موبایل قابل انجام باشد.

شواهد: `apps/api/core/schedule/tests/test_a7_p4_import_experience.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I18 — ردیابی اقدام و نتیجه واردسازی

مرجع: 029 FR-014؛ FR-CORE-003/014؛ مالک: A.7-P2؛ نتیجه: تأیید فنی.

کاربر، زمان، پروژه، فایل، حالت و نتیجه قابل پیگیری و انتساب گره‌ها روشن باشد.

شواهد: `apps/api/core/schedule/tests/test_a7_p2_import_safety.py`, `apps/api/core/schedule/tests/test_a7_p5_lifecycle.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I19 — نگهداری و پاک‌سازی فایل‌ها

مرجع: 029 FR-019؛ مالک: A.7-P5؛ نتیجه: تأیید فنی.

قاعده نگهداری فایل اصلی/مشتق/نتیجه مشخص و اعمال شود؛ دسترسی بین پروژه‌ها بسته بماند.

شواهد: `apps/api/core/schedule/tests/test_a7_p5_retention.py`, `apps/api/core/schedule/tests/test_a7_p5_artifact_privacy.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`, `specs/055-a7-p5-import-operations/evidence/runtime/manifest.json`, `specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml`

## I20 — حد زمان و منابع پردازش

مرجع: 029 FR-020؛ SC-006؛ مالک: A.7-P5؛ نتیجه: تأیید فنی.

فایل سنگین/خراب در حد مشخص تمام شود؛ منابع آزاد و worker برای کار بعدی سالم بماند.

شواهد: `apps/api/core/schedule/tests/test_a7_p5_preparation.py`, `apps/api/core/schedule/tests/test_a7_p5_recovery.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`, `specs/055-a7-p5-import-operations/evidence/runtime/manifest.json`, `specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml`

## I21 — مجموعه نمونه سازگاری و برابری MPP/XML

مرجع: 029 FR-021؛ SC-002/003/005؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

تاریخ، مدت، milestone، درصد، hierarchy، رابطه/lag و هشدارها با داده ذخیره‌شده مقایسه شوند؛ ۹۵٪ فقط برای corpus اعلام‌شده معنی دارد.

شواهد: `apps/api/core/schedule/tests/test_mpp_equivalence.py`, `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## I22 — فایل واقعی کارفرما و ارقام کنترل

مرجع: A.7.01/02؛ R.0.01؛ مالک: A.7-P3؛ نتیجه: تأیید فنی.

WBS، برگ‌ها، روابط، مقادیر مهم و هشدارهای مورد انتظار پیش از import ثبت و پس از آن تطبیق شوند.

شواهد: `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## D01 — ماتریس نمونه، نگاشت و اختلاف‌ها

مرجع: A.7.01؛ مالک: A.7-P1؛ نتیجه: تأیید فنی.

فایل مرجع با hash، نسخه، نگاشت و انتظار هر هشدار ضمیمه شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## D02 — آمادگی محیط واقعی تبدیل و worker

مرجع: A.7.02؛ 029 FR-020؛ مالک: A.7-P5؛ نتیجه: تأیید فنی.

همان نسخه در محیط تحویل با MPXJ/JRE و worker واقعی، فایل کارفرما را پردازش کند.

شواهد: `apps/api/core/schedule/tests/test_a7_p5_runtime_manifest.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`, `specs/055-a7-p5-import-operations/evidence/runtime/manifest.json`, `specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml`

## D03 — آزمون مرورگری یک پروژه مرجع

مرجع: A.7.04؛ SC-PRJ/WBS/SCH/MPP؛ مالک: A.7-P6؛ نتیجه: تأیید فنی.

ایجاد → تصویب → WBS/قالب → preview → import → کنترل جمع‌ها → تکرار/جایگزینی → بایگانی/بازیابی با نقش‌ها ثبت شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`

## D04 — نسخه تحویلی، راهنمای تست و نتیجه پذیرش

مرجع: معیار پذیرش A.7؛ FR-CORE-002/008/009؛ مالک: A.7-P6؛ نتیجه: تأیید فنی.

commit، محیط، حساب نقش‌ها، راهنمای کوتاه، نتیجه هر سناریو، نقص‌های باز و پاسخ کارفرما طبق روال داخلی ثبت شود.

شواهد: `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py`, `specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml`, `specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json`
