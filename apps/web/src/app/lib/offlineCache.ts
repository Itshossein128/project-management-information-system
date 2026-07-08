/**
 * Silent cache warming for offline use (Sprint 4, Section 1.6).
 *
 * Fetches the project reference data the daily-report form needs and mirrors it
 * into IndexedDB. Every step is best-effort: a failure (e.g. an endpoint not yet
 * deployed) never blocks the others.
 */
import { apiJson } from "@/app/lib/api-client";
import { fetchActivities } from "@/app/lib/api/activities";
import { fetchProject } from "@/app/lib/api/projects";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";
import {
  cacheActivities,
  cacheManpowerTitles,
  cacheProject,
  cacheSubcontractors,
  cacheWBS,
  isOfflineDBAvailable,
  type CachedManpowerTitle,
} from "@/app/lib/offlineDB";

interface JobTitleDTO {
  id: string;
  category: "indirect" | "direct";
  title?: string;
  [key: string]: unknown;
}

interface SubcontractorDTO {
  id: string;
  name?: string;
  counterparty?: string;
  [key: string]: unknown;
}

export async function warmProjectCache(projectId: string): Promise<void> {
  if (!isOfflineDBAvailable() || !projectId) return;

  await Promise.allSettled([
    fetchProject(projectId).then((project) =>
      cacheProject({ ...project, project_id: projectId }),
    ),
    fetchWBSFlat(projectId).then((nodes) =>
      cacheWBS(nodes.map((node) => ({ ...node, project_id: projectId }))),
    ),
    fetchActivities(projectId, { per_page: 500 }).then((res) =>
      cacheActivities(res.results.map((a) => ({ ...a, project_id: projectId }))),
    ),
    apiJson<JobTitleDTO[] | { results: JobTitleDTO[] }>(
      `/${PATHS.API_PROJECTS}/${projectId}/manpower/job-titles/`,
    ).then((data) => {
      const rows = Array.isArray(data) ? data : (data.results ?? []);
      cacheManpowerTitles(rows as unknown as CachedManpowerTitle[]);
    }),
    apiJson<SubcontractorDTO[] | { results: SubcontractorDTO[] }>(
      `/${PATHS.API_PROJECTS}/${projectId}/contracts/`,
    ).then((data) => {
      const rows = Array.isArray(data) ? data : (data.results ?? []);
      cacheSubcontractors(projectId, rows);
    }),
  ]);
}
