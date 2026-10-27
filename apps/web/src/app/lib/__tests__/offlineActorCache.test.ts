import assert from "node:assert/strict";
import { it } from "node:test";
import { clearProjectSessionQueries, queryClient } from "../react-query.ts";

it("evicts local unit reports and rows on an account transition", () => {
  const current = ["businesses", "p1", "unit-report", "electrical", "current", "2026-10-27"];
  const rows = ["businesses", "p1", "unit-report", "electrical", "r1", "activities"];
  const structured = ["unit-section", "p1", "electrical", "r1", "general-activities"];
  queryClient.setQueryData(current, { notes: "account a private draft" });
  queryClient.setQueryData(rows, [{ description: "account a private row" }]);
  queryClient.setQueryData(structured, [{ description: "account a private section" }]);
  clearProjectSessionQueries();
  assert.equal(queryClient.getQueryData(current), undefined);
  assert.equal(queryClient.getQueryData(rows), undefined);
  assert.equal(queryClient.getQueryData(structured), undefined);
});
