import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "../locales/en.json";
import fa from "../locales/fa.json";

export const supportedLanguages = ["fa", "en"] as const;
export type SupportedLanguage = (typeof supportedLanguages)[number];

export const languageNames: Record<SupportedLanguage, string> = {
  fa: "فارسی",
  en: "English",
};

export const isRTL = (lang: string = i18n.language): boolean => lang === "fa";

function resolveInitialLanguage(): SupportedLanguage {
  if (typeof window === "undefined") return "fa";
  const stored =
    window.localStorage.getItem("app-language") ??
    window.localStorage.getItem("i18nextLng");
  if (stored === "fa" || stored === "en") return stored;
  return "fa";
}

const initialLng = resolveInitialLanguage();

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      fa: { translation: fa },
    },
    fallbackLng: "fa",
    lng: initialLng,
    supportedLngs: [...supportedLanguages],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      // Prefer the app language store key; keep i18nextLng as secondary.
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "app-language",
    },
  });

export default i18n;
