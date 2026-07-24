/**
 * Resolve chart stroke/fill colors from design tokens at runtime.
 * Prefer these over hardcoded hex so charts follow the shared palette.
 */

const TOKEN_VARS = {
  brand: "--palette-brand-500",
  brandStrong: "--palette-brand-600",
  brandMuted: "--palette-brand-300",
  success: "--palette-success-500",
  successStrong: "--palette-success-600",
  warning: "--palette-warning-500",
  warningStrong: "--palette-warning-600",
  danger: "--palette-danger-500",
  dangerStrong: "--palette-danger-600",
  info: "--palette-info-500",
  accent: "--palette-accent-500",
  accentStrong: "--palette-accent-600",
  neutral: "--palette-neutral-400",
  neutralStrong: "--palette-neutral-500",
  chart1: "--chart-1",
  chart2: "--chart-2",
  chart3: "--chart-3",
  chart4: "--chart-4",
  chart5: "--chart-5",
} as const;

export type ChartToken = keyof typeof TOKEN_VARS;

/** Fallback hex when CSS vars are unavailable (SSR / tests). */
const FALLBACKS: Record<ChartToken, string> = {
  brand: "#475569",
  brandStrong: "#334155",
  brandMuted: "#94a3b8",
  success: "#059669",
  successStrong: "#047857",
  warning: "#d97706",
  warningStrong: "#b45309",
  danger: "#dc2626",
  dangerStrong: "#b91c1c",
  info: "#3b82a8",
  accent: "#ea580c",
  accentStrong: "#c2410c",
  neutral: "#94a3b8",
  neutralStrong: "#64748b",
  chart1: "#475569",
  chart2: "#059669",
  chart3: "#ea580c",
  chart4: "#3b82a8",
  chart5: "#d97706",
};

function readCssVar(varName: string): string | null {
  if (typeof window === "undefined" || typeof document === "undefined") return null;
  const value = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
  return value || null;
}

/** Resolve a single chart token to a usable CSS color. */
export function chartColor(token: ChartToken): string {
  return readCssVar(TOKEN_VARS[token]) ?? FALLBACKS[token];
}

/** Snapshot of common series colors for multi-series charts. */
export function chartPalette() {
  return {
    brand: chartColor("brand"),
    success: chartColor("success"),
    warning: chartColor("warning"),
    danger: chartColor("danger"),
    info: chartColor("info"),
    accent: chartColor("accent"),
    neutral: chartColor("neutral"),
    chart1: chartColor("chart1"),
    chart2: chartColor("chart2"),
    chart3: chartColor("chart3"),
    chart4: chartColor("chart4"),
    chart5: chartColor("chart5"),
  };
}
