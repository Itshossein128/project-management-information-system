import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const projectBase = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface ReportCatalogEntry {
  report_type: string;
  title: string;
  supported_filters: string[];
  approved_only_default: boolean;
}

export interface ReportCatalogResponse {
  results: ReportCatalogEntry[];
}

export interface ReportExportMetadata {
  id: string;
  report_type: string;
  project_id: string | null;
  filters: Record<string, unknown>;
  extracted_at: string;
  extracted_by: string;
  approved_only: boolean;
  payload_sha256: string | null;
  download_url: string;
}

export type StandardReportBody = Record<string, unknown>;

function normalizeApiPath(path: string): string {
  if (path.startsWith("/api/")) return path.slice(4);
  return path.startsWith("/") ? path : `/${path}`;
}

function queryFromFilters(filters: Record<string, string | boolean | undefined>) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v === undefined || v === "") continue;
    search.set(k, String(v));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function fetchProjectReportCatalog(projectId: string) {
  return apiJson<ReportCatalogResponse>(`${projectBase(projectId)}/reports/catalog/`);
}

export function fetchPortfolioReportCatalog() {
  return apiJson<ReportCatalogResponse>("/v1/portfolio/reports/catalog/");
}

export function runProjectReport(
  projectId: string,
  reportType: string,
  filters: Record<string, string | boolean | undefined> = {},
) {
  return apiJson<StandardReportBody>(
    `${projectBase(projectId)}/reports/${reportType}/${queryFromFilters(filters)}`,
  );
}

export function exportProjectReport(
  projectId: string,
  reportType: string,
  body: { filters?: Record<string, unknown>; format?: string } = {},
) {
  return apiJson<ReportExportMetadata>(`${projectBase(projectId)}/reports/${reportType}/export/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function exportPortfolioReport(
  reportType: string,
  body: { filters?: Record<string, unknown>; format?: string } = {},
) {
  return apiJson<ReportExportMetadata>(`/v1/portfolio/reports/${reportType}/export/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchProjectReportExportMetadata(projectId: string, exportId: string) {
  return apiJson<ReportExportMetadata>(
    `${projectBase(projectId)}/reports/exports/${exportId}/`,
  );
}

export function downloadProjectReportExport(projectId: string, exportId: string) {
  return apiJson<Record<string, unknown>>(
    `${projectBase(projectId)}/reports/exports/${exportId}/download/`,
  );
}

export function downloadReportExportByUrl(downloadUrl: string) {
  return apiJson<Record<string, unknown>>(normalizeApiPath(downloadUrl));
}
