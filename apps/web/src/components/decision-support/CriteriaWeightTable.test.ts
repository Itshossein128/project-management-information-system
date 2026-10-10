import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { formatWeightDecimal, formatWeightPercent, isConsistent } from "./criteria-weight-rules.ts";

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

  it("evaluates consistency correctly based on CR <= 0.10 threshold", () => {
    assert.equal(isConsistent(0.0), true);
    assert.equal(isConsistent(0.05), true);
    assert.equal(isConsistent(0.10), true);
    assert.equal(isConsistent(0.101), false);
    assert.equal(isConsistent(0.25), false);
  });
});
