import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  shouldWarnInactiveSiteActivity,
  INACTIVE_ACTIVITY_WARNING_FA,
  INACTIVE_ACTIVITY_WARNING_EN,
} from "../../../components/daily_reports/activity-guard.ts";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const faLocale = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, "../../locales/fa.json"), "utf8"),
);
const enLocale = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, "../../locales/en.json"), "utf8"),
);

describe("Inactive site activity guard", () => {
  it("triggers shouldWarnInactiveSiteActivity only when site status is inactive and quantity is strictly positive", () => {
    // Should trigger:
    assert.equal(shouldWarnInactiveSiteActivity("inactive", 1), true);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", 0.1), true);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "5"), true);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "0.01"), true);

    // Should NOT trigger when active:
    assert.equal(shouldWarnInactiveSiteActivity("active", 10), false);
    assert.equal(shouldWarnInactiveSiteActivity("active", 1), false);
    assert.equal(shouldWarnInactiveSiteActivity(null, 10), false);
    assert.equal(shouldWarnInactiveSiteActivity(undefined, 10), false);

    // Should NOT trigger when quantity <= 0 or empty/null/NaN:
    assert.equal(shouldWarnInactiveSiteActivity("inactive", 0), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "0"), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", -1), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "-5"), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", ""), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", null), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", undefined), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", "invalid"), false);
    assert.equal(shouldWarnInactiveSiteActivity("inactive", NaN), false);
  });

  it("verifies INACTIVE_ACTIVITY_WARNING_FA equals the approved Persian text verbatim", () => {
    const approvedFa =
      "کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟";
    assert.equal(INACTIVE_ACTIVITY_WARNING_FA, approvedFa);
  });

  it("verifies INACTIVE_ACTIVITY_WARNING_EN equals the approved English text", () => {
    const approvedEn =
      "The site is marked inactive on this date; are you sure you want to record execution activity with positive volume?";
    assert.equal(INACTIVE_ACTIVITY_WARNING_EN, approvedEn);
  });

  it("verifies constants match the locale catalogs", () => {
    assert.equal(
      INACTIVE_ACTIVITY_WARNING_FA,
      faLocale.dailyReports.inactiveSiteActivityWarning,
    );
    assert.equal(
      INACTIVE_ACTIVITY_WARNING_EN,
      enLocale.dailyReports.inactiveSiteActivityWarning,
    );
  });
});
