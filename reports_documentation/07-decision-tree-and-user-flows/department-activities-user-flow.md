# جریان کاربری و ماتریس گزارشات دپارتمان‌های ۵گانه (Department Activities User Flow)

این سند جایگزین ۳۵ پوشه و فایل تکراری شده و تمامی مسیرها، عملیات و خروجی‌های گزارش‌گیری ۵ دپارتمان تخصصی کارگاه را به‌صورت یک ماتریس استاندارد، تمیز و یکپارچه خلاصه می‌کند.

---

## ۱. ماتریس مسیرها و کامپوننت‌های دپارتمان‌های ۵ گانه

| دپارتمان / واحد | مسیر صفحه اصلی در سامانه | شناسه کدینگ دپارتمان (`department`) | کامپوننت روت |
| :--- | :--- | :--- | :--- |
| **ابنیه و ساختمانی (Civil)** | `/projects/:businessId/buildings` | `civil` | `BusinessBuildingsRoute` |
| **تأسیسات الکتریکی (Electrical)** | `/projects/:businessId/electrical` | `electrical` | `BusinessElectricalRoute` |
| **تأسیسات مکانیکی (Mechanical)** | `/projects/:businessId/mechanical` | `mechanical` | `BusinessMechanicalRoute` |
| **ماشین‌آلات و تجهیزات (Machinery)** | `/projects/:businessId/machinery` | `machinery` | `BusinessMachineryRoute` |
| **انبار و مصالح (Warehouse)** | `/projects/:businessId/warehouse` | `warehouse` | `BusinessWarehouseRoute` |

---

## ۲. عملیات‌های مشترک کاربری در هر ۵ دپارتمان

تمامی ۵ دپارتمان فوق از یک موتور مشترک تعاملی و بک‌اند واحد (`/api/v1/projects/{project_id}/department-activity-records/`) بهره می‌برند:

| عملیات کاربر (User Decision) | تعامل رابط کاربری (Trigger) | اثر و نتیجه شبکه / سامانه | فرمت خروجی / پارامترها |
| :--- | :--- | :--- | :--- |
| **دریافت گزارش روزانه واحد (`[daily-report]`)** | کلیک بر روی دکمه «دانلود گزارش روزانه» | دانلود ورک‌بوک اکسل گزارش روزانه واحد بر اساس تاریخ انتخابی | `GET .../reports/daily/?department={dept}&date={YYYY-MM-DD}` |
| **دریافت گزارش هفتگی واحد (`[weekly-report]`)** | کلیک بر روی دکمه «دانلود گزارش هفتگی» | دانلود ورک‌بوک اکسل جمع‌بندی احجام و رکوردهای هفته | `GET .../reports/weekly/?department={dept}&week_start={...}` |
| **ثبت رکورد فعالیت جدید (`[create-activity-record]`)** | کلیک روی «ثبت فعالیت جدید» | باز شدن مودال ورود اطلاعات روزانه واحد و ارسال به سرور | `POST .../department-activity-records/` |
| **ورود اطلاعات گروهی از اکسل (`[import-activity-excel]`)** | درگ یا انتخاب فایل اکسل شیت واحد | اعتبارسنجی ستون‌ها و ورود دسته‌ای رکوردهای روزانه | `POST .../import-excel/` |
| **خروجی اکسل فیلترشده (`[export-report]`)** | کلیک روی «خروجی اکسل» | تولید فایل اکسل از رکوردهای جدول بر اساس فیلترهای فعال | `GET .../export-excel/?department={dept}&date_from=...` |
| **فیلتر و تغییر نمای جدول (`filter-and-change-view`)** | انتخاب تاریخ، پیمانکار، شیفت یا جبهه کاری | فیلتر آنی ردیف‌های جدول در صفحه دپارتمان | ارسال کوئری‌پارامترهای فیلتر به API |

---

## ۳. فیلدهای اختصاصی دپارتمان انبار (`warehouse`) در برابر سایر واحدها

مطابق با مشخصات **اسپک 001** (`spec_001_warehouse.md`):
- در دپارتمان‌های **ابنیه، برق، مکانیک و ماشین‌آلات**: فیلدهای فعالیت شامل `activity_description`، `contractor`، `location`، `executed_quantity` و `unit` است.
- در دپارتمان **انبار (`warehouse`)**: فرمت ورود و خروجی اکسل به جای شرح فعالیت‌های عمرانی، روی **گردش مصالح کارگاه** متمرکز است:
  - `material_type` (نوع مصالح)
  - `quantity_in` (مقدار ورودی به انبار)
  - `quantity_out` (مقدار خروجی از انبار به جبهه‌های کاری)
  - `unit` (واحد اندازه‌گیری)
  - `supplier` (تأمین‌کننده)
  - `consumption_location` (محل مصرف در کارگاه)
  - `description` (توضیحات حواله یا رسید)
