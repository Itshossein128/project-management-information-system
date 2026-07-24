import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useLanguageStore } from "src/app/store/languageStore";

/** Keeps i18next language in sync with the Zustand language store. */
export default function I18nSync() {
  const { i18n } = useTranslation();
  const language = useLanguageStore((state) => state.language);

  useEffect(() => {
    const current = (i18n.language || "").split("-")[0];
    if (current !== language) {
      void i18n.changeLanguage(language);
    }
  }, [language, i18n]);

  return null;
}
