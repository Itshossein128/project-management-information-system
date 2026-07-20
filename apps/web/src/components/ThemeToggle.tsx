import { Button } from "@/components/form";
import { useThemeStore } from "@/app/store/themeStore";
import { Moon, Sun } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";

export function ThemeToggle() {
  const { t } = useTranslation();
  const theme = useThemeStore((s) => s.theme);
  const toggleTheme = useThemeStore((s) => s.toggleTheme);
  const isDark = theme === "dark";

  return (
    <Button
      id="button-themeToggle"
      type="button"
      variant="ghost"
      size="icon-sm"
      aria-label={isDark ? t("theme.switchToLight") : t("theme.switchToDark")}
      title={isDark ? t("theme.light") : t("theme.dark")}
      onClick={toggleTheme}
      className={cn(
        "relative rounded-full hover:bg-muted focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-colors",
        "h-9 w-9"
      )}
    >
      <Sun
        id="icon-themeLight"
        className={cn(
          "size-4 absolute transition-all",
          isDark ? "rotate-90 scale-0" : "rotate-0 scale-100"
        )}
        aria-hidden
      />
      <Moon
        id="icon-themeDark"
        className={cn(
          "size-4 absolute transition-all",
          isDark ? "rotate-0 scale-100" : "-rotate-90 scale-0"
        )}
        aria-hidden
      />
    </Button>
  );
}
