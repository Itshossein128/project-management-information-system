import test from "node:test";
import assert from "node:assert/strict";
import {
  isSavedCase,
  isRunEnvelope,
  isHistoryPage,
  isCompletedRun,
  classifyHistory,
} from "./execution-record-rules.ts";
import { saw, ahp, snapshot, partial } from "./execution-record-fixtures.ts";
test("provenance guards reject fabricated envelopes but retain legacy partial content", () => {
  for (const v of [
    null,
    {},
    [],
    { ...saw, id: "" },
    { ...saw, extracted_at: "broken" },
    { ...saw, extracted_by: null },
    { ...saw, method: "wrong" },
  ])
    assert.equal(isRunEnvelope(v), false);
  assert.equal(
    isRunEnvelope({ ...saw, input_snapshot: null, result: null }),
    true,
  );
  assert.equal(isRunEnvelope(saw, "other"), false);
  for (const v of [
    null,
    {},
    { count: -1, next: null, previous: null, results: [] },
    { count: 1, next: 4, previous: null, results: [saw] },
    { count: 1, next: null, previous: null, results: [{}] },
  ])
    assert.equal(isHistoryPage(v), false);
  assert.equal(
    isHistoryPage({ count: 1, next: null, previous: null, results: [partial] }),
    true,
  );
});
test("strict new completion requires expected method complete frozen inputs and named output", () => {
  assert.equal(isCompletedRun(saw, "saw"), true);
  assert.equal(isCompletedRun(ahp, "ahp"), true);
  for (const v of [
    null,
    {},
    partial,
    { ...saw, method: "topsis" },
    { ...saw, input_snapshot: null },
    {
      ...saw,
      result: {
        ...saw.result,
        ranking: [{ option: "Unknown", score: 1, rank: 1 }],
      },
    },
    { ...saw, input_snapshot: { ...snapshot, weights_normalized: undefined } },
    {
      ...saw,
      result: {
        ...saw.result,
        ranking: [
          { option: "Alpha", score: Infinity, rank: 1 },
          { option: "Beta", score: 0, rank: 2 },
        ],
      },
    },
  ])
    assert.equal(isCompletedRun(v, "saw"), false);
  const topsis = {
    ...saw,
    method: "topsis",
    result: { ...saw.result, engine: "topsis" },
  };
  assert.equal(isCompletedRun(topsis, "topsis"), false);
  assert.equal(classifyHistory(topsis).ranking.length, 2);
  assert.equal(
    classifyHistory({
      ...ahp,
      result: {
        ...ahp.result,
        weights: [{ criterion: "Unknown", weight: 1, rank: 1 }],
      },
    }).ahp,
    null,
  );
});
test("historical sections are independently usable with zero distinct from absence and stored order", () => {
  const h = classifyHistory(partial);
  assert.deepEqual(h.criteria, snapshot.criteria);
  assert.equal(h.snapshot.performance_matrix[0][0], 0);
  assert.equal(h.snapshot.performance_matrix[0][1], null);
  assert.equal(h.snapshot.weights_normalized, undefined);
  assert.equal(h.ranking, null);
  assert.deepEqual(classifyHistory(ahp).ahp.weights, ahp.result.weights);
  assert.equal(classifyHistory({ ...saw, input_snapshot: null }).ranking, null);
  assert.equal(classifyHistory({ ...saw, result: null }).ranking, null);
});
test("draft-compatible metadata never treats unrelated raw method matrices as executable", () => {
  const saved = {
    id: "case",
    title: "Draft",
    criteria: ["A"],
    alternatives: [],
    selected_methods: ["ism"],
    weights: [],
    types: [],
    performance_matrix: [],
    ahp_matrix: [],
    ism_matrix: null,
    dematel_matrix: [],
  };
  assert.equal(isSavedCase(saved, "case"), true);
  assert.equal(isSavedCase({ ...saved, ism_matrix: 4 }, "case"), true);
  for (const v of [
    null,
    {},
    { ...saved, id: "other" },
    { ...saved, title: null },
    { ...saved, criteria: [true] },
    { ...saved, selected_methods: ["wrong"] },
    { ...saved, weights: undefined },
  ])
    assert.equal(isSavedCase(v, "case"), false);
});
import { dematel } from "./execution-record-fixtures.ts";
test("DEMATEL signed rows/policies are stored review only with dimension and name guards", () => {
  assert.equal(
    classifyHistory(dematel).dematel?.criteria_results[1].relation,
    -0.5,
  );
  for (const v of [
    {
      ...dematel,
      result: { ...dematel.result, numerical_policy: { version: "wrong" } },
    },
    { ...dematel, result: { ...dematel.result, total_relation_matrix: [[0]] } },
    { ...dematel, input_snapshot: { criteria: ["C", "B", "A"] } },
  ])
    assert.equal(classifyHistory(v).dematel, null);
  assert.equal(isCompletedRun(dematel, "dematel"), false);
});
test("zero ranking weights remain valid rather than being converted to missing", () => {
  assert.equal(
    isCompletedRun(
      {
        ...saw,
        input_snapshot: {
          ...snapshot,
          weights: [0, 3],
          weights_normalized: [0, 1],
        },
      },
      "saw",
    ),
    true,
  );
});
import { ism } from "./execution-record-fixtures.ts";
test("shared historical classifier retains literal ISM groups and rejects wrong frozen membership", () => {
  assert.deepEqual(
    classifyHistory(ism).ism?.mutual_groups,
    ism.result.mutual_groups,
  );
  assert.equal(isCompletedRun(ism, "ism"), true);
  assert.equal(
    classifyHistory({
      ...ism,
      input_snapshot: { criteria: ["Other", "Quality"] },
    }).ism,
    null,
  );
});
test("method identifiers must be primitive strings rather than coercible arrays", () => {
  assert.equal(isRunEnvelope({ ...saw, method: ["saw"] }), false);
  assert.equal(
    isHistoryPage({
      count: 1,
      next: null,
      previous: null,
      results: [{ ...saw, method: ["saw"] }],
    }),
    false,
  );
  const saved = {
    id: "case",
    title: "Draft",
    criteria: [],
    alternatives: [],
    selected_methods: [["ism"]],
    weights: [],
    types: [],
    performance_matrix: [],
    ahp_matrix: [],
    ism_matrix: null,
    dematel_matrix: [],
  };
  assert.equal(isSavedCase(saved, "case"), false);
});
test("stored named rows and role identifiers reject coercible non-string values", () => {
  assert.equal(
    classifyHistory({
      ...saw,
      result: {
        ...saw.result,
        ranking: [
          { option: ["Alpha"], score: 0.8, rank: 1 },
          { option: "Beta", score: 0.7, rank: 2 },
        ],
      },
    }).ranking,
    null,
  );
  assert.equal(
    classifyHistory({
      ...dematel,
      result: {
        ...dematel.result,
        criteria_results: dematel.result.criteria_results.map((r, i) =>
          i === 0 ? { ...r, role: ["influencing"] } : r,
        ),
      },
    }).dematel,
    null,
  );
});
