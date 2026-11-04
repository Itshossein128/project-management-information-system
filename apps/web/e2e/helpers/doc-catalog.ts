import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const repoRoot = path.resolve(here, "../../../..");

export type DecisionScenario = {
  path: string;
  title: string;
  route: string;
  trigger: string;
  permissions: string;
  apiCall: string;
  navigation: string;
  desired: string;
  protected: boolean;
  kind: string;
  readme: string;
  missingReadme: boolean;
};

export type StoryScenario = {
  id: string;
  spec: string;
  story: string;
  priority: string;
  kind: "acceptance" | "edge" | "independent";
  given: string;
  when: string;
  then: string;
  route: string;
};

type InventoryNode = { path: string; protected?: boolean; kind?: string };

const SPEC_ROUTES: Record<string, string> = {
  "001": "/projects/:businessId/warehouse",
  "002": "/projects/:projectId/wbs",
  "003": "/projects/:projectId/activities",
  "004": "/projects/:projectId/wbs",
  "005": "/projects/:projectId/activities",
  "006": "/hr/users",
  "007": "/projects/:projectId/daily-reports",
  "008": "/projects/:projectId/overview",
  "009": "/projects/:projectId/progress",
  "010": "/projects/:projectId/costs",
  "011": "/projects/:projectId/contracts",
  "012": "/projects/:projectId/costs",
  "013": "/projects/:projectId/cash-flow",
  "014": "/projects/:projectId/progress",
  "015": "/projects/:projectId/risk-register",
  "016": "/projects/:projectId/documents",
  "017": "/portfolio/dashboard",
  "018": "/projects/:projectId/decision-support",
  "019": "/projects/:projectId/decision-support",
  "020": "/projects/:projectId/decision-support",
  "021": "/projects/:projectId/decision-support",
  "022": "/projects/:projectId/decision-support",
  "023": "/projects/:projectId/decision-support",
  "024": "/projects/:projectId/decision-support",
  "025": "/projects/:projectId/decision-support",
  "026": "/projects/:projectId/overview",
  "027": "/projects/:projectId/stakeholders",
  "028": "/projects/:projectId/daily-reports",
  "029": "/projects/:projectId/schedule/gantt",
  "030": "/projects/:projectId/daily-reports",
  "031": "/projects/:projectId/daily-reports",
  "032": "/projects/:projectId/daily-reports",
  "033": "/projects/:projectId/daily-reports",
  "034": "/projects/:projectId/daily-reports",
  "035": "/projects/:projectId/daily-reports",
  "036": "/projects/:projectId/daily-reports",
  "037": "/projects/:projectId/daily-reports",
  "038": "/projects/:projectId/daily-reports",
  "039": "/projects/:projectId/daily-reports",
  "040": "/projects/:projectId/progress",
  "041": "/projects/:projectId/progress",
  "042": "/projects/:businessId/buildings",
  "043": "/projects/:businessId/warehouse",
  "044": "/projects/:projectId/daily-reports/:reportId/view",
};

function readText(file: string): string {
  return fs.readFileSync(file, "utf8");
}

function field(text: string, label: string): string {
  const match = text.match(new RegExp(`\\*\\*${label}\\*\\*:\\s*(.+)`, "i"));
  return match?.[1]?.trim().replace(/^`+|`+$/g, "") ?? "";
}

function decisionTitle(text: string, fallback: string): string {
  const heading = text.match(/^#\s+(.+)$/m)?.[1]?.trim() ?? fallback;
  return heading.replace(/^Decision:\s*/i, "").trim();
}

function specNumber(specRel: string): string {
  return specRel.match(/(\d{3})-/)?.[1] ?? "";
}

function routeForStory(specRel: string, title: string): string {
  const number = specNumber(specRel);
  if (number === "044" && /Decision Tree|درخت تصمیم/.test(title)) {
    return "/projects/:projectId/daily-reports";
  }
  if (number === "044" && /Activity Log|FILE 1|فیلتر/.test(title)) {
    return "/projects/:projectId/activity-log";
  }
  if (number === "044" && /Electrical|FILE 6|برقی/.test(title)) {
    return "/projects/:businessId/electrical";
  }
  if (number === "044" && /Civil|FILE 5|ابنیه/.test(title)) {
    return "/projects/:businessId/buildings";
  }
  if (number === "044") return SPEC_ROUTES["044"];
  return SPEC_ROUTES[number] ?? "/projects/:projectId/overview";
}

function parseGivenBlocks(section: string): Array<{ given: string; when: string; then: string }> {
  const chunks = section.split(/\d+\.\s+\*\*Given\*\*/).slice(1);
  return chunks.map((chunk) => {
    const whenAt = chunk.search(/\*\*When\*\*/);
    const thenAt = chunk.search(/\*\*Then\*\*/);
    const given = (whenAt >= 0 ? chunk.slice(0, whenAt) : chunk).replace(/\*\*When\*\*[\s\S]*$/, "").trim();
    const when =
      whenAt >= 0
        ? chunk.slice(whenAt).replace(/^\*\*When\*\*/, "").split(/\*\*Then\*\*/)[0].trim()
        : "";
    const then = thenAt >= 0 ? chunk.slice(thenAt).replace(/^\*\*Then\*\*/, "").trim() : "";
    return { given, when, then };
  }).filter((block) => block.given || block.when || block.then);
}

function storyBodies(text: string): Array<{ title: string; priority: string; body: string }> {
  const matches = [...text.matchAll(/^### User Story\s+(\d+)\s+-\s+(.+)$/gm)];
  return matches.map((match, index) => {
    const start = match.index ?? 0;
    const end = index + 1 < matches.length ? (matches[index + 1].index ?? text.length) : text.length;
    const title = match[2].replace(/\s*\(Priority:.*\)\s*$/i, "").trim();
    const priority = match[2].match(/Priority:\s*([^)]+)\)/i)?.[1]?.trim() ?? "";
    return { title, priority, body: text.slice(start, end) };
  });
}

function edgeCases(text: string, specRel: string): StoryScenario[] {
  const start = text.search(/^### Edge Cases/m);
  if (start < 0) return [];
  const body = text.slice(start).split(/^## /m)[0];
  const blocks = body.split(/\n-\s+\*\*/).slice(1);
  return blocks.map((block, index) => {
    const title = block.split("**")[0]?.replace(/[:*]/g, "").trim() || `Edge ${index + 1}`;
    const requirement = block.match(/\*Requirement\*:\s*([\s\S]+)/)?.[1]?.trim() ?? block.trim();
    return {
      id: `${specRel}#edge-${index + 1}`,
      spec: specRel,
      story: title,
      priority: "edge",
      kind: "edge" as const,
      given: title,
      when: "the documented edge condition occurs",
      then: requirement,
      route: routeForStory(specRel, `${title} ${requirement}`),
    };
  });
}

export function loadDecisionScenarios(): DecisionScenario[] {
  const inventoryPath = path.join(repoRoot, "docs/decision-tree/inventory.json");
  const inventory = JSON.parse(readText(inventoryPath)) as { nodes?: InventoryNode[] };
  const byPath = new Map<string, InventoryNode>();
  for (const node of inventory.nodes ?? []) byPath.set(node.path, node);

  const root = path.join(repoRoot, "docs/decision-tree");
  const scenarios: DecisionScenario[] = [];
  const seen = new Set<string>();

  const walk = (dir: string) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name === "README.md") {
        const rel = path.relative(root, path.dirname(full)).split(path.sep).join("/");
        if (!rel || rel === ".") continue;
        const text = readText(full);
        if (!text.includes("**Trigger**") && !text.includes("**Route**")) continue;
        seen.add(rel);
        const meta = byPath.get(rel);
        scenarios.push({
          path: rel,
          title: decisionTitle(text, rel),
          route: field(text, "Route"),
          trigger: field(text, "Trigger"),
          permissions: field(text, "Required Permissions"),
          apiCall: field(text, "API Call"),
          navigation: field(text, "Navigation"),
          desired: (text.split("## Desired Result")[1] ?? "").split("## ")[0]?.trim() ?? "",
          protected: Boolean(meta?.protected ?? rel.includes("[")),
          kind: meta?.kind ?? "local",
          readme: path.relative(repoRoot, full),
          missingReadme: false,
        });
      }
    }
  };
  walk(root);

  for (const [nodePath, meta] of byPath) {
    if (seen.has(nodePath)) continue;
    scenarios.push({
      path: nodePath,
      title: nodePath.split("/").pop() ?? nodePath,
      route: "",
      trigger: "",
      permissions: "",
      apiCall: "",
      navigation: "",
      desired: "",
      protected: Boolean(meta.protected),
      kind: meta.kind ?? "local",
      readme: path.join("docs/decision-tree", nodePath, "README.md"),
      missingReadme: true,
    });
  }

  return scenarios.sort((a, b) => a.path.localeCompare(b.path));
}

export function loadStoryScenarios(): StoryScenario[] {
  const specsRoot = path.join(repoRoot, "specs");
  const files: string[] = [];
  const walk = (dir: string) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name === "spec.md") files.push(full);
    }
  };
  walk(specsRoot);

  const scenarios: StoryScenario[] = [];
  for (const file of files.sort()) {
    const spec = path.relative(repoRoot, file);
    const text = readText(file);
    for (const story of storyBodies(text)) {
      const marked = story.body.split(/\*\*Acceptance Scenarios\*\*:/i)[1];
      const acceptance = (marked ? marked.split(/^### |^## /m)[0] : story.body);
      const blocks = parseGivenBlocks(acceptance);
      if (blocks.length === 0) {
        const independent = story.body.match(/\*\*آزمون مستقل:\*\*\s*(.+)/)?.[1]
          ?? story.body.match(/\*\*Independent Test\*\*:?\s*([\s\S]+?)(?:\n\n|\*\*Acceptance)/)?.[1]
          ?? story.body.split("\n").slice(1, 6).join(" ").trim();
        scenarios.push({
          id: `${spec}#${story.title}#independent`,
          spec,
          story: story.title,
          priority: story.priority,
          kind: "independent",
          given: story.title,
          when: "the independent test is performed",
          then: independent.trim(),
          route: routeForStory(spec, story.title),
        });
        continue;
      }
      blocks.forEach((block, index) => {
        scenarios.push({
          id: `${spec}#${story.title}#${index + 1}`,
          spec,
          story: story.title,
          priority: story.priority,
          kind: "acceptance",
          given: block.given,
          when: block.when,
          then: block.then,
          route: routeForStory(spec, `${story.title} ${block.then}`),
        });
      });
    }
    scenarios.push(...edgeCases(text, spec));
  }
  return scenarios;
}

export const decisionScenarios = loadDecisionScenarios();
export const storyScenarios = loadStoryScenarios();
