import { useLanguageStore } from "src/app/store/languageStore";
import { useTranslation } from "react-i18next";
import { cn } from "src/app/lib/utils";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

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
      {(["en", "fa"] as const).map((lang) => {
        const label = lang === "en" ? t("language.english") : t("language.persian");
        return (
          <Tooltip key={lang}>
            <TooltipTrigger asChild>
              <ToggleGroupItem
                id={`button-language-${lang}`}
                value={lang}
                aria-label={label}
                className="uppercase data-[state=on]:bg-background data-[state=on]:shadow-sm rounded-sm px-3 py-1.5 h-auto text-xs font-medium"
              >
                {lang}
              </ToggleGroupItem>
            </TooltipTrigger>
            <TooltipContent side="bottom">{label}</TooltipContent>
          </Tooltip>
        );
      })}
    </ToggleGroup>
  );
};
