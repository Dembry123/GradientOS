# Agent Review Discipline

Use this checklist before returning findings for a branch review or approving a broad implementation branch. The goal is to catch architecture, maintainability, safety, and duplicated-code issues before focusing on isolated line-level bugs.

## Required inventory

1. Compare the branch against the intended base and inspect the full diff stat.
2. Identify large new or heavily changed files. Do not flag size alone; flag mixed responsibilities, unclear data flow, hard-to-test boundaries, or excessive coupling.
3. Identify all new scripts, CLIs, background workers, protocol helpers, and generic utilities.
4. Search the repo for existing helpers with overlapping purpose before accepting new helper APIs or scripts.
5. Check whether new abstractions are paid for by real reuse, isolation, testability, or domain clarity.
6. Check whether duplicated code should be centralized, or whether local duplication is intentionally clearer and safer.
7. Check safety and hardware-facing paths for stale-command races, validation gaps, unchecked status packets, timeout behavior, and misleading operator guarantees.
8. Check test coverage at the risk boundary, not just at the public happy path.
9. Call out branch scope mismatch when unrelated concerns make review or rollback difficult.

## Finding standards

Findings should lead with concrete bugs, behavioral regressions, safety risks, missing validation, weak abstractions, excessive indirection, and duplication that creates drift. Style comments are only useful when they materially affect readability, correctness, or maintainability.

For performance, distinguish real hot paths from premature optimization. Prefer direct readable code unless there is evidence that optimization matters.

When reviewing large files, explain the responsibility split that would improve the code. A useful split follows IO, state, and domain boundaries; an unhelpful split merely moves functions into more files.

When reviewing scripts, compare them against existing repo tools and libraries. Hardware/protocol scripts should usually be thin CLIs over shared parsing, validation, and command helpers so fixes land once.

## Minimum review commands

```bash
git status --short --branch
git diff --stat <base>...HEAD
git diff --name-only <base>...HEAD
rg -n "new helper or protocol symbols" relevant/paths
```

Use additional language-specific tests and builds based on the touched files.
