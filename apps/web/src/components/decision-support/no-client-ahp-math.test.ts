import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));

const FILES = [
  "AhpMethodPanel.tsx",
  "SquareMatrixEditor.tsx",
  "CriteriaWeightTable.tsx",
];

describe("no client AHP math", () => {
  for (const file of FILES) {
    it(`${file} does not embed AHP weighting/eigenvalue/CR math`, () => {
      const fullPath = join(dir, file);
      if (!existsSync(fullPath)) return;
      const src = readFileSync(fullPath, "utf8");
      assert.equal(/geom_mean/i.test(src), false);
      assert.equal(/lambda_max\s*=/i.test(src), false);
      assert.equal(/eigenvalue/i.test(src), false);
      assert.equal(/consistency_ratio\s*=/i.test(src), false);
      assert.equal(/SAATY_RI/i.test(src), false);
      assert.equal(/ci\s*=\s*\(lambda/i.test(src), false);
    });
  }
});
