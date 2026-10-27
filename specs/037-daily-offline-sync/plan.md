# Implementation Plan: ثبت آفلاین و همگام‌سازی مطمئن گزارش واحد

**Branch**: `develop` (شاخه واقعی؛ setup_plan نام feature `037-daily-offline-sync` را گزارش می‌کند) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

## Summary

قابلیت را روی صفحات موجود واحد تخصصی و مدل موجود `DisciplineSubReport` بسازید: تغییر محلی و صف عملیات هدف‌دار، ذخیره اتمی، بازیابی، قرارداد نسخه‌دار با تأیید عملیات، ثبت اتمیک نتیجه و اثر در سرور، کنترل نسخه هدف، بررسی مجدد قفل/مجوز، و رسیدگی صریح تعارض. مسیر قدیمی و همه مسیرهای نوشتن خلاصه باید امن شوند؛ وضعیت موجود یا موفقیت تست محدود معادل تحقق نیست. طراحی و شواهد در [research](research.md)، [data model](data-model.md) و [contracts](contracts/) آمده است.

## Technical Context

**Language/Version**: Python 3.12.3 محیط جاری؛ TypeScript و Node 25.2.1 محیط جاری؛ نسخه‌های پشتیبانی‌شده پروژه طبق lockfile و CI کنترل شوند.
**Primary Dependencies**: Django 4.2.11/DRF، React Router 7، React، Vite، `idb` موجود؛ بدون ارتقای framework یا افزودن صف موازی.
**Storage**: PostgreSQL برای منبع و دفتر تأیید اتمیک؛ IndexedDB موجود `ipcas-offline` برای snapshot/operation و مراجع؛ Redis وابستگی محیط API. ساختار و ارتقا در data-model است.
**Testing**: pytest/pytest-django، آزمون منطق TypeScript با runner موجود/قابل اجرا، API integration، Playwright واقعی، PostgreSQL دو اتصال مستقل، migration و typecheck. نام آزمون‌های جدید تا مرحله tasks/implementation قطعی نیست.
**Target Platform**: مرورگر پشتیبانی‌شده با همان پروفایل و API پروژه؛ اولین ورود آفلاین و sync بین دستگاه قبل از سرور خارج از دامنه.
**Project Type**: monorepo وب/API.
**Performance Goals**: ده عملیات مستقل با نتایج قابل تطبیق در اتصال مجدد طبق SC-01؛ زمان یا throughput عددی دیگری مصوب نشده، هدف غیرمستند اختراع نشود.
**Constraints**: حفظ داده، احراز و مجوز فعلی، محافظت قفل و derived، فارسی/انگلیسی، عملیات اتمیک مستقل، بدون تصمیم workflow آفلاین؛ سازگاری و ارتقا/بازگشت داده ضروری است.
**Scale/Scope**: شش واحد canonical و تمام بخش‌های ساخت‌یافته فعال فعلی؛ مقیاس بار عمومی تعیین نشده است و طراحی نباید آن را مفروض بگیرد.

## Constitution Check

**پیش از طراحی و پس از طراحی: PASS مشروط به اجرای gates، نه تأیید پیاده‌سازی.** I: هر خواندن/نوشتن دفتر و مقصد با عضویت و مجوز سمت سرور در محدوده پروژه، با استثنای admin طبق policy فعلی؛ II/IV: migration حفظ داده، عملیات هدف‌دار، lineage و تأیید صریح حذف؛ III/VII: دو زبان، خطای پایدار و دسترسی صفحه‌کلید؛ V: توسعه مدل، سرویس و UI موجود و عدم منبع موازی؛ VI: TDD و تفکیک شواهد backend/browser/migration/typecheck/live. هیچ نقض عمدی قانون اساسی طراحی نشده است. تطبیق عملی همه writerها با قفل مشترک و قرارداد جدید شرط عبور در پیاده‌سازی است.

## Project Structure

### Documentation (this feature)

```text
specs/037-daily-offline-sync/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   ├── sync-v2.md
│   └── ui-recovery.md
├── quickstart.md
└── checklists/requirements.md
```

`tasks.md` متعلق به مرحله بعد است و در این مرحله ساخته نمی‌شود.

### Source Code (repository root)

```text
apps/api/core/sub_reports/           # منبع واحد، بخش‌ها، workflow و آزمون‌ها
apps/api/core/field_reports/         # summary، aggregation، legacy sync و آزمون‌ها
apps/api/core/permissions/           # policy عضویت/مجوز پروژه
apps/web/src/components/department/  # صفحات و فرم‌های واحد
apps/web/src/app/lib/                # offlineDB، offlineWrite، syncService، API
apps/web/src/app/hooks/              # اتصال، mutation و cache
apps/web/src/components/sync/        # تجربه تعارض موجود
apps/web/e2e/tests/                  # Playwright موجود
```

**Structure Decision**: تکامل مسیرهای موجود؛ دفتر عملیات سرور یک سند idempotency در همان مرز domain است، نه مخزن موازی گزارش. فهرست دقیق فایل‌های تأثیرپذیر باید با جست‌وجوی نهایی همه writerها هنگام tasks و implementation بسته شود.

## Implementation strategy and dependencies

1. **Baseline و RED**: از G01–G13 و FRها تست canonical رفتاری بسازید؛ ابتدا ریسک‌های legacy derived، فقدان تأیید، rollback و race را reproduce کنید. تست‌های تثبیت‌کننده رفتار مخرب را با اثبات رفتار جدید و توضیح ناسازگاری جایگزین کنید، نه صرفاً حذف یا تضعیف.
2. **قرارداد و امنیت**: endpoint نسخه‌دار عملیات را مطابق contract اضافه؛ legacy `results/summary` حفظ شود اما مسیرهای ناامن reject شوند. تمام ورودهای create/PATCH/child/batch/legacy برای derived و دسترسی پروژه بررسی شوند. این تغییر رفتار legacy در مورد درخواست مخرب مستند و برای مصرف‌کننده قابل تشخیص است.
3. **سرور، concurrency و idempotency**: دفتر عملیات و نسخه هدف با migration غیرمخرب؛ transaction هر عملیات شامل mutation و receipt، قفل parent مشترک با همه writers و workflow، بررسی مجدد current/status/access، و کنترل تغییر همان هدف. برای ایجاد همزمان از constraint موجود و مسیر conflict قطعی استفاده شود. ترتیب قفل ثابت و بررسی بن‌بست؛ یک optimistic token سطح گزارش به تنهایی تغییرات مستقل را به‌اشتباه متعارض نکند.
4. **حفظ/ارتقای محلی**: schema افزایشی IndexedDB، تبدیل فقط با مدرک قطعی مالک و مقصد، نگهداری نسخه خام legacy و قرنطینه ابهام؛ بدون clear. تست upgrade failure و rollback خواندنی پیش از فعال‌سازی sync جدید.
5. **UI واحد و عملیات**: داده cache لازم، ذخیره اتمی snapshot+operation، ردیف‌های pending و draft در همان فرم‌ها، بازخوانی پس از restart، automatic sync و error/retry هدف‌دار؛ همه بخش‌های مؤثر پروژه inventory و پوشش شوند، نه فقط سه بخش نمونه.
6. **تعارض و recovery**: دو نسخه کامل، انتخاب server با reconciliation اتمیک محدود، یا مقصد رسمی اصلاحی پس از بازبینی؛ claim قابل بازیابی و ایمنی چند تب با idempotency سرور. استقلال local report/row/operation و نسخه عملیات حفظ شود.
7. **Verification نهایی**: اجرای سناریوهای [quickstart](quickstart.md) روی درخت نهایی؛ ثبت جداگانه backend، integration، race، browser، migration، typecheck و live؛ هیچ دسته اجرا نشده سبز اعلام نشود.

## Complexity Tracking

هیچ استثنای قانون اساسی پیشنهاد نشده است. دفتر receipt و revision هدف برای قابلیت retry و تشخیص تعارض ضروری‌اند؛ نگهداری صرف یک وضعیت report-level یا اتکا به ترتیب پاسخ جایگزین کافی نیست.
