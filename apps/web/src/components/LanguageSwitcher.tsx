import { useLanguageStore } from "src/app/store/languageStore";

// Function to manage LanguageSwitcher
export const LanguageSwitcher = () => {
  const { language, setLanguage } = useLanguageStore();

  return (
    <div
      id="container-languageSwitcher"
      className="segmented-control"
      role="group"
      aria-label="Language"
    >
      {(["en", "fa"] as const).map((lang) => (
        <button
          key={lang}
          id={`button-language-${lang}`}
          type="button"
          className="segmented-control-item"
          data-active={language === lang ? "true" : "false"}
          aria-pressed={language === lang}
          onClick={() => setLanguage(lang)}
        >
          {lang}
        </button>
      ))}
    </div>
  );
};
