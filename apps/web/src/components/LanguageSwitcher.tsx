import { useLanguageStore } from "src/app/store/languageStore";
import { useTranslation } from "react-i18next";
import { cn } from "src/app/lib/utils";

export const LanguageSwitcher = () => {
  const { t } = useTranslation();
  const { language, setLanguage } = useLanguageStore();

  return (
    <div
      id="container-languageSwitcher"
      className="segmented-control"
      role="group"
      aria-label={t("language.select")}
    >
      {(["en", "fa"] as const).map((lang) => (
        <button
          key={lang}
          id={`button-language-${lang}`}
          type="button"
          className={cn("segmented-control-item", "uppercase")}
          data-active={language === lang ? "true" : "false"}
          aria-pressed={language === lang}
          aria-label={lang === "en" ? t("language.english") : t("language.persian")}
          title={lang === "en" ? t("language.english") : t("language.persian")}
          onClick={() => setLanguage(lang)}
        >
          {lang}
        </button>
      ))}
    </div>
  );
};
