/* Audit probes evaluate current TypeScript with mocked API/storage boundaries.
 * PASS confirms the observed behavior. These are not browser/IndexedDB tests.
 * Run from repository root: node reports_gaps/04/evidence/probe_frontend.cjs
 */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const ts = require(path.resolve('node_modules/.pnpm/typescript@5.9.3/node_modules/typescript'));
let queue = [], reports = [], conflicts = [], calls = 0, seq = 0;
const db = {
  generateUUID: () => `00000000-0000-4000-8000-${String(++seq).padStart(12, '0')}`,
  isOfflineDBAvailable: () => true,
  getOfflineReportsByProject: async () => structuredClone(reports),
  getOfflineReport: async id => structuredClone(reports.find(r => r.local_id === id)),
  saveOfflineReport: async r => { reports = reports.filter(x => x.local_id !== r.local_id); reports.push(r); },
  updateOfflineReport: async (id, p) => { const r = reports.find(r => r.local_id === id); if (r) Object.assign(r, p); },
  getPendingQueue: async () => structuredClone(queue.filter(q => q.status === 'pending')),
  getQueueByProject: async () => structuredClone(queue),
  getUnresolvedConflicts: async () => conflicts,
  addToQueue: async q => queue.push(q),
  updateQueueItem: async (id, p) => Object.assign(queue.find(q => q.queue_id === id), p),
  addConflict: async c => conflicts.push(c),
  clearSyncedItems: async () => { queue = queue.filter(q => q.status !== 'synced'); },
  normalizePayloadWeather: p => p,
};
let batchResult;
function load(file, extra = '') {
  const code = ts.transpileModule(fs.readFileSync(file, 'utf8') + extra, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const module = { exports: {} };
  const mocks = {
    '@/app/lib/offlineDB': db,
    '@/app/routeVars': { PATHS: { API_PROJECTS: 'v1/projects' } },
    '@/app/lib/temperatureValidation': { validateTemperatures: () => ({ isValid: true }) },
    '@/app/lib/api-client': { apiFetch: async () => { throw Error('unexpected individual request'); } },
    '@/app/lib/api/daily-reports': { syncBatch: async () => { calls++; return batchResult; } },
    '@/app/lib/api/files': {},
  };
  vm.runInNewContext(code, {
    exports: module.exports, module,
    require: name => { assert.ok(name in mocks, name); return mocks[name]; },
    structuredClone, console,
  }, { filename: file });
  return module.exports;
}
const sync = load('apps/web/src/app/lib/syncService.ts',
  '\nexport const audit = { parseChildEndpoint, buildReportBatchPayload };');
const write = load('apps/web/src/app/lib/offlineWrite.ts');
const reset = () => { queue = []; reports = []; conflicts = []; calls = 0; };
async function main() {
  reset();
  await write.queueChildWrite('project', 'report', 'activities', 'POST', { activity_description: 'offline new row' });
  assert.equal(sync.audit.parseChildEndpoint(queue[0].endpoint), null);
  const payload = await sync.audit.buildReportBatchPayload('project', 'report', [], queue);
  assert.equal(payload.activities, undefined);
  assert.equal(queue[0].payload.client_id, undefined);
  const statusMap = await write.buildChildRowSyncMap('project', 'report', 'activities');
  assert.equal(statusMap.size, 0);
  console.log('POST_COLLECTION: parser=null; batch omits activities; client_id absent; row-status map empty');

  reset();
  await write.queueChildWrite('project', 'report', 'activities', 'PATCH', { quantity: 3 }, 'existing-row');
  const patch = await sync.audit.buildReportBatchPayload('project', 'report', [], queue);
  assert.equal(JSON.stringify(patch.activities), '[]');
  console.log('PATCH_WITHOUT_SNAPSHOT: activities=[] despite queued quantity=3');

  reset();
  reports = [{ project_id: 'project', local_id: 'report', report_date: '2024-10-01', _dirty: true }];
  await write.queueChildWrite('project', 'report', 'activities', 'POST', { activity_description: 'lost row' });
  batchResult = { results: [{ status: 'merged', server_id: 'report', child_errors: [] }] };
  const success = await sync.syncPendingQueue();
  assert.equal(queue.length, 0);
  assert.equal(reports[0]._dirty, false);
  console.log(`POST_FALSE_SUCCESS: synced=${success.synced}; queue cleared although new row omitted`);

  reset();
  reports = [{ project_id: 'project', local_id: 'report', report_date: '2024-10-01', _dirty: true }];
  await write.queueChildWrite('project', 'report', 'activities', 'PATCH', { quantity: -1 }, 'row');
  batchResult = { results: [{ status: 'error', conflict_reason: 'invalid children', child_errors: [
    { section: 'activities', index: 0, errors: { quantity: ['must be positive'] } },
  ] }] };
  await sync.syncPendingQueue();
  assert.equal(queue[0].status, 'failed');
  assert.equal(JSON.stringify(queue[0]).includes('must be positive'), false);
  calls = 0;
  const retry = await sync.syncPendingQueue();
  assert.equal(calls, 0);
  assert.equal(retry.synced, 0);
  console.log('FAILED_ROW: field error not stored; syncPendingQueue() makes zero requests for failed-only queue');

  queue[0].status = 'syncing'; calls = 0;
  await sync.syncPendingQueue();
  assert.equal(calls, 0);
  console.log('INTERRUPTED_SYNC: syncing-only queue makes zero requests on next run');

  reset();
  await write.queueReportHeader('project', 'report', { report_date: '2024-10-01' });
  await write.queueLaborBatch('project', 'report', [{ labor_category: 'direct', count: 1 }]);
  await write.queueLaborBatch('project', 'report', [{ labor_category: 'direct', count: 2 }]);
  queue[0].status = 'failed';
  await write.queueLaborBatch('project', 'report', [{ labor_category: 'direct', count: 3 }]);
  assert.equal(queue.length, 2);
  const built = await sync.audit.buildReportBatchPayload('project', 'report', [queue[1]], []);
  assert.equal(built.labor[0].count, 3);
  console.log('LABOR_SNAPSHOT: latest cached labor does reach builder when an active queue entry exists (control)');
  console.log('6 audit scenarios completed; storage/network mocked; no browser persistence claim.');
}
main().catch(e => { console.error(e); process.exitCode = 1; });
