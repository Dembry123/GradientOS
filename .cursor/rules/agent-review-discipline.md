---
description: "Cursor shim for cross-agent branch review discipline."
alwaysApply: true
---

# Agent Review Discipline

The canonical branch-review guidance lives in `AGENTS.md` and `docs/agent-review-discipline.md`.

Before returning branch-review findings, inventory the full diff, large files, new scripts, duplicated helpers, abstraction boundaries, safety-sensitive paths, test coverage, and branch scope. Do not treat `.cursor/rules` as the source of truth for non-Cursor agents.
