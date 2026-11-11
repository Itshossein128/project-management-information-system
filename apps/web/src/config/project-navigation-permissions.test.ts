import assert from "node:assert/strict";
import test from "node:test";
import { filterProjectNavByPermissions } from "./project-navigation-permissions.ts";

const project = "projects/11111111-1111-4111-8111-111111111111";
const items = [{ label: "Commercial", icon: "business" as const, path: `${project}/contracts`, children: [
  { label: "Costs", path: `${project}/costs` },
  { label: "Documents", path: `${project}/documents` },
  { label: "Contracts", path: `${project}/contracts` },
] }];

test("a viewer gets no commercial destinations; enabled modules alone grant nothing", () => {
  assert.deepEqual(filterProjectNavByPermissions(items, code => ["view_project", "view_wbs"].includes(code)), []);
});

test("finance keeps costs and contracts while document access remains absent", () => {
  const result = filterProjectNavByPermissions(items, code => ["view_costs", "view_contracts"].includes(code));
  assert.deepEqual(result[0].children?.map(item => item.label), ["Costs", "Contracts"]);
  assert.equal(items[0].children.length, 3);
});

test("write permission does not imply read and unknown destinations fail closed", () => {
  assert.deepEqual(filterProjectNavByPermissions(items, code => code === "edit_costs"), []);
  assert.deepEqual(filterProjectNavByPermissions([{ label: "New module", icon: "business", path: `${project}/unknown` }], () => true), []);
});

test("alternative read permissions and slash-prefixed paths retain authorized tools", () => {
  const reports = [{ label: "Reports", icon: "business" as const, path: `/${project}/standard-reports` }];
  assert.equal(filterProjectNavByPermissions(reports, code => code === "view_reports").length, 1);
  assert.equal(filterProjectNavByPermissions(reports, code => code === "view_dashboard").length, 1);
  assert.equal(filterProjectNavByPermissions(reports, () => false).length, 0);
});
