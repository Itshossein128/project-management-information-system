/**
 * One Playwright test per decision-tree node in docs/decision-tree.
 * Product code is intentionally not adjusted from these results.
 */
import { expect, test } from "@playwright/test";
import { decisionScenarios } from "../../helpers/doc-catalog";
import { exerciseDecision, exerciseDenial } from "../../helpers/scenario-runner";

test.describe.configure({ timeout: 90_000 });

const groups = new Map<string, typeof decisionScenarios>();
for (const scenario of decisionScenarios) {
  const parts = scenario.path.split("/");
  const key = parts.slice(0, Math.min(4, parts.length)).join(" / ");
  const bucket = groups.get(key) ?? [];
  bucket.push(scenario);
  groups.set(key, bucket);
}

  test("decision catalog includes every inventoried node", () => {
    expect(decisionScenarios.length).toBeGreaterThanOrEqual(520);
    expect(decisionScenarios.filter((scenario) => scenario.missingReadme).map((scenario) => scenario.path)).toEqual([
      "login/submit-valid-credentials/[navigate-org-refs]/create-contract-type",
      "login/submit-valid-credentials/[navigate-org-refs]/create-unit",
    ]);
  });

for (const [group, scenarios] of groups) {
  test.describe(group, () => {
    for (const scenario of scenarios) {
      test(`${scenario.title} [${scenario.path}]`, async ({ page }, info) => {
        info.annotations.push({ type: "source", description: scenario.readme });
        await exerciseDecision(page, scenario, info.workerIndex);
      });

      const denialCandidate = scenario.protected && (scenario.kind === "mutation" || scenario.kind === "page");
      if (!denialCandidate || scenario.missingReadme) continue;
      test(`${scenario.title} denies a non-member [${scenario.path}]`, async ({ page }, info) => {
        info.annotations.push({ type: "source", description: scenario.readme });
        await exerciseDenial(page, scenario, info.workerIndex);
      });
    }
  });
}
