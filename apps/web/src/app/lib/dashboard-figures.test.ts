import test from "node:test";
import assert from "node:assert/strict";
import { formatFigureValue } from "./dashboard-figures.ts";

const figure = (
  value: number | string | null,
  status: "ok" | "unavailable" | "inactive" = "ok",
  figure_key = "evm.spi",
) => ({ value, status, figure_key });

test("unavailable or inactive indicators never display a stale numeric value", () => {
  assert.equal(formatFigureValue(figure(0.9, "unavailable")), "—");
  assert.equal(formatFigureValue(figure(0, "inactive")), "—");
  assert.equal(formatFigureValue(figure(null)), "—");
});

test("real zero values are retained and financial and count values match the UI language", () => {
  assert.equal(
    formatFigureValue(figure(0, "ok", "cash.net_balance"), "en"),
    "0",
  );
  assert.equal(
    formatFigureValue(figure(12345, "ok", "cash.net_balance"), "en"),
    "12,345",
  );
  assert.equal(
    formatFigureValue(figure(12345, "ok", "cash.net_balance"), "fa"),
    "۱۲٬۳۴۵",
  );
  assert.equal(
    formatFigureValue(figure(12, "ok", "schedule.critical_activities"), "fa"),
    "۱۲",
  );
});

test("indices retain three decimals and signed variance retains its meaning", () => {
  assert.equal(formatFigureValue(figure(0.9567), "en"), "0.957");
  assert.equal(
    formatFigureValue(figure(-12.34, "ok", "progress.plan_vs_actual"), "en"),
    "-12.3%",
  );
});
