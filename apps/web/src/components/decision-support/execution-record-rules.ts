import type {
  DecisionCase,
  DecisionRun,
  DecisionRunSummary,
  DecisionMethod,
  RankingRow,
  AhpRunResult,
} from "../../app/lib/api/decision-support.ts";
import {
  isIsmRunResult,
  isIsmRunResponse,
  type IsmRunResult,
  // @ts-expect-error Native Node guard tests require an explicit source extension.
} from "./ism-result-rules.ts";
export const object = (v: unknown): v is Record<string, unknown> =>
  !!v && typeof v === "object" && !Array.isArray(v);
const methods = ["saw", "topsis", "ahp", "ism", "dematel"];
const text = (v: unknown): v is string => typeof v === "string" && !!v.trim();
const finite = (v: unknown): v is number =>
  typeof v === "number" && Number.isFinite(v);
export const names = (v: unknown): v is string[] =>
  Array.isArray(v) &&
  v.length > 0 &&
  v.length <= 10 &&
  v.every(text) &&
  new Set(v).size === v.length;
export function isSavedCase(v: unknown, id?: string): v is DecisionCase {
  return (
    object(v) &&
    text(v.id) &&
    (!id || v.id === id) &&
    text(v.title) &&
    Array.isArray(v.criteria) &&
    v.criteria.every((x) => typeof x === "string") &&
    Array.isArray(v.alternatives) &&
    v.alternatives.every((x) => typeof x === "string") &&
    Array.isArray(v.selected_methods) &&
    v.selected_methods.every(
      (x) => typeof x === "string" && methods.includes(x),
    ) &&
    [
      "weights",
      "types",
      "performance_matrix",
      "ahp_matrix",
      "dematel_matrix",
      "ism_matrix",
    ].every((k) => v[k] !== undefined)
  );
}
export function isRunEnvelope(v: unknown, id?: string): v is DecisionRun {
  return (
    object(v) &&
    text(v.id) &&
    (!id || v.id === id) &&
    typeof v.method === "string" &&
    methods.includes(v.method) &&
    text(v.extracted_by) &&
    typeof v.extracted_at === "string" &&
    Number.isFinite(Date.parse(v.extracted_at)) &&
    (v.extracted_by_name === undefined ||
      v.extracted_by_name === null ||
      typeof v.extracted_by_name === "string")
  );
}
export function isHistoryPage(v: unknown): v is {
  count: number;
  next: string | null;
  previous: string | null;
  results: DecisionRunSummary[];
} {
  return (
    object(v) &&
    Number.isInteger(v.count) &&
    Number(v.count) >= 0 &&
    [v.next, v.previous].every((x) => x === null || typeof x === "string") &&
    Array.isArray(v.results) &&
    v.results.every((x) => isRunEnvelope(x)) &&
    new Set(v.results.map((x) => x.id)).size === v.results.length &&
    v.results.length <= Number(v.count)
  );
}
const vector = (
  v: unknown,
  n: number,
  predicate: (value: unknown) => boolean = finite,
): v is number[] => Array.isArray(v) && v.length === n && v.every(predicate);
const matrix = (
  v: unknown,
  m: number,
  n: number,
  predicate: (value: unknown) => boolean = finite,
): v is number[][] =>
  Array.isArray(v) &&
  v.length === m &&
  v.every((row) => vector(row, n, predicate));
function rows(
  v: unknown,
  axis: string[],
  label: string,
  value: string,
): v is Record<string, unknown>[] {
  if (
    !Array.isArray(v) ||
    v.length !== axis.length ||
    !v.every(
      (r) =>
        object(r) &&
        typeof r[label] === "string" &&
        axis.includes(r[label] as string) &&
        finite(r[value]) &&
        Number.isInteger(r.rank) &&
        Number(r.rank) > 0,
    )
  )
    return false;
  return (
    new Set(v.map((r) => r[label])).size === axis.length &&
    new Set(v.map((r) => r.rank)).size === axis.length
  );
}
export function isHistoricalAhp(v: unknown, axis: unknown): v is AhpRunResult {
  return (
    names(axis) &&
    object(v) &&
    v.status === "ok" &&
    v.engine === "ahp" &&
    rows(v.weights, axis, "criterion", "weight") &&
    (v.weights as Record<string, unknown>[]).every(
      (r) => Number(r.weight) > 0,
    ) &&
    [v.lambda_max, v.ci, v.cr].every(finite) &&
    typeof v.is_consistent === "boolean"
  );
}
export type DematelResult = {
  status: "ok";
  engine: "dematel";
  normalization_factor?: number;
  normalized_matrix?: number[][];
  total_relation_matrix?: number[][];
  criteria_results: {
    criterion: string;
    d: number;
    r: number;
    prominence: number;
    relation: number;
    role: string;
  }[];
  numerical_policy: Record<string, unknown>;
};
export function isHistoricalDematel(
  v: unknown,
  axis: unknown,
): v is DematelResult {
  if (
    !names(axis) ||
    !object(v) ||
    v.status !== "ok" ||
    v.engine !== "dematel" ||
    !object(v.numerical_policy) ||
    !Array.isArray(v.criteria_results) ||
    v.criteria_results.length !== axis.length
  )
    return false;
  const policy = {
    version: "dematel-v1",
    normalization: "max_row_sum",
    condition_limit: 1e8,
    residual_tolerance: 1e-10,
    total_relation_roundoff_factor: 1e-12,
    role_neutrality_tolerance: 1e-9,
  };
  const stored = v.numerical_policy;
  return (
    Object.entries(policy).every(([k, x]) => stored[k] === x) &&
    v.criteria_results.every(
      (r, i) =>
        object(r) &&
        r.criterion === axis[i] &&
        [r.d, r.r, r.prominence, r.relation].every(finite) &&
        typeof r.role === "string" &&
        ["influencing", "receiving", "balanced"].includes(r.role),
    ) &&
    ["normalized_matrix", "total_relation_matrix"].every(
      (k) => v[k] === undefined || matrix(v[k], axis.length, axis.length),
    ) &&
    (v.normalization_factor === undefined || finite(v.normalization_factor))
  );
}
export function classifyHistory(v: unknown) {
  const record = object(v) ? v : {};
  const snapshot = object(record.input_snapshot) ? record.input_snapshot : {};
  const criteria = names(snapshot.criteria) ? snapshot.criteria : [];
  const alternatives = names(snapshot.alternatives)
    ? snapshot.alternatives
    : [];
  const result = object(record.result) ? record.result : {};
  const ranking =
    (record.method === "saw" || record.method === "topsis") &&
    result.status === "ok" &&
    result.engine === record.method &&
    alternatives.length &&
    rows(result.ranking, alternatives, "option", "score")
      ? (result.ranking as unknown as RankingRow[])
      : null;
  return {
    snapshot,
    criteria,
    alternatives,
    ranking,
    ahp:
      record.method === "ahp" && isHistoricalAhp(result, criteria)
        ? result
        : null,
    ism:
      record.method === "ism" && isIsmRunResult(result, criteria)
        ? (result as IsmRunResult)
        : null,
    dematel:
      record.method === "dematel" && isHistoricalDematel(result, criteria)
        ? result
        : null,
  };
}
export function isCompletedRun(
  v: unknown,
  method: DecisionMethod | string,
): v is DecisionRun {
  if (!isRunEnvelope(v) || v.method !== method || !object(v.input_snapshot))
    return false;
  const h = classifyHistory(v);
  const s = h.snapshot,
    n = h.criteria.length;
  if (!n) return false;
  if (method === "ism") return isIsmRunResponse(v);
  if (method === "ahp")
    return !!h.ahp && matrix(s.ahp_matrix, n, n, (x) => finite(x) && x > 0);
  if (method === "dematel") return false; // No live engine in this feature.
  if (
    !h.ranking ||
    !h.alternatives.length ||
    !vector(s.weights, n, (x) => finite(x) && x >= 0) ||
    !vector(s.weights_normalized, n, (x) => finite(x) && x >= 0) ||
    !Array.isArray(s.types) ||
    s.types.length !== n ||
    !s.types.every((x) => x === "cost" || x === "benefit") ||
    !matrix(s.performance_matrix, h.alternatives.length, n)
  )
    return false;
  return (
    method === "saw" ||
    h.ranking.every((row) => {
      const values = row as unknown as Record<string, unknown>;
      return [values.d_best, values.d_worst, values.closeness].every(finite);
    })
  );
}
