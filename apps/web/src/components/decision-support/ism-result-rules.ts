import type { DecisionRun } from "@/app/lib/api/decision-support";

export type IsmLayer = { level: number; criteria: string[] };
export type IsmRunResult = {
  status: "ok";
  engine: "ism";
  reachability_matrix: number[][];
  layers: IsmLayer[];
  mutual_groups: IsmLayer[];
  derivation_policy: {
    version: "ism-v1";
    self_inclusion: "binary_or";
    closure: "transitive";
    layer_rule: "reach_equals_intersection";
    layer_order: "top_to_bottom";
    mutual_groups: "maximal_non_singleton";
  };
};
const policy = {
  version: "ism-v1",
  self_inclusion: "binary_or",
  closure: "transitive",
  layer_rule: "reach_equals_intersection",
  layer_order: "top_to_bottom",
  mutual_groups: "maximal_non_singleton",
};
const object = (value: unknown): value is Record<string, unknown> =>
  !!value && typeof value === "object" && !Array.isArray(value);
/** Checks wire structure and frozen membership only; never derives scientific results. */
export function isIsmRunResult(
  value: unknown,
  criteria: unknown,
): value is IsmRunResult {
  if (
    !Array.isArray(criteria) ||
    criteria.length < 1 ||
    criteria.length > 10 ||
    criteria.some((name) => typeof name !== "string" || !name.trim()) ||
    new Set(criteria).size !== criteria.length
  )
    return false;
  if (
    !object(value) ||
    value.status !== "ok" ||
    value.engine !== "ism" ||
    !object(value.derivation_policy)
  )
    return false;
  const recordedPolicy = value.derivation_policy;
  if (Object.entries(policy).some(([key, id]) => recordedPolicy[key] !== id))
    return false;
  const n = criteria.length;
  if (
    !Array.isArray(value.reachability_matrix) ||
    value.reachability_matrix.length !== n ||
    value.reachability_matrix.some(
      (row) =>
        !Array.isArray(row) ||
        row.length !== n ||
        row.some(
          (cell) => typeof cell !== "number" || (cell !== 0 && cell !== 1),
        ),
    )
  )
    return false;
  if (
    !Array.isArray(value.layers) ||
    !value.layers.length ||
    value.layers.length > n ||
    !Array.isArray(value.mutual_groups)
  )
    return false;
  const memberships = new Map<string, number>();
  const orderedMembers = (
    members: unknown,
    min: number,
  ): members is string[] => {
    if (!Array.isArray(members) || members.length < min) return false;
    let last = -1;
    for (const member of members) {
      const index = criteria.indexOf(member);
      if (index <= last) return false;
      last = index;
    }
    return true;
  };
  for (const [i, layer] of value.layers.entries()) {
    if (
      !object(layer) ||
      layer.level !== i + 1 ||
      !orderedMembers(layer.criteria, 1)
    )
      return false;
    for (const name of layer.criteria) {
      if (memberships.has(name)) return false;
      memberships.set(name, i + 1);
    }
  }
  if (memberships.size !== n) return false;
  const grouped = new Set<string>();
  let lastLevel = 0;
  let lastIndex = -1;
  for (const group of value.mutual_groups) {
    if (
      !object(group) ||
      typeof group.level !== "number" ||
      !orderedMembers(group.criteria, 2)
    )
      return false;
    const index = criteria.indexOf(group.criteria[0]);
    if (
      group.level < lastLevel ||
      (group.level === lastLevel && index <= lastIndex)
    )
      return false;
    lastLevel = group.level;
    lastIndex = index;
    for (const name of group.criteria) {
      if (grouped.has(name) || memberships.get(name) !== group.level)
        return false;
      grouped.add(name);
    }
  }
  return true;
}

/** Validate the metadata consumed by the host; unrelated finite-invalid drafts stay raw. */
export function isIsmSavedCase(value: unknown, caseId: string): boolean {
  return (
    object(value) &&
    value.id === caseId &&
    typeof value.title === "string" &&
    !!value.title.trim() &&
    Array.isArray(value.criteria) &&
    value.criteria.every((name) => typeof name === "string") &&
    Array.isArray(value.selected_methods) &&
    value.selected_methods.every((method) => typeof method === "string") &&
    value.ism_matrix !== undefined
  );
}

/** Guard a completed execution before it can release the operation or reach callbacks. */
export function isIsmRunResponse(
  value: unknown,
): value is DecisionRun & { result: IsmRunResult } {
  if (
    !object(value) ||
    typeof value.id !== "string" ||
    !value.id ||
    value.method !== "ism" ||
    typeof value.extracted_at !== "string" ||
    !Number.isFinite(Date.parse(value.extracted_at)) ||
    typeof value.extracted_by !== "string" ||
    !value.extracted_by ||
    !object(value.input_snapshot) ||
    !isIsmRunResult(value.result, value.input_snapshot.criteria)
  )
    return false;
  const criteria = value.input_snapshot.criteria as string[];
  const direct = value.input_snapshot.ism_matrix;
  return (
    Array.isArray(direct) &&
    direct.length === criteria.length &&
    direct.every(
      (row) =>
        Array.isArray(row) &&
        row.length === criteria.length &&
        row.every(
          (cell) => typeof cell === "number" && (cell === 0 || cell === 1),
        ),
    )
  );
}
