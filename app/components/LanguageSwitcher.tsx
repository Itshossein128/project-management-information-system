import { useTranslation } from "react-i18next";
import { Globe } from "lucide-react";
import { Button } from "./form/Button";
import {
  supportedLanguages,
  languageNames,
  isRTL,
  type SupportedLanguage,
} from "../lib/i18n";

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lang: SupportedLanguage) => {
    i18n.changeLanguage(lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = isRTL(lang) ? "rtl" : "ltr";
  };

  const currentLang = i18n.language as SupportedLanguage;
  const nextLang = currentLang === "fa" ? "en" : "fa";

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => changeLanguage(nextLang)}
      className="gap-2"
    >
      <Globe className="h-4 w-4" />
      <span>{languageNames[nextLang]}</span>
    </Button>
  );
}

export function LanguageDropdown() {
  const { i18n } = useTranslation();

  const changeLanguage = (lang: SupportedLanguage) => {
    i18n.changeLanguage(lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = isRTL(lang) ? "rtl" : "ltr";
  };

  return (
    <div className="flex gap-2">
      {supportedLanguages.map((lang) => (
        <Button
          key={lang}
          variant={i18n.language === lang ? "default" : "outline"}
          size="sm"
          onClick={() => changeLanguage(lang)}
        >
          {languageNames[lang]}
        </Button>
      ))}
    </div>
  );
}
