import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  INACTIVE_ACTIVITY_WARNING_FA,
  shouldWarnInactiveSiteActivity,
} from "../activity-guard.ts";

describe("Inactive site activity confirmation guard", () => {
  it("has the exact Persian confirmation prompt", () => {
    assert.equal(
      INACTIVE_ACTIVITY_WARNING_FA,
      "کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت کارکرد اجرایی اطمینان دارید؟",
    );
  });

  it("triggers warning only when site is inactive and quantity is greater than 0", () => {
    // Inactive with positive quantity -> triggers warning
    assert.equal(shouldWarnInactiveSiteActivity("inactive", 10), true);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "5.5"), true);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", 0.1), true);

    // Inactive with 0, negative, or empty quantity -> no warning
    assert.equal(shouldWarnInactiveSiteActivity("inactive", 0), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "0"), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", -1), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", null), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", ""), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", undefined), false);

    // Active site -> never triggers warning even with large positive quantity
    assert.equal(shouldWarnInactiveSiteActivity("active", 100), false);
    assert.equal(shouldWarnInactiveSiteActivity("active", "50"), false);
    assert.equal(shouldWarnInactiveSiteActivity("active", 0), false);
  });
});
