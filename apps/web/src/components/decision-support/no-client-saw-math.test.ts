import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));

const FILES = [
  "SawMethodPanel.tsx",
  "WeightVectorEditor.tsx",
  "RectangularMatrixEditor.tsx",
  "CriterionTypeToggle.tsx",
  "RankingResultTable.tsx",
  "RunActionBar.tsx",
];

describe("no client SAW math", () => {
  for (const file of FILES) {
    it(`${file} does not embed SAW normalize/score loops`, () => {
      const src = readFileSync(join(dir, file), "utf8");
      assert.equal(src.includes("max_i"), false);
      assert.equal(src.includes("ideal_best"), false);
      assert.equal(/score\s*=\s*sum/i.test(src), false);
      assert.equal(src.includes("r[i,j]"), false);
    });
  }
});
