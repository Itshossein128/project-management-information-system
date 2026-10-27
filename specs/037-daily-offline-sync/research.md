# Research: وضعیت جاری و تصمیم‌های طراحی

مبنای بررسی: checkout `develop` در `89ac5db` به‌علاوه فایل‌های untracked feature 037، 2026-10-27. بررسی این مرحله ایستا است؛ تست محصول جدید اجرا نشده است. ممیزی `reports_gaps/04` در commit قدیمی‌تر snapshot است. چهار probe موفق آن با assertion رفتار معیوب، تست پذیرش سبز نیست؛ رقابت آن monkeypatch است نه دو اتصال. گراف موجود ابزار مسیریابی بود و CLI آن قدیمی‌تر از skill است؛ منابع زیر مستقیماً بازبینی شدند.

## وضعیت موجود و شکاف قابل اثبات

| محدوده | آنچه واقعاً در کد هست | نقص مشاهده‌شده/مرز اثبات |
|---|---|---|
| G01/G08 | `section-activities.tsx`, `section-labor.tsx` و `unit-daily-report-panel.tsx` mutation/query واحد دارند. | مسیرهای بررسی‌شده مستقیماً شبکه را می‌خوانند؛ اتصال ذخیره محلی و draft بازیافتنی مشاهده نشد. E2E فعلی اثبات ثبت واقعی نیست. |
| G02/G09 | `offlineWrite.ts` و `syncService.ts` صف/تبدیل و sync دارند. | regex در `syncService.ts:64` slash پایانی collection را نمی‌پذیرد؛ نتیجه report-level در `:238` بر اساس ترتیب به همه آیتم‌ها نسبت داده می‌شود. payload و ack per-operation وجود ندارد. |
| G03/G04 | `field_reports/services/__init__.py:198-249` پردازش nested موجود دارد؛ guard child معمولی در `daily_report_views.py:572` هست. | replace کل section؛ batch موجود guard را دور می‌زند. `daily_report_views.py:232-285` نیز PATCH summary draft/rejected با `activities` را delete/recreate می‌کند، حتی آرایه خالی. تمام مسیرها باید بررسی شوند. |
| G05/G12 | constraint جاری واحد در `sub_reports/models.py:146-165` و قفل برخی عملیات هدر در `unit_report_services.py` موجود است. | بررسی batch قبل transaction و ensure در `field_reports/services/__init__.py:299-337,426-443` است؛ در probe ممیزی shell پس از خطا و overwrite approved دیده شده؛ نمونه race واقعی دو اتصال هنوز اثبات نشده. Section mutationها در `unit_report_views.py:624-700` چک قبل mutation دارند؛ همه writers نیاز به پروتکل مشترک دارند. |
| G06/G07 | `offlineDB.ts` و `offlineWrite.ts` UUID و وضعیت دارند؛ retry وجود دارد. | `QueueItem` فقط `project_id/local_id` دارد؛ row ID، actor، unit و operation version قراردادی نیستند؛ retry موجود کل صف را اجرا می‌کند؛ نشانگر POST جدید متصل نیست. |
| G08/G11 | IndexedDB `ipcas-offline` نسخه 3 و hook reconnect `useAutoSync.ts` موجود است. | pending-only خوانده می‌شود، syncing رهاشده recovery ندارد؛ guard در سطح hook است نه تب‌ها؛ snapshot و queue در مسیر قدیم الزام اتمی مشترک ندارند. |
| G10 | UI تعارض موجود است. | `ConflictMergeEditor.tsx:48` آرایه‌ها/objects را حذف می‌کند؛ `ConflictCard.tsx:74-114` ارسال مستقیم و resolve یک آیتم دارد، نه انتقال رسمی و reconciliation snapshot. |
| G13 | `field_reports/tests/test_sync_batch.py` و `apps/web/e2e/tests/offline-sync.spec.ts` وجود دارند. | تست‌های قبلی و probeها، مرورگر واقعی، race مستقل، حفظ همه داده، ۱۰ عملیات و retry را اثبات نمی‌کنند؛ نتیجه فعلی این مرحله فقط بازخوانی است. |

مدل aggregation در `field_reports/services/daily_report_aggregation.py:51-69`، eligible current submitted/approved و عدم quarantine را کنترل می‌کند؛ حفظ و تست شود. `unit_report_services.py:320-368` جریان اصلاح واحد و lineage دارد، اما idempotency انتقال و پوشش کامل داده را به‌تنهایی اثبات نمی‌کند. `permissions/project.py` عضویت فعال کاربر عادی و استثنای admin فعلی را پیاده می‌کند؛ سند قدیمی ادعای عدم بررسی عضویت دارد و باید اصلاح شود.

## تصمیم‌ها

### قرارداد عملیات نسخه‌دار
**Decision:** مسیر جدید صریح v2 با عملیات هدف‌دار و receipt per-operation؛ `results/summary` و semantics قدیم برای مشتری legacy نگه داشته می‌شود، اما mutation derived یا unsafe در تمام مسیرهای قدیمی با خطای روشن رد می‌شود. **Rationale:** `local_id` گزارش در قرارداد قدیمی هویت عملیات نیست و بازتفسیر خاموش آن ack کاذب می‌سازد. **Alternatives:** افزودن معنی جدید به همان وضعیت قدیمی یا تبدیل snapshot ناقص به operation حدسی؛ هر دو مردود. شکل مسیر و payload در [contract](contracts/sync-v2.md) تصمیم طراحی است.

### اتمیک بودن و تکرار
**Decision:** هر عملیات در یک transaction، همراه ثبت receipt یکتای actor/project/operation و fingerprint محتوای immutable و نتیجه نهایی؛ تکرار همان fingerprint نتیجه قبلی، reuse شناسه با محتوای متفاوت خطای پایدار. خطاهای retryable قبل commit receipt موفق نمی‌سازند؛ validation terminal قابل بازیابی است و اصلاح، شناسه جدید دارد. **Rationale:** timeout بعد commit و دو تب را با یک منبع حقیقت حل می‌کند. **Alternatives:** قفل صرف مرورگر یا dedup داخل یک batch، در برابر crash و چند دستگاه کافی نیست.

### رقابت و نسخه هدف
**Decision:** قفل parent در transaction برای همه writerهای رقیب، workflow، ensure و correction و بازخوانی current/status/permission قبل mutation؛ ترتیب واحد قفل‌ها برای parent سپس child/receipt و ثبت نتیجه. برای شناسایی تعارض محتوایی، revision مستقل هدف (هدر یا ردیف) با مقدار پایه و update آن در همه writerهای online/legacy؛ تغییر مستقل ردیف دیگر conflict نمی‌شود. Parent lock به تنهایی تغییر قبلی همان ردیف را تشخیص نمی‌دهد. عدم وجود parent با قفل کلید scope قابل اتکا و constraint فعلی رسیدگی شود، با بازخوانی conflict پس از برخورد uniqueness؛ جزئیات اجرایی باید در تست دو اتصال تثبیت شود. **Alternatives:** report-wide revision یا `updated_at` بدون تضمین همه writers؛ اولی conflict کاذب و دومی پوشش نامطمئن دارد.

### بخش‌ها و ownership
**Decision:** استفاده از سرویس‌های validate موجود هر بخش با write هدف‌دار؛ بدون nested replace. allowlist واحد واقعاً `form_code`, `revision_number`, `weather_condition`, `site_status` در `unit_report_views.py:167-174` است، notes عملیات بخش جداست. هدر summary از allowlist `daily_report_views.py:237-242` و اعتبارسنجی فعلی استفاده کند؛ تاریخ/shift identity و `local_id/synced_from_offline` مجوز تجاری نیستند. حفظ workflow و overrideهای موجود، نه اجازه نوشتن هر فیلد serializer. **Alternatives:** ارسال تمام serializer fields یا snapshot بخش؛ ریسک دورزدن مالکیت/حذف.

### local persistence و انتقال داده قدیم
**Decision:** نسخه افزایشی IndexedDB، transaction واحد برای snapshot+operation و نتیجه/reconcile؛ مالک/پروژه/واحد صریح. نسخه خام legacy و mapping audit حفظ می‌شود؛ صرفاً آیتم با actor، مقصد، هویت و payload قطعی تبدیل می‌شود، بقیه با اطلاعات کامل و عدم auto-send در وضعیت نیازمند تصمیم قرار می‌گیرند. upgrade failure باید نسخه قبلی را قابل بازیابی نگه دارد؛ rollback پس از نوشتن داده جدید با export/backup و بازگردانی سازگار برنامه‌ریزی می‌شود، نه downgrade کور IndexedDB. **Alternatives:** clear store یا حدس واحد از `local_id` قدیمی؛ نقض حفظ داده.

### مدیریت همپوشانی و تعارض
**Decision:** claim زمان‌دار در transaction محلی با owner و fencing token؛ بازیابی claim منقضی، ارسال امن پس از crash و سرور idempotent حتی در lease دوگانه. resolve-server اتمیک و محدود به دامنه تصمیم؛ اصلاحیه از workflow رسمی با intent شناسه‌دار و پیش‌نمایش، انتقال عملیات جداگانه و حفظ local تا ack مقصد. **Alternatives:** flag در یک hook، مستقیم PATCH approved، یا حذف snapshot هنگام نمایش تعارض؛ ناکافی/نامجاز.

### شواهد و rollout
**Decision:** red→green، API و PostgreSQL دو اتصال واقعی، browser واقعی و ارتقا/بازگشت داده جدا؛ عرضه v2 فقط پس از امن شدن legacy و آمادگی reader جدید، عدم پاکسازی قبل از تأیید و امکان توقف ارسال. **Alternatives:** اتکا به ۱۷ تست یا probe PASS، یا rollout با داده مهاجرت‌نشده؛ فاقد اثبات و پرخطر.
