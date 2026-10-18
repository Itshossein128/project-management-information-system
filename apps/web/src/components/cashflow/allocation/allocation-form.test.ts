import test from "node:test";
import assert from "node:assert/strict";
import {
  normalizeLiquidityAmount,
  allocationDecisionBlocker,
} from "./allocation-form.ts";

test("liquidity accepts Persian and Arabic digits without losing monetary precision", () => {
  assert.equal(normalizeLiquidityAmount("۵٬۰۰۰٬۰۰۰٫۵۰"), "5000000.50");
  assert.equal(normalizeLiquidityAmount("٥٠٠٠"), "5000");
  assert.equal(
    normalizeLiquidityAmount("9007199254740993.25"),
    "9007199254740993.25",
  );
  assert.equal(normalizeLiquidityAmount("0"), "0");
});

test("empty, negative, exponent and malformed amounts cannot create a cycle", () => {
  for (const value of [
    "",
    " ",
    "-10",
    "1e9",
    "NaN",
    "1.234",
    "3..5",
    "1,23",
    "1,,000",
  ])
    assert.equal(normalizeLiquidityAmount(value), null, value);
});

const ready = {
  cycleId: "cycle-a",
  proposalCycleId: "cycle-a",
  lineCount: 1,
  ownerId: "owner",
  rationale: "A reason",
  overlapRequired: false,
  acknowledged: false,
};
test("a proposal from another cycle and whitespace-only decision details are blocked", () => {
  assert.equal(allocationDecisionBlocker(ready), null);
  assert.equal(
    allocationDecisionBlocker({ ...ready, proposalCycleId: "cycle-b" }),
    "proposalRequired",
  );
  assert.equal(
    allocationDecisionBlocker({ ...ready, lineCount: 0 }),
    "proposalRequired",
  );
  assert.equal(
    allocationDecisionBlocker({ ...ready, ownerId: " " }),
    "ownerRequired",
  );
  assert.equal(
    allocationDecisionBlocker({ ...ready, rationale: " " }),
    "rationaleRequired",
  );
});
test("overlap acknowledgement requires an explicit user choice", () => {
  assert.equal(
    allocationDecisionBlocker({ ...ready, overlapRequired: true }),
    "acknowledgementRequired",
  );
  assert.equal(
    allocationDecisionBlocker({
      ...ready,
      overlapRequired: true,
      acknowledged: true,
    }),
    null,
  );
});
