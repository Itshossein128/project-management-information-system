"""Process-level evidence and deploy/CI wiring regressions for R.0.04."""
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import drill_gate_failure as drill


@pytest.mark.parametrize('scenario', drill.SCENARIOS)
def test_real_gate_process_exit_and_immediate_decision(scenario):
    result = drill.run_drill(scenario)
    assert result.returncode == (0 if scenario == 'success' else 1)


def test_drill_rejects_unexpected_gate_success():
    with patch.object(drill.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')):
        with pytest.raises(RuntimeError, match='expected gate exit=1'):
            drill.run_drill('api-failure')


def workflow(name):
    return yaml.safe_load((ROOT / '.github/workflows' / name).read_text())


def test_deploy_cannot_bypass_failed_gate():
    jobs = workflow('deploy.yml')['jobs']
    gate, deploy = jobs['verify-ci-gate'], jobs['deploy']
    assert deploy['needs'] == ['verify-ci-gate']
    # With no job-level if, Actions applies success() to needs automatically.
    assert 'if' not in deploy
    assert not gate.get('continue-on-error', False)
    steps = gate['steps']
    checks = [s for s in steps if 'verify_ci_gate.py' in s.get('run', '')]
    assert len(checks) == 1
    assert not checks[0].get('continue-on-error', False)
    assert '||' not in checks[0]['run']
    assert '--required-jobs "web,api"' in checks[0]['run']
    assert 'COMMIT_SHA' in checks[0]['run']
    assert 'target_sha || github.sha' in checks[0]['env']['COMMIT_SHA']
    deploy_script = '\n'.join(s.get('with', {}).get('script', '') for s in deploy['steps'])
    assert 'git reset --hard "${RELEASE_SHA}"' in deploy_script


def test_smoke_failure_fails_required_api_ci_job():
    job = workflow('ci.yml')['jobs']['api']
    smoke_steps = [s for s in job['steps'] if 'rehearse_r0_gate_and_smoke.sh' in s.get('run', '')]
    assert len(smoke_steps) == 1
    step = smoke_steps[0]
    assert not step.get('continue-on-error', False)
    assert 'if' not in step
    smoke_command = next(line for line in step['run'].splitlines() if 'rehearse_r0_gate_and_smoke.sh' in line)
    assert '||' not in smoke_command
    assert not job.get('continue-on-error', False)
    assert 'redis' in job['services']


def test_unified_runner_stops_after_unexpected_failure(tmp_path):
    # Run the real shell wrapper with a recording interpreter stub; smoke must
    # never execute after a drill fails its assertion.
    executable = tmp_path / 'python'
    record = tmp_path / 'calls'
    executable.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$RECORD"\nexit 1\n')
    executable.chmod(0o755)
    import os
    result = subprocess.run(['bash', str(ROOT / 'scripts/rehearse_r0_gate_and_smoke.sh')],
                            env={**os.environ, 'R0_PYTHON': str(executable), 'RECORD': str(record)},
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert len(record.read_text().splitlines()) == 1
    assert 'Phase C' not in result.stdout


def test_unified_runner_propagates_smoke_failure(tmp_path):
    executable = tmp_path / 'python'
    record = tmp_path / 'calls'
    executable.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$RECORD"\n'
                          'case "$1" in *run_smoke_test.py) exit 1;; esac\nexit 0\n')
    executable.chmod(0o755)
    import os
    result = subprocess.run(['bash', str(ROOT / 'scripts/rehearse_r0_gate_and_smoke.sh')],
                            env={**os.environ, 'R0_PYTHON': str(executable), 'RECORD': str(record)},
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert len(record.read_text().splitlines()) == 7
    assert 'Phase C' in result.stdout
    assert 'PASS R.0 gate and integration smoke rehearsal' not in result.stdout
