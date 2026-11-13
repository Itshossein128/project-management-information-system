# نتایج اجرای ۲۸ سناریوی پذیرش یکپارچه (A.7-P6 Acceptance Scenarios)

این سند نتایج اجرای فنی ۲۸ سناریوی پذیرش (`POS-01` تا `POS-10`، `NEG-01` تا `NEG-14` و `OPS-01` تا `OPS-04`) را به تفکیک نتیجه فنی و ستون تصمیم کارفرما ثبت می‌کند.

| کد سناریو | عنوان سناریو | دسته | کدهای ممیزی | پرسونا | کانال آزمون | نتیجه فنی | تصمیم کارفرما | مدرک فنی |
|---|---|---|---|---|---|---|---|---|
| `POS-01` | ایجاد کاتالوگ‌های مرجع، ثبت پروژه در وضعیت پیش‌نویس و ذخیره ۶ بخش منشور آغازین | `positive` | `P01`, `P02`, `P04`, `M01`, `M02`, `M03` | `multi_role` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `POS-02` | ارسال پروژه برای تصویب، تصویب توسط تصویب‌کننده مستقل و قفل فیلدهای پایه همراه با روال تغییر رسمی | `positive` | `P03`, `P05`, `P06`, `P10`, `P11`, `M03` | `multi_role` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `POS-03` | مدیریت دستی درخت WBS سه‌سطحی، بازترتیب و جابه‌جایی ایمن زیرشاخه | `positive` | `W01`, `W02`, `W04` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `POS-04` | ایجاد قالب WBS و اعمال کپی مستقل روی پروژه مقصد بدون وابستگی مرجع | `positive` | `W06`, `M04` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `POS-05` | پیش‌نمایش بدون تغییر داده برای فایل‌های MSP XML، Primavera P6 XER/XML و فایل مرجع real-data/plan.mpp | `positive` | `I01`, `I02`, `I05`, `I12`, `D01`, `D02` | `creator_planner` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.json` |
| `POS-06` | ورود قطعی و ثبت اولیه خط مبنا برای فایل مرجع real-data/plan.mpp و فیکسچرهای XML/XER | `positive` | `I03`, `I04`, `I07`, `I11`, `I13`, `I14`, `I15`, `I16`, `I17`, `I18`, `I19`, `I20`, `I21`, `S02` | `creator_planner` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.json` |
| `POS-07` | تکرار ورود در حالت الحاقی (Repeat Append Idempotency) بدون ایجاد رکورد یا خط مبنای تکراری | `positive` | `W05`, `I06`, `I08`, `S02` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.json` |
| `POS-08` | جایگزینی ایمن (Replace Mode): مجاز روی پروژه بدون سابقه محافظت‌شده و مسدود روی پروژه دارای فعالیت/خط مبنای قفل‌شده | `positive` | `W05`, `S03` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `POS-09` | تاریخ‌های ۴گانه فعالیت، مایلستون، گزارش تأخیر، خروجی گانت و گیت اعتبار مسیر بحرانی | `positive` | `S01`, `S04`, `S05`, `S06`, `S07`, `S08` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `POS-10` | چرخه عمر کامل وضعیت‌های پروژه (تعلیق/رفع تعلیق، تکمیل/لغو تکمیل، بایگانی/بازگردانی) با حفظ ۱۰۰٪ داده‌ها | `positive` | `P07`, `P08`, `P09`, `M03` | `multi_role` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/lifecycle-archived-restore-fa-1280.png` |
| `NEG-01` | مسدودسازی تصویب پروژه دارای اطلاعات پایه ناقص (گیت‌های فعال‌سازی) | `negative` | `P04`, `P05` | `independent_approver` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-02` | مسدودسازی خودتصویبی ایجادکننده پروژه (جداسازی وظایف) | `access_boundary` | `P05` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-03` | رد کد تکراری WBS، نام خالی و ایجاد چرخه در درخت WBS | `negative` | `W01`, `W02` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-04` | مسدودسازی حذف گره WBS دارای زیرشاخه، فعالیت، پیشرفت، هزینه یا خط مبنای قفل‌شده | `negative` | `W03` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-05` | مسدودسازی جایگزینی کامل WBS (Replace) در صورت وجود سابقه محافظت‌شده | `negative` | `W05`, `S03` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-06` | رد فایل‌های نامعتبر، خالی، آسیب‌دیده، پسوند غیرمجاز، بیش از سقف حجم، چرخه وابستگی و بدون ساختار قابل ورود | `negative` | `I01`, `I07`, `I22` | `creator_planner` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-07` | تراکنش اتمی، Rollback کامل در خطای میانی و بازیابی در همان نشست بدون رکورد یتیم | `negative` | `I09`, `I22` | `creator_planner` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-fa-1280.png` |
| `NEG-08` | مهار استثناهای مفسر/مبدل خارجی، محدودیت منابع (cgroup/scratch) و بازیافت کارهای ناتمام | `operational` | `I03`, `I22` | `creator_planner` | `real_worker` | `pass` | `pending` | `specs/055-a7-p5-import-operations/evidence/runtime/independent-complete-matrix.json` |
| `NEG-09` | حفظ زمینه کاربر/پروژه در صف، قفل هم‌زمانی هر پروژه و جلوگیری از اجرای موازی تکراری | `concurrency` | `I08`, `I10`, `I11` | `creator_planner` | `combined` | `pass` | `pending` | `specs/055-a7-p5-import-operations/evidence/runtime/concurrent-delivery.json` |
| `NEG-10` | لغو ایمن کار صف‌بندی‌شده در صورت سلب مجوز کاربر یا بایگانی پروژه پیش از شروع پردازش | `access_boundary` | `I10`, `P09` | `viewer` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-11` | جداسازی کامل بین دو پروژه مستقل (Project A در برابر Project B) در API و مرورگر | `access_boundary` | `I10`, `P02` | `creator_planner` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-12` | محدودیت نقش مشاهده‌گر (Viewer / view_only) در برابر تغییر WBS و ورود فایل زمان‌بندی | `access_boundary` | `W01`, `I10` | `viewer` | `combined` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/viewer-readonly-fa-1280.png` |
| `NEG-13` | استثنای مشاهده مدیر سامانه (System Admin) و انحصار عملیات لغو تکمیل و بازگردانی از بایگانی | `access_boundary` | `P07`, `P09`, `I10` | `system_admin` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `NEG-14` | فقط‌خواندنی بودن کامل پروژه بایگانی‌شده در برابر ویرایش اطلاعات پایه و ورود زمان‌بندی | `access_boundary` | `P09`, `M03` | `creator_planner` | `api_db` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml` |
| `OPS-01` | چیدمان راست‌به‌چپ فارسی (fa RTL) در عرض‌های دسکتاپ (1280x800) و موبایل (390x844) بدون سرریز افقی | `bilingual_ux` | `I12`, `D03` | `creator_planner` | `browser_e2e` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-fa-390.png` |
| `OPS-02` | چیدمان چپ‌به‌راست انگلیسی (en LTR) در عرض‌های دسکتاپ (1280x800) و موبایل (390x844) بدون سرریز افقی | `bilingual_ux` | `I12`, `D03` | `creator_planner` | `browser_e2e` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-en-1280.png` |
| `OPS-03` | دسترس‌پذیری صفحه‌کلید (Tab/Enter/Escape) و اعلام وضعیت زنده در دیالوگ‌های ورود و چرخه عمر | `bilingual_ux` | `I11`, `I12`, `P07`, `P09` | `creator_planner` | `browser_e2e` | `pass` | `pending` | `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-en-390.png` |
| `OPS-04` | نگهداری ۷روزه بایت‌های فایل خام پس از اتمام کار و پاک‌سازی فقط‌بایت با حفظ متادیتا و تاریخچه | `operational` | `I10`, `I11`, `D04` | `system_admin` | `real_worker` | `pass` | `pending` | `specs/055-a7-p5-import-operations/evidence/runtime/independent-complete-matrix.json` |

## خلاصه وضعیت اجرای سناریوها

- **تعداد کل سناریوها**: ۲۸ سناریو (`10` مثبت، `14` منفی/مرزی/هم‌زمانی، `4` دوزبانه/عملیاتی)
- **تعداد سناریوهای قبول‌شده فنی (`pass`)**: ۲۸ از ۲۸
- **تعداد نقص‌های باز مسدودکننده (`defect_id`)**: `0`
- **وضعیت تصمیم کارفرما (`employer_result`)**: `pending` (در انتظار بررسی و امضای نماینده محترم کارفرما)
