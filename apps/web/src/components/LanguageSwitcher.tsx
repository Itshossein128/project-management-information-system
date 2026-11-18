import { useLanguageStore } from "src/app/store/languageStore";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
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
  const isEn = language === "en";

  return (
    <ToggleGroup
      id="container-languageSwitcher"
      type="single"
      spacing={1}
      value={language}
      onValueChange={(val) => {
        if (val) setLanguage(val as "en" | "fa");
      }}
      aria-label={t("language.select")}
      dir="ltr"
      className="relative inline-grid h-9 grid-cols-2 items-center rounded-full border border-border/70 bg-muted/80 p-1 shadow-2xs"
    >
      <span
        aria-hidden="true"
        className={cn(
          "pointer-events-none absolute inset-y-1 start-1 w-[calc(50%-4px)] rounded-full bg-background shadow-xs ring-1 ring-border/40 transition-transform duration-200 ease-out dark:bg-card",
          isEn ? "translate-x-full" : "translate-x-0"
        )}
      />
      {OPTIONS.map(({ lang, short, native }) => {
        const label = lang === "en" ? t("language.english") : t("language.persian");
        return (
          <Tooltip key={lang}>
            <TooltipTrigger asChild>
              <ToggleGroupItem
                id={`button-language-${lang}`}
                value={lang}
                aria-label={label}
                className="relative z-10 h-7 min-w-9 cursor-pointer rounded-full bg-transparent px-2.5 text-xs leading-none font-semibold text-muted-foreground transition-colors hover:bg-transparent hover:text-foreground aria-[checked=true]:bg-transparent aria-[checked=true]:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
              >
                {short}
              </ToggleGroupItem>
            </TooltipTrigger>
            <TooltipContent>{native}</TooltipContent>
          </Tooltip>
        );
      })}
    </ToggleGroup>
  );
};
