import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { KPICard } from "@/components/progress/KPICard";
import { formatFaAmount } from "@/app/lib/api/economic";
import type { ProjectKpis } from "@/app/lib/api/kpis";
import { PATHS } from "@/app/routeVars";

function fmtPct(v: number | null | undefined, digits = 1): string {
  if (v == null || Number.isNaN(v)) return "—";
  return `${v.toFixed(digits)}%`;
}

function fmtIndex(v: number | null | undefined): string {
  if (v == null || Number.isNaN(v)) return "—";
  return v.toFixed(3);
}

function fmtCount(v: number | null | undefined): string {
  if (v == null) return "—";
  return String(v);
}

type Section = "schedule" | "cost" | "cash" | "alerts";

export function ExecutiveKpiPanel({
  projectId,
  kpis,
  canViewSchedule,
  canViewCost,
  canViewCash,
  canViewAlerts,
}: {
  projectId: string;
  kpis: ProjectKpis;
  canViewSchedule: boolean;
  canViewCost: boolean;
  canViewCash: boolean;
  canViewAlerts: boolean;
}) {
  const { t } = useTranslation();
  const p = kpis?.panel;
  if (!p) return null;
  const base = `/${PATHS.PROJECT}/${projectId}`;

  const cards: Array<{
    section: Section;
    key: string;
    title: string;
    value: string;
    subtitle?: string;
    href: string;
    trend?: { label: string; positive: boolean } | null;
  }> = [
    {
      section: "schedule",
      key: "spi",
      title: "SPI",
      value: fmtIndex(p.spi),
      subtitle: t("dashboard.spiSubtitle"),
      href: `${base}/${PATHS.PROJECT_PROGRESS}`,
      trend:
        p.spi == null
          ? null
          : {
              label: p.spi >= 1 ? t("dashboard.onTrack") : t("dashboard.behindSchedule"),
              positive: p.spi >= 1,
            },
    },
    {
      section: "schedule",
      key: "physical",
      title: t("dashboard.physicalProgress"),
      value: fmtPct(p.physical_actual_pct),
      subtitle: `${t("dashboard.variance")}: ${fmtPct(p.schedule_variance_pct)}`,
      href: `${base}/${PATHS.PROJECT_PROGRESS}`,
    },
    {
      section: "schedule",
      key: "sv",
      title: t("dashboard.scheduleVariance"),
      value: fmtPct(p.schedule_variance_pct),
      href: `${base}/schedule/${PATHS.PROJECT_GANTT}`,
      trend:
        p.schedule_variance_pct == null
          ? null
          : {
              label:
                p.schedule_variance_pct >= 0
                  ? t("dashboard.aheadOfSchedule")
                  : t("dashboard.behindSchedule"),
              positive: p.schedule_variance_pct >= 0,
            },
    },
    {
      section: "schedule",
      key: "critical",
      title: t("dashboard.criticalActivities"),
      value: fmtCount(p.critical_activities),
      href: `${base}/schedule/${PATHS.PROJECT_GANTT}`,
    },
    {
      section: "schedule",
      key: "behind",
      title: t("dashboard.behindSchedule"),
      value: fmtCount(p.behind_schedule),
      href: `${base}/${PATHS.PROJECT_PROGRESS}`,
      trend:
        p.behind_schedule > 0
          ? { label: t("dashboard.actionNeeded"), positive: false }
          : { label: t("dashboard.noDelay"), positive: true },
    },
    {
      section: "cost",
      key: "cpi",
      title: "CPI",
      value: fmtIndex(p.cpi),
      subtitle: t("dashboard.cpiSubtitle"),
      href: `${base}/${PATHS.PROJECT_COSTS}`,
      trend:
        p.cpi == null
          ? null
          : {
              label: p.cpi >= 1 ? t("dashboard.underBudget") : t("dashboard.overBudget"),
              positive: p.cpi >= 1,
            },
    },
    {
      section: "cost",
      key: "budget",
      title: t("dashboard.budgetConsumption"),
      value: fmtPct(p.budget_consumption_pct),
      href: `${base}/${PATHS.PROJECT_COSTS}`,
    },
    {
      section: "cash",
      key: "net_cash",
      title: t("dashboard.netCash"),
      value: formatFaAmount(p.net_cash),
      href: `${base}/${PATHS.PROJECT_CASH_FLOW}`,
      trend: p.has_cash_gap
        ? { label: t("dashboard.cashGap"), positive: false }
        : { label: t("dashboard.noCashGap"), positive: true },
    },
    {
      section: "cash",
      key: "cash_gap",
      title: t("dashboard.cashGap"),
      value: p.has_cash_gap ? t("common.yes") : t("common.no"),
      href: `${base}/${PATHS.PROJECT_CASH_FLOW}`,
    },
    {
      section: "alerts",
      key: "alerts",
      title: t("dashboard.openAlerts"),
      value: fmtCount(p.open_alerts),
      href: `${base}/${PATHS.PROJECT_ALERTS}`,
      trend:
        p.open_alerts > 0
          ? { label: t("dashboard.needsReview"), positive: false }
          : { label: t("dashboard.allClear"), positive: true },
    },
  ];

  const visible = cards.filter((c) => {
    if (c.section === "schedule") return canViewSchedule;
    if (c.section === "cost") return canViewCost;
    if (c.section === "cash") return canViewCash;
    if (c.section === "alerts") return canViewAlerts;
    return false;
  });

  if (visible.length === 0) return null;

  return (
    <section className="mb-8" data-testid="executive-kpi-panel">
      <div className="mb-3 flex items-baseline justify-between gap-2">
        <h2 className="text-lg font-semibold">{t("dashboard.executiveTitle")}</h2>
        <span className="text-xs text-muted-foreground">{t("dashboard.asOf", { date: kpis.as_of })}</span>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {visible.map((c) => (
          <Link key={c.key} to={c.href} className="block transition hover:opacity-90">
            <KPICard title={c.title} value={c.value} subtitle={c.subtitle} trend={c.trend} />
          </Link>
        ))}
      </div>
    </section>
  );
}
