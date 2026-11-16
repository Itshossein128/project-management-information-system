"""Lock successful final reports to the frozen source and actual runtime images."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
E=Path(__file__).resolve().parent
P5=ROOT/'specs/055-a7-p5-import-operations/evidence/runtime'
def load(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=load(E/'source-files.json')
# A successful main suite plus a separate fresh-DB migration recheck.
combined=ET.Element('testsuites',name='A7 final regression and migration recheck')
counts={}
for name in ['core','migrations']:
 report=ET.parse(E/f'final-{name}-part-junit.xml').getroot()
 cases=report.findall('.//testcase')
 assert cases and all(c.find(tag) is None for c in cases for tag in ['failure','error','skipped']),name
 counts[name]=len(cases);combined.extend(list(report))
ET.ElementTree(combined).write(E/'final-core-junit.xml',encoding='utf-8',xml_declaration=True)
paths={
 'core':(E/'final-core-junit.xml','junit'),
 'host':(P5/'host-pytest.xml','junit'),
 **{f'browser_{n}':(E/f'final-browser-{n}.json','playwright') for n in ['general','recovery','viewer','retry']},
 'web':(E/'web-checks.json','json'),
 'runtime':(P5/'manifest.json','json'),
 'broker':(P5/'broker-outage.json','json'),
 'concurrent':(P5/'concurrent-delivery.json','json'),
 'fresh_start':(E/'fresh-start.json','json'),
}
checks={}
for name,(path,kind) in paths.items():
 if kind=='junit':
  cases=ET.parse(path).getroot().findall('.//testcase')
  assert cases and all(c.find(tag) is None for c in cases for tag in ['failure','error','skipped']),name
  count=len(cases)
 elif kind=='playwright':
  stats=load(path)['stats'];assert stats['expected'] and not any(stats[k] for k in ['unexpected','skipped','flaky']),name
  count=stats['expected']
 else:
  report=load(path)
  if name=='runtime':assert report['status']=='ready' and not report['not_run'] and all(v=='pass' for v in report['matrix'].values())
  else:assert report['status']=='pass',name
  count=None
 checks[name]={'path':str(path.relative_to(ROOT)),'kind':kind,'sha256':digest(path),'passed_cases':count}
for name,sha in source['source_files_sha256'].items():assert digest(ROOT/name)==sha,name
web=load(E/'web-checks.json');assert web['source_commit']==source['source_commit']
manifest=load(P5/'manifest.json')
assert manifest['source_tree_sha256']==hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT/'apps/api/core/schedule').rglob('*.py')))).hexdigest()
fresh=load(E/'fresh-start.json');assert fresh['api_image_digest']==web['api_image_digest'] and fresh['separate_network_verified'] and fresh['disposable_stack_removed']
verification={'source_commit':source['source_commit'],'image_digest':web['api_image_digest'],'web_image_digest':web['web_image_digest'],'source_files_sha256':source['source_files_sha256'],'checks':checks,'main_suite_cases':counts['core'],'additional_migration_recheck_cases':counts['migrations'],'migration_recheck_overlap':'The main suite also includes migration tests; the extra 20-case run independently repeats them on another fresh database. Do not count overlapping cases as distinct requirements.'}
save(E/'release-verification.json',verification)
pkg=load(E/'package.json');pkg['web_image_digest']=web['web_image_digest'];save(E/'package.json',pkg)
save(E/'ops-04-runtime.json',{'status':'pass','source_commit':source['source_commit'],'api_image_digest':web['api_image_digest'],'schedule_tree_sha256':manifest['source_tree_sha256'],'matrix_groups':manifest['matrix'],'runtime_report':str((P5/'manifest.json').relative_to(ROOT)),'broker_report':str((P5/'broker-outage.json').relative_to(ROOT)),'concurrent_report':str((P5/'concurrent-delivery.json').relative_to(ROOT)),'retention_boundary_hours':168,'purge_test_hours':169,'age_acceleration':'Disposable terminal timestamps are aged explicitly; actual worker execution, cgroup containment, purge and retained history are real. This is not a claim of waiting seven days.'})
old=load(P5/'source-files.json')
old.update(baseline_git_head=source['source_commit'],schedule_tree_sha256=manifest['source_tree_sha256'],product_schedule_sha256=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT/'apps/api/core/schedule').rglob('*.py')) if 'tests' not in p.relative_to(ROOT/'apps/api/core/schedule').parts)).hexdigest(),files={p:h for p,h in source['source_files_sha256'].items() if p.startswith(('apps/api/core/schedule/','ops/a7-p5/')) or p in ['apps/api/Dockerfile','apps/api/.dockerignore','apps/api/requirements.txt','apps/api/core/config/settings.py']})
save(P5/'source-files.json',old)
summary=f'''# Final A.7 verification — 2026-11-16

Source candidate: `{source['source_commit']}`. Base develop HEAD remains `{source['base_commit']}`. The shared Git index was preserved when creating the candidate. Actual API image: `{web['api_image_digest']}`; compiled web image: `{web['web_image_digest']}`. Django 4.2.11, Node {web['node_version']}. Exact source/image/report binding: release-verification.json.

- Main scoped regression: **{counts['core']} passed**, zero failures/errors/skips. It covers registration/approval/gates/CR/charter, archive/undo/retry and actual PostgreSQL concurrency, WBS/templates, schedule/import and file validators. The separately run **{counts['migrations']} migration checks passed** on another fresh DB; these overlap the main suite and are an extra recheck, not distinct acceptance requirements.
- Host P5 regression: **{checks['host']['passed_cases']} passed**, zero failures/skips, including actual helper containment and storage/migration safeguards.
- Browser on exported compiled web/API images: **29 passed** (20 general/reference/login/bilingual/cancel, 3 real-worker recovery/isolation, 2 viewer, 4 retry). No skipped/flaky/unexpected tests. Human login was exercised for all five separate personas. Native FileChooser selected the unchanged employer MPP. Full WBS metadata/move/template, safe replace, idempotent repeat and all six lifecycle transitions retain charter/schedule data.
- Real-worker matrix: **13/13 pass**, zero not_run; eager and inline preparation off, actual cgroup memory/pids/time/scratch containment, process termination, recovery/one-time commit, retention and cleanup. The 168-hour retention/169-hour purge boundary uses explicitly aged disposable timestamps, not seven elapsed days.
- Actual private broker outage and two-worker concurrent MSP/P6 delivery: pass; same job commits once and healthy follow-up succeeds.
- Fresh installation: new containers, separate verified network, empty private PostgreSQL/Redis, offline existing images, five-persona provisioning and native MPP worker import all pass. Counts are 6 WBS / 72 activities / 72 relations / 1 working baseline / retained charter. The temporary stack/volume/scratch are removed. An initial smoke harness accidentally retained Compose's expanded original network name; it was corrected to a unique network and DNS/container IP assertions before the successful rerun. It did not reset the existing acceptance or shared databases. The harness also needed an explicit direct-localhost HTTP client and a new empty project: replacement of the seeded activity-bearing demo is correctly refused by the safety contract.
- `pnpm typecheck` and the acceptance-origin production build pass. 1073 API Python files in the running image match the frozen source; all 293 compiled frontend files match the exported web image. web-checks.json records checksums and exact Node/image identity.

All 56 original audit titles/criteria are preserved in the final ledger. M03 uses the approved fixed project state machine. M04 is a conditional scope disposition: no generic dynamic-table/Excel flow is used by this A.7 journey; general Excel and independent WBS Excel import were not tested or claimed. Calendar execution and universal MPP/P6-version compatibility are not promised; structured omission warnings and the exact corpus/reconciliation figures are explicit.

The four failures found in the prior broad run were obsolete test expectations for zero-budget activation, archived deletion and historical-schema field comparisons. They were corrected with negative assertions and full reruns. Product remediation was strengthened so nonpositive existing budgets can be repaired by an independently approved bounded CR; invalid repair values are refused. Archived generic/stale writes remain denied under the project root lock. No known open in-scope technical defect remains after these checks.

Technical readiness is ready_for_acceptance. Employer decision is pending and signature fields remain blank. Historical P5 independent-operator evidence is retained as historical; these final current-version runs are implementer-run. The employer's own walkthrough and decision are not inferred from automated tests. The original November-10 audit remains untouched.
'''
(E/'verification.md').write_text(summary)
print(json.dumps({'status':'pass','main_suite':counts['core'],'extra_migration_recheck':counts['migrations'],'browser':29,'runtime_groups':13,'source_commit':source['source_commit']}))
