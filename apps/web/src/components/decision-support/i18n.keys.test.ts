import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "../../app/locales");

const REQUIRED = [
  "nav.projectDecisionSupport",
  "decisionSupport.title",
  "decisionSupport.subtitle",
  "decisionSupport.methods",
  "decisionSupport.criteria",
  "decisionSupport.alternatives",
  "decisionSupport.historyEmpty",
  "decisionSupport.validation",
  "decisionSupport.createCase",
  "decisionSupport.save",
  "decisionSupport.weights",
  "decisionSupport.criterionTypes",
  "decisionSupport.performanceMatrix",
  "decisionSupport.sawPanelTitle",
  "decisionSupport.topsisPanelTitle",
  "decisionSupport.ahpPanelTitle",
  "decisionSupport.pairwiseMatrix",
  "decisionSupport.runMethod",
  "decisionSupport.colScore",
  "decisionSupport.colCriterion",
  "decisionSupport.colWeight",
  "decisionSupport.colPercent",
  "decisionSupport.colDBest",
  "decisionSupport.colDWorst",
  "decisionSupport.colCloseness",
  "decisionSupport.crConsistent",
  "decisionSupport.crInconsistent",
  "decisionSupport.errors.name_empty",
  "decisionSupport.errors.name_duplicate",
  "decisionSupport.errors.dimension_invalid",
  "decisionSupport.errors.empty_cell",
  "decisionSupport.errors.cell_empty",
  "decisionSupport.errors.cell_non_positive",
  "decisionSupport.errors.ahp_diagonal_invalid",
  "decisionSupport.errors.ahp_reciprocal_mismatch",
  "decisionSupport.errors.benefit_column_all_zero",
  "decisionSupport.errors.topsis_denom_zero",
  "decisionSupport.errors.decision_input_invalid",
  "decisionSupport.errors.run_immutable",
  "decisionSupport.errors.method_not_selected",
];

function hasKey(obj: unknown, dotted: string): boolean {
  const parts = dotted.split(".");
  let cur: unknown = obj;
  for (const p of parts) {
    if (!cur || typeof cur !== "object" || !(p in (cur as object))) return false;
    cur = (cur as Record<string, unknown>)[p];
  }
  return typeof cur === "string" && cur.length > 0;
}

describe("decision support i18n keys", () => {
  for (const locale of ["en.json", "fa.json"]) {
    it(`has required keys in ${locale}`, () => {
      const data = JSON.parse(readFileSync(join(root, locale), "utf8"));
      for (const key of REQUIRED) {
        assert.ok(hasKey(data, key), `missing ${key} in ${locale}`);
      }
    });
  }
});

const uiSources = [
  "IsmMethodPanel.tsx", "BinaryRelationEditor.tsx", "IsmLayerList.tsx",
  "AhpMethodPanel.tsx", "SquareMatrixEditor.tsx", "CriteriaWeightTable.tsx",
  "RunActionBar.tsx", "NamedListEditor.tsx", "ExecutionHistoryList.tsx",
  "InputSnapshotViewer.tsx", "ValidationIssueList.tsx",
  "../../app/routes/project-decision-support.tsx",
].map(file => readFileSync(join(root, "../../components/decision-support", file), "utf8"));
const allEn = JSON.parse(readFileSync(join(root, "en.json"), "utf8")).decisionSupport;
const allFa = JSON.parse(readFileSync(join(root, "fa.json"), "utf8")).decisionSupport;

function flatten(obj: Record<string, unknown>, prefix = ""): Record<string, string> {
  return Object.fromEntries(Object.entries(obj).flatMap(([key, value]) =>
    typeof value === "string" ? [[prefix + key, value]] :
    Object.entries(flatten(value as Record<string, unknown>, prefix + key + "."))));
}

it("covers every static AHP UI key and preserves interpolation arguments in both languages", () => {
  const english = flatten(allEn);
  const persian = flatten(allFa);
  const used = new Set([...uiSources.join("\n").matchAll(/t\(['"]decisionSupport\.([\w.]+)['"]/g)].map(match => match[1]!));
  for (const key of [
    "errors.invalid_type", "errors.non_numeric", "errors.non_finite", "errors.cell_empty",
    "errors.cell_non_positive", "errors.ahp_diagonal_invalid", "errors.ahp_reciprocal_mismatch",
    "errors.name_empty", "errors.name_duplicate", "errors.ism_relation_invalid", "errors.ism_derivation_failed",
  ]) used.add(key);
  for (const key of [...used].filter(key => !key.endsWith("."))) {
    assert.ok(english[key]?.trim(), "missing English " + key);
    assert.ok(persian[key]?.trim(), "missing Persian " + key);
    const parameters = (text: string) => [...text.matchAll(/{{\s*(\w+)\s*}}/g)].map(match => match[1]).sort();
    assert.deepEqual(parameters(english[key]!), parameters(persian[key]!), "interpolation differs: " + key);
  }
});
