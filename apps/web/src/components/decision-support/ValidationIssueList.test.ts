import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  formatIssueLabel,
  localizeIssueMessage,
  parseApiValidationIssues,
} from "./validation-issues.ts";

describe("ValidationIssueList parsing", () => {
  it("renders path + message from API-shaped issues", () => {
    const issues = parseApiValidationIssues({
      error: {
        code: "decision_input_invalid",
        details: {
          issues: [{ code: "empty_cell", path: "performance_matrix.0.1", message: "Cell cannot be empty." }],
        },
      },
    });
    assert.equal(issues.length, 1);
    assert.equal(formatIssueLabel(issues[0]!), "performance_matrix.0.1: Cell cannot be empty.");
  });

  it("localizes message via stable code when t provides a translation", () => {
    const t = (key: string, fallback = "") =>
      key === "decisionSupport.errors.empty_cell" ? "خانه نمی‌تواند خالی باشد." : fallback;
    const label = formatIssueLabel(
      { code: "empty_cell", path: "performance_matrix.0.1", message: "Cell cannot be empty." },
      t,
    );
    assert.equal(label, "performance_matrix.0.1: خانه نمی‌تواند خالی باشد.");
    assert.equal(
      localizeIssueMessage({ code: "name_empty", message: "Name cannot be empty." }, t),
      "Name cannot be empty.",
    );
  });
});
