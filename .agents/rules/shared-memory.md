# Shared Project Memory

## Canonical Source and Priority

- The Git-tracked shared-memory SSOT is `.agents/memory/`. Keep `MEMORY.md` as a short index and place bodies in leaf files.
- Name leaves `fact-`, `decision-`, `workflow-`, or `pitfall-<slug>.md`.
- Code, configuration, test results, live SSOTs, other rules, and `wiki/journal/CURRENT.md` take priority over memory. If they conflict, follow actual state and update memory.

## Tool Boundaries

- `.claude/memory/` is the inbox for Claude native automatic memory and legacy candidates. Do not redirect the native junction to `.agents/memory/`.
- Codex may Read `.claude/memory/` only as reference. Do not modify, delete, or bulk-migrate it.
- `~/.codex/memories/` is Codex-generated local state, not the Git-tracked shared canonical source.

## Writer and Natural Migration

- Only the task's main Director writes shared memory. Specialists, auditors, parallel agents, reviewers, and review tasks are read-only.
- Migrate a legacy entry naturally into a leaf only when actual reuse, updates, and cross-tool need arise and the entry has been verified against current repository state. Do not bulk-copy.
- Wrap-up reviews candidates only. Writing no leaf is normal when durable value or evidence is insufficient.

## Do Not Record

- Secrets or authentication clues, personal PC paths, temporary session values, completion history, duplicate rules, or facts that are easy to rediscover from code.
