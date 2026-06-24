import { useEffect } from "react";
import { applyTheme, useThemeStore } from "@/app/store/themeStore";

/** Keeps `html.dark` and color-scheme in sync with the theme store after hydration. */
export function ThemeSync() {
  const theme = useThemeStore((s) => s.theme);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return null;
}
