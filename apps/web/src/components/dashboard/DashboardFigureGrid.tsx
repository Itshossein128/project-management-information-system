import { useTranslation } from "react-i18next";
import {
  type DashboardFigure,
  figureTitleKey,
  formatFigureValue,
} from "@/app/lib/api/dashboards";
import { KPICard } from "@/components/progress/KPICard";
import { cn } from "@/app/lib/utils";

export function DashboardFigureGrid({
  figures,
  onFigureClick,
  className,
}: {
  figures: DashboardFigure[];
  onFigureClick?: (figure: DashboardFigure) => void;
  className?: string;
}) {
  const { t } = useTranslation();

  if (!figures.length) {
    return (
      <p className="text-sm text-muted-foreground">{t("dashboard.noFigures")}</p>
    );
  }

  return (
    <div className={cn("grid gap-4 sm:grid-cols-2 lg:grid-cols-3", className)}>
      {figures.map((figure) => {
        const clickable =
          figure.status === "ok" && figure.drill?.href && Boolean(onFigureClick);
        const title = t(figureTitleKey(figure.figure_key), figure.figure_key);
        const statusNote =
          figure.status === "inactive"
            ? t("dashboard.statusInactive")
            : figure.status === "unavailable"
              ? t("dashboard.statusUnavailable")
              : figure.label_unapproved
                ? t("dashboard.unapprovedLabel")
                : undefined;

        return (
          <button
            key={figure.figure_key}
            type="button"
            disabled={!clickable}
            onClick={() => clickable && onFigureClick?.(figure)}
            className={cn(
              "text-start",
              clickable && "cursor-pointer transition hover:opacity-90",
              !clickable && "cursor-default",
            )}
            data-testid={`dashboard-figure-${figure.figure_key}`}
          >
            <KPICard
              title={title}
              value={formatFigureValue(figure)}
              subtitle={statusNote}
              footer={
                clickable ? (
                  <span className="text-primary">{t("dashboard.drillHint")}</span>
                ) : null
              }
            />
          </button>
        );
      })}
    </div>
  );
}
