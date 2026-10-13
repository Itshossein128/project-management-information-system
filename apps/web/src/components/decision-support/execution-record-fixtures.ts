export const snapshot = {
  title: "Frozen",
  criteria: ["Cost", "Quality"],
  alternatives: ["Alpha", "Beta"],
  types: ["cost", "benefit"],
  weights: [2, 3],
  weights_normalized: [0.4, 0.6],
  performance_matrix: [
    [4, 6],
    [2, 3],
  ],
  ahp_matrix: [
    [1, 2],
    [0.5, 1],
  ],
  ism_matrix: [
    [0, 1],
    [0, 0],
  ],
  dematel_matrix: [
    [0, 1],
    [2, 0],
  ],
};
export const saw = {
  id: "run",
  method: "saw",
  extracted_at: "2026-10-13T00:00:00Z",
  extracted_by: "actor",
  input_snapshot: snapshot,
  result: {
    status: "ok",
    engine: "saw",
    ranking: [
      { option: "Alpha", score: 0.8, rank: 1 },
      { option: "Beta", score: 0.7, rank: 2 },
    ],
  },
};
export const ahp = {
  ...saw,
  method: "ahp",
  result: {
    status: "ok",
    engine: "ahp",
    weights: [
      { criterion: "Quality", weight: 1 / 3, rank: 2 },
      { criterion: "Cost", weight: 2 / 3, rank: 1 },
    ],
    lambda_max: 2,
    ci: 0,
    cr: 0,
    is_consistent: true,
  },
};
export const partial = {
  ...saw,
  input_snapshot: {
    ...snapshot,
    weights_normalized: undefined,
    performance_matrix: [
      [0, null],
      [2, 3],
    ],
  },
  result: { status: "stub", engine: null },
};
// Test-only completed DEMATEL stored result, not live engine evidence.
export const dematel = {
  ...saw,
  method: "dematel",
  input_snapshot: {
    criteria: ["A", "B", "C"],
    dematel_matrix: [
      [0, 4, 0],
      [0, 0, 2],
      [0, 0, 0],
    ],
  },
  result: {
    status: "ok",
    engine: "dematel",
    normalization_factor: 4,
    normalized_matrix: [
      [0, 1, 0],
      [0, 0, 0.5],
      [0, 0, 0],
    ],
    total_relation_matrix: [
      [0, 1, 0.5],
      [0, 0, 0.5],
      [0, 0, 0],
    ],
    criteria_results: [
      {
        criterion: "A",
        d: 1.5,
        r: 0,
        prominence: 1.5,
        relation: 1.5,
        role: "influencing",
      },
      {
        criterion: "B",
        d: 0.5,
        r: 1,
        prominence: 1.5,
        relation: -0.5,
        role: "receiving",
      },
      {
        criterion: "C",
        d: 0,
        r: 1,
        prominence: 1,
        relation: -1,
        role: "receiving",
      },
    ],
    numerical_policy: {
      version: "dematel-v1",
      normalization: "max_row_sum",
      condition_limit: 1e8,
      residual_tolerance: 1e-10,
      total_relation_roundoff_factor: 1e-12,
      role_neutrality_tolerance: 1e-9,
    },
  },
};
export const ism = {
  ...saw,
  method: "ism",
  input_snapshot: {
    ...snapshot,
    ism_matrix: [
      [0, 1],
      [1, 0],
    ],
  },
  result: {
    status: "ok",
    engine: "ism",
    reachability_matrix: [
      [1, 1],
      [1, 1],
    ],
    layers: [{ level: 1, criteria: ["Cost", "Quality"] }],
    mutual_groups: [{ level: 1, criteria: ["Cost", "Quality"] }],
    derivation_policy: {
      version: "ism-v1",
      self_inclusion: "binary_or",
      closure: "transitive",
      layer_rule: "reach_equals_intersection",
      layer_order: "top_to_bottom",
      mutual_groups: "maximal_non_singleton",
    },
  },
};
