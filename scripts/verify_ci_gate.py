#!/usr/bin/env python3
"""
Verify that the required CI checks have passed for a specific commit SHA
before allowing deployment to proceed.

Exit codes:
  0: CI workflow and all required jobs succeeded for the commit SHA.
  1: CI failed, timed out, was cancelled, or required checks are missing.
  2: Invalid arguments or runtime environment failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def github_api_request(
    endpoint: str,
    token: str | None = None,
    api_url: str = "https://api.github.com",
) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "velora-ci-gate",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_msg = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {exc.code} for {url}: {err_msg}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach GitHub API at {url}: {exc.reason}") from exc


def get_workflow_runs(
    repo: str,
    sha: str,
    token: str | None = None,
    api_url: str = "https://api.github.com",
) -> list[dict[str, Any]]:
    endpoint = f"/repos/{repo}/actions/runs?head_sha={sha}"
    data = github_api_request(endpoint, token=token, api_url=api_url)
    return data.get("workflow_runs", [])


def get_run_jobs(
    repo: str,
    run_id: int,
    token: str | None = None,
    api_url: str = "https://api.github.com",
) -> list[dict[str, Any]]:
    endpoint = f"/repos/{repo}/actions/runs/{run_id}/jobs"
    data = github_api_request(endpoint, token=token, api_url=api_url)
    return data.get("jobs", [])


def verify_ci_gate(
    repo: str,
    sha: str,
    token: str | None = None,
    workflow_name: str = "CI",
    required_jobs: list[str] | None = None,
    timeout: int = 1200,
    poll_interval: int = 15,
    grace_period: int = 60,
    api_url: str = "https://api.github.com",
) -> bool:
    if required_jobs is None:
        required_jobs = ["web", "api"]

    print(f"==> [CI-GATE] Verifying CI checks for repository: {repo}")
    print(f"==> [CI-GATE] Target commit SHA: {sha}")
    print(f"==> [CI-GATE] Required workflow: '{workflow_name}'")
    print(f"==> [CI-GATE] Required jobs: {required_jobs}")
    print(f"==> [CI-GATE] Polling timeout: {timeout}s (interval: {poll_interval}s)")

    start_time = time.time()
    grace_deadline = start_time + grace_period
    run_found = None

    while True:
        elapsed = int(time.time() - start_time)
        if elapsed > timeout:
            print(f"ERROR: [CI-GATE] Timed out after {elapsed}s waiting for CI on commit {sha}.")
            return False

        try:
            runs = get_workflow_runs(repo, sha, token=token, api_url=api_url)
        except Exception as exc:
            print(f"WARNING: [CI-GATE] Failed to query workflow runs: {exc}. Retrying in {poll_interval}s...")
            time.sleep(poll_interval)
            continue

        matching_runs = [r for r in runs if r.get("name") == workflow_name]

        if not matching_runs:
            if time.time() < grace_deadline:
                print(f"[CI-GATE] No run for workflow '{workflow_name}' discovered yet ({elapsed}s elapsed). Waiting for trigger...")
                time.sleep(poll_interval)
                continue
            else:
                print(f"ERROR: [CI-GATE] No workflow run named '{workflow_name}' found for commit {sha} after {elapsed}s.")
                return False

        # Pick the most recent run if multiple exist
        run_found = matching_runs[0]
        run_id = run_found["id"]
        status = run_found.get("status")
        conclusion = run_found.get("conclusion")
        html_url = run_found.get("html_url", "")

        if status != "completed":
            print(f"[CI-GATE] Workflow '{workflow_name}' (Run #{run_id}) is '{status}'... waiting ({elapsed}s elapsed).")
            time.sleep(poll_interval)
            continue

        # Status is completed! Check conclusion
        print(f"[CI-GATE] Workflow '{workflow_name}' (Run #{run_id}) completed with conclusion: '{conclusion}'.")
        print(f"[CI-GATE] Details URL: {html_url}")

        if conclusion != "success":
            print(f"ERROR: [CI-GATE] Workflow '{workflow_name}' did not succeed (conclusion: '{conclusion}'). Deployment blocked!")
            return False

        # Verify individual required jobs
        try:
            jobs = get_run_jobs(repo, run_id, token=token, api_url=api_url)
        except Exception as exc:
            print(f"WARNING: [CI-GATE] Failed to query jobs for run #{run_id}: {exc}.")
            return False

        job_status_map = {j.get("name"): j.get("conclusion") for j in jobs}
        missing_or_failed = []

        for req_job in required_jobs:
            job_conclusion = job_status_map.get(req_job)
            if job_conclusion is None:
                missing_or_failed.append(f"{req_job} (NOT FOUND)")
            elif job_conclusion != "success":
                missing_or_failed.append(f"{req_job} (conclusion: {job_conclusion})")

        if missing_or_failed:
            print(f"ERROR: [CI-GATE] The following required jobs did not succeed: {', '.join(missing_or_failed)}.")
            return False

        print(f"SUCCESS: [CI-GATE] All required CI checks passed for commit {sha}! Proceeding to deployment.")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify CI gate before deployment.")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="GitHub repository (owner/repo)")
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA"), help="Commit SHA to verify")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"), help="GitHub token")
    parser.add_argument("--workflow-name", default="CI", help="Name of required workflow (default: CI)")
    parser.add_argument("--required-jobs", default="web,api", help="Comma-separated list of required job names")
    parser.add_argument("--timeout", type=int, default=1200, help="Max wait time in seconds (default: 1200)")
    parser.add_argument("--poll-interval", type=int, default=15, help="Polling interval in seconds (default: 15)")
    parser.add_argument("--grace-period", type=int, default=60, help="Grace period for CI to appear (default: 60)")
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"), help="GitHub API base URL")

    args = parser.parse_args()

    if not args.repo:
        print("ERROR: [CI-GATE] Repository not specified. Set --repo or GITHUB_REPOSITORY.", file=sys.stderr)
        return 2

    if not args.sha:
        print("ERROR: [CI-GATE] Commit SHA not specified. Set --sha or GITHUB_SHA.", file=sys.stderr)
        return 2

    required_jobs = [j.strip() for j in args.required_jobs.split(",") if j.strip()]

    success = verify_ci_gate(
        repo=args.repo,
        sha=args.sha,
        token=args.token,
        workflow_name=args.workflow_name,
        required_jobs=required_jobs,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
        grace_period=args.grace_period,
        api_url=args.api_url,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
