import { useTranslation } from "react-i18next";
import {
  Activity,
  ArrowUpRight,
  Banknote,
  ChartNoAxesColumn,
  Clock3,
  Gauge,
  TriangleAlert,
  Wallet,
} from "lucide-react";
import {
  type DashboardFigure,
  figureTitleKey,
  formatFigureValue,
} from "@/app/lib/api/dashboards";
import { cn } from "@/app/lib/utils";

const figureIcons = {
  "evm.spi": Clock3,
  "evm.cpi": Gauge,
  "progress.plan_vs_actual": Activity,
  "cash.net_balance": Wallet,
  "schedule.critical_activities": TriangleAlert,
  "finance.budget": Banknote,
  "finance.actual_cost": Banknote,
};

export function DashboardFigureGrid({
  figures,
  onFigureClick,
  className,
}: {
  figures: DashboardFigure[];
  onFigureClick?: (figure: DashboardFigure) => void;
  className?: string;
}) {
  const { t, i18n } = useTranslation();
  if (!figures.length)
    return (
      <p className="text-sm text-muted-foreground">
        {t("dashboard.noFigures")}
      </p>
    );

  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-3 min-[380px]:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5",
        className,
      )}
    >
      {figures.map((figure, index) => {
        const available = figure.status === "ok" && figure.value != null;
        const clickable =
          available && Boolean(figure.drill?.href && onFigureClick);
        const title = t(figureTitleKey(figure.figure_key), figure.figure_key);
        const Icon =
          figureIcons[figure.figure_key as keyof typeof figureIcons] ??
          ChartNoAxesColumn;
        const statusNote =
          figure.status === "inactive"
            ? t("dashboard.statusInactive")
            : !available
              ? t("dashboard.statusUnavailable")
              : figure.label_unapproved
                ? t("dashboard.unapprovedLabel")
                : undefined;
        const description =
          figure.figure_key === "evm.spi"
            ? t("dashboard.portfolio.spiDescription")
            : figure.figure_key === "evm.cpi"
              ? t("dashboard.portfolio.cpiDescription")
              : null;
        const Tile = clickable ? "button" : "div";

        return (
          <Tile
            key={figure.figure_key}
            type={clickable ? "button" : undefined}
            onClick={clickable ? () => onFigureClick?.(figure) : undefined}
            aria-label={
              clickable
                ? t("dashboard.portfolio.openIndicator", {
                    indicator: title,
                    value: formatFigureValue(figure, i18n.language),
                  })
                : undefined
            }
            className={cn(
              "flex h-full min-h-40 min-w-0 flex-col rounded-xl border border-border/80 bg-background/70 p-4 text-start",
              figures.length % 2 === 1 &&
                index === figures.length - 1 &&
                "min-[380px]:col-span-2 lg:col-span-1",
              clickable &&
                "group cursor-pointer transition-colors hover:border-primary/40 hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              !available && "border-dashed bg-muted/20",
            )}
            data-testid={`dashboard-figure-${figure.figure_key}`}
          >
            <span className="flex min-h-10 items-start justify-between gap-2">
              <span className="text-sm font-medium leading-snug">{title}</span>
              <Icon
                className={cn(
                  "size-4 shrink-0",
                  available ? "text-primary" : "text-muted-foreground",
                )}
                aria-hidden="true"
              />
            </span>
            <span className="my-2 break-words text-2xl font-semibold tabular-nums tracking-tight">
              <bdi>{formatFigureValue(figure, i18n.language)}</bdi>
            </span>
            {description ? (
              <span className="mb-2 text-xs leading-relaxed text-muted-foreground">
                {description}
              </span>
            ) : null}
            {statusNote ? (
              <span
                className={cn(
                  "mt-auto text-xs leading-relaxed",
                  figure.label_unapproved && available
                    ? "text-warning-800 dark:text-warning-300"
                    : "text-muted-foreground",
                )}
              >
                {statusNote}
              </span>
            ) : null}
            {clickable ? (
              <span className="mt-auto flex items-center justify-between gap-2 pt-2 text-xs font-medium text-foreground/80 group-hover:text-foreground">
                {t("dashboard.portfolio.viewDetails")}
                <ArrowUpRight
                  className="size-3.5 shrink-0 rtl:-scale-x-100"
                  aria-hidden="true"
                />
              </span>
            ) : null}
          </Tile>
        );
      })}
    </div>
  );
}
