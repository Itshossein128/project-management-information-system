from pathlib import Path
import json,sys,xml.etree.ElementTree as ET
F=Path('specs/056-a7-p6-delivery-acceptance');E=F/'evidence';p=json.loads((E/'package.json').read_text());v=p['version_id'];image=p['acceptance_image_digest']
identity=f"نسخه منبع: `{v}`؛ تصویر API: `{image}`؛ محیط: `{p['environment_id']}`؛ Django: `4.2.11`."
(F/'guide.md').write_text('''# راهنمای تحویل و آزمون کارفرما — A.7

@IDENTITY@

وضعیت فنی: `ready_for_acceptance`. هر ۲۸ سناریوی پذیرش pass است و نقص فنی بازِ شناخته‌شده‌ای در دامنه این تحویل ثبت نشده است. نتیجه انسانی `pending` و محل امضا خالی است.

از ۵۶ ردیف ممیزی، P06 قبلاً موجود و روی نسخه حاضر تأیید شد و ۵۵ ردیف در این فاز تکمیل، اصلاح یا تعیین تکلیف و آزموده شدند. سبد باز/اجرانشده صفر است. «قابل آزمون برای کارفرما» ویژگی هر ۵۶ ردیف است؛ آن را به‌عنوان سبد هم‌پوشان دوباره نمی‌شماریم. M04 تعیین تکلیف شرطی دامنه است، نه ادعای آزمون Excel.

## راه‌اندازی نسخه تحویل

بسته `output/a7-delivery-2026-11-16` شامل منبع، خروجی build وب، تصاویر API/Postgres/Redis، راهنما، شواهد و SHA256SUMS است. ابتدا `README-fa.md` داخل بسته را اجرا کنید. محیط پذیرش Linux دارای systemd، cgroup v2 و Docker Compose می‌خواهد. سرویس‌ها فقط به localhost متصل‌اند. این بسته تحویل پذیرش است؛ انتشار روی نشانی عمومی و اتصال پایگاه داده واقعی مستلزم تنظیمات محیط مقصد است.

از ریشه منبع، روی محیط پذیرش آماده:

```bash
ops/a7-p5/prepare-host.sh
# فقط اگر فایل خصوصی وجود ندارد:
cp -n ops/a7-p5/.env.acceptance.example ops/a7-p5/.env.acceptance
chmod 600 ops/a7-p5/.env.acceptance
# تصویر بارگذاری‌شده را بدون build مجدد اجرا کنید:
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml -f ops/a7-p5/compose.web.yml up -d --no-build --pull never
python3 ops/a7-p5/seed-delivery.py
```

نشانی ورود: `http://127.0.0.1:15173/login`. API: پورت 18000، Postgres خصوصی: 55434، Redis خصوصی: 56379. تصویر وب کامپایل‌شده داخل بسته است؛ نمایش نسخه آماده به نصب وابستگی یا build دوباره نیاز ندارد. فایل خصوصی `.runtime-delivery.json` با مجوز 0600 نام کاربری و رمز تصادفی پنج نقش را نگه می‌دارد؛ آن را در مخزن یا گزارش عمومی قرار ندهید. با اجرای seed مجدد، حساب‌ها و پروژه‌های آزمایشی جدید ساخته می‌شوند و داده قبلی حذف نمی‌شود.

## حساب‌های جلسه پذیرش

- `creator_planner`: ایجاد پروژه و برنامه‌ریزی؛ عضو مجاز پروژه، فاقد امکان خودتصویبی.
- `independent_approver`: شخص مستقل برای تصویب پروژه و درخواست تغییر.
- `viewer`: خواندن پروژه/منشور/WBS/برنامه و خط مبنا؛ تمام نوشتن‌ها ممنوع.
- `system_admin`: گروه مدیر سیستم؛ مشاهده سازمانی حتی بدون عضویت و اختیار ویژه بازگردانی خاتمه/بایگانی. نوشتن عادی نیاز به عضویت فعال و مجوز پروژه دارد؛ is_staff به‌تنهایی این اختیار نیست.
- `org_reference_steward`: مدیریت واحد سازمانی، نوع قرارداد و واحد اندازه‌گیری؛ دسترسی نوشتن مرجع طبق سیاست A.6.

برای تست مثبت، از پروژه مرجع دارای عضویت پنج نقش استفاده کنید. ساخت پروژه جدید، عضویت اولیه ایجادکننده را می‌سازد؛ تصویب‌کننده و مدیر باید پیش از عملیات پروژه به آن افزوده شوند. اسکریپت و آزمون مرجع این عضویت‌ها را ایجاد می‌کنند.

## مسیر نمایش در جلسه

1. متولی مرجع در `/settings/org-refs` واحد سازمانی، نوع قرارداد و واحد اندازه‌گیری را بسازد. برنامه‌ریز در `/projects/new` آن‌ها را انتخاب کند، مشخصات را ذخیره و پس از بازگشایی تطبیق دهد. واحد اندازه‌گیری در تنظیمات قابل انتخاب و پاک‌کردن است.
2. شش بخش منشور (توجیه، معیار موفقیت، محدودیت‌ها، فرض‌ها، ذی‌نفعان و اختیار مدیر) را ثبت و بازخوانی کند. ارسال برای تصویب، خودتصویبی را رد می‌کند. مدیر پروژه، دامنه و مبلغ بزرگ‌تر از صفر هر سه برای فعال‌سازی لازم‌اند. تصویب‌کننده مستقل پروژه را فعال کند.
3. ویرایش مستقیم اطلاعات مصوب رد شود. درخواست تغییر پروژه ساخته و ارسال شود؛ تصویب مستقل مقدار را تغییر دهد، رد یا لغو مقدار را حفظ کند. درخواست تغییر زمان‌بندی مسیر جداگانه و تاریخچه مستقل دارد.
4. در WBS سه سطح بسازید، مسئول و معیار تکمیل برگ را ثبت و بازخوانی کنید؛ جابه‌جایی، عمق و کدگذاری مجدد را ببینید. جمع وزن خواهرها ۱ است و مقدار نامعتبر هشدار دارد. قالب را ذخیره و روی پروژه دوم اعمال کنید؛ ویرایش مبدأ/قالب، کپی قبلی را تغییر نمی‌دهد. گره دارای وابستگی قابل حذف/جایگزینی مخرب نیست.
5. فایل `real-data/plan.mpp` را از دکمه انتخاب فایل باز کنید. پیش‌نمایش نباید رکورد یا job بسازد. لغو با دکمه یا Escape همین شرط را حفظ می‌کند. نمونه‌های MSP XML و P6 XER نیز ضمیمه‌اند.
6. ورود اول به پروژه خالی یا جایگزینی فاقد تاریخچه محافظت‌شده اجرا شود. ارقام نهایی فایل مرجع **۶ WBS، ۷۲ فعالیت، ۷۲ رابطه و یک خط مبنای کاری** است. نسخه کاری وارداتی با خط مبنای قطعیِ مصوب تفاوت دارد.
7. همان فایل را در حالت افزایشی تکرار کنید: `nothing_changed=true` و هیچ ردیف یا baseline اضافی. جایگزینی روی برنامه دارای پیشرفت، خط مبنای قفل/مصوب یا سایر تاریخچه محافظت‌شده باید مسدود شود.
8. جدول، گانت و وضعیت زمان‌بندی را باز کنید: تاریخ جاری، مصوب، واقعی و پیش‌بینی جدا هستند. نقطه عطف و تأخیر دیده می‌شود. داده ناقص یا روابط حذف‌شده نباید مسیر بحرانی معتبر جلوه کند.
9. تعلیق → ازسرگیری با دلیل، تکمیل → بازگردانی تکمیل، بایگانی → بازیابی را با نقش مجاز اجرا کنید. بعد از هر مرحله منشور و رکوردهای زمان‌بندی ثابت‌اند. تأیید کهنه یا سلب مجوز رد می‌شود؛ تکرار همان درخواست موفقیت دوم نمی‌سازد. پروژه آرشیوشده فقط‌خواندنی است؛ استثنای محدود رفع نقص برای بازیابی نیاز به اختیار مدیر و مجوز/عضویت فعال دارد و جایگزین ویرایش عمومی نیست.
10. با مشاهده‌گر تلاش برای تغییر پروژه، WBS، baseline و ورود فایل رد شود. کاربر پروژه A حتی با شناسه واقعی پروژه B به زمان‌بندی، گانت، baseline یا وضعیت job آن دسترسی ندارد. در ورود فعال، قطع ارتباط و reload همان تلاش را بازیابی می‌کند و job تکراری نمی‌سازد.
11. مراحل اصلی، خطا و بازیابی را در فارسی/انگلیسی، عرض ۱۲۸۰ و ۳۹۰ و با Tab، Shift+Tab، Enter و Escape بررسی کنید. انتخاب فایل با رویداد واقعی FileChooser مرورگر خودکار آزموده شده است؛ نمایش خود پنجره سیستم‌عامل را می‌توانید در جلسه ببینید.

## ارقام کنترل و محدودیت‌های مصوب

فایل مرجع ۸۰ وظیفه دارد: ۶ خلاصه و ۷۴ برگ. دو برگ بدون والد «شروع/پایان» با هشدار کنار گذاشته می‌شوند؛ ۷۲ فعالیت باقی می‌ماند. از ۸۳ پیوند خام، ۴ پیش‌نیاز خلاصه و ۷ پیوند وابسته به ردیف‌های حذف‌شده کنار می‌رود و ۷۲ رابطه ذخیره می‌شود. تقویم منبع با `calendar_not_applied` گزارش می‌شود؛ موتور کامل تقویم/CPM تعهد این تحویل نیست. تبدیل lag بر مبنای ۴۸۰ دقیقه روز کاری است.

پشتیبانی شامل MPP خواندنی در corpus اعلام‌شده، MSP XML و P6 XER است؛ پذیرش همه نسخه‌های تاریخی MSP یا هر P6 XML ادعا نمی‌شود. شناسه تاریخی `valid_p6_xml` در دفتر تطبیق، در واقع فایل MSPDI کسری/بدون والد است و نتیجه صحیح آن صفر ردیف به‌همراه هشدارهای صریح است. `evidence/reconciliation.json` اثر انگشت و شمارش چهار فایل را ثبت کرده است.

وضعیت‌های پروژه چرخه ثابت دارند و کاتالوگ مرجع مجوز ساخت وضعیت دلخواه نمی‌دهد (M03). جریان این فاز از جداول پویا و ورود Excel عمومی استفاده نمی‌کند؛ ورود مستقل WBS از Excel خارج از دامنه است (M04). نگهداری بایت فایل اصلی تا ۱۶۸ ساعت پس از پایان job است؛ پاک‌سازی بایت، تاریخچه و نتیجه را حذف نمی‌کند.

## بازاجرای فنی و صورت‌جلسه

دستورات `quickstart.md` و اسکریپت‌های check-delivery، check-host و check-delivery-browser تمام شواهد را بازتولید می‌کنند. آزمون‌های fault/worker باید پشت سر هم روی stack خصوصی اجرا شوند. بازاجرای آن‌ها روی داده واقعی کارفرما مجاز نیست. صورت‌جلسه `evidence/minutes.md` را نماینده کارفرما پس از آزمون پر می‌کند؛ هیچ تصمیم یا امضای انسانی از پیش ثبت نشده است.
'''.replace('@IDENTITY@',identity))
(F/'quickstart.md').write_text('''# Reproduce the A.7 acceptance release

@IDENTITY@

Use Linux/systemd with cgroup v2, Docker Compose, native PostgreSQL/Redis for host regressions, Node and pnpm. Preserve private environments. Do not run fault-control suites concurrently or against a shared/production database.

From repository root:

```bash
ops/a7-p5/run-acceptance.sh
python3 ops/a7-p5/check-broker-outage.py
python3 ops/a7-p5/check-concurrent-delivery.py
ops/a7-p5/check-host.sh
ops/a7-p5/check-delivery.sh
pnpm typecheck
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm build
# Separate terminal; test the compiled release:
HOST=127.0.0.1 PORT=15173 pnpm --filter web start
# Main terminal:
ops/a7-p5/check-delivery-browser.sh
python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py
```

The host scripts source `.env` but create uniquely named test databases. check-delivery runs project registration/lifecycle/restore/concurrency, WBS/template and schedule regressions; check-host runs containment-specific P5 regressions. Fresh migration seeds are important: a reused database flushed by transactional tests can lack permission catalog rows and produce misleading 403s. These test settings do not prove real background execution; the separate 13-group matrix, broker outage, duplicate-delivery and browser recovery tests do.

The browser runner provisions distinct human logins, then runs positive/bilingual/cancellation, ordinary-planner recovery/isolation, ordinary-viewer and P5 retry suites sequentially. It saves credentials only in mode-0600 ignored files and secret-free JSON reports in evidence. Current server must use the matching build/API image. A passing package validator requires report checksums, zero failures/skips, matching source files and schedule-tree digest, all 56 faithful audit rows and all 28 scenarios pass. Employer fields remain pending/blank.

`release-verification.json` is the final verification lock; changing tested source requires rerunning the affected checks and regenerating this lock, never copying old success labels. The original November-10 requirements snapshot stays untouched. Historical P5 independent-operator reproduction is retained separately; this final current-version execution is implementer-run. For delivery artifact loading and checksums use the bundle's README-fa.md.
'''.replace('@IDENTITY@',identity))
(E/'accounts.md').write_text('''# حساب‌های پذیرش A.7

پنج حساب مستقل با رمز تصادفی توسط `python3 ops/a7-p5/seed-delivery.py` روی پایگاه خصوصی a7p5 ساخته می‌شوند. رمز، نام ورود و توکن فقط در فایل نادیده‌گرفته‌شده `ops/a7-p5/.runtime-delivery.json` با مجوز 0600 ذخیره می‌شوند. گزارش و بسته عمومی فاقد رمز و JWT است. seed داده قبلی را پاک نمی‌کند؛ برای جلسه تازه پروژه‌های تازه می‌سازد.

- creator_planner: عضو فعال با مجوز پروژه؛ ساخت و ارسال، بدون خودتصویبی.
- independent_approver: کاربر مستقل برای approve_project و تأیید درخواست تغییر؛ عضویت مستقل.
- viewer: مجوزهای خواندن، بدون نوشتن پروژه، منشور، WBS، زمان‌بندی یا baseline.
- system_admin: گروه admin (یا اختیار معادل معتبر)؛ مشاهده سازمانی بدون عضویت و اختیار ویژه undo-completion/restore؛ نوشتن عادی نیاز به عضویت فعال و مجوز پروژه دارد. is_staff به‌تنهایی معادل مدیر سیستم نیست.
- org_reference_steward: متولی مجاز کاتالوگ سازمان، نوع قرارداد و واحد اندازه‌گیری.

هر پنج حساب با فرم ورود واقعی مرورگر آزموده شده‌اند. برای پروژه‌ای که دستی ساخته می‌شود عضویت تصویب‌کننده/مدیر را صریح اضافه کنید. ابزارهای strict recovery و viewer سوژه‌های جداگانه با کمترین اختیار می‌سازند؛ نام admin_auth در ساختار fixture بازیابی صرفاً نام قدیمی فیلد است و حساب آن مدیر سیستم نیست.

فایل‌های خصوصی را تنها از کانال مجاز خودتان به اپراتور جلسه بدهید. آن‌ها در آرشیو عمومی تحویل نیستند. اجرای seed روی محیط تازه روش بازیابی دسترسی است و به رمز ثابت توسعه وابسته نیست.
''')
sc=json.loads((E/'scenarios.json').read_text())
minutes=['# صورت‌جلسه پذیرش کارفرما — A.7','',identity,'','آمادگی فنی: `ready_for_acceptance`؛ ۲۸ pass، صفر fail، صفر not_run؛ ۵۶ ردیف تعیین تکلیف فنی شده، صفر نقص باز شناخته‌شده در دامنه تحویل. تعیین تکلیف M04 مشروط به عدم استفاده از Excel عمومی است.','', 'تصمیم کارفرما: `pending`','نقش/نام نماینده کارفرما: __________________','تاریخ و ساعت: __________________','امضا: __________________','','نتیجه فنی به معنی پذیرش انسانی نیست. ستون نظر و نتیجه را نماینده در جلسه تکمیل می‌کند.','', '| سناریو | عنوان | نتیجه فنی | نظر کارفرما |','|---|---|---|---|']
for s in sc:minutes.append(f"| {s['scenario_id']} | {s['title']} | pass | pending |")
minutes+=['','تصمیم نهایی: pending / accepted / rejected','موارد اعلامی نماینده: __________________','موعد رسیدگی توافق‌شده: __________________','']
(E/'minutes.md').write_text('\n'.join(minutes))
(F/'handoff.md').write_text('''# A.7 final technical handoff

@IDENTITY@

Technical readiness: `ready_for_acceptance`. Employer decision: `pending`; signer and signing time are blank. All 56 original audit IDs have faithful titles/acceptance criteria and technical dispositions in audit-disposition.json; all 28 catalog scenarios pass. There are no known open in-scope technical defects. M04 is an explicitly resolved conditional scope item, not a claim that general Excel import was tested.

The source commit is immutable and was created through a separate Git index; the shared develop branch and unrelated staged work were preserved. release-verification.json binds API/web/ops/test source hashes, image identity and actual final test reports. The delivery archive includes the final evidence overlay and source candidate. The original requirements audit is unchanged.

Evidence: final-core-junit.xml; P5 runtime/host-pytest.xml; final-browser-general/recovery/viewer/retry.json; P5 runtime/manifest.json, broker-outage.json and concurrent-delivery.json; web-checks.json; source-files.json; package-validator.json. Historical P5 independent reproduction stays in the P5 reproduction document; final runs are implementer-run and do not replace human employer sign-off.

The compiled frontend in the exported web image was served for final browser acceptance. Five distinct personas logged in through the real form. The reference UI journey covers governed measurement unit, six charter sections, independent approval and CR, three-level WBS metadata/move, template independence, native MPP chooser/import, protected replace, idempotent repeat, four-date views and all six lifecycle transitions with retained charter/schedule data. Strict real-worker offline/reload recovery, cross-project schedule/baseline isolation and 15 viewer-denied writes have separate fixtures.

Reference plan.mpp is unchanged (777216 bytes; SHA-256 3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553). Reconciled target is 6 WBS / 72 activities / 72 relations / one working baseline. Unsupported parentless milestones/calendar behavior is explicit in guide.md and reconciliation.md. Compatibility is limited to the declared corpus, not every MPP version or arbitrary P6 XML.

Start with the bundle README-fa.md, then guide.md and the unsigned minutes. This is a localhost isolated acceptance release. Production credentials, customer data migration, public deployment and the employer's decision are not performed by these tests.
'''.replace('@IDENTITY@',identity))
(E/'defects.md').write_text('''# A.7 final defect disposition — 2026-11-16

@IDENTITY@

Known open in-scope technical defects: **0**. Human acceptance remains pending. Earlier dated runs in predecessor evidence are historical; the current lock is release-verification.json.

- P6-GATE-001: historical P5 independent reproduction retained. Current candidate additionally reruns all 13 real-worker groups, broker outage, duplicate consumers, host containment and browser recovery. The new runs are implementer-run.
- P6-DOC-001: phase traceability artifacts exist; the final 56-row ledger now preserves exact original titles/acceptance and owning phases.
- P6-CONV-001: protected replace rejects with baseline_replace_forbidden and retains baseline/progress/report/change-request/measurement history.
- P6-CONV-002: missing lifecycle/charter, duplicate import, indirect-cycle rollback, cancel-without-job, actual offline/reload recovery, cross-project baseline/schedule and viewer project/baseline checks are executed. The final OPS-04 matrix is rebound to the final image/source hash.
- P6-DELIVERY-001: measurement unit API field now has create/settings selectors, including clearing and reselecting; persisted FK is checked in the browser.
- P6-DELIVERY-002: template/empty-WBS text is localized; template and charter fields have associated labels; project-list sort typecheck is fixed.
- P6-DELIVERY-003: a valid MPP chosen through the native browser chooser was rejected because host MIME associated .mpp with audio/x-musepack. MPP detection now relies on extension plus mandatory OLE signature and the bounded parser; non-OLE remains rejected. MIME variants have regression tests and native upload passes.
- P6-DELIVERY-004: archive read-only enforcement inadvertently blocked legitimate missing-data remediation. Only a missing manager on an active-origin archive may be repaired by a global admin with active project permission; scope/budget use an independently approved cycle-bound CR. Generic and stale serializer/CR writes remain denied under the root row lock. Cancelling stale completion remediation remains allowed without writing project data. Real concurrency tests pass.
- P6-DELIVERY-005: stale audit/scenario mappings, file hashes/counts, role descriptions, version IDs and readiness summaries were regenerated and validator now enforces their ties to successful current reports.

Recorded policy boundaries (not defects): M03 fixed project lifecycle; M04 no dynamic Excel in the A.7 journey; calendar_not_applied; parentless-row omission; fixture-scoped compatibility. No unsupported behavior is presented as implemented.
'''.replace('@IDENTITY@',identity))
print('Human guide, handoff, role guide, minutes and defect dispositions generated')
