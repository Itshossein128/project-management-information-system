import { create } from "zustand";
import i18n, { type SupportedLanguage } from "src/app/lib/i18n";

interface LanguageState {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
}

/** Single storage key shared with i18next detector + API Accept-Language. */
export const LANGUAGE_STORAGE_KEY = "app-language";

export const useLanguageStore = create<LanguageState>((set) => ({
  // I18nSync restores browser preferences after hydration.
  language: "fa",

  setLanguage: (lang) => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    localStorage.setItem("i18nextLng", lang);
    void i18n.changeLanguage(lang);
    set({ language: lang });
  },
}));
