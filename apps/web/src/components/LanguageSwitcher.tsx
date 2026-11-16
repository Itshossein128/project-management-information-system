import { Globe } from "lucide-react";
import { useLanguageStore } from "src/app/store/languageStore";
import { useTranslation } from "react-i18next";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

/** Native language names so each option is recognisable regardless of the active UI language. */
const OPTIONS = [
  { lang: "fa", short: "فا", native: "فارسی" },
  { lang: "en", short: "EN", native: "English" },
] as const;

export const LanguageSwitcher = () => {
  const { t } = useTranslation();
  const { language, setLanguage } = useLanguageStore();

  return (
    <div className="flex h-9 items-center gap-1.5 rounded-lg border border-border bg-background pe-1 ps-2.5 shadow-xs">
      <Globe className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
      <ToggleGroup
        id="container-languageSwitcher"
        type="single"
        value={language}
        onValueChange={(val) => {
          if (val) setLanguage(val as "en" | "fa");
        }}
        aria-label={t("language.select")}
        dir="ltr"
        className="gap-0.5 rounded-md bg-muted p-0.5"
      >
        {OPTIONS.map(({ lang, short, native }) => {
          const label = lang === "en" ? t("language.english") : t("language.persian");
          return (
            <Tooltip key={lang}>
              <TooltipTrigger asChild>
                <ToggleGroupItem
                  id={`button-language-${lang}`}
                  value={lang}
                  aria-label={label}
                  className="h-7 min-w-9 rounded-[5px] px-2.5 text-xs font-semibold text-muted-foreground transition-colors hover:bg-background/60 hover:text-foreground aria-[checked=true]:bg-primary aria-[checked=true]:text-primary-foreground aria-[checked=true]:shadow-sm aria-[checked=true]:hover:bg-primary aria-[checked=true]:hover:text-primary-foreground focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {short}
                </ToggleGroupItem>
              </TooltipTrigger>
              <TooltipContent>{native}</TooltipContent>
            </Tooltip>
          );
        })}
      </ToggleGroup>
    </div>
  );
};
