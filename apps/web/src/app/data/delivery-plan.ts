export type DeliveryTask = { id: string; title: string; status: "implemented" | "remaining"; start?: string; finish?: string };
export type DeliveryPhase = { id: string; title: string; start: string; finish: string; acceptance: string; tasks: DeliveryTask[] };

// Employer-facing snapshot of the reviewed minimum scenario. Existing capabilities
// are separate from remaining work; implementation does not imply final acceptance.
export const deliveryPlan: { baselineStart: string; finish: string; updatedAt: string; phases: DeliveryPhase[] } = {
  "baselineStart": "2026-11-04",
  "finish": "2027-03-10",
  "updatedAt": "2026-11-06",
  "phases": [
    {
      "id": "R.0",
      "title": "تثبیت قرارداد تحویل و مسیر آزمون/انتشار",
      "start": "2026-11-04",
      "finish": "2026-11-07",
      "acceptance": "2026-11-09",
      "tasks": [
        {
          "id": "R.0-available-1",
          "title": "تهیه فهرست مراحل و ریزکارهای تحویل",
          "status": "implemented"
        },
        {
          "id": "R.0.01",
          "title": "توافق بر فهرست خروجی‌ها و مسئول تأیید",
          "status": "remaining",
          "start": "2026-11-04",
          "finish": "2026-11-04"
        },
        {
          "id": "R.0.02",
          "title": "کنترل آماده‌بودن نسخه‌ها پیش از انتشار",
          "status": "remaining",
          "start": "2026-11-04",
          "finish": "2026-11-05"
        },
        {
          "id": "R.0.03",
          "title": "آماده‌سازی محیط بررسی کارفرما",
          "status": "remaining",
          "start": "2026-11-05",
          "finish": "2026-11-06"
        },
        {
          "id": "R.0.04",
          "title": "بررسی سلامت نسخه پیش از ارائه",
          "status": "remaining",
          "start": "2026-11-06",
          "finish": "2026-11-07"
        }
      ]
    },
    {
      "id": "A.6",
      "title": "کاربران و مرز دسترسی",
      "start": "2026-11-07",
      "finish": "2026-11-15",
      "acceptance": "2026-11-17",
      "tasks": [
        {
          "id": "A.6-available-1",
          "title": "تعریف نقش‌ها و اختیارات پایه کاربران",
          "status": "implemented"
        },
        {
          "id": "A.6.01",
          "title": "تعیین اختیارات هر نقش",
          "status": "remaining",
          "start": "2026-11-07",
          "finish": "2026-11-09"
        },
        {
          "id": "A.6.02",
          "title": "تکمیل محدودیت ثبت و ویرایش اطلاعات",
          "status": "remaining",
          "start": "2026-11-09",
          "finish": "2026-11-11"
        },
        {
          "id": "A.6.03",
          "title": "بررسی محرمانگی اطلاعات و دسترسی پروژه‌ها",
          "status": "remaining",
          "start": "2026-11-11",
          "finish": "2026-11-13"
        },
        {
          "id": "A.6.04",
          "title": "بررسی کار با نقش‌های مختلف",
          "status": "remaining",
          "start": "2026-11-14",
          "finish": "2026-11-15"
        }
      ]
    },
    {
      "id": "A.7",
      "title": "پروژه، اطلاعات پایه و ورود گروهی",
      "start": "2026-11-15",
      "finish": "2026-11-20",
      "acceptance": "2026-11-22",
      "tasks": [
        {
          "id": "A.7-available-1",
          "title": "ایجاد پروژه و ساختار شکست کار",
          "status": "implemented"
        },
        {
          "id": "A.7-available-2",
          "title": "ورود برنامه زمان‌بندی پروژه",
          "status": "implemented"
        },
        {
          "id": "A.7.01",
          "title": "آماده‌سازی نمونه اطلاعات پروژه",
          "status": "remaining",
          "start": "2026-11-15",
          "finish": "2026-11-16"
        },
        {
          "id": "A.7.02",
          "title": "تکمیل ورود برنامه و ساختار شکست کار",
          "status": "remaining",
          "start": "2026-11-16",
          "finish": "2026-11-17"
        },
        {
          "id": "A.7.03",
          "title": "بررسی ورود تکراری و بازیابی پروژه",
          "status": "remaining",
          "start": "2026-11-17",
          "finish": "2026-11-18"
        },
        {
          "id": "A.7.04",
          "title": "اجرای کامل ایجاد پروژه و ورود اطلاعات",
          "status": "remaining",
          "start": "2026-11-19",
          "finish": "2026-11-20"
        }
      ]
    },
    {
      "id": "A.1",
      "title": "تطبیق و تحویل اولیه گزارش روزانه",
      "start": "2026-11-20",
      "finish": "2026-11-27",
      "acceptance": "2026-11-29",
      "tasks": [
        {
          "id": "A.1-available-1",
          "title": "خروجی Excel و PDF گزارش روزانه",
          "status": "implemented"
        },
        {
          "id": "A.1.01",
          "title": "نهایی‌کردن قواعد اطلاعات روزانه",
          "status": "remaining",
          "start": "2026-11-20",
          "finish": "2026-11-21"
        },
        {
          "id": "A.1.02",
          "title": "تطبیق تمام بخش‌های گزارش با روز مرجع",
          "status": "remaining",
          "start": "2026-11-21",
          "finish": "2026-11-23"
        },
        {
          "id": "A.1.03",
          "title": "رفع اختلاف ارقام و نمایش خروجی‌ها",
          "status": "remaining",
          "start": "2026-11-24",
          "finish": "2026-11-25"
        },
        {
          "id": "A.1.04",
          "title": "ارائه نمونه نهایی و تأیید اولیه گزارش",
          "status": "remaining",
          "start": "2026-11-25",
          "finish": "2026-11-27"
        }
      ]
    },
    {
      "id": "A.8",
      "title": "عملیات، پیشرفت و منابع",
      "start": "2026-11-27",
      "finish": "2026-12-03",
      "acceptance": "2026-12-05",
      "tasks": [
        {
          "id": "A.8-available-1",
          "title": "ثبت گزارش تخصصی واحدها و تجمیع روزانه",
          "status": "implemented"
        },
        {
          "id": "A.8-available-2",
          "title": "ذخیره گزارش در حالت قطع اینترنت",
          "status": "implemented"
        },
        {
          "id": "A.8.01",
          "title": "تطبیق گزارش واحدها با گزارش روزانه و پیشرفت",
          "status": "remaining",
          "start": "2026-11-27",
          "finish": "2026-11-29"
        },
        {
          "id": "A.8.02",
          "title": "بررسی ذخیره و ارسال اطلاعات پس از قطع اینترنت",
          "status": "remaining",
          "start": "2026-11-29",
          "finish": "2026-12-01"
        },
        {
          "id": "A.8.03",
          "title": "رفع اختلاف منابع و اطلاعات تکراری",
          "status": "remaining",
          "start": "2026-12-01",
          "finish": "2026-12-02"
        },
        {
          "id": "A.8.04",
          "title": "بررسی نهایی عملیات با مسئول کارگاه",
          "status": "remaining",
          "start": "2026-12-02",
          "finish": "2026-12-03"
        }
      ]
    },
    {
      "id": "A.2",
      "title": "تکمیل مدیریت پیمانکاران",
      "start": "2026-12-04",
      "finish": "2026-12-08",
      "acceptance": "2026-12-10",
      "tasks": [
        {
          "id": "A.2-available-1",
          "title": "ثبت پرونده و ارتباط اولیه با قرارداد",
          "status": "implemented"
        },
        {
          "id": "A.2.01",
          "title": "نهایی‌کردن اطلاعات پرونده پیمانکار",
          "status": "remaining",
          "start": "2026-12-04",
          "finish": "2026-12-04"
        },
        {
          "id": "A.2.02",
          "title": "جست‌وجوی نام و اطلاعات تماس پیمانکار",
          "status": "remaining",
          "start": "2026-12-04",
          "finish": "2026-12-05"
        },
        {
          "id": "A.2.03",
          "title": "دریافت خروجی فهرست و پرونده پیمانکار",
          "status": "remaining",
          "start": "2026-12-05",
          "finish": "2026-12-07"
        },
        {
          "id": "A.2.04",
          "title": "کنترل ارتباط پیمانکار و قرارداد پروژه",
          "status": "remaining",
          "start": "2026-12-07",
          "finish": "2026-12-07"
        },
        {
          "id": "A.2.05",
          "title": "بررسی ثبت، جست‌وجو و خروجی پرونده",
          "status": "remaining",
          "start": "2026-12-07",
          "finish": "2026-12-08"
        }
      ]
    },
    {
      "id": "A.3",
      "title": "فهرست ذی‌نفعان و خروجی پایه",
      "start": "2026-12-09",
      "finish": "2026-12-12",
      "acceptance": "2026-12-14",
      "tasks": [
        {
          "id": "A.3-available-1",
          "title": "ثبت فهرست ذی‌نفعان و اطلاعات تماس",
          "status": "implemented"
        },
        {
          "id": "A.3.01",
          "title": "تعیین قواعد تشخیص ذی‌نفع تکراری",
          "status": "remaining",
          "start": "2026-12-09",
          "finish": "2026-12-09"
        },
        {
          "id": "A.3.02",
          "title": "کنترل ثبت و ویرایش اطلاعات تکراری",
          "status": "remaining",
          "start": "2026-12-09",
          "finish": "2026-12-10"
        },
        {
          "id": "A.3.03",
          "title": "خروجی فهرست با حفظ محرمانگی تماس‌ها",
          "status": "remaining",
          "start": "2026-12-10",
          "finish": "2026-12-11"
        },
        {
          "id": "A.3.04",
          "title": "تکمیل دسته‌بندی ذی‌نفعان",
          "status": "remaining",
          "start": "2026-12-11",
          "finish": "2026-12-11"
        },
        {
          "id": "A.3.05",
          "title": "بررسی نهایی فهرست و اطلاعات تماس",
          "status": "remaining",
          "start": "2026-12-11",
          "finish": "2026-12-12"
        }
      ]
    },
    {
      "id": "A.4",
      "title": "مکاتبات، ارجاع و پیوست",
      "start": "2026-12-12",
      "finish": "2026-12-21",
      "acceptance": "2026-12-23",
      "tasks": [
        {
          "id": "A.4-available-1",
          "title": "ثبت نامه، شماره و مهلت پاسخ",
          "status": "implemented"
        },
        {
          "id": "A.4.01",
          "title": "تعیین روال ارجاع، پاسخ و پیوست نامه",
          "status": "remaining",
          "start": "2026-12-12",
          "finish": "2026-12-13"
        },
        {
          "id": "A.4.02",
          "title": "ثبت مسئول ارجاع و سابقه پیگیری",
          "status": "remaining",
          "start": "2026-12-13",
          "finish": "2026-12-15"
        },
        {
          "id": "A.4.03",
          "title": "افزودن و دریافت پیوست نامه",
          "status": "remaining",
          "start": "2026-12-15",
          "finish": "2026-12-17"
        },
        {
          "id": "A.4.04",
          "title": "کنترل یکتایی شماره مکاتبات",
          "status": "remaining",
          "start": "2026-12-17",
          "finish": "2026-12-17"
        },
        {
          "id": "A.4.05",
          "title": "تکمیل جست‌وجو، وضعیت و مهلت پاسخ",
          "status": "remaining",
          "start": "2026-12-17",
          "finish": "2026-12-18"
        },
        {
          "id": "A.4.06",
          "title": "فعال‌کردن اعلان ارجاع و سررسید",
          "status": "remaining",
          "start": "2026-12-18",
          "finish": "2026-12-18"
        },
        {
          "id": "A.4.07",
          "title": "بررسی کامل ثبت تا بستن مکاتبه",
          "status": "remaining",
          "start": "2026-12-19",
          "finish": "2026-12-21"
        }
      ]
    },
    {
      "id": "A.9",
      "title": "اسناد، نسخه‌ها و کارتابل",
      "start": "2026-12-21",
      "finish": "2026-12-30",
      "acceptance": "2027-01-01",
      "tasks": [
        {
          "id": "A.9-available-1",
          "title": "ثبت اسناد و نگهداری نسخه‌های قبلی",
          "status": "implemented"
        },
        {
          "id": "A.9.01",
          "title": "تعیین روال بررسی و تأیید نسخه سند",
          "status": "remaining",
          "start": "2026-12-21",
          "finish": "2026-12-22"
        },
        {
          "id": "A.9.02",
          "title": "اتصال وضعیت سند به مراحل بررسی و تأیید",
          "status": "remaining",
          "start": "2026-12-22",
          "finish": "2026-12-24"
        },
        {
          "id": "A.9.03",
          "title": "تکمیل برگشت، اصلاح و حفاظت نسخه مصوب",
          "status": "remaining",
          "start": "2026-12-24",
          "finish": "2026-12-25"
        },
        {
          "id": "A.9.04",
          "title": "نمایش کارتابل مسئول و سابقه اقدامات",
          "status": "remaining",
          "start": "2026-12-25",
          "finish": "2026-12-27"
        },
        {
          "id": "A.9.05",
          "title": "اعلان بررسی و تغییر وضعیت سند",
          "status": "remaining",
          "start": "2026-12-27",
          "finish": "2026-12-28"
        },
        {
          "id": "A.9.06",
          "title": "بررسی کامل ارسال، اصلاح و تأیید سند",
          "status": "remaining",
          "start": "2026-12-28",
          "finish": "2026-12-30"
        }
      ]
    },
    {
      "id": "A.3.C",
      "title": "ارتباطات یکپارچه ذی‌نفعان",
      "start": "2026-12-30",
      "finish": "2027-01-06",
      "acceptance": "2027-01-08",
      "tasks": [
        {
          "id": "A.3.C-available-1",
          "title": "ثبت برنامه ارتباطات و ماتریس نفوذ و علاقه",
          "status": "implemented"
        },
        {
          "id": "A.3.C.01",
          "title": "نهایی‌کردن روال ارتباط با ذی‌نفعان",
          "status": "remaining",
          "start": "2026-12-30",
          "finish": "2026-12-30"
        },
        {
          "id": "A.3.C.02",
          "title": "اتصال جلسات و مکاتبات به ذی‌نفع و برنامه ارتباطی",
          "status": "remaining",
          "start": "2026-12-30",
          "finish": "2027-01-01"
        },
        {
          "id": "A.3.C.03",
          "title": "کنترل ارتباط صحیح مخاطب و پروژه",
          "status": "remaining",
          "start": "2027-01-01",
          "finish": "2027-01-02"
        },
        {
          "id": "A.3.C.04",
          "title": "نمایش یکپارچه سوابق ارتباطات",
          "status": "remaining",
          "start": "2027-01-02",
          "finish": "2027-01-03"
        },
        {
          "id": "A.3.C.05",
          "title": "تکمیل برگشت و تأیید ارتباطات",
          "status": "remaining",
          "start": "2027-01-03",
          "finish": "2027-01-04"
        },
        {
          "id": "A.3.C.06",
          "title": "بررسی پیوندها، دسترسی‌ها و سوابق",
          "status": "remaining",
          "start": "2027-01-04",
          "finish": "2027-01-06"
        }
      ]
    },
    {
      "id": "A.5",
      "title": "هزینه، پرداخت و جریان نقد",
      "start": "2027-01-06",
      "finish": "2027-01-19",
      "acceptance": "2027-01-21",
      "tasks": [
        {
          "id": "A.5-available-1",
          "title": "ثبت بودجه، تعهد و پرداخت",
          "status": "implemented"
        },
        {
          "id": "A.5-available-2",
          "title": "ثبت دریافت و پرداخت صورت‌وضعیت در جریان نقد",
          "status": "implemented"
        },
        {
          "id": "A.5.01",
          "title": "تعیین منبع ارقام و دفتر مرجع مالی",
          "status": "remaining",
          "start": "2027-01-06",
          "finish": "2027-01-07"
        },
        {
          "id": "A.5.02",
          "title": "تطبیق جمع هزینه، تعهد، پرداخت و مانده",
          "status": "remaining",
          "start": "2027-01-08",
          "finish": "2027-01-09"
        },
        {
          "id": "A.5.03",
          "title": "کنترل پرداخت تکراری و تأیید مستقل",
          "status": "remaining",
          "start": "2027-01-09",
          "finish": "2027-01-12"
        },
        {
          "id": "A.5.04",
          "title": "اصلاح محاسبات روزهای پایانی ماه و دقت ارقام",
          "status": "remaining",
          "start": "2027-01-12",
          "finish": "2027-01-13"
        },
        {
          "id": "A.5.05",
          "title": "تکمیل اصلاح و برگشت مبالغ ثبت‌شده",
          "status": "remaining",
          "start": "2027-01-13",
          "finish": "2027-01-14"
        },
        {
          "id": "A.5.06",
          "title": "تکمیل نمایش وضعیت و پیام‌های مالی",
          "status": "remaining",
          "start": "2027-01-14",
          "finish": "2027-01-16"
        },
        {
          "id": "A.5.07",
          "title": "بررسی چرخه مالی با ارقام مرجع",
          "status": "remaining",
          "start": "2027-01-16",
          "finish": "2027-01-19"
        }
      ]
    },
    {
      "id": "A.10",
      "title": "گزارش‌های استاندارد، دوره‌ای و داشبورد",
      "start": "2027-01-19",
      "finish": "2027-02-06",
      "acceptance": "2027-02-08",
      "tasks": [
        {
          "id": "A.10-available-1",
          "title": "تولید اولیه گزارش‌های دوره‌ای و شاخص‌های پروژه",
          "status": "implemented"
        },
        {
          "id": "A.10.01",
          "title": "اصلاح گزارش‌های هفتگی و ماهانه و فیلترها",
          "status": "remaining",
          "start": "2027-01-19",
          "finish": "2027-01-22"
        },
        {
          "id": "A.10.02",
          "title": "تکمیل قابلیت پیگیری منابع ارقام ماهانه",
          "status": "remaining",
          "start": "2027-01-22",
          "finish": "2027-01-24"
        },
        {
          "id": "A.10.03",
          "title": "خروجی رسمی گزارش دوره‌ای با شماره و تاریخ ثابت",
          "status": "remaining",
          "start": "2027-01-24",
          "finish": "2027-01-27"
        },
        {
          "id": "A.10.04",
          "title": "تکمیل شاخص‌ها و جزئیات داشبورد هر نقش",
          "status": "remaining",
          "start": "2027-01-27",
          "finish": "2027-01-29"
        },
        {
          "id": "A.10.05",
          "title": "تطبیق گزارش‌ها و داشبورد با اطلاعات مشترک",
          "status": "remaining",
          "start": "2027-01-29",
          "finish": "2027-02-01"
        },
        {
          "id": "A.10.06",
          "title": "تکمیل گزارش‌های روزانه، برنامه پیش‌رو، ذی‌نفعان، تغییرات، قراردادها و نقدینگی",
          "status": "remaining",
          "start": "2027-02-02",
          "finish": "2027-02-06"
        }
      ]
    },
    {
      "id": "A.11",
      "title": "آزمون جامع، امنیت، بازیابی و پذیرش",
      "start": "2027-02-07",
      "finish": "2027-02-21",
      "acceptance": "2027-02-23",
      "tasks": [
        {
          "id": "A.11-available-1",
          "title": "تهیه سناریوهای بررسی و پذیرش سامانه",
          "status": "implemented"
        },
        {
          "id": "A.11.01",
          "title": "بررسی یکپارچه کار بخش‌های سامانه",
          "status": "remaining",
          "start": "2027-02-07",
          "finish": "2027-02-10"
        },
        {
          "id": "A.11.02",
          "title": "بررسی دسترسی‌ها و سرعت پاسخ‌گویی",
          "status": "remaining",
          "start": "2027-02-10",
          "finish": "2027-02-13"
        },
        {
          "id": "A.11.03",
          "title": "بررسی بازیابی نسخه پشتیبان و بازگشت به نسخه قبل",
          "status": "remaining",
          "start": "2027-02-13",
          "finish": "2027-02-16"
        },
        {
          "id": "A.11.04",
          "title": "اجرای سناریوهای پذیرش با کاربران کارفرما",
          "status": "remaining",
          "start": "2027-02-17",
          "finish": "2027-02-19"
        },
        {
          "id": "A.11.05",
          "title": "رفع نقص‌های پذیرش و بررسی مجدد",
          "status": "remaining",
          "start": "2027-02-19",
          "finish": "2027-02-21"
        }
      ]
    },
    {
      "id": "A.12",
      "title": "انتقال داده، آموزش، پایلوت و تحویل",
      "start": "2027-02-24",
      "finish": "2027-03-08",
      "acceptance": "2027-03-10",
      "tasks": [
        {
          "id": "A.12-available-1",
          "title": "راه‌اندازی نسخه اولیه سامانه روی وبسایت",
          "status": "implemented"
        },
        {
          "id": "A.12.01",
          "title": "انتقال اطلاعات و تطبیق با داده‌های مبنا",
          "status": "remaining",
          "start": "2027-02-24",
          "finish": "2027-02-26"
        },
        {
          "id": "A.12.02",
          "title": "آموزش کاربران و تحویل راهنمای نقش‌ها",
          "status": "remaining",
          "start": "2027-02-26",
          "finish": "2027-02-28"
        },
        {
          "id": "A.12.03",
          "title": "استقرار نسخه آماده بهره‌برداری",
          "status": "remaining",
          "start": "2027-03-01",
          "finish": "2027-03-02"
        },
        {
          "id": "A.12.04",
          "title": "پایش حداقل پنج روز بهره‌برداری پایدار",
          "status": "remaining",
          "start": "2027-03-02",
          "finish": "2027-03-04"
        },
        {
          "id": "A.12.05",
          "title": "تحویل کد، دسترسی‌ها و صورتجلسه نهایی",
          "status": "remaining",
          "start": "2027-03-07",
          "finish": "2027-03-08"
        }
      ]
    }
  ]
};
