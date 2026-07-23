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

function resolveStoredLanguage(): SupportedLanguage | null {
  if (typeof window === "undefined") return null;
  const stored =
    window.localStorage.getItem("app-language") ??
    window.localStorage.getItem("i18nextLng");
  if (stored === "fa" || stored === "en") return stored;
  return null;
}

/**
 * Always boot with the same default on server + first client paint to avoid
 * hydration mismatches. I18nSync / language store then apply the stored lang.
 */
const BOOT_LNG: SupportedLanguage = "fa";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      fa: { translation: fa },
    },
    fallbackLng: "fa",
    lng: BOOT_LNG,
    supportedLngs: [...supportedLanguages],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      // Prefer the app language store key; keep i18nextLng as secondary.
      // Disabled on first paint — sync happens via I18nSync after mount.
      order: [],
      caches: ["localStorage"],
      lookupLocalStorage: "app-language",
    },
  });

if (typeof window !== "undefined") {
  const stored = resolveStoredLanguage();
  if (stored && stored !== BOOT_LNG) {
    // Defer until after hydration so <html lang/dir> match SSR markup.
    queueMicrotask(() => {
      void i18n.changeLanguage(stored);
    });
  }
}

export default i18n;
