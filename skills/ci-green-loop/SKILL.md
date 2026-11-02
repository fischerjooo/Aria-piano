---
name: ci-green-loop
description: Wait for GitHub Actions CI on an exact commit SHA, inspect failed jobs, fix issues, commit the fixes, and repeat until the required workflows finish successfully. Use when making repository changes that must not be declared complete until CI has finished and all required tests are green, especially for pull requests, feature/fix branches, or any task governed by AGENTS.md CI completion rules.
---

# CI Green Loop

Use this skill as the final gate for repository changes.

## Required loop

1. Finish the code change and commit it.
2. Run the repository's local build/tests first when available.
3. Resolve the exact commit SHA to validate.
4. Run `scripts/wait_for_ci.py` for that SHA and the required workflow(s).
5. Do not declare completion while a required workflow is queued, pending, or in progress.
6. If CI fails, inspect the failed job/step logs, fix the underlying issue, commit the fix, then restart the wait against the new exact SHA.
7. Repeat until every required workflow for the current exact SHA is completed with conclusion `success`.
8. Report the validated SHA and CI result. Never reuse a green result from an older SHA.

## Poller

Use:

```bash
python skills/ci-green-loop/scripts/wait_for_ci.py \
  --repo OWNER/REPO \
  --sha "$(git rev-parse HEAD)" \
  --workflow Validate
```

The script waits for matching GitHub Actions runs to appear, polls until all matching runs finish, prints run URLs and conclusions, and exits non-zero if any matching run finishes unsuccessfully or if the timeout is reached.

Authentication is resolved in this order:

1. `GH_TOKEN`
2. `GITHUB_TOKEN`
3. authenticated `gh api`
4. unauthenticated GitHub REST for public repositories

Use `--help` for timeout, poll interval, and workflow filtering options.

## Failure handling

When the poller exits non-zero because CI failed:

- Inspect the failed workflow run and job logs.
- Fix product code or tests according to the intended behavior; do not weaken valid tests merely to make CI green.
- Commit the fix.
- Run local checks again.
- Run the poller again against the new HEAD SHA.

Stop only when the required workflow set is green for the current SHA, or when a genuine external blocker prevents CI from completing. If blocked externally, state the blocker and do not claim CI passed.
