/**
 * One Playwright test per spec user-story acceptance scenario and edge-case requirement.
 * Specs live in specs/; the decision tree and delivery contract point at the same flows.
 * Product code is intentionally not adjusted from these results.
 */
import { expect, test } from "@playwright/test";
import { storyScenarios } from "../../helpers/doc-catalog";
import { exerciseStory } from "../../helpers/scenario-runner";

test.describe.configure({ timeout: 90_000 });

test("user-story catalog includes acceptance scenarios from every feature spec", () => {
  expect(storyScenarios.filter((scenario) => scenario.kind === "acceptance").length).toBeGreaterThanOrEqual(754);
  const specs = new Set(storyScenarios.map((scenario) => scenario.spec));
  expect(specs.size).toBeGreaterThanOrEqual(45);
});

const groups = new Map<string, typeof storyScenarios>();
for (const scenario of storyScenarios) {
  const bucket = groups.get(scenario.spec) ?? [];
  bucket.push(scenario);
  groups.set(scenario.spec, bucket);
}

for (const [spec, scenarios] of groups) {
  test.describe(spec, () => {
    for (const scenario of scenarios) {
      const label = `${scenario.kind}: ${scenario.story} — ${scenario.id.split("#").pop()}`;
      test(label, async ({ page }, info) => {
        info.annotations.push({ type: "source", description: `${scenario.spec} ${scenario.story}` });
        await exerciseStory(page, scenario, info.workerIndex);
      });
    }
  });
}
