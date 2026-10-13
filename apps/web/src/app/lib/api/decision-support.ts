import {isRunEnvelope,isHistoryPage,isHistoricalAhp} from "@/components/decision-support/execution-record-rules";
export {isSavedCase,isCompletedRun} from "@/components/decision-support/execution-record-rules";
import { PATHS } from "@/app/routeVars";
import { apiFetch, apiJson } from "@/app/lib/api-client";
export { isIsmRunResult, isIsmRunResponse, isIsmSavedCase } from "@/components/decision-support/ism-result-rules";
export type { IsmRunResult, IsmLayer } from "@/components/decision-support/ism-result-rules";
import type { IsmRunResult } from "@/components/decision-support/ism-result-rules";

export type DecisionMethod = "saw" | "topsis" | "ahp" | "dematel" | "ism";

export const DECISION_METHODS: DecisionMethod[] = ["saw", "topsis", "ahp", "dematel", "ism"];

export type CriterionType = "benefit" | "cost";

export type SawRankingRow = {
  option: string;
  score: number;
  rank: number;
};

export type TopsisRankingRow = {
  option: string;
  d_best: number;
  d_worst: number;
  closeness: number;
  score: number;
  rank: number;
};

export type RankingRow = SawRankingRow | TopsisRankingRow;

export type DecisionCase = {
  id: string;
  title: string;
  selected_methods: DecisionMethod[];
  criteria: string[];
  alternatives: string[];
  weights: number[];
  types: CriterionType[];
  performance_matrix: (number | null)[][];
  ahp_matrix: (number | null)[][];
  dematel_matrix: unknown[];
  ism_matrix: unknown;
  criteria_count?: number;
  alternatives_count?: number;
  created_at?: string;
  updated_at?: string;
};

export type DecisionCaseSummary = {
  id: string;
  title: string;
  selected_methods: DecisionMethod[];
  criteria_count: number;
  alternatives_count: number;
  updated_at: string;
};

export type AhpWeightRow = {
  criterion: string;
  weight: number;
  rank: number;
};

export type AhpRunResult = {
  status: "ok";
  engine: "ahp";
  weights: AhpWeightRow[];
  lambda_max: number;
  ci: number;
  cr: number;
  is_consistent: boolean;
};

export type DecisionRunResult = Partial<Omit<IsmRunResult, "status" | "engine">> & {
  status?: string;
  engine?: string | null;
  ranking?: RankingRow[];
  weights?: AhpWeightRow[];
  lambda_max?: number;
  ci?: number;
  cr?: number;
  is_consistent?: boolean;
};

export type DecisionRunSummary = {
  id: string;
  method: DecisionMethod;
  extracted_at: string;
  extracted_by: string;
  extracted_by_name?: string;
  result: DecisionRunResult;
};

export type DecisionRun = DecisionRunSummary & {
  input_snapshot: Record<string, unknown>;
};

export class DecisionSupportRequestError extends Error {
  payload: unknown;
  constructor(message: string, payload: unknown) {
    super(message);
    this.name = "DecisionSupportRequestError";
    this.payload = payload;
  }
}

function base(projectId: string) {
  return `/${PATHS.API_PROJECTS}/${projectId}/decision-cases`;
}

async function jsonOrThrow<T>(path: string, options: RequestInit): Promise<T> {
  const res = await apiFetch(path, options);
  const raw = await res.text();
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    throw new DecisionSupportRequestError("Invalid JSON response", null);
  }
  if (!res.ok) {
    const errObj = data as { error?: { message?: string } | string };
    const message =
      typeof errObj?.error === "object" && errObj?.error?.message
        ? errObj.error.message
        : typeof errObj?.error === "string"
          ? errObj.error
          : res.statusText || "Request failed";
    throw new DecisionSupportRequestError(message, data);
  }
  return data as T;
}

export function listDecisionCases(projectId: string) {
  return apiJson<{ count: number; results: DecisionCaseSummary[] }>(`${base(projectId)}/`);
}

export function getDecisionCase(projectId: string, caseId: string) {
  return apiJson<DecisionCase>(`${base(projectId)}/${caseId}/`);
}

export function createDecisionCase(
  projectId: string,
  body: Partial<DecisionCase> & { title: string },
) {
  return jsonOrThrow<DecisionCase>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function patchDecisionCase(projectId: string, caseId: string, body: Partial<DecisionCase>) {
  return jsonOrThrow<DecisionCase>(`${base(projectId)}/${caseId}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function listDecisionRuns(
  projectId: string, caseId: string,
  options: { method?: DecisionMethod; page?: number; pageSize?: number; signal?: AbortSignal } = {},
) {
  const query = new URLSearchParams();
  if (options.method) query.set("method", options.method);
  if (options.page) query.set("page", String(options.page));
  if (options.pageSize) query.set("page_size", String(options.pageSize));
  const value = await jsonOrThrow<unknown>(
    `${base(projectId)}/${caseId}/runs/?${query}`,
    { method: "GET", signal: options.signal },
  );
  if (!isHistoryPage(value)) throw new DecisionSupportRequestError("Invalid execution history response", null);
  return value;
}

export async function getDecisionRun(projectId: string, caseId: string, runId: string, signal?: AbortSignal) {
  const value = await jsonOrThrow<unknown>(`${base(projectId)}/${caseId}/runs/${runId}/`, {method:"GET",signal});
  if (!isRunEnvelope(value,runId)) throw new DecisionSupportRequestError("Invalid execution detail response", null);
  return value;
}

export function createDecisionRun(projectId: string, caseId: string, method: DecisionMethod) {
  return jsonOrThrow<DecisionRun>(`${base(projectId)}/${caseId}/runs/`, {
    method: "POST",
    body: JSON.stringify({ method }),
  });
}

/** Accept completed server output only; older stub rows remain inspectable. */
export function isAhpRunResult(result: unknown): result is AhpRunResult {
  if (!result || typeof result !== "object" || !Array.isArray((result as AhpRunResult).weights)) return false;
  const value = result as AhpRunResult;
  return isHistoricalAhp(value, value.weights.map(row => row && typeof row === "object" ? row.criterion : undefined));
}
