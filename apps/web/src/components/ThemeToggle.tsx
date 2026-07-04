import { Button } from "@/components/form";
import { useThemeStore } from "@/app/store/themeStore";
import { Moon, Sun } from "lucide-react";
import { useTranslation } from "react-i18next";

// Function to manage ThemeToggle
export function ThemeToggle() {
  const { t } = useTranslation();
  // Variable holding theme
  const theme = useThemeStore((s) => s.theme);
  // Variable holding toggleTheme
  const toggleTheme = useThemeStore((s) => s.toggleTheme);
  // Variable holding isDark
  const isDark = theme === "dark";

  return (
    <Button
      id="button-themeToggle"
      type="button"
      variant="outline"
      size="icon-sm"
      aria-label={isDark ? t("theme.switchToLight") : t("theme.switchToDark")}
      title={isDark ? t("theme.light") : t("theme.dark")}
      onClick={toggleTheme}
    >
      {isDark ? (
        <Sun id="icon-themeLight" className="size-4" aria-hidden />
      ) : (
        <Moon id="icon-themeDark" className="size-4" aria-hidden />
      )}
    </Button>
  );
}
