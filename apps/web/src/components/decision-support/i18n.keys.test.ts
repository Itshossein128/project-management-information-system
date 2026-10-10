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
  "decisionSupport.errors.name_empty",
  "decisionSupport.errors.name_duplicate",
  "decisionSupport.errors.dimension_invalid",
  "decisionSupport.errors.empty_cell",
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
