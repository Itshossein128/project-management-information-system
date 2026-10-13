import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { recoverExecutionHistory } from "./execution-recovery.ts";
const require = createRequire(import.meta.url);
const { QueryClient } = require("@tanstack/react-query");
const page = { count: 0, next: null, previous: null, results: [] };
test("actual QueryClient force-fresh unfiltered read keeps checking until settlement", async () => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: 3 } } });
  const key = ["decision-runs", "p", "a", "", 1];
  qc.setQueryData(key, { count: 99 });
  let release!: (v: unknown) => void;
  const held = new Promise((r) => (release = r));
  const states: unknown[] = [];
  let calls = 0,
    visible = 0;
  const flow = recoverExecutionHistory({
    qc,
    projectId: "p",
    caseId: "a",
    read: async () => {
      calls++;
      return held;
    },
    onRecovered: () => visible++,
    setState: (x: unknown) => states.push(x),
    timeoutMs: 1000,
  });
  await new Promise((r) => setTimeout(r, 20));
  assert.deepEqual(states, ["checking"]);
  assert.equal(calls, 1);
  assert.equal(visible, 0);
  release(page);
  await flow;
  assert.deepEqual(states, ["checking", "refreshed"]);
  assert.equal(visible, 1);
  assert.deepEqual(qc.getQueryData(key), page);
  qc.clear();
});
test("failed malformed and timed-out lookup does not retry or publish late success", async () => {
  for (const mode of ["fail", "malformed", "timeout"]) {
    const qc = new QueryClient();
    const states: unknown[] = [];
    let count = 0,
      visible = 0;
    let signal: AbortSignal | undefined;
    await recoverExecutionHistory({
      qc,
      projectId: "p",
      caseId: "a",
      read: async (s: AbortSignal) => {
        count++;
        signal = s;
        if (mode === "fail") throw new Error("lost");
        if (mode === "malformed") return {};
        await new Promise((r) => setTimeout(r, 60));
        return page;
      },
      onRecovered: () => visible++,
      setState: (x: unknown) => states.push(x),
      timeoutMs: 20,
    });
    await new Promise((r) => setTimeout(r, 80));
    assert.equal(count, 1);
    assert.deepEqual(states, ["checking", "failed"]);
    assert.equal(visible, 0);
    if (mode === "timeout") assert.equal(signal!.aborted, true);
    qc.clear();
  }
});
test("recovery never reuses a history GET started before the execution committed", async () => {
  const qc = new QueryClient();
  let release!: (v: unknown) => void;
  const old = new Promise((r) => (release = r));
  const key = ["decision-runs", "p", "a", "", 1];
  const obsolete = qc
    .fetchQuery({ queryKey: key, queryFn: () => old })
    .catch(() => undefined);
  let reads = 0;
  const states: unknown[] = [];
  const fresh = {
    count: 1,
    next: null,
    previous: null,
    results: [
      {
        id: "committed",
        method: "saw",
        extracted_at: "2026-10-13T00:00:00Z",
        extracted_by: "actor",
      },
    ],
  };
  const recovery = recoverExecutionHistory({
    qc,
    projectId: "p",
    caseId: "a",
    read: async () => {
      reads++;
      return fresh;
    },
    setState: (x: unknown) => states.push(x),
    onRecovered: () => {},
    timeoutMs: 1000,
  });
  await new Promise((r) => setTimeout(r, 20));
  assert.equal(
    reads,
    1,
    "must start one new post-commit read rather than reuse the pre-commit promise",
  );
  release(page);
  await obsolete;
  await recovery;
  assert.deepEqual(qc.getQueryData(key), fresh);
  assert.deepEqual(states, ["checking", "refreshed"]);
  qc.clear();
});
