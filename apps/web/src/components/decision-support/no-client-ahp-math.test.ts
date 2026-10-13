import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const files = [
  "AhpMethodPanel.tsx", "SquareMatrixEditor.tsx", "CriteriaWeightTable.tsx",
  "square-matrix-rules.ts", "criteria-weight-rules.ts", "InputSnapshotViewer.tsx",
  "../../app/routes/project-decision-support.tsx", "../../app/lib/api/decision-support.ts",
];
describe("AHP presentation boundary", () => {
  for (const file of files) {
    it(file + " exists and contains no weighting or consistency derivation", () => {
      // Missing production targets fail the audit instead of silently passing.
      const src = readFileSync(join(dir, file), "utf8");
      assert.doesNotMatch(src, /geom_mean|geometricMean|SAATY_RI|eigenvalue|Math\.(pow|log|exp)|consistency_ratio\s*=|ci\s*=\s*\(lambda|\bcr\s*<=/i);
    });
  }
});
