import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const dir = dirname(fileURLToPath(import.meta.url));
for (const file of [
  "IsmMethodPanel.tsx",
  "BinaryRelationEditor.tsx",
  "IsmLayerList.tsx",
  "ism-input-rules.ts",
  "ism-result-rules.ts",
  "InputSnapshotViewer.tsx",
  "../../app/routes/project-decision-support.tsx",
  "../../app/lib/api/decision-support.ts",
]) {
  test("ISM presentation boundary: " + file, () => {
    const source = readFileSync(join(dir, file), "utf8");
    assert.doesNotMatch(
      source,
      /\b(compute_ism|extract_layers|floydWarshall|tarjan|transitiveClosure|stronglyConnectedComponents)\s*\(|reach\[i\]\[j\]\s*=|reachability_matrix\s*=|antecedent\s*=|Math\.(pow|log|exp)/i,
    );
  });
}
