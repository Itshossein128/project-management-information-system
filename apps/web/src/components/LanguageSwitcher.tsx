import { useLanguageStore } from "src/app/store/languageStore";
import { useTranslation } from "react-i18next";
import { cn } from "src/app/lib/utils";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

export const LanguageSwitcher = () => {
  const { t } = useTranslation();
  const { language, setLanguage } = useLanguageStore();

  return (
    <ToggleGroup
      id="container-languageSwitcher"
      type="single"
      value={language}
      onValueChange={(val) => {
        if (val) setLanguage(val as "en" | "fa");
      }}
      aria-label={t("language.select")}
      className="bg-muted p-1 rounded-md"
    >
      {(["en", "fa"] as const).map((lang) => (
        <ToggleGroupItem
          key={lang}
          id={`button-language-${lang}`}
          value={lang}
          aria-label={lang === "en" ? t("language.english") : t("language.persian")}
          title={lang === "en" ? t("language.english") : t("language.persian")}
          className="uppercase data-[state=on]:bg-background data-[state=on]:shadow-sm rounded-sm px-3 py-1.5 h-auto text-xs font-medium"
        >
          {lang}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
};
