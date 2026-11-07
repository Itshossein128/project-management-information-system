"""Tests for scripts/verify_ci_gate.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ directory is in sys.path
scripts_dir = Path(__file__).resolve().parent.parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import verify_ci_gate  # noqa: E402


def test_verify_ci_gate_success():
    mock_runs = [
        {
            "id": 1001,
            "name": "CI",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/repo/actions/runs/1001",
        }
    ]
    mock_jobs = [
        {"id": 201, "name": "web", "status": "completed", "conclusion": "success"},
        {"id": 202, "name": "api", "status": "completed", "conclusion": "success"},
    ]

    with patch.object(verify_ci_gate, "get_workflow_runs", return_value=mock_runs), \
         patch.object(verify_ci_gate, "get_run_jobs", return_value=mock_jobs):
        result = verify_ci_gate.verify_ci_gate(
            repo="owner/repo",
            sha="abcdef123456",
            token="dummy-token",
            workflow_name="CI",
            required_jobs=["web", "api"],
            timeout=10,
            poll_interval=1,
            grace_period=2,
        )

    assert result is True


def test_verify_ci_gate_workflow_failure():
    mock_runs = [
        {
            "id": 1002,
            "name": "CI",
            "status": "completed",
            "conclusion": "failure",
            "html_url": "https://github.com/example/repo/actions/runs/1002",
        }
    ]

    with patch.object(verify_ci_gate, "get_workflow_runs", return_value=mock_runs):
        result = verify_ci_gate.verify_ci_gate(
            repo="owner/repo",
            sha="abcdef123456",
            token="dummy-token",
            workflow_name="CI",
            required_jobs=["web", "api"],
            timeout=10,
            poll_interval=1,
            grace_period=2,
        )

    assert result is False


def test_verify_ci_gate_missing_required_job():
    mock_runs = [
        {
            "id": 1003,
            "name": "CI",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/repo/actions/runs/1003",
        }
    ]
    mock_jobs = [
        {"id": 301, "name": "web", "status": "completed", "conclusion": "success"},
        # "api" job is missing
    ]

    with patch.object(verify_ci_gate, "get_workflow_runs", return_value=mock_runs), \
         patch.object(verify_ci_gate, "get_run_jobs", return_value=mock_jobs):
        result = verify_ci_gate.verify_ci_gate(
            repo="owner/repo",
            sha="abcdef123456",
            token="dummy-token",
            workflow_name="CI",
            required_jobs=["web", "api"],
            timeout=10,
            poll_interval=1,
            grace_period=2,
        )

    assert result is False


def test_verify_ci_gate_required_job_failed():
    mock_runs = [
        {
            "id": 1004,
            "name": "CI",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/repo/actions/runs/1004",
        }
    ]
    mock_jobs = [
        {"id": 401, "name": "web", "status": "completed", "conclusion": "success"},
        {"id": 402, "name": "api", "status": "completed", "conclusion": "failure"},
    ]

    with patch.object(verify_ci_gate, "get_workflow_runs", return_value=mock_runs), \
         patch.object(verify_ci_gate, "get_run_jobs", return_value=mock_jobs):
        result = verify_ci_gate.verify_ci_gate(
            repo="owner/repo",
            sha="abcdef123456",
            token="dummy-token",
            workflow_name="CI",
            required_jobs=["web", "api"],
            timeout=10,
            poll_interval=1,
            grace_period=2,
        )

    assert result is False


def test_verify_ci_gate_polling_until_success():
    in_progress_runs = [
        {
            "id": 1005,
            "name": "CI",
            "status": "in_progress",
            "conclusion": None,
        }
    ]
    completed_runs = [
        {
            "id": 1005,
            "name": "CI",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/repo/actions/runs/1005",
        }
    ]
    mock_jobs = [
        {"id": 501, "name": "web", "status": "completed", "conclusion": "success"},
        {"id": 502, "name": "api", "status": "completed", "conclusion": "success"},
    ]

    # First call in_progress, second call completed
    with patch.object(verify_ci_gate, "get_workflow_runs", side_effect=[in_progress_runs, completed_runs]), \
         patch.object(verify_ci_gate, "get_run_jobs", return_value=mock_jobs), \
         patch("time.sleep", return_value=None):
        result = verify_ci_gate.verify_ci_gate(
            repo="owner/repo",
            sha="abcdef123456",
            token="dummy-token",
            workflow_name="CI",
            required_jobs=["web", "api"],
            timeout=10,
            poll_interval=1,
            grace_period=2,
        )

    assert result is True


def test_verify_ci_gate_no_runs_found_timeout():
    with patch.object(verify_ci_gate, "get_workflow_runs", return_value=[]), \
         patch("time.sleep", return_value=None):
        result = verify_ci_gate.verify_ci_gate(
            repo="owner/repo",
            sha="abcdef123456",
            token="dummy-token",
            workflow_name="CI",
            required_jobs=["web", "api"],
            timeout=2,
            poll_interval=1,
            grace_period=0,  # Grace period expired immediately
        )

    assert result is False


def test_main_cli_missing_args(monkeypatch):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    monkeypatch.setattr(sys, "argv", ["verify_ci_gate.py"])
    exit_code = verify_ci_gate.main()
    assert exit_code == 2


def test_main_cli_success(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "verify_ci_gate.py",
            "--repo", "test/repo",
            "--sha", "1234567890abcdef",
            "--token", "secret",
            "--required-jobs", "web,api",
        ],
    )
    with patch.object(verify_ci_gate, "verify_ci_gate", return_value=True):
        exit_code = verify_ci_gate.main()
    assert exit_code == 0
