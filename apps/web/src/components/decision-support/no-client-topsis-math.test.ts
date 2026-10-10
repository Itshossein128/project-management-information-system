import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));

const FILES = [
  "TopsisMethodPanel.tsx",
  "RankingResultTable.tsx",
];

describe("no client TOPSIS math", () => {
  for (const file of FILES) {
    it(`${file} does not embed TOPSIS scoring/distance math`, () => {
      const src = readFileSync(join(dir, file), "utf8");
      assert.equal(src.includes("Math.sqrt"), false);
      assert.equal(/sqrt\(/i.test(src), false);
      assert.equal(/ideal_best\s*=/i.test(src), false);
      assert.equal(/ideal_worst\s*=/i.test(src), false);
      assert.equal(/d_best\s*=/i.test(src), false);
      assert.equal(/d_worst\s*=/i.test(src), false);
      assert.equal(/closeness\s*=/i.test(src), false);
    });
  }
});
