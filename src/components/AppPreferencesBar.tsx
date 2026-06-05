import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";

/** Language + theme controls for headers and auth screens. */
export function AppPreferencesBar() {
  return (
    <div id="container-appPreferences" className="flex items-center gap-2">
      <ThemeToggle />
      <LanguageSwitcher />
    </div>
  );
}
