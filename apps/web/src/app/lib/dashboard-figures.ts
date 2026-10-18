import type { DashboardFigure } from "./api/dashboards.ts";

/** Format display values without treating missing data as a real zero. */
export function formatFigureValue(
  figure: Pick<DashboardFigure, "figure_key" | "status" | "value">,
  locale = "fa-IR",
): string {
  if (figure.status !== "ok" || figure.value == null) return "—";
  const numeric = Number(figure.value);
  if (!Number.isFinite(numeric) || figure.value === "")
    return String(figure.value);
  if (figure.figure_key.startsWith("evm.")) {
    return numeric.toLocaleString(locale, {
      minimumFractionDigits: 3,
      maximumFractionDigits: 3,
    });
  }
  if (figure.figure_key === "progress.plan_vs_actual") {
    return new Intl.NumberFormat(locale, {
      style: "percent",
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(numeric / 100);
  }
  return numeric.toLocaleString(locale);
}
