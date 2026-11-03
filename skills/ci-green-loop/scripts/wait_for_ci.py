#!/usr/bin/env python3
"""Wait for GitHub Actions runs on an exact SHA and require them to finish green."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

TERMINAL = {"completed"}
SUCCESS = {"success"}


@dataclass(frozen=True)
class Run:
    run_id: int
    name: str
    event: str
    status: str
    conclusion: str | None
    html_url: str
    head_sha: str


def _request_json(url: str) -> dict[str, Any]:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ci-green-loop",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        if token or exc.code not in {401, 403}:
            raise RuntimeError(f"GitHub API HTTP {exc.code}: {body}") from exc

    try:
        proc = subprocess.run(
            ["gh", "api", url],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "GitHub API access failed. Set GH_TOKEN/GITHUB_TOKEN or install and authenticate gh."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"gh api failed: {exc.stderr.strip()}") from exc
    return json.loads(proc.stdout)


def _load_fixture(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def fetch_runs(repo: str, sha: str, fixture: str | None = None) -> list[Run]:
    if fixture:
        payload = _load_fixture(fixture)
    else:
        query = urllib.parse.urlencode({"head_sha": sha, "per_page": 100})
        payload = _request_json(f"https://api.github.com/repos/{repo}/actions/runs?{query}")
    runs = []
    for raw in payload.get("workflow_runs", []):
        if raw.get("head_sha") != sha:
            continue
        runs.append(
            Run(
                run_id=int(raw["id"]),
                name=str(raw.get("name") or raw.get("display_title") or "unnamed"),
                event=str(raw.get("event") or ""),
                status=str(raw.get("status") or ""),
                conclusion=raw.get("conclusion"),
                html_url=str(raw.get("html_url") or raw.get("url") or ""),
                head_sha=str(raw.get("head_sha") or ""),
            )
        )
    return runs


def select_runs(runs: list[Run], workflows: list[str]) -> list[Run]:
    if not workflows:
        return runs
    wanted = {name.casefold() for name in workflows}
    return [run for run in runs if run.name.casefold() in wanted]


def summarize(runs: list[Run]) -> None:
    for run in sorted(runs, key=lambda item: (item.name, item.run_id)):
        conclusion = run.conclusion or "-"
        print(
            f"{run.name}: status={run.status} conclusion={conclusion} "
            f"event={run.event} id={run.run_id} {run.html_url}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repository in OWNER/REPO form")
    parser.add_argument("--sha", required=True, help="Exact commit SHA to validate")
    parser.add_argument(
        "--workflow",
        action="append",
        default=[],
        help="Required workflow name; repeat for multiple workflows. If omitted, all runs for the SHA are required.",
    )
    parser.add_argument("--poll-seconds", type=float, default=10.0, help="Polling interval (default: 10)")
    parser.add_argument("--timeout-seconds", type=float, default=1800.0, help="Overall timeout (default: 1800)")
    parser.add_argument(
        "--appear-timeout-seconds",
        type=float,
        default=180.0,
        help="How long to wait for required runs to appear (default: 180)",
    )
    parser.add_argument("--fixture", help=argparse.SUPPRESS)
    parser.add_argument("--once", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.poll_seconds <= 0 or args.timeout_seconds <= 0 or args.appear_timeout_seconds <= 0:
        print("poll and timeout values must be positive", file=sys.stderr)
        return 2

    started = time.monotonic()
    appeared_deadline = started + args.appear_timeout_seconds
    overall_deadline = started + args.timeout_seconds
    last_signature: tuple[tuple[Any, ...], ...] | None = None

    while True:
        try:
            matching = select_runs(fetch_runs(args.repo, args.sha, args.fixture), args.workflow)
        except (RuntimeError, json.JSONDecodeError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        signature = tuple(sorted((r.run_id, r.name, r.status, r.conclusion) for r in matching))
        if signature != last_signature:
            if matching:
                summarize(matching)
            else:
                names = ", ".join(args.workflow) if args.workflow else "any workflow"
                print(f"Waiting for {names} on {args.sha} to appear...")
            last_signature = signature

        now = time.monotonic()
        if not matching:
            if now >= appeared_deadline:
                print("error: required CI runs did not appear before the appearance timeout", file=sys.stderr)
                return 3
        else:
            incomplete = [run for run in matching if run.status not in TERMINAL]
            if not incomplete:
                failed = [run for run in matching if run.conclusion not in SUCCESS]
                if failed:
                    print("CI finished with failures:", file=sys.stderr)
                    summarize(failed)
                    return 1
                print(f"CI green for exact SHA {args.sha}: {len(matching)} required run(s) succeeded.")
                return 0

        if args.once:
            return 4
        if now >= overall_deadline:
            print("error: timed out waiting for CI to finish", file=sys.stderr)
            return 3
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
