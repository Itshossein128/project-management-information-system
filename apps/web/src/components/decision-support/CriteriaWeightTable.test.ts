import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { formatWeightDecimal, formatWeightPercent } from "./criteria-weight-rules.ts";

describe("CriteriaWeightTable formatting rules", () => {
  it("formats weights as percentages accurately", () => {
    assert.equal(formatWeightPercent(0.63698), "63.7%");
    assert.equal(formatWeightPercent(0.25), "25.0%");
    assert.equal(formatWeightPercent(0.1), "10.0%");
  });

  it("formats weights as 4-decimal numbers", () => {
    assert.equal(formatWeightDecimal(0.636985), "0.6370");
    assert.equal(formatWeightDecimal(0.25), "0.2500");
  });

  it("keeps consistency inference on the server", () => {
    const helpers = readFileSync(new URL("./criteria-weight-rules.ts", import.meta.url), "utf8");
    assert.doesNotMatch(helpers, /function isConsistent|cr\s*<=/);
    const table = readFileSync(new URL("./CriteriaWeightTable.tsx", import.meta.url), "utf8");
    assert.doesNotMatch(table, /isConsistent = true/);
  });
});
