// src/components/I18nSync.tsx
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useLanguageStore } from "src/app/store/languageStore";

// این یک کامپوننت "نامرئی" است که فقط منطق همگام‌سازی را اجرا می‌کند
const I18nSync = () => {
  const { i18n } = useTranslation();
  // Variable holding language
  const language = useLanguageStore((state) => state.language);

  useEffect(() => {
    // اگر زبان i18next با زبان store ما متفاوت بود، آن را تغییر بده
    if (i18n.language !== language) {
      i18n.changeLanguage(language);
    }
  }, [language, i18n]);

  return null; // این کامپوننت هیچ چیزی رندر نمی‌کند
};

export default I18nSync;
