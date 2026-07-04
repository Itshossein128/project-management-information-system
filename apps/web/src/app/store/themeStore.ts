import { create } from "zustand";

export type Theme = "light" | "dark";

const STORAGE_KEY = "app-theme";

// Function to manage getInitialTheme
export function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "light";
  // Variable holding stored
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;
  return "light";
}

// Function to manage applyTheme
export function applyTheme(theme: Theme) {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle("dark", theme === "dark");
  document.documentElement.style.colorScheme = theme;
}

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: getInitialTheme(),

  setTheme: (theme) => {
    localStorage.setItem(STORAGE_KEY, theme);
    applyTheme(theme);
    set({ theme });
  },

  toggleTheme: () => {
    // Variable holding next
    const next = get().theme === "dark" ? "light" : "dark";
    get().setTheme(next);
  },
}));
