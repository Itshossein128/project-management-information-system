import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  formatIssueLabel,
  localizeIssueMessage,
  parseApiValidationIssues,
  parseApiRequestIssues,
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


describe("request failure feedback", () => {
  for (const code of ["permission_denied", "not_found", "throttled", "not_authenticated", "authentication_failed"]) {
    it("preserves " + code + " as an actionable general issue", () => {
      assert.deepEqual(parseApiRequestIssues({error:{code,message:"Rejected",details:{detail:"Rejected"}}}),
        [{code,path:"",message:"Rejected"}]);
    });
  }
  it("preserves locatable domain issues rather than replacing them", () => {
    const payload={error:{code:"decision_input_invalid",details:{issues:[{code:"cell_empty",path:"ahp_matrix.0.1",message:"Empty"}]}}};
    assert.deepEqual(parseApiRequestIssues(payload),parseApiValidationIssues(payload));
  });
  for (const payload of [null, {}, {error:{code:"unknown"}}, "<html>Server error</html>"]) {
    it("provides safe generic feedback for " + JSON.stringify(payload), () => {
      assert.deepEqual(parseApiRequestIssues(payload),[{code:"request_failed",path:"",message:""}]);
    });
  }
});
