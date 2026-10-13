import * as recordRules from "../../../components/decision-support/execution-record-rules.ts";
import test from "node:test";
import assert from "node:assert/strict";
import { isIsmRunResult } from "../../../components/decision-support/ism-result-rules.ts";
const policy = {
  version: "ism-v1",
  self_inclusion: "binary_or",
  closure: "transitive",
  layer_rule: "reach_equals_intersection",
  layer_order: "top_to_bottom",
  mutual_groups: "maximal_non_singleton",
};
export const result = {
  status: "ok",
  engine: "ism",
  reachability_matrix: [
    [1, 1],
    [0, 1],
  ],
  layers: [
    { level: 1, criteria: ["B"] },
    { level: 2, criteria: ["A"] },
  ],
  mutual_groups: [],
  derivation_policy: policy,
};
test("completed ISM is structurally guarded using frozen names", () => {
  assert.equal(isIsmRunResult(result, ["A", "B"]), true);
  for (const data of [
    { status: "stub", engine: null },
    { ...result, engine: "ahp" },
    {
      ...result,
      reachability_matrix: [
        [true, 1],
        [0, 1],
      ],
    },
    { ...result, reachability_matrix: [[1]] },
    { ...result, derivation_policy: { ...policy, version: "unknown" } },
    {
      ...result,
      layers: [
        { level: 1, criteria: ["X"] },
        { level: 2, criteria: ["A"] },
      ],
    },
    {
      ...result,
      layers: [
        { level: 1, criteria: ["B"] },
        { level: 3, criteria: ["A"] },
      ],
    },
  ])
    assert.equal(isIsmRunResult(data, ["A", "B"]), false);
});

test("frozen groups reject unknown, duplicate, mismatched levels and invalid order", () => {
  const cyclic = {
    ...result,
    reachability_matrix: [
      [1, 1],
      [1, 1],
    ],
    layers: [{ level: 1, criteria: ["A", "B"] }],
    mutual_groups: [{ level: 1, criteria: ["A", "B"] }],
  };
  assert.equal(isIsmRunResult(cyclic, ["A", "B"]), true);
  for (const groups of [
    [{ level: 1, criteria: ["A", "X"] }],
    [{ level: 2, criteria: ["A", "B"] }],
    [{ level: 1, criteria: ["B", "A"] }],
    [
      { level: 1, criteria: ["A", "B"] },
      { level: 1, criteria: ["A", "B"] },
    ],
    [{ level: 1, criteria: ["A"] }],
  ])
    assert.equal(
      isIsmRunResult({ ...cyclic, mutual_groups: groups }, ["A", "B"]),
      false,
    );
});

// Exercise the real HTTP parsing boundary with deterministic responses, without an API.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
const require = createRequire(import.meta.url);
const ts = require("typescript") as typeof import("typescript");
function responseApi(raw: string) {
  const source = readFileSync(
    new URL("./decision-support.ts", import.meta.url),
    "utf8",
  );
  const exports: Record<string, (...args: unknown[]) => Promise<unknown>> = {};
  runInNewContext(
    ts.transpileModule(source, {
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        target: ts.ScriptTarget.ES2022,
      },
    }).outputText,
    {
      exports,
      URLSearchParams,
      require: (id: string) => {
        if (id === "@/app/routeVars")
          return { PATHS: { API_PROJECTS: "projects" } };
        if (id === "@/app/lib/api-client")
          return {
            apiFetch: async () => ({ ok: true, text: async () => raw }),
          };
        if (id === "@/components/decision-support/ism-result-rules") return {};
        if (id === "@/components/decision-support/execution-record-rules")
          return recordRules;
        throw new Error("Unexpected API import: " + id);
      },
    },
  );
  return exports;
}
test("successful HTTP responses with empty, non-JSON or truncated bodies are rejected", async () => {
  for (const raw of ["", "<html>Broken response</html>", '{"id":']) {
    const api = responseApi(raw);
    await assert.rejects(
      api.patchDecisionCase!("project", "case", { ism_matrix: [[0]] }),
    );
    await assert.rejects(api.createDecisionRun!("project", "case", "ism"));
  }
});
test("valid JSON remains available for independent method and raw draft guards", async () => {
  const raw = { id: "case", criteria: ["A"], ism_matrix: null };
  assert.deepEqual(
    JSON.parse(
      JSON.stringify(
        await responseApi(JSON.stringify(raw)).patchDecisionCase!(
          "project",
          "case",
          {},
        ),
      ),
    ),
    raw,
  );
});

import {
  isIsmSavedCase,
  isIsmRunResponse,
} from "../../../components/decision-support/ism-result-rules.ts";

test("ISM saved-case metadata is guarded without validating unrelated or raw draft inputs", () => {
  const saved = {
    id: "case",
    title: "Draft",
    criteria: ["A", "B"],
    selected_methods: ["ism"],
    ism_matrix: null,
    performance_matrix: 4,
  };
  for (const draft of [null, [[null]], [[true]], 4, [[9]]])
    assert.equal(isIsmSavedCase({ ...saved, ism_matrix: draft }, "case"), true);
  for (const value of [
    null,
    {},
    [],
    { ...saved, id: "other" },
    { ...saved, title: null },
    { ...saved, criteria: undefined },
    { ...saved, criteria: [true] },
    { ...saved, selected_methods: null },
    { ...saved, ism_matrix: undefined },
  ])
    assert.equal(isIsmSavedCase(value, "case"), false);
});

test("completed ISM run envelope includes method, frozen binary input and provenance", () => {
  const envelope = {
    id: "run",
    method: "ism",
    extracted_at: "2026-10-13T00:00:00Z",
    extracted_by: "actor",
    input_snapshot: {
      criteria: ["A", "B"],
      ism_matrix: [
        [0, 1],
        [0, 0],
      ],
    },
    result,
  };
  assert.equal(isIsmRunResponse(envelope), true);
  for (const value of [
    null,
    {},
    [],
    { ...envelope, id: "" },
    { ...envelope, method: "ahp" },
    { ...envelope, extracted_at: "invalid date" },
    { ...envelope, extracted_by: null },
    { ...envelope, input_snapshot: undefined },
    {
      ...envelope,
      input_snapshot: {
        criteria: ["A", "B"],
        ism_matrix: [
          [true, 1],
          [0, 0],
        ],
      },
    },
    { ...envelope, input_snapshot: { criteria: ["A", "B"], ism_matrix: null } },
    {
      ...envelope,
      input_snapshot: {
        criteria: ["X", "B"],
        ism_matrix: [
          [0, 1],
          [0, 0],
        ],
      },
    },
    { ...envelope, result: { status: "stub", engine: null } },
  ])
    assert.equal(isIsmRunResponse(value), false);
});

test("actual history HTTP boundary rejects malformed envelopes and wrong selected IDs", async () => {
  for (const raw of [
    "",
    "<html>bad</html>",
    "null",
    "{}",
    JSON.stringify({ count: -1, next: null, previous: null, results: [] }),
  ]) {
    const api = responseApi(raw);
    await assert.rejects(api.listDecisionRuns!("p", "c"));
    await assert.rejects(api.getDecisionRun!("p", "c", "r"));
  }
  const row = {
    id: "r",
    method: "saw",
    extracted_at: "2026-10-13T00:00:00Z",
    extracted_by: "actor",
    input_snapshot: null,
    result: null,
  };
  await assert.rejects(
    responseApi(JSON.stringify(row)).getDecisionRun!("p", "c", "other"),
  );
  assert.equal(
    (
      (await responseApi(JSON.stringify(row)).getDecisionRun!(
        "p",
        "c",
        "r",
      )) as { id: string }
    ).id,
    "r",
  );
});
test("public AHP completed guard is unknown-safe for malformed scalar rows", () => {
  const api = responseApi("{}");
  for (const value of [
    null,
    {},
    4,
    { weights: 4 },
    { weights: [null] },
    { weights: [4] },
  ])
    assert.equal(api.isAhpRunResult!(value), false);
});
