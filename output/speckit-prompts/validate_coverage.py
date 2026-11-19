"""Validate Stage 2 inventory traceability; does not test the product."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'knowledge/agent-instructions.md').is_file())
BASE = ROOT / 'output/a1-requirements-2026-11-18'
CANON = BASE / 'speckit-prompts'
MIRROR = ROOT / 'output/speckit-prompts'

def read(path):
    return json.loads(path.read_text())

c = read(HERE / 'coverage.json')
assert c['stage'] == 2 and c['granularity'] == 'multi'
order = [f'B{i:02}' for i in range(1, 7)]
assert c['execution_order'] == order
stages = {s['id']: s for s in c['stages']}
assert len(stages) == len(c['stages']) == 6
for i, b in enumerate(order):
    s = stages[b]
    assert s['granularity'] == 'single'
    assert s['sequence_predecessor'] == (order[i - 1] if i else None)
    assert all(order.index(d) < i for d in s['hard_dependencies'])
    text = (HERE / s['prompt_file']).read_text()
    assert text.count('/speckit-specify') >= 1
    assert text.count('```text') == 1 and text.count('```') == 2
    assert 'plan، tasks، analyze، implement' in text
    assert b in text and c['original_workflow_input']['input'] in text

source_req = read(BASE / 'requirements.json')['requirements']
actual_req = c['requirements']
assert len(actual_req) == len(source_req) == 61
assert len({r['id'] for r in actual_req}) == 61
byid = {r['id']: r for r in actual_req}
assert set(byid) == {r['id'] for r in source_req}
for r in source_req:
    got = byid[r['id']]
    assert all(got[k] == v for k, v in r.items()), r['id']
    b = got['primary_owner']
    assert r['id'] in stages[b]['primary_requirements']
    assert sum(r['id'] in s['primary_requirements'] for s in stages.values()) == 1
    assert got['prompt_file'] == stages[b]['prompt_file']
    text = (HERE / got['prompt_file']).read_text()
    assert r['id'] in text and r['title'] in text and r['acceptance'] in text
    assert r['remaining'] in text and got['disposition']
    assert got['final_acceptance_stage'] == 'B06'
    if r['id'].startswith('X') and r['id'] != 'X07':
        assert got['disposition'] == 'external_phase_handoff_and_A1_compatibility'
    assert b not in got['supporting_stages']

for source_name, key, count in [('source-clauses.json', 'source_clauses', 370), ('atomic-stories.json', 'atomic_stories', 42)]:
    source = read(BASE / source_name)
    actual = c[key]
    assert len(source) == len(actual) == count
    makekey = lambda r: f"{r['source']}:{r['line']}:{r['id']}"
    source_map = {makekey(r): r for r in source}
    actual_map = {r['key']: r for r in actual}
    assert len(source_map) == count and set(source_map) == set(actual_map)
    for k, r in source_map.items():
        got = actual_map[k]
        assert all(got[x] == v for x, v in r.items()), k
        assert got['final_acceptance_stage'] == 'B06'
        if key == 'source_clauses':
            b = byid[r['group']]['primary_owner']
            assert got['primary_owner'] == b
            assert got['prompt_file'] == stages[b]['prompt_file']
            assert f"{r['source']}:{r['line']} | {r['id']}" in (HERE / got['prompt_file']).read_text()
        else:
            assert {g['group'] for g in got['stage_assignments']} == set(r['groups'])
            for a in got['stage_assignments']:
                assert a['owner'] == byid[a['group']]['primary_owner']
                assert r['id'] in (HERE / a['prompt_file']).read_text()

source_decisions = {m.group(1): m.group(0).strip() for m in re.finditer(r'^## (C\d{2}) — .*?(?=^## |\Z)', (BASE / 'scope-decisions.md').read_text(), re.M | re.S)}
assert len(c['scope_decisions']) == len(source_decisions) == 10
assert {d['id'] for d in c['scope_decisions']} == set(source_decisions)
for d in c['scope_decisions']:
    assert d['source_text'] == source_decisions[d['id']]
    assert d['decision_owner'] == 'B01'
    assert d['source_text'] in (HERE / stages['B01']['prompt_file']).read_text()
assert len(c['broader_daily_sections']) == 18
assert {s['id'] for s in c['broader_daily_sections']} == set(range(1, 19))
assert len(c['reproduced_gap_routes']) == 6
for gap in c['reproduced_gap_routes']:
    assert (BASE / gap['evidence']).is_file()
    assert all(byid[g]['primary_owner'] == gap['owner'] for g in gap['groups'])
for route in c['conditional_routes']:
    assert route['decision'] in source_decisions
    assert all(g in byid for g in route['groups'])
    assert all(b in stages for b in route['delivery_stages'])
for src in c['source_manifest']:
    assert hashlib.sha256((ROOT / src['path']).read_bytes()).hexdigest() == src['sha256'], src['path']
assert c['summary']['unmapped'] == []
assert c['summary']['implementation_coverage_percent'] is None
assert c['summary']['employer_acceptance'] == 'not_performed'
combined = (HERE / 'all-prompts.md').read_text()
for s in c['stages']:
    assert (HERE / s['prompt_file']).read_text() in combined
for f in CANON.iterdir():
    if f.is_file():
        assert (MIRROR / f.name).read_bytes() == f.read_bytes(), f.name
print('PASS: 6 ordered prompts; 61/61 groups; 370/370 clauses; 42/42 stories; 10/10 decisions; 18 sections; 6 gap routes; exact source text; source hashes; identical mirror.')
print('Coverage is prompt traceability only. Product tests and employer acceptance were not run.')
