# پرامپت مستقل A6-P4 — پوشش یکسان دسترسی و محرمانگی در همه ماژول‌های موجود

## قرارداد اجرای این پرامپت

این متن، ورودی اجرای همین یک زیر‌فاز با مهارت‌های Spec Kit است. ابتدا مشخصات را بساز و پس از رفع ابهام‌های مؤثر، چرخه را تا پیاده‌سازی و راستی‌آزمایی همین دامنه ادامه بده. به زیر‌فاز بعد وارد نشو. اگر اکنون فقط پرامپت را بررسی می‌کنی و کاربر اجرای آن را نخواسته، خود این متن مجوز شروع تغییر محصول نیست.

ریشه پروژه: /home/hossein/Desktop/projects/building-management
فهرست مبنا: /home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/inventory.json
شرح فازبندی: /home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/implementation-phases.md
گزارش و منابع: /home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/requirements-and-delivery.md
معیارهای مشتری: /home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/acceptance.md
ماتریس حوزه‌ها: /home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/module-access-matrix.md

فهرست مبنا، عکس وضعیت ۱۴ آبان ۱۴۰۵ در commit 2e9a82e97e92ac4410e040298ffbdfba2bfa85ca است؛ پس از اجرای فازهای قبلی تغییر می‌کند. ۱۲۶ تست موفق و سه نقص بازتولیدشده، شاهد تاریخی‌اند و صحت نسخه فعلی را ثابت نمی‌کنند. منابع پیش‌نویس و پیشنهادهای اسناد را تأیید مستقل مشتری جا نزن؛ A6-R54 اختیاری است.

پیش از تفسیر درخواست، AGENTS.md، knowledge/agent-instructions.md و constitution را بخوان و context را با متن کامل همین پرامپت اجرا کن. freshness را بسنج؛ نمایه hybrid را lexical نکن و indexing همزمان نساز. در صورت نیاز فقط سرویس embedding محلی از قبل مجاز را استفاده کن. خطای بازیابی را گزارش کن و منبع اصلی را مستقیم بخوان؛ بدون شاهد کافی تصمیم امنیتی نگیر. Graphify برای یافتن کد مفید است، اما گراف و رتبه بازیابی اثبات اجرای صحیح نیستند. برای بازسازی گراف یا مدل تولیدیِ غیرلازم منابع مصرف نکن.

cwd، HEAD و تغییرات موجود را ثبت و کار نامرتبط را حفظ کن. Feature فعال را به‌صورت پیش‌فرض متعلق به این فاز فرض نکن. Feature همین شناسه را از روی مدارک پیدا کن و اگر واقعاً وجود ندارد، فقط یک Feature جدید با سازوکار نصب‌شده بساز؛ شماره بعدی spec را حدس نزن. نگاشت شناسه این فاز به پوشه Feature و وابستگی‌هایش را ثبت کن. پیش از هر مهارت، FEATURE_DIR منتخب را کنترل کن تا spec دیگری بازنویسی نشود. در صورت ایجاد شاخه، پیشوند پیش‌فرض codex/ باشد. این پرامپت دستور push، merge یا استقرار نیست.

## هویت، هدف و وابستگی این فاز

شناسه: A6-P4
نام کوتاه پیشنهادی Feature: a6-p4-module-access
کاربران: اعضای دارای مجوز و فاقد مجوز، غیرعضو، عضو غیرفعال، مشاهده‌گر، مدیر مجاز، ثبت‌کننده و تأییدکننده دوم.

هدف: سه تحویل داخلی متوالی برای ۲۹ حوزه؛ هر بسته با اصلاح و تست خودش بسته شود. ساخت منطق تجاری جدید فازهای دیگر در این فاز تعهد نمی‌شود.

پیش‌نیاز: خروجی قابل آزمون و تصمیم‌های ثبت‌شده A6-P3 لازم است. مدارک و نتیجه انتقال را پیدا و تطبیق بده؛ تیک tasks به‌تنهایی کفایت نمی‌کند. اگر خروجی لازم واقعاً وجود ندارد، همان پیش‌نیاز را گزارش کن و پنهانی فاز قبلی را از صفر اجرا نکن.

## نیازمندی‌های مرجع و وضعیت تاریخی

ردیف‌های زیر برای فهم شکاف‌اند؛ رفتار فعلی را دوباره از کد اصلی و تست بررسی کن. طراحی فنی را از روی این متن تحمیل نکن.

### A6-R30 — محدود کردن پروژه‌های قابل مشاهده به عضویت فعال/اختیار سازمانی

- وضعیت مبنا: موجود + تست backend مرتبط موفق.
- شاهد تاریخی: ProjectViewSet فهرست را برای عضو فعال محدود می‌کند؛ helper و تست‌های منع غیرعضو وجود دارند و مجموعه منتخب موفق است.
- انتظار تحویل: کارفرما فهرست/جزئیات/API مستقیم دو پروژه را با حساب‌های مجاز و غیرمجاز تست کند.
- آزمون متناظر: کاربرP1 شناسهP2 را در URL عوض کند؛ دادهP2 افشا نشود؛ admin طبق استثنای مصوب مشاهده کند.
- منبع: TEAM, CORE, RPT؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/views.py:132-167؛ /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/project.py:22-71؛ /home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/tests/test_unit_report_permissions.py.

### A6-R33 — رد پیوند به شیء پروژه دیگر و جلوگیری از دورزدن شناسه

- وضعیت مبنا: موجود؛ راستی‌آزمایی تکمیلی لازم.
- شاهد تاریخی: ProjectScopedViewSet و چند serializer پروژه را محدود می‌کنند؛ پوشش همه relationهای تمام ماژول‌ها امروز اثبات نشده است.
- انتظار تحویل: برای create/update و actionها هم پروژه شیء مقصد و پروژه مرجع همسان کنترل شود.
- آزمون متناظر: درP1 شناسه قرارداد/عضو/فایلP2 بدهید؛ درخواست رد و هیچ رابطه ناسازگار ساخته نشود.
- منبع: CORE, BASE؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/common/viewsets.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/project.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/documents/serializers.py.

### A6-R34 — هم‌راستایی منو/دکمه با مجوز مؤثر و کنترل مستقل سرور

- وضعیت مبنا: ناقص / نیازمند اصلاح.
- شاهد تاریخی: usePermission و guardهای سرور موجودند؛ برخی UIها از گروه سراسری و برخی از مجوز پروژه استفاده می‌کنند؛ سناریوی admin فاقد membership باید تست شود.
- انتظار تحویل: پنهان‌کردن دکمه فقط کمک UI باشد؛ API مستقل و admin/عضو/غیرعضو در UI و سرور مطابق ماتریس عمل کنند.
- آزمون متناظر: دکمه ممنوع دیده نشود؛ همان درخواست مستقیم403 شود؛ admin مجاز بدون عضویت هم UI مناسب داشته باشد.
- منبع: CORE, TEAM؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/web/src/app/contexts/project-context.tsx:44-57؛ /home/hossein/Desktop/projects/building-management/apps/api/core/projects/member_views.py:53-61؛ /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/project.py:7-12.

### A6-R35 — اعمال لغو مجوز و تغییر نقش در درخواست و صف بعدی

- وضعیت مبنا: موجود؛ راستی‌آزمایی تکمیلی لازم.
- شاهد تاریخی: مجوز سرور از عضویت فعلی محاسبه می‌شود؛ actor/cache و بررسی پس از lock در مسیرهای آفلاین موجود است. همه موارد لغو همزمان امروز اجرا نشده‌اند.
- انتظار تحویل: تغییر حساب/مجوز، retry و ادامه صف باید با هویت و مجوز فعلی عمل کند و اطلاعات شخص قبلی نمایان نشود.
- آزمون متناظر: در حال آفلاین مجوز را لغو و سپس وصل کنید؛ تغییر ممنوع ارسال نشود و payload با پیام قابل بازیابی حفظ شود.
- منبع: CORE, OFF؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/project.py:34-47؛ /home/hossein/Desktop/projects/building-management/apps/web/src/app/contexts/auth-context.tsx:71-94؛ /home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/unit_report_views.py.

### A6-R38 — کنترل مسیرهای جایگزین، legacy، import/export و actionها

- وضعیت مبنا: ناقص / نیازمند اصلاح.
- شاهد تاریخی: probeهای legacy نشان می‌دهند داشتن guard اصلی به معنی پوشش همه URLها نیست.
- انتظار تحویل: موجودی endpointهای فعال و ماتریس تست مستقل GET/POST/PATCH/DELETE/import/download/approve برای همه ماژول‌ها تحویل شود.
- آزمون متناظر: از مسیر canonical و alias قدیمی همان عملیات را امتحان کنید؛ سیاست یکسان باشد.
- منبع: BASE, CORE؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/config/urls.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/business_meta/permissions.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/inventory/views.py:39-47.

### A6-R39 — نمایش/ویرایش دستمزد و نرخ فقط با مجوز مستقل

- وضعیت مبنا: موجود + تست backend مرتبط موفق.
- شاهد تاریخی: view_wage/edit_wage روی dossier/member/rate/estimate در مسیرهای بررسی‌شده اعمال می‌شوند؛ تست‌های منتخب موفق‌اند.
- انتظار تحویل: در فرم، API، برآورد و خروجی‌های تحویلی همان مرز رعایت شود؛ داده ساختگی برای آزمون مشتری تهیه شود.
- آزمون متناظر: viewer نرخ و مبلغ حساس را نبیند؛ دارندهview فقط بخواند؛ ویرایش فقط باedit مجاز باشد.
- منبع: HR, CORE, RPT؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/hr/capacity_views.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/business_meta/serializers.py:145-181؛ /home/hossein/Desktop/projects/building-management/apps/api/core/hr/tests/test_wage_acl_and_cost_estimate.py.

### A6-R40 — اطلاعات تماس حساس ذی‌نفع مطابق مجوز

- وضعیت مبنا: موجود + تست backend مرتبط موفق.
- شاهد تاریخی: StakeholderSerializer ایمیل/تلفن را برای کاربر فاقد مجوز mask می‌کند؛ تست ACL تماس‌ها موفق است.
- انتظار تحویل: ماتریس نقشِ مجاز مشاهده تماس به کارفرما اعلام و همین سیاست در گزارش وضعیت حفظ شود.
- آزمون متناظر: کاربرعادی و کاربرview_sensitive_contacts یک رکورد را بخوانند؛ فقط دومی تماس را ببیند.
- منبع: CORE, RPT, COL؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/stakeholder_views.py:15-65؛ /home/hossein/Desktop/projects/building-management/apps/api/core/projects/tests/test_stakeholder_contacts_acl.py.

### A6-R41 — اطلاعات اعضا و جست‌وجوی افراد با سیاست اعلام‌شده

- وضعیت مبنا: ناقص / نیازمند اصلاح.
- شاهد تاریخی: lookup برای هر authenticated نام/ایمیل/موبایل را برمی‌گرداند؛ roster نیز اطلاعات تماس دارد. سیاست این داده‌ها باید مستقل از تماس ذی‌نفع روشن شود.
- انتظار تحویل: تعیین شود چه کسی دایرکتوری سازمان/پروژه و اطلاعات تماس افراد را می‌بیند؛ فیلتر و redaction مطابق همان سیاست اعمال شود.
- آزمون متناظر: غیرعضو و مشاهده‌گر جست‌وجو کنند؛ فقط داده مجاز برای وظیفه تخصیص عضو نمایش داده شود.
- منبع: CORE, TEAM, HR؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/member_views.py:170-197؛ /home/hossein/Desktop/projects/building-management/apps/api/core/projects/member_serializers.py:20-64.

### A6-R42 — محرمانگی گزارش/داشبورد/خروجی در عمق داده

- وضعیت مبنا: ناقص / نیازمند اصلاح.
- شاهد تاریخی: بخشی از مسیرها redaction دارند؛ _redact_wage_fields در catalog فقط کلید wage سطح اول را حذف می‌کند و محرمانگی همه ساختارهای تو‌در‌تو اثبات نشده است.
- انتظار تحویل: فیلد حساس در خروجی/تجمیع/drill و export جدید با همان مجوز مرجع پنهان شود؛ نشت واقعی از روی این تابع به‌تنهایی ادعا نمی‌شود.
- آزمون متناظر: گزارش دارای داده حساس تو‌در‌تو را با دو نقش بگیرید؛ عدد و متن و فایل غیرمجاز افشا نشود.
- منبع: RPT, CORE, HR؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/services/report_export_service.py:194-206؛ /home/hossein/Desktop/projects/building-management/apps/api/core/projects/report_views.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/hr/tests/test_wage_acl_and_cost_estimate.py.

### A6-R43 — پیوست و لینک دانلود تابع دسترسی منبع و پروژه

- وضعیت مبنا: موجود؛ راستی‌آزمایی تکمیلی لازم.
- شاهد تاریخی: مجوز عضویت فعال و uploader برای فایل عمومی و کنترل signing مکاتبات موجودند؛ تست signing منتخب موفق است. منطق عمومی فایل به‌تنهایی ACL تمام منابع محرمانه را ثابت نمی‌کند.
- انتظار تحویل: مجوز مشاهده منبع، دانلود، انقضای لینک و لغو عضویت در مسیرهای فایل/خروجی تحویلی بازآزمایی شوند.
- آزمون متناظر: فایلP1 و سند محدود را با غیرعضو/عضو فاقد مجوز بگیرید؛ لینک باید مطابق سیاست رد یا کوتاه‌عمر باشد.
- منبع: CORE, RPT, COL؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/storage/permissions.py:10-32؛ /home/hossein/Desktop/projects/building-management/apps/api/core/storage/views.py:23-80؛ /home/hossein/Desktop/projects/building-management/apps/api/core/documents/tests/test_attachment_signing_security.py.

### A6-R44 — ثبت‌کننده، تأییدکننده نهاییِ تنها نباشد

- وضعیت مبنا: ناقص / نیازمند اصلاح.
- شاهد تاریخی: SoD برای هزینه واقعی، بودجه، IPC و workflow وجود دارد؛ approve_commitment هنوز actor نمی‌گیرد و guard یکسان در آن دیده نشد.
- انتظار تحویل: فهرست تراکنش مهم و مسیرهای final approve تثبیت و guard در همه مسیرهای فعال اعمال شود؛ محاسبات مالی جدید جزءA.6 نیست.
- آزمون متناظر: ثبت‌کننده عادی نتواند تعهد/هزینه/IPC خود را تنها نهایی کند؛ بازبین دومِ مجاز بتواند.
- منبع: RPT, CORE؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/sod.py:14-27؛ /home/hossein/Desktop/projects/building-management/apps/api/core/cost_control/cbs_services.py:57-63؛ /home/hossein/Desktop/projects/building-management/apps/api/core/workflow/services/instance_service.py:203-206.

### A6-R45 — اختیار اقدام گردش‌کار تابع نقش و پروژه باشد

- وضعیت مبنا: موجود؛ راستی‌آزمایی تکمیلی لازم.
- شاهد تاریخی: engine مرحله/تأییدکننده و مجوز پروژه دارد؛ اتصال کامل هر موضوع و چرخه سند درA.9 کار مستقلی است.
- انتظار تحویل: A.6، حق اقدام و بازبینی را روی گردش‌های موجود کنترل کند؛ هر اتصال جدیدA.5/A.9 نیز همین آزمون‌ها را پاس کند.
- آزمون متناظر: شخص خارج از مرحله یا پروژه نتواند تأیید/برگشت دهد؛ مسئول همان مرحله بتواند.
- منبع: COL, RPT؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/workflow/services/instance_service.py؛ /home/hossein/Desktop/projects/building-management/apps/api/core/workflow/views.py.

### A6-R46 — استثناهای superuser و داده فاقد ثبت‌کننده روشن و قابل ردیابی باشند

- وضعیت مبنا: ناقص / نیازمند اصلاح.
- شاهد تاریخی: helper برای superuser یا created_by=None عبور می‌کند؛ این رفتار نباید به معنی تفکیک وظیفه بی‌استثنا اعلام شود.
- انتظار تحویل: سیاست استثنا، حساب اضطراری، دلیل و مدرک ممیزی تأیید شود؛ داده جدید سازنده مشخص داشته باشد.
- آزمون متناظر: با حساب عادی و اضطراری و رکورد بدون سازنده تست کنید؛ نتیجه و مجوز استثنا مطابق قرارداد ثبت شود.
- منبع: RPT, CORE, TEAM؛ مسیرهای راهنمای بررسی: /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/sod.py:14-27؛ /home/hossein/Desktop/projects/building-management/apps/api/core/permissions/tests/test_sod.py.

## نتیجه‌های لازم در همین فاز

1. اجرای سیاست نهایی P1 روی تمام عملیات موجود، مسیرهای مستقیم، قدیمی، ورود/خروج فایل و اقدامات پس‌زمینه؛ جلوگیری از استفاده شناسه پروژه دیگر و لغو مجوز در صف آفلاین.
2. یکسان‌سازی منو و دکمه با مجوز مؤثر، همراه کنترل مستقل سرور؛ پوشش نقش بدون عضویت، عضو غیرفعال، مشاهده‌گر و استثنای سازمانی.
3. محرمانگی حقوق/نرخ، تماس افراد و ذی‌نفعان، گزارش تو‌در‌تو، داشبورد، پیوست و دانلود مطابق مجوز منبع.
4. تکمیل اختیار اقدام در گردش‌های موجود و منع تأیید نهایی توسط ثبت‌کننده عادی، از جمله تعهدات؛ ثبت استثناهای مجاز و رویدادهای حساس.

## تصمیم‌های محصول و پیش‌نیازهای روشن‌شدن دامنه

- ماتریس سیاست P1 و قرارداد نقش/مجوز P2 و وضعیت P3 مبنای واحدند؛ مقررات موازی از روی نام گروه یا دکمه‌های موجود اختراع نکن.
- فهرست عملیات را از URL/action و کار واقعی هر ماژول استخراج کن؛ permission catalog یا عنوان ماژول معادل پوشش تمام مسیرها نیست.
- درباره دسترسی دایرکتوری افراد، اطلاعات حساس و استثناهای superuser/سازنده نامعلوم فقط تصمیم ثبت‌شده را اجرا کن؛ ابهام مؤثر را پیش از پیاده‌سازی همان بخش حل کن.

## سناریوهای پذیرش اختصاصی

### A6-P4-AC01 — استقلال دو پروژه

شرایط و اقدام: عضو مجاز A، شناسه رکورد، پیوند یا فایل B را در خواندن/ثبت/ویرایش/اقدام وارد می‌کند.

نتیجه مورد انتظار: داده یا تغییر خارج از محدوده مجاز رخ ندهد؛ اشیای مرجع نیز به پروژه صحیح محدود شوند؛ نتیجه مجاز همان عملیات در A موفق بماند.

### A6-P4-AC02 — مسیر مستقیم و قدیمی

شرایط و اقدام: دکمه برای عضو فاقد مجوز پنهان است ولی درخواست مستقیم، مسیر قدیمی، ورود یا خروج فایل را امتحان می‌کند.

نتیجه مورد انتظار: کنترل مستقل سرور مطابق ماتریس اعمال شود؛ مسیر جایگزین یا سراسری اجازه بیشتری نسازد؛ مرجع عمومی واقعاً مشترک به اشتباه پروژه‌ای فرض نشود.

### A6-P4-AC03 — لغو در حین کار

شرایط و اقدام: عضویت یا مجوز در زمانی که صف آفلاین، retry یا اقدام در جریان است لغو می‌شود.

نتیجه مورد انتظار: عملیات بعدی طبق مجوز و هویت فعلی بررسی شود؛ تعویض حساب عملیات شخص قبلی را به نام دیگری نفرستد؛ race حساس مرتبط آزموده شود.

### A6-P4-AC04 — فیلد و خروجی حساس

شرایط و اقدام: دو نقش با دسترسی متفاوت گزارش، داشبورد، اطلاعات تماس، حقوق/نرخ، خروجی و داده تو‌در‌تو را می‌خوانند.

نتیجه مورد انتظار: نقش فاقد اختیار اطلاعات حساس را در جزئیات، تجمیع، drill یا فایل دریافت نکند؛ داده مجازِ نقش دیگر حذف یا تحریف نشود.

### A6-P4-AC05 — فایل و منبع

شرایط و اقدام: کاربر لینک یا شناسه فایل منبعی خارج از مجوز خود را درخواست می‌کند یا پس از لغو عضویت دوباره لینک می‌خواهد.

نتیجه مورد انتظار: صدور لینک و دانلود طبق سیاست مجوز منبع و پروژه و عمر لینک رفتار کنند؛ صرف عضویت عمومی مجوز منبع محرمانه تلقی نشود؛ فایل واقعی در محیط آزمون بررسی شود.

### A6-P4-AC06 — ثبت‌کننده و تأییدکننده

شرایط و اقدام: ثبت‌کننده عادی تعهد یا تراکنش مهم خودش را نهایی می‌کند؛ سپس شخص دوم مجاز اقدام می‌کند.

نتیجه مورد انتظار: اولی طبق قرارداد تفکیک وظیفه رد و دومی مجاز باشد؛ مسیر approve_commitment و اقدام مستقیم هم پوشش داده شوند؛ استثنای اضطراری محدود و قابل ممیزی باشد.

### A6-P4-AC07 — راهنمای UI و کنترل سرور

شرایط و اقدام: نقش، استثنا یا پروژه جاری تغییر می‌کند.

نتیجه مورد انتظار: منو و دکمه مطابق اختیار فعلی شوند؛ مدیر دارای استثنای مصوب بی‌دلیل در UI مسدود نشود و ظاهر مجاز نتواند منع سرور را دور بزند.

## بسته‌های داخلی اجباری و پوشش حوزه‌ها

این سه بسته درون همین Feature هستند. در plan/tasks برای هر کدام ردیابی مستقل داشته باش؛ بسته قبلی و تست متأثر آن را پیش از بعدی ببند. فهرست ۲۹ حوزه سرنخ است؛ تمام URL/actionهای واقعاً فعال باید با روش و نقش و پروژه در ماتریس بیایند. مورد ناموجود با دلیل N/A ثبت شود؛ اجرا نشده را سبز نکن.

### بسته ۱: حساب، پروژه و کارگاه

- M01 — حساب و نشست: ورود، تمدید، خروج، بازیابی، ساخت حساب، فهرست و assignments؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/authentication/urls.py.
- M02 — عضویت، نقش و سمت: members/permissions/positions، role CRUD، کاتالوگ مجوز؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/urls.py.
- M03 — پروژه و چرخه عمر: فهرست، جزئیات، ایجاد، تغییر وضعیت، بازگردانی، منشور و درخواست تغییر؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/urls.py.
- M04 — قالب و پیکربندی گزارش: قالب عمومی/پروژه، ساخت از قالب، ذخیره و تنظیم گزارش؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/project_templates/urls.py.
- M05 — اطلاعات مرجع سازمانی: خواندن و تغییر مرجع‌های مشترک و دسترسی HR/admin؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/master_data/urls.py.
- M06 — جداول پویا و روابط: تعریف جدول/فیلد، ردیف، ورود/خروج فایل و روابط؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/business_meta/views.py.
- M07 — ساختار شکست کار: مشاهده، ایجاد، ویرایش، حذف و پیوند WBS؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/wbs/urls.py.
- M08 — برنامه زمان‌بندی: فعالیت، پیشرفت، تأیید و ورود/خروج برنامه موجود؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/schedule/urls.py.
- M09 — گزارش روزانه کارگاه: خواندن، ثبت، ویرایش، وضعیت، Excel/PDF و همگام‌سازی؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/urls.py.
- M10 — بتن و عملیات اجرایی: ثبت و مشاهده عملیات، پیوند پروژه و گزارش؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/concrete_operations/urls.py.
- M14 — گزارش واحد و قرنطینه: مشاهده/ثبت گزارش، Excel، تأیید و صف قرنطینه؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/urls.py.

### بسته ۲: مالی، قرارداد و منابع

- M13 — منابع انسانی: پرونده، تخصیص، ظرفیت و داده دستمزد/نرخ؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/hr/urls.py.
- M15 — هزینه و بودجه: ثبت، اصلاح، تصویب، تعهد، قفل مالی و تفکیک وظیفه؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/cost_control/urls.py.
- M16 — جریان نقدی: پروژه و مسیرهای سراسری، خواندن/نوشتن و خروجی موجود؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/cash_flow/urls.py.
- M17 — قرارداد و صورت‌وضعیت: قرارداد، IPC، ادعا، ثبت/ویرایش/تأیید و پیوست؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/contracts/urls.py.
- M18 — پیمانکار جزء: پرونده و عملیات پیمانکار مرتبط با پروژه؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/subcontractors/urls.py.
- M19 — خرید و تدارکات: درخواست، سفارش، تأیید، تأمین و پیوست؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/procurement/urls.py.
- M20 — انبار و منابع: مسیرهای پروژه و قدیمی سراسری، کالا و تراکنش؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/inventory/urls.py.
- M21 — منابع پروژه: خواندن، ثبت و تغییر منابع/نرخ در مسیرهای موجود؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/resources/urls.py.
- M26 — اقتصادی: تحلیل پروژه و مسیرهای سراسری موجود؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/economic/urls.py.

### بسته ۳: اسناد، تعاملات و خروجی‌های مدیریتی

- M11 — ریسک: خواندن، تغییر، ارزیابی و پیوند ریسک؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/risk/urls.py.
- M12 — پشتیبانی تصمیم: مشاهده و تغییر سناریو/تحلیل موجود؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/decision_support/urls.py.
- M22 — اسناد و مکاتبات: فهرست، ویرایش، نسخه/وضعیت، مکاتبه و امضای لینک؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/documents/urls.py.
- M23 — گردش‌کار: تعریف، شروع، اقدام مرحله، نقش مسئول و SoD؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/workflow/urls.py.
- M24 — ذی‌نفع و ارتباطات: ذی‌نفع، ماتریس، برنامه ارتباطی و تماس حساس؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/stakeholder_views.py.
- M25 — داشبورد، گزارش و سبد: KPI/drill، role pack، گزارش، خروجی، سبد چند پروژه؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/projects/report_views.py.
- M27 — هشدار و اعلان: اعلان فردی/پروژه‌ای، مشاهده/تغییر وضعیت و هشدار؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/notifications/urls.py.
- M28 — ذخیره‌سازی و دانلود: آپلود، ثبت نهایی، لینک و دسترسی منبع فایل؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/storage/urls.py.
- M29 — ممیزی و مدیریت: ثبت رویداد حساس، مخفی‌سازی راز و مشاهده تاریخچه مجاز؛ مرجع ناوبری: /home/hossein/Desktop/projects/building-management/apps/api/core/audit/middleware.py.

## مرز با فازهای دیگر

تمام عملیات موجود در ۲۹ حوزه در دامنه‌اند؛ ساخت محاسبات مالی جدید، گزارش‌ساز جدید، گردش تجاری یا اتصال تعاملات جدید متعلق به فازهای دیگر نیست. یک گزارش حساس موجود باید اصلاح شود، اما ناقص بودن محتوای تجاری آن مجوز گسترش A.6 نیست.

علاوه بر ردیف‌های اصلی، پوشش فراگیر A6-R10/R31/R32/R36/R37 از P1 و لغو/نشست از P3 باید اینجا بسته شود. رعایت قرارداد P2 در همه مصرف‌کنندگان لازم است. رخدادهای حساس به هسته تاریخچه متصل شوند؛ صفحه و دوام نهایی ممیزی در P5 است.

نکته اجرایی اختصاصی: این فاز یک Feature با سه بسته داخلی متوالی است؛ به ازای هر بسته taskها و شواهد جدا ثبت کن و پس از سبز شدن به بعدی برو. طبقه‌بندی نقص: سیاست، دامنه پروژه، فیلد حساس، اقدام/SoD، فایل، UI، صف/نشست. تست‌های موفق قبلی wage/contact/signing را حفظ کن، اما mocks امضای فایل اثبات سرویس فایل واقعی نیستند.

## ترتیب استفاده از مهارت‌ها

۱. `speckit-specify`: فقط همین Feature را مشخص کن؛ کاربران، ارزش، رفتار و سناریوهای قابل آزمون را بنویس. FR/SCها را به A6-Rها وصل کن. وضعیت موجود را با نیاز مطلوب قاطی نکن و جزئیات فنی را به plan بسپار.
۲. `speckit-clarify`: اسکن ابهام انجام بده؛ پاسخ ثبت‌شده قبلی را دوباره سؤال نکن. فقط ابهام مؤثر و بی‌پاسخ در اختیار، محرمانگی یا دامنه را مطرح کن؛ سؤال لازم را با علت و اثر گزینه‌ها بپرس و وابستگی مربوط را تا پاسخ حدس نزن.
۳. `speckit-plan`: با معماری واقعی پروژه، ساختار داده، قرارداد UI/API، مهاجرت و سازگاری، راه بازگشت و روش آزمون را طراحی کن. سازوکار موجود را توسعه بده؛ سامانه موازی و بازنویسی نامرتبط نساز.
۴. `speckit-tasks`: taskهای ردیابی‌پذیر بر اساس داستان و وابستگی بساز؛ اصلاح، تست مثبت/منفی، فرم، خطا و مستندات را پوشش بده. موارد موجود را با شاهد به بازآزمایی یا یکپارچه‌سازی تبدیل کن، نه ساخت دوباره.
۵. `speckit-analyze`: پس از تکمیل tasks و فقط به‌صورت خواندنی اجرا کن. اگر تعارض مهم یافت شد، خارج از این مهارت و در گام اصلاح مستقلِ همین دامنه، artifact مربوط را اصلاح و تحلیل را دوباره اجرا کن؛ داخل analyze فایل تغییر نده. این پرامپت اجازه همان اصلاح‌های لازم داخل دامنه را می‌دهد؛ تغییر سیاست حل‌نشده نیازمند پاسخ است.
۶. `speckit-implement`: پس از رفع تعارض مسدودکننده اجرا کن؛ آزمون بازتولید نقص پیش از اصلاح و نتیجه پس از اصلاح ثبت شود. task با شاهد تکمیل شود، نه صرفاً با وجود کد.
۷. `speckit-converge`: فقط پس از اجرای implement روی tasks کامل اجرا کن. این مهارت فقط کار باقی‌مانده را به انتهای tasks اضافه می‌کند؛ spec، plan و کد را تغییر ندهد. اگر task افزود، برای اجرای آن‌ها دوباره `speckit-implement` را واقعاً اجرا و سپس converge را تکرار کن. اگر نیاز جدیدی خارج از artifacts پیدا شد، آن را جدا ثبت کن؛ converge ابزار گسترش دامنه نیست. در نبود شکاف، tasks بدون تغییر بماند.
۸. جمع‌بندی با شواهد نسخه نهایی: نتیجه واقعی تست‌ها، مسیر Feature، ردیف‌های پوشش‌داده‌شده، محدودیت و شرط انتقال به فاز بعد. hooks و پیش‌نیازهای هر مهارت را طبق SKILL.md نصب‌شده رعایت کن؛ صرف نوشتن نام مهارت به معنی اجرای آن نیست.

## قواعد آزمون و تحویل مشترک

- هر مرحله شامل API و فرم قابل استفاده، پیام خطای روشن، فارسی/انگلیسی و تست مرتبط خودش است؛ آزمون نهایی جای آزمون حین توسعه را نمی‌گیرد.
- حداقل دو پروژه مستقل، عضو مجاز/فاقد مجوز، غیرعضو، عضو غیرفعال، مشاهده‌گر، چندنقشی، استثنای اعطا/منع و مدیر دارای استثنای مصوب را متناسب با سناریو استفاده کن. نتیجه مثبت را کنار نتیجه منفی ثبت کن؛ نوع سیاست سازمانی را در spec تعیین کن.
- Django با pytest و پایگاه تست مستقل اجرا شود؛ پایگاه واقعی را reset یا حذف نکن. به Redis/PostgreSQL و تنظیمات واقعی توجه کن. Django 4.2 را با نصب requirements-dev ارتقا نده. typecheck، تست‌های بک‌اند، مرورگر، migration و سرویس واقعی شواهد متفاوت‌اند. خرابی قدیمی را بدون بازتولید، نامرتبط اعلام نکن.
- تغییر مدل، مهاجرت سازگار و آزمون حفظ داده/بازگشتِ مناسب می‌خواهد. حساب یا عضو خروج‌کرده، سابقه تاریخی را از بین نبرد. secret یا داده شخصی واقعی وارد log و artifact نشود.
- برای این تغییرات دسترسی، آزمون‌های معنادار امنیتی و رفتاری ضروری‌اند؛ تستی که همان کد را تکرار می‌کند یا فقط mock و checkbox را می‌سنجد کافی نیست.
- در Feature، نگاشت A6-R → FR/Story → Task → Test → شاهد نسخه نهایی بساز. برای هر ردیف مشخص کن چه چیزی حفظ، اصلاح یا اضافه شد؛ پوشش جزئی را کامل معرفی نکن.
- موارد انجام‌شده، تست‌نشده، وابسته به سرویس/پاسخ انسانی و خارج از دامنه را جدا اعلام کن. پذیرش کارفرما و انتشار محصول را خودکار فرض نکن. وضعیت snapshots قدیمی را تغییر نده؛ گزارش جدید را با نسخه جدید ثبت کن.

## شرط پایان و گزارش اجباری این فاز

در هر بسته ماژولی، آزمون مثبت و منفی و دو پروژه مستقل موفق باشد؛ مسیر مستقیم API، دانلود و عملیات جایگزین اختیار بیشتری از سیاست مصوب ندهند.

پایان کار، مسیر Feature منتخب و artifacts واقعی، نسخه نهایی، نتیجه آخرین analyze و converge، taskهای باقی‌مانده، شواهد آزمون و راه نمایش خروجی را گزارش کن. برای هر الزام «حفظ شد / اصلاح شد / اضافه شد / جزئی باقی است» را با شاهد مشخص کن. قرارداد مورد نیاز فاز بعد و تصمیم‌های حل‌نشده را تحویل بده؛ بدون نتیجه قابل اثبات، فاز را complete اعلام نکن. پذیرش یا انتشار واقعی را از آماده‌شدن فنی جدا نگه دار.
