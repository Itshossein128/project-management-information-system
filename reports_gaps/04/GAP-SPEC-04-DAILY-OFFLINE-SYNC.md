# گزارش شکاف‌های ثبت آفلاین، همگام‌سازی دسته‌ای و رفع تعارض

**شناسه:** `GAP-SPEC-04-DAILY-OFFLINE-SYNC`  
**تاریخ ارزیابی:** 2026-10-27، منطقه زمانی Asia/Tehran  
**مخزن:** `/home/hossein/Desktop/projects/building-management`  
**مبنای کد:** شاخه `develop`، commit `765e54b` به‌همراه working tree هنگام بررسی  
**سند هدف:** [SPEC-04](/home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-04-DAILY-OFFLINE-SYNC.md)  
**نوع کار:** ممیزی و بازتولید؛ بدون اصلاح پیاده‌سازی محصول.

## ۱. نتیجه ارزیابی

**SPEC-04 در وضعیت فعلی قابل تأیید نیست.** IndexedDB، صف، تشخیص اتصال، اجرای خودکار sync، endpoint دسته‌ای و صفحه تعارض وجود دارند؛ اما زنجیره «ثبت ردیف → نگهداری قابل بازیابی → ارسال دقیق همان عملیات → تأیید همان ردیف → اصلاح خطا یا بازیابی تعارض» کامل نیست.

۱۳ شکاف ثبت شده است: **۹ مورد P1** و **۴ مورد P2**. P1 یعنی خطر از دست رفتن/تغییر نامعتبر داده یا مسدود شدن سناریوی اصلی؛ P2 یعنی نقص قرارداد، نمایش، اتمیک بودن خطا یا پوشش اثبات. این اولویت‌بندی پیشنهاد ممیزی است.

مهم‌ترین یافته‌ها:

- ردیف جدید با endpoint دارای `/` پایانی از parser عبور نمی‌کند؛ در شرایط بازتولید، از batch حذف می‌شود ولی صف با پاسخ موفق پاک می‌شود.
- ویرایش ردیف بدون snapshot محلی می‌تواند `activities: []` بسازد؛ سرور بخش ارسال‌شده را حذف و دوباره درج می‌کند.
- `sync-batch` محدودیت `derived_readonly` مسیر عادی را دور می‌زند؛ حذف ردیف تجمیعی در دیتابیس تست بازتولید شد.
- بررسی وضعیت گزارش خارج از قفل انجام می‌شود؛ در بازتولید ترتیب رخدادها، تأییدِ بین بررسی و ذخیره از بین رفت. مسیر ensure نیز وضعیت تأییدشده را دوباره کنترل نمی‌کند.
- مسیر فعلی ثبت گزارش واحد تخصصی به صف آفلاین متصل نیست؛ بیشتر زیرساخت آفلاین به فرم قدیمی گزارش پروژه متصل است.

## ۲. روش بررسی و مرز شواهد

۱. سند هدف، قرارداد endpoint، مدل، serializer، سرویس batch، aggregation، صف و فرم‌های فعلی بررسی شدند. گراف موجود Graphify برای یافتن فایل‌های مرتبط query شد؛ خروجی آن نقشه راه بود و ادعاهای گزارش با فایل جاری کنترل شدند. نسخه CLI با skill متفاوت بود؛ گراف بازسازی و بسته‌ای ارتقا داده نشد.

۲. مجموعه موجود `field_reports/tests/test_sync_batch.py` روی PostgreSQL با دیتابیس تست مستقل اجرا شد: **۱۷ passed، دو warning، 87.07 ثانیه**. این نتیجه تأیید پوشش موجود است؛ اثبات انتهابه‌انتهای SPEC-04 نیست. [لاگ اجرا](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/pytest-sync-batch.txt)

۳. چهار probe بک‌اند با APIClient واقعی و دیتابیس تست اجرا شدند: **۴ passed، 88.47 ثانیه**؛ هر چهار رفتار معیوب را تأیید کردند. شش سناریوی فرانت‌اند با اجرای TypeScript جاری و مرزهای mock برای شبکه/ذخیره‌سازی با exit code صفر تمام شدند؛ پنج مورد رفتار ناقص و یک مورد کنترل مثبت بود. **PASS probe معیوب یعنی نقص مشاهده شده است، نه اینکه قابلیت درست کار می‌کند.** [کد probe بک‌اند](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/probe_backend.py)، [کد probe فرانت‌اند](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/probe_frontend.cjs)

۴. تست مرورگر، قطع شبکه واقعی، بسته‌شدن مرورگر، ماندگاری IndexedDB در مرورگر، Service Worker تولید، چند تب، و رقابت دو اتصال مستقل PostgreSQL اجرا نشدند. probe رقابت بک‌اند یک interleaving قطعی با monkeypatch است؛ زمان‌بندی همزمان واقعی را اثبات نمی‌کند، ولی نبود بررسی مجدد و اثر ذخیره instance قدیمی را نشان می‌دهد.

۵. دو تغییر قبلی در `apps/web/playwright-report/index.html` و `specs/034-daily-lifecycle-lock/tasks.md` مبنای نتیجه‌گیری نبودند و تغییر داده نشدند. فایل موقت probe در محل تست‌های بک‌اند پس از اجرا حذف شد؛ نسخه قابل بازتولید آن در همین پوشه نگهداری شده است.

## ۳. پوشش معیارهای پذیرش

- **US-DR-15 / سناریو ۱؛ تشخیص قطعی و Client UUID:** تشخیص و ذخیره در صف قدیمی وجود دارد؛ مسیر واحد تخصصی و شناسه پایدار ردیف ناقص‌اند. مرتبط: G01، G07.
- **US-DR-15 / سناریو ۲؛ ابر زرد کنار ردیف:** اجزای نمایش وضعیت وجود دارند؛ ردیف جدید به وضعیت صف متصل نمی‌شود و نماد pending نیز ساعت است. مرتبط: G07.
- **US-DR-15 / سناریو ۳؛ حفظ و بازیابی بعد از refresh:** store پایدار وجود دارد؛ hydration ردیف‌ها به فرم و بازیابی عملیات `syncing` کامل نیست. مرتبط: G08، G11. ماندگاری واقعی مرورگر تأیید نشده است.
- **US-DR-16 / سناریو ۱؛ ارسال ۱۰ عملیات و `synced_ids`:** endpoint و trigger وجود دارند؛ تبدیل عملیات می‌تواند آن‌ها را حذف یا تغییر دهد و wire contract پاسخ متفاوت است. مرتبط: G02، G03، G09.
- **US-DR-16 / سناریو ۲؛ گزارش approved و بازیابی تعارض:** گزارش از پیش approved معمولاً conflict می‌شود؛ کدهای قرارداد، رقابت با تأیید و بازیابی امن داده محلی ناقص‌اند. مرتبط: G05، G09، G10.
- **US-DR-16 / سناریو ۳؛ خطای ردیف، اصلاح و retry:** دکمه retry وجود دارد؛ خطای فیلد و هدف‌گیری ردیف و بازگرداندن failed به pending در دکمه جدول ناقص است. مرتبط: G06.
- **محدودیت معماری 028:** ایجاد مستقیم عادی رد می‌شود و شاخه جدید batch از ensure استفاده می‌کند؛ اما منبع تخصصی در آفلاین پوشش ندارد و شاخه گزارش موجود قابل دور زدن است. ساخت shell خودکار از طریق ensure به‌تنهایی به عنوان نقض معماری شمرده نشده است. مرتبط: G01، G04، G12.

## ۴. یافته‌های تفصیلی

### G01 — P1 — ثبت آفلاین به مسیر فعلی واحد تخصصی متصل نیست

**انتظار:** کاربر در محل اصلی ثبت فعالیت، نفرات و مصالح بتواند عملیات را آفلاین ادامه دهد؛ محدودیت 028 نیز حفظ شود.

**شاهد:** [SectionActivities:107](/home/hossein/Desktop/projects/building-management/apps/web/src/components/department/section-activities.tsx:107) از mutationهای واحد استفاده می‌کند. [queries:559](/home/hossein/Desktop/projects/building-management/apps/web/src/app/hooks/queries.ts:559) مستقیماً `createUnitReportActivity` را فراخوانی می‌کند و [unit-reports:342](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/unit-reports.ts:342) درخواست شبکه می‌فرستد. در components/department و API واحد، اتصال به `offlineWrite`، IndexedDB یا صف یافت نشد. `EntityType` نیز فقط موجودیت‌های قدیمی را دارد: [offlineDB:33](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineDB.ts:33).

در مقابل، صف از [useDailyReportForm:21](/home/hossein/Desktop/projects/building-management/apps/web/src/app/hooks/useDailyReportForm.ts:21) و تب‌های قدیمی گزارش پروژه فراخوانی می‌شود؛ نمای فعلی گزارش پروژه ردیف‌ها را read-only می‌گذارد: [daily-report-view:206](/home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-report-view.tsx:206).

**اثر:** وجود صف قدیمی به معنای کارکرد آفلاین محصول فعلی نیست. رفتار دقیق pause/retry کتابخانه mutation در مرورگر بررسی نشده؛ صف پایدار اختصاصی واحد در کد بررسی‌شده وجود ندارد.

**اقدام:** قرارداد source-of-truth آفلاین را برای گزارش واحد و ردیف‌های آن تعریف و همان فرم‌ها را متصل کنید؛ sync نباید نوشتن مستقیم در summary پروژه را جایگزین آن کند.

### G02 — P1 — ردیف POST ممکن است حذف شود و تأیید کاذب بگیرد

**شاهد:** [offlineWrite:265](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineWrite.ts:265) برای ردیف جدید endpoint با شکل `.../activities/` می‌سازد. regex در [syncService:64](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:64) این collection endpoint با slash پایانی را match نمی‌کند. در [syncService:144](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:144) عملیات parse‌نشده کنار گذاشته می‌شود، ولی همه queue IDهای همان گزارش در [syncService:247](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:247) synced می‌شوند.

**بازتولید:** parser مقدار `null` داد؛ `activities` در payload نبود؛ با فرض snapshot هدر دارای تاریخ و پاسخ موفق سرور، `synced=1` شد و صف پاک شد. این پاسخ در harness mock است؛ عبور واقعی آن از شبکه مرورگر ادعا نشده است. [خروجی probe](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/probe-frontend.txt)

**اقدام/تست پذیرش:** endpoint را ساخت‌یافته نگهداری کنید؛ هیچ عملیاتی بدون تأیید قابل تطبیق پاک نشود. ثبت ۱۰ ردیف POST با slash پایانی باید دقیقاً ۱۰ ردیف روی منبع مجاز سرور بسازد و تنها همان شناسه‌ها پاک شوند.

### G03 — P1 — تبدیل PATCH/DELETE به snapshot ناقص، جایگزینی مخرب می‌سازد

**شاهد:** builder در [syncService:149](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:149) در نبود snapshot از `[]` شروع می‌کند و PATCH را صرفاً با `map` روی آن اعمال می‌کند. `queueChildWrite` ردیف یا snapshot گزارش را ذخیره نمی‌کند: [offlineWrite:257](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineWrite.ts:257). cache warming هم فقط داده مرجع است: [offlineCache:37](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineCache.ts:37).

سرور برای هر section ارسالی ابتدا همه ردیف‌های آن را حذف و سپس درج می‌کند: [services:202](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:202)، [services:237](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:237).

**بازتولید:** یک PATCH با `quantity=3` و بدون snapshot، payload با `activities: []` ساخت. حذف همه ردیف‌های یک summary با همین آرایه خالی در probe بک‌اند نیز مشاهده شد. حتی با snapshot قدیمی، جایگزینی کامل می‌تواند ردیف‌های جدید سرور را حذف کند؛ این حالت آخر تحلیل کد است و تست دو کاربر اجرا نشد.

**اقدام:** قرارداد operation-based با شناسه پایدار و کنترل نسخه، یا snapshot کامل دارای precondition لازم است. PATCH/DELETE یک ردیف نباید ردیف دیگری را پاک کند؛ omission بخش با آرایه خالی معنای یکسان ندارد.

### G04 — P1 — مسیر batch حفاظت ردیف‌های تجمیعی را دور می‌زند

**شاهد:** مسیر عادی در [daily_report_views:557](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py:557) هر تغییر child در `is_auto_summary` را با `derived_readonly` رد می‌کند. شاخه existing در [services:337](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:337) چنین guardی ندارد و `_replace_children` را اجرا می‌کند. محدودیت child فقط در شاخه نبود گزارش اعمال می‌شود: [services:397](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:397).

**بازتولید API/DB:** روی summary دارای ردیف `is_derived=True`، درخواست عادی افزودن child برابر 400 شد؛ batch با `activities: []` برابر 200/merged شد و ردیف اصلی دیگر در دیتابیس نبود.

**اثر:** نقض منبع تخصصی و حذف داده تجمیعی؛ روابط provenance نیز ممکن است از ردیف موجود جدا شوند، هرچند اثر نهایی همه روابط در این ممیزی تست نشده است.

**اقدام:** guard مشترک در لایه سرویس و batch برای summary؛ تغییرات ردیف باید از منبع تخصصی پذیرفته و summary بازتجمیع شود.

### G05 — P1 — تأیید همزمان گزارش در برابر sync ایمن نیست

**شاهد:** خواندن گزارش و بررسی status در [services:299](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:299) تا 335، قبل از `transaction.atomic` است؛ `select_for_update` و بازخوانی status پیش از merge وجود ندارد. serializer در [services:187](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:187) همان instance را ذخیره می‌کند. در شاخه جدید نیز پس از `ensure_daily_report_summary` وضعیت دوباره چک نمی‌شود: [services:430](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:430).

**بازتولید قطعی ترتیب رخداد:** وضعیت دیتابیس بین بررسی اولیه و `_apply_header_merge` به approved تغییر داده شد؛ ذخیره instance قدیمی آن را دوباره draft کرد و پاسخ merged بود. در probe جداگانه، approved ایجادشده بین جست‌وجوی اولیه و ensure، notes جدید دریافت کرد و نتیجه created بود.

**اقدام/تست پذیرش:** ترتیب قفل سازگار با aggregation و workflow، قفل رکورد معتبر جاری و بازبینی status بلافاصله قبل از هر mutation. تست transaction با دو اتصال مستقل لازم است؛ نتیجه باید conflict باشد و status، notes و children گزارش approved عوض نشوند.

### G06 — P1 — Retry Row خطای اختصاصی را حفظ نمی‌کند و ردیف failed را دوباره نمی‌فرستد

**شاهد:** سرور `child_errors` شامل section/index/errors می‌دهد؛ کلاینت در [syncService:243](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:243) آن را فقط برای تشخیص شکست استفاده و در [syncService:300](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:300) پیام عمومی روی تمام عملیات گزارش می‌گذارد.

دکمه جدول در [InlineGridTab:156](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/InlineGridTab.tsx:156) تنها `syncPendingQueue()` را صدا می‌زند و row را نادیده می‌گیرد؛ [offlineDB:305](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineDB.ts:305) فقط pending می‌خواند. بنابراین failed دوباره ارسال نمی‌شود و با این حال toast موفقیت نمایش داده می‌شود. صفحه صف تابع reset-to-pending دارد، ولی تنها همان payload قبلی را retry می‌کند: [syncService:394](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:394)، [sync-conflicts:127](/home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/sync-conflicts.tsx:127).

**بازتولید:** خطای فیلد `must be positive` در QueueItem باقی نماند؛ اجرای مجدد روی صف failed-only صفر درخواست فرستاد.

**اقدام:** خطای ساخت‌یافته با شناسه ردیف حفظ شود؛ ویرایش همان payload و retry هدفمند، با گزارش نتیجه واقعی، فراهم شود.

### G07 — P2 — UUID عملیات جای شناسه پایدار ردیف را گرفته و نشانگر ردیف جدید وصل نیست

**شاهد:** `queue_id` با UUID تولید می‌شود، ولی [queueChildWrite:267](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineWrite.ts:267) هیچ `client_id` برای ردیف تولید/ثبت نمی‌کند؛ `local_id` شناسه گزارش است. [buildChildRowSyncMap:140](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineWrite.ts:140) row ID را از endpoint می‌گیرد؛ POST collection فاقد آن است و skip می‌شود. [InlineGridTab:179](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/InlineGridTab.tsx:179) هم نمایش را به `row.id` وابسته می‌کند. وضعیت pending در [EditableGrid:71](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/EditableGrid.tsx:71) آیکون Clock دارد.

**بازتولید:** payload ردیف `client_id` نداشت و map وضعیت برای POST خالی بود. تفاوت ساعت/ابر یک مغایرت ظاهری مستقل و کم‌خطرتر است؛ نقص اصلی اتصال شناسه ردیف به وضعیت و تأیید است.

**اقدام:** قرارداد UUIDv4 پایدار ردیف و تطبیق local/server؛ نشانگر زرد برای ردیف جدید، ویرایش‌شده و failed بر همین مبنا نمایش داده شود.

### G08 — P1 — وجود صف پایدار، بازیابی قابل استفاده ردیف‌ها پس از refresh را تضمین نمی‌کند

**شاهد:** IndexedDB store و CRUD صف وجود دارند: [offlineDB:205](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineDB.ts:205)، [offlineDB:300](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineDB.ts:300). با این حال [InlineGridTab:76](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/InlineGridTab.tsx:76) فقط از `serverRows` می‌سازد؛ `EditableGrid` داده خود را در state حافظه نگه می‌دارد: [EditableGrid:132](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/EditableGrid.tsx:132). queueChildWrite snapshot را به‌روز نمی‌کند و فرم گزارش را از API می‌خواند: [DailyReportForm:102](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/DailyReportForm.tsx:102). فهرست آفلاین نیز فقط تاریخ/نشانگر می‌دهد و مسیر بازکردن داده محلی ندارد: [daily-reports-list:204](/home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-reports-list.tsx:204).

**اثر:** payload ممکن است در store باقی بماند، اما ردیف جدید یا مقدار ویرایش‌شده پس از reload در جدول قابل بازیابی/اصلاح نیست. این نتیجه تحلیل اتصال داده‌هاست؛ پاک شدن فیزیکی IndexedDB ادعا نمی‌شود.

**اقدام:** hydration از snapshot به‌همراه replay صف روی داده سرور، مسیر بازکردن draft محلی و تست reload/close/reopen واقعی لازم است.

### G09 — P2 — قرارداد wire با SPEC-04 یکسان نیست و اسناد نیز با هم اختلاف دارند

SPEC-04 در خطوط 49 و 53 از `synced_ids`، `conflict_report_approved` و `sync_conflict` نام می‌برد. پاسخ فعلی [services:456](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:456) برابر `results + summary` است؛ هر نتیجه `local_id/server_id/status` دارد و conflict در [services:167](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:167) متن فارسی به جای کد پایدار برمی‌گرداند. [نوع کلاینت:599](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/daily-reports.ts:599) نیز همین قرارداد فعلی را می‌شناسد.

[سند endpoint:73](/home/hossein/Desktop/projects/building-management/reports_documentation/03-daily-field-reports-and-apis/field_reports_ENDPOINTS.md:73) برخلاف سند اتمیک، آرایه report payload و وضعیت `conflict` را شرح می‌دهد؛ بنابراین همه تفاوت‌ها را نمی‌توان صرفاً باگ مصرف‌کننده نامید. HTTP 200 در پاسخ دسته‌ای با خطای per-item به خودی خود مغایرت نیست؛ سناریوی ۱ هم 200 می‌خواهد.

**اقدام:** یک قرارداد مرجع تصویب شود: تطبیق operation/client ID با تأیید، کد پایدار approved و خطای فیلدی. `syncPendingQueue` در کد نام تابع است و store واقعی `offline_queue`؛ تفاوت نام store به‌تنهایی gap مستقل محسوب نشده است.

### G10 — P1 — تعارض approved مسیر بازیابی امن به اصلاحیه/منبع جدید ندارد

**شاهد:** [ConflictCard:74](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ConflictCard.tsx:74) payload گزارش را به endpoint اصلی آیتم صف و با PATCH/POST می‌فرستد. اقدام ایجاد درخواست اصلاح یا انتقال به draft واحد تخصصی وجود ندارد. مسیر approved همان قفل را دارد؛ endpoint child نیز payload گزارش را به عنوان یک child دریافت خواهد کرد. [ConflictMergeEditor:48](/home/hossein/Desktop/projects/building-management/apps/web/src/components/sync/ConflictMergeEditor.tsx:48) آرایه‌ها و objectها را از نمایش کنار می‌گذارد؛ بنابراین فعالیت/مصالح محلی برای مرور یا ادغام دیده نمی‌شوند.

انتخاب نسخه سرور فقط conflict و آیتم صف را تغییر می‌دهد: [ConflictCard:108](/home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ConflictCard.tsx:108). snapshot `_dirty` محلی در این مسیر reconcile نمی‌شود؛ ارسال دوباره آن در batch بعدی یک خطر قابل استنتاج از builder است و در این ممیزی مرورگری بازتولید نشده است.

**اقدام:** مشاهده کامل و قابل بازیابی داده محلی، حفظ آن تا تأیید مقصد، و مسیر اصلاحیه مجاز/نسخه جدید گزارش واحد. عبارت «گزارش جدید» در AC باید با منع گزارش خام پروژه هماهنگ شود؛ بازگرداندن create مستقل پروژه راه‌حل این gap نیست.

### G11 — P1 — قطع اجرای sync می‌تواند عملیات را برای همیشه در syncing نگه دارد

**شاهد:** [syncService:219](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:219) status را قبل از شبکه به syncing تبدیل می‌کند. پس از reload، [getPendingQueue:305](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/offlineDB.ts:305) آن را نمی‌خواند؛ صف ناموفق هم تنها failed را می‌خواند. recovery یا lease برای syncing رهاشده یافت نشد.

**بازتولید منطق:** صف syncing-only باعث صفر درخواست در اجرای بعدی شد. بستن واقعی مرورگر حین درخواست اجرا نشده است. `useAutoSync` یک running ref محلی دارد، اما سرویس قفل سراسری در برابر sync دستی/چند تب ندارد: [useAutoSync:15](/home/hossein/Desktop/projects/building-management/apps/web/src/app/hooks/useAutoSync.ts:15)، [syncService:367](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/syncService.ts:367). خطر همپوشانی از کد است؛ چندتب تست نشده است.

**اقدام:** claim/lease زمان‌دار، recovery عملیات نیمه‌تمام، idempotency روی سرور و جلوگیری از اجرای همپوشان؛ تست قطع اجرا درست بعد از claim و درست بعد از commit سرور.

### G12 — P2 — خطای هدر در مسیر ایجاد، shell جدید را rollback نمی‌کند

**شاهد:** [services:430](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py:430) ابتدا ensure می‌کند؛ اگر `_apply_header_merge` خطا بدهد، نتیجه error append و `continue` می‌شود، اما rollback علامت نمی‌خورد. در شاخه دیگری از همین سرویس برای خطای children از `transaction.set_rollback(True)` استفاده شده است.

**بازتولید API/DB:** تاریخ جدید با `temp_min=40/temp_max=10` پاسخ per-item error گرفت، ولی گزارش همان تاریخ در دیتابیس ساخته شده بود.

**اثر:** نتیجه error با mutation پنهان همراه است. این مورد مستقل از تصمیم محصول درباره مجاز بودن shell تجمیعی خالی است.

**اقدام:** validate قبل از ensure یا rollback کل آیتم روی خطای اعتبارسنجی؛ یک batch مختلط باید آیتم معتبر را ذخیره کند و هیچ اثری از آیتم نامعتبر نگذارد.

### G13 — P2 — تست‌های موجود سناریوهای اصلی SPEC-04 را اثبات نمی‌کنند

**شاهد:** ۱۷ تست backend وضعیت‌های موجود، اعتبارسنجی و جایگزینی را پوشش می‌دهند، ولی برابری تعداد فرزندان در retry جای اثبات حفظ شناسه، provenance، تغییرات کاربر دیگر و قفل همزمان را نمی‌گیرد. [test_sync_batch:181](/home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tests/test_sync_batch.py:181)

[offlineDB.test.ts](/home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/__tests__/offlineDB.test.ts) فقط normalization هوا را بررسی می‌کند. سه تست [offline-sync.spec.ts](/home/hossein/Desktop/projects/building-management/apps/web/e2e/tests/offline-sync.spec.ts) banner، مسیرها و نمایش summary را بررسی می‌کنند؛ ثبت ۱۰ ردیف، reload، flush دقیق، خطای ردیف و بازیابی conflict انجام نمی‌دهند. تست سوم به `/status/` درخواست می‌زند و موفقیت پاسخ را assert نمی‌کند: [offline-sync:79](/home/hossein/Desktop/projects/building-management/apps/web/e2e/tests/offline-sync.spec.ts:79)؛ در URLهای فعلی field_reports چنین مسیر workflowای وجود ندارد. از عنوان این تست نمی‌توان تأیید گزارش را نتیجه گرفت.

**اقدام:** تست‌های سناریویی زیر به مجموعه canonical اضافه شوند؛ probeهای این ممیزی جای آن‌ها را نمی‌گیرند.

## ۵. اجزای موجود که نباید به اشتباه «پیاده‌نشده» نامیده شوند

- ذخیره پایدار صف، گزارش محلی، conflict log و cache داده مرجع در IndexedDB وجود دارد.
- `navigator.onLine`، listenerهای اتصال و `useAutoSync` در AppShell وجود دارند.
- endpoint با مجوز `edit_reports` و پاسخ 200 دسته‌ای موجود است.
- گزارش از پیش approved، submitted یا under_review در جریان معمول batch به conflict می‌رود؛ snapshot سرور و diff هدر نیز برمی‌گردد.
- اعتبارسنجی children قبل از حذف در مسیر existing، و جلوگیری از پاک شدن داده در صورت child نامعتبر وجود دارد؛ تست موجود آن پاس شد.
- child-authored create در شاخه نبود گزارش رد می‌شود و مسیر ensure-summary استفاده می‌شود.
- صفحه تعارض و صف ناموفق و retry دستی از آن صفحه وجود دارند؛ نقص، کامل نبودن بازیابی و ویرایش ردیف است.

## ۶. ترتیب پیشنهادی رفع شکاف‌ها و معیار پایان

۱. **قرارداد و منبع داده:** G01 و G09؛ مشخص شود عملیات آفلاین واحد چگونه به summary می‌رسد، شناسه عملیات/ردیف و پاسخ تأیید چه هستند، و اصلاحیه چگونه با قفل و lineage سازگار می‌ماند.

۲. **حفظ داده و قفل:** G02 تا G05 و G12؛ قبل از اصلاح UI، حذف خاموش عملیات، replacement ناقص و bypass/race بسته شوند. هر عملیات یا تأیید قابل تطبیق بگیرد یا payload و خطایش برای بازیابی بماند.

۳. **بازیابی صف و UI:** G06 تا G08 و G10 تا G11؛ hydrate، نشانگر، ویرایش خطا، recovery اجرا و بازیابی تعارض کامل شوند.

۴. **اثبات انتهابه‌انتها:** G13 با این سناریوها:

- کاربر واردشده در فرم فعلی واحد، ۱۰ ردیف در فعالیت/نفرات/مصالح ثبت کند؛ همه client IDها UUIDv4 پایدار داشته باشند.
- refresh و بستن/بازکردن مرورگر آفلاین، همه مقادیر، خطاها و نشانگرها را برگرداند.
- reconnect دقیقاً همان عملیات را ثبت کند؛ retry پس از گم شدن پاسخ سرور duplicate نسازد و داده ردیف‌های دیگر را پاک نکند.
- PATCH/DELETE با نبود snapshot و snapshot قدیمی، ردیف‌های نامرتبط و provenance را تغییر ندهد.
- تأیید همزمان با دو اتصال مستقل، هیچ mutationی روی approved نگذارد؛ batch خروجی conflict با کد پایدار بدهد.
- یک ردیف نامعتبر میان ردیف‌های معتبر، خطای section/row/field بدهد؛ کاربر آن را اصلاح و فقط عملیات لازم را retry کند. مرز اتمیک بودن report/section/row باید در قرارداد صریح باشد.
- تعارض، داده محلی را کامل نشان دهد و تا موفقیت مقصد اصلاحیه/گزارش واحد حفظ کند؛ انتخاب سرور، صف و snapshot را با هم reconcile کند.
- قطع اجرا در وضعیت syncing و اجرای دستی/خودکار همزمان موجب گیر دائمی یا حذف دوباره داده نشود.

## ۷. شواهد و بازاجرای بررسی

- [تست‌های موجود بک‌اند](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/pytest-sync-batch.txt)
- [خروجی probe بک‌اند](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/probe-backend.txt)
- [خروجی probe فرانت‌اند](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/probe-frontend.txt)
- [دستورهای بازاجرا و محدودیت probeها](/home/hossein/Desktop/projects/building-management/reports_gaps/04/evidence/README.md)

این گزارش وضعیت همان snapshot کد را ارزیابی می‌کند. پاس شدن تست‌های موجود یا وجود taskهای تیک‌خورده، رفع G01 تا G13 یا آمادگی انتشار قابلیت آفلاین را ثابت نمی‌کند.
