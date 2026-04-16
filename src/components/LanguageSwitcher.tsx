// src/components/LanguageSwitcher.tsx

import { useLanguageStore } from "src/app/store/languageStore";
import "./LanguageSwitcher.css"; // فایل استایل برای نمایش دکمه فعال

export const LanguageSwitcher = () => {
  // از هوک useLanguageStore برای دسترسی به state و actions استفاده می‌کنیم
  const { language, setLanguage } = useLanguageStore();

  return (
    <div className='language-switcher'>
      <button
        // اگر زبان فعلی 'en' بود، کلاس 'active' را به دکمه اضافه کن
        className={language === "en" ? "active" : ""}
        onClick={() => setLanguage("en")}
      >
        en
      </button>
      <button
        // اگر زبان فعلی 'fa' بود، کلاس 'active' را به دکمه اضافه کن
        className={language === "fa" ? "active" : ""}
        onClick={() => setLanguage("fa")}
      >
        fa
      </button>
    </div>
  );
};
