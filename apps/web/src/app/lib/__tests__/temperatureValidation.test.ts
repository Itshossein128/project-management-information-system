import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { validateTemperatures } from "../temperatureValidation.ts";

describe("Temperature validation", () => {
  it("accepts empty optional temperatures", () => {
    const res = validateTemperatures("", "");
    assert.equal(res.isValid, true);
    assert.equal(res.tempMinError, null);
    assert.equal(res.tempMaxError, null);
    assert.equal(res.parsedMin, null);
    assert.equal(res.parsedMax, null);
  });

  it("accepts valid temperatures within [-40, 60] inclusive", () => {
    const res = validateTemperatures("-40", "60");
    assert.equal(res.isValid, true);
    assert.equal(res.tempMinError, null);
    assert.equal(res.tempMaxError, null);
    assert.equal(res.parsedMin, "-40");
    assert.equal(res.parsedMax, "60");
  });

  it("accepts equal min and max temperatures", () => {
    const res = validateTemperatures("25.5", "25.5");
    assert.equal(res.isValid, true);
    assert.equal(res.tempMinError, null);
    assert.equal(res.tempMaxError, null);
  });

  it("accepts single valid temperature when other is empty", () => {
    const res1 = validateTemperatures("10", "");
    assert.equal(res1.isValid, true);
    assert.equal(res1.parsedMin, "10");
    assert.equal(res1.parsedMax, null);

    const res2 = validateTemperatures("", "20");
    assert.equal(res2.isValid, true);
    assert.equal(res2.parsedMin, null);
    assert.equal(res2.parsedMax, "20");
  });

  it("rejects values below -40 with min_value", () => {
    const res = validateTemperatures("-40.1", "10");
    assert.equal(res.isValid, false);
    assert.equal(res.tempMinError, "min_value");
  });

  it("rejects values above 60 with max_value", () => {
    const res = validateTemperatures("10", "60.1");
    assert.equal(res.isValid, false);
    assert.equal(res.tempMaxError, "max_value");
  });

  it("rejects temp_max lower than temp_min and attaches error only to temp_max", () => {
    const res = validateTemperatures("20", "15");
    assert.equal(res.isValid, false);
    assert.equal(res.tempMinError, null);
    assert.equal(res.tempMaxError, "temp_max_must_be_gte_temp_min");
  });

  it("handles incomplete in-focus tokens without emitting premature pair errors during typing", () => {
    // When typing "-" or "1.", isBlurOrSubmit=false
    const res = validateTemperatures("-", "15", { isBlurOrSubmit: false });
    assert.equal(res.isValid, false); // cannot save yet
    assert.equal(res.tempMinError, null); // no premature error while typing
    assert.equal(res.tempMaxError, null);
  });

  it("flags incomplete tokens as invalid on blur or submit", () => {
    const res = validateTemperatures("-", "15", { isBlurOrSubmit: true });
    assert.equal(res.isValid, false);
    assert.equal(res.tempMinError, "invalid_number");
  });
});
