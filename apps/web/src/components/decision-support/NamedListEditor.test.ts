import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MAX_NAMED_LIST, addNamedItem, canAddNamedItem, validateNamedList } from "./named-list-rules.ts";

describe("NamedListEditor rules", () => {
  it("rejects 11th name", () => {
    const names = Array.from({ length: MAX_NAMED_LIST }, (_, i) => `n${i}`);
    assert.equal(canAddNamedItem(names), false);
    const { issues } = addNamedItem(names, "extra");
    assert.equal(issues[0]?.code, "dimension_invalid");
  });

  it("surfaces empty and duplicate", () => {
    assert.ok(validateNamedList(["", "a"]).some((i) => i.code === "name_empty"));
    assert.ok(validateNamedList(["a", "a"]).some((i) => i.code === "name_duplicate"));
    const { issues } = addNamedItem(["a"], "a");
    assert.equal(issues[0]?.code, "name_duplicate");
  });
});
