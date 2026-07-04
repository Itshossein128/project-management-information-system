// src/stores/languageStore.ts

import { create } from "zustand";

// تعریف تایپ‌های مربوط به state و actions
// این کار در TypeScript به شدت توصیه می‌شود
interface LanguageState {
  language: "fa" | "en";
  setLanguage: (lang: "fa" | "en") => void;
}

// کلید برای ذخیره‌سازی در LocalStorage
const LOCAL_STORAGE_KEY = "app-language";

// تابع برای خواندن مقدار اولیه با اطمینان از اجرا در سمت کلاینت
const getInitialLanguage = (): "fa" | "en" => {
  // این شرط برای جلوگیری از خطا در محیط‌های Server-Side Rendering (SSR) است
  if (typeof window === "undefined") {
    return "fa"; // مقدار پیش‌فرض در سمت سرور
  }
  // Variable holding storedLang
  const storedLang = localStorage.getItem(LOCAL_STORAGE_KEY);
  if (storedLang === "fa" || storedLang === "en") {
    return storedLang;
  }
  return "fa"; // مقدار پیش‌فرض در سمت کلاینت
};

export const useLanguageStore = create<LanguageState>((set) => ({
  // 1. مقدار اولیه را از تابع کمکی می‌خوانیم
  language: getInitialLanguage(),

  // 2. اکشن برای تغییر زبان
  setLanguage: (lang) => {
    console.log("resid", lang);
    // 2.1. مقدار جدید را در LocalStorage ذخیره می‌کنیم
    localStorage.setItem(LOCAL_STORAGE_KEY, lang);

    // 2.2. استیت داخلی Zustand را آپدیت می‌کنیم تا کامپوننت‌ها دوباره رندر شوند
    set({ language: lang });
  },
}));
