import { create } from "zustand";
import i18n, { type SupportedLanguage } from "src/app/lib/i18n";

interface LanguageState {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
}

/** Single storage key shared with i18next detector + API Accept-Language. */
export const LANGUAGE_STORAGE_KEY = "app-language";

const getInitialLanguage = (): SupportedLanguage => {
  if (typeof window === "undefined") {
    return "fa";
  }
  const stored =
    localStorage.getItem(LANGUAGE_STORAGE_KEY) ??
    localStorage.getItem("i18nextLng");
  if (stored === "fa" || stored === "en") {
    return stored;
  }
  return "fa";
};

export const useLanguageStore = create<LanguageState>((set) => ({
  language: getInitialLanguage(),

  setLanguage: (lang) => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    localStorage.setItem("i18nextLng", lang);
    void i18n.changeLanguage(lang);
    set({ language: lang });
  },
}));
