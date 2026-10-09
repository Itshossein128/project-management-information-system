import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";
import type { ProjectKpis } from "@/app/lib/api/kpis";

const projectBase = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export type FigureStatus = "ok" | "inactive" | "unavailable";

export interface DashboardFigure {
  figure_key: string;
  value: number | string | null;
  status: FigureStatus;
  source_type: string;
  source_id: string | null;
  source_path: string;
  source_approved: boolean;
  last_updated_at: string | null;
  label_unapproved: boolean;
  drill: { href: string } | null;
}

export interface ProjectKpisWithFigures extends ProjectKpis {
  figures?: DashboardFigure[];
}

export interface KpiDrillRow {
  id: string;
  display: string;
  amount: number | null;
  approval_status: string;
  approved: boolean;
  last_updated_at: string | null;
  source_path: string;
}

export interface KpiDrillResponse {
  figure_key: string;
  results: KpiDrillRow[];
}

export interface DashboardPackGroup {
  group_key: string;
  title: string;
  figures: DashboardFigure[];
}

export interface ProjectDashboardPack {
  pack_id: string;
  project_id: string;
  as_of: string;
  groups: DashboardPackGroup[];
}

export interface PortfolioProjectRow {
  project_id: string;
  project_name: string;
  figures: DashboardFigure[];
}

export interface PortfolioDashboard {
  pack_id: string;
  as_of: string;
  projects: PortfolioProjectRow[];
}

function queryString(params: Record<string, string | undefined>) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v != null && v !== "") search.set(k, v);
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function fetchProjectKpisWithFigures(
  projectId: string,
  params: { as_of?: string; force_refresh?: string } = {},
) {
  return apiJson<ProjectKpisWithFigures>(
    `${projectBase(projectId)}/kpis/${queryString(params)}`,
  );
}

export function fetchKpiDrill(
  projectId: string,
  params: { figure_key: string; as_of?: string; approved_only?: string },
) {
  return apiJson<KpiDrillResponse>(
    `${projectBase(projectId)}/kpis/drill/${queryString(params)}`,
  );
}

export function fetchProjectDashboardPack(
  projectId: string,
  params: { pack?: string; as_of?: string } = {},
) {
  return apiJson<ProjectDashboardPack>(
    `${projectBase(projectId)}/dashboard/pack/${queryString(params)}`,
  );
}

export function fetchPortfolioDashboard(params: { as_of?: string } = {}) {
  return apiJson<PortfolioDashboard>(`/v1/portfolio/dashboard/${queryString(params)}`);
}

export function formatFigureValue(figure: DashboardFigure): string {
  if (figure.status === "inactive") return "—";
  if (figure.value == null) return "—";
  const key = figure.figure_key;
  if (key.startsWith("evm.")) {
    const n = Number(figure.value);
    return Number.isFinite(n) ? n.toFixed(3) : String(figure.value);
  }
  if (key === "progress.plan_vs_actual") {
    const n = Number(figure.value);
    return Number.isFinite(n) ? `${n.toFixed(1)}%` : String(figure.value);
  }
  if (key.startsWith("finance.") || key.startsWith("cash.")) {
    const n = Number(figure.value);
    return Number.isFinite(n) ? n.toLocaleString("fa-IR") : String(figure.value);
  }
  return String(figure.value);
}

export function figureTitleKey(figureKey: string): string {
  return `dashboard.figures.${figureKey.replace(/\./g, "_")}`;
}
