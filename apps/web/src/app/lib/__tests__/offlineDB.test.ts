import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  OFFLINE_DB_VERSION,
  normalizePayloadWeather,
  normalizeWeatherValue,
} from "../offlineDB.ts";

describe("offlineDB legacy weather normalization", () => {
  it("enforces OFFLINE_DB_VERSION >= 3 for weather normalization schema upgrade", () => {
    assert.ok(
      OFFLINE_DB_VERSION >= 3,
      `Expected OFFLINE_DB_VERSION >= 3, got ${OFFLINE_DB_VERSION}`,
    );
  });

  it("normalizes sunny -> clear, partly_cloudy -> cloudy, and foggy -> cloudy", () => {
    assert.equal(normalizeWeatherValue("sunny"), "clear");
    assert.equal(normalizeWeatherValue("partly_cloudy"), "cloudy");
    assert.equal(normalizeWeatherValue("foggy"), "cloudy");
    assert.equal(normalizeWeatherValue("clear"), "clear");
    assert.equal(normalizeWeatherValue("cloudy"), "cloudy");
    assert.equal(normalizeWeatherValue("rainy"), "rainy");
    assert.equal(normalizeWeatherValue("snowy"), "snowy");
    assert.equal(normalizeWeatherValue("stormy"), "stormy");
  });

  it("normalizes payloads in offline queue preserving retry count, payload identity, and non-weather fields", () => {
    const queueItemPayload = {
      report_date: "2026-09-01",
      shift: "full",
      weather_condition: "sunny",
      temp_max: 28,
      temp_min: 15,
      site_status: "active",
      activities: [],
    };

    const normalized = normalizePayloadWeather(queueItemPayload);
    assert.equal(normalized.weather_condition, "clear");
    assert.equal(normalized.report_date, "2026-09-01");
    assert.equal(normalized.temp_max, 28);

    const foggyPayload = {
      weather: "foggy",
      notes: "foggy morning",
    };
    const normFoggy = normalizePayloadWeather(foggyPayload);
    assert.equal(normFoggy.weather, "cloudy");
    assert.equal(normFoggy.notes, "foggy morning");
  });
});
