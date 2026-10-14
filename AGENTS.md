# Excel CAD Label Maker Agent Entry

Canonical instructions for the public development and release repository. This harness derives from the 900 starter.

## Identity and boundaries
- PROJECT_IDENTITY: Windows Excel-to-DXF duct-label converter for electrical control cabinets.
- Original developer nickname: 직장인. Fork maintainer and continuing developer: plcmanjp. Preserve both credits.
- One repository owns development and GitHub Releases. Work instructions: GitHub Issues in plcmanjp/excel-cad-label-maker. CURRENT is progress only.
- Version 0.1.0 distributes the supplied original executable unchanged. Never claim it was rebuilt from the imported source.
- Original source in project/original/ is preserved as received. It has syntax damage. A repaired implementation requires a separate approved product task.
- DXF output is supported by the baseline. Native DWG export is not implemented or verified.

## Startup
1. In the managed parent checkout, Read ../../AGENTS.md common invariants only. A standalone checkout has no parent dependency. Never load parent-only supervisor rules.
2. Classify authorization before synchronization or writes. Review or unclear authorization is read-only. Inspect with git --no-optional-locks. Preserve index, HEAD and refs; do not fetch or write records.
3. Read every rule listed below, wiki/journal/CURRENT.md and the exact assigned GitHub Issue. If Issue access fails, stop dependent work.
4. For authorized execution, follow git-sync.md. Preserve unrelated work and ask before dependent edits when another session has unexpected changes.
5. If the SessionStart hook did not run, execute python -B .agents/hooks/session_start_status.py and read its fallback sources. Hook output is separate from rule loading.

## Required rules
Codex and other tools manually Read all six sources at startup. Claude imports the same sources below.
@.agents/rules/harness-workflow.md
@.agents/rules/git-sync.md
@.agents/rules/multi-agent-delegation.md
@.agents/rules/wiki-management.md
@.agents/rules/response-format.md
@.agents/rules/shared-memory.md
@.agents/memory/MEMORY.md

## Operating principles
- Use Korean for user conversations and human-operated documents; concise English for agent-only rules. UTF-8 without BOM.
- Do not use enclosed alphanumerics or prohibited human-visible punctuation from parent invariant 13. External originals remain byte-preserved.
- Fix and verify faults within scope; prefer deterministic prevention. Documents describe current state; Git owns change history.
- Director depth 0 may delegate only to a leaf Specialist. Do not spawn workspace-manager. Read role SSOTs first.
- Ordinary commits and pushes are autonomous within approved execution. Public releases, deployments, force push and remote changes require current user authorization. Recheck repository, version and asset hashes before release publication.
- Never commit personal paths, secrets, operating credentials, real customer workbooks or CAD drawings. Use synthetic public samples.
- Preserve attribution. Redistribution permission does not authorize inventing an MIT, GPL or other license for original work.

## Tool differences
- Codex owns .codex/. Register local absolute hooks with .codex/setup/register-hooks.ps1. Local hooks.json is ignored; hooks.example.json is portable. Trust and /hooks approval remain user runtime actions.
- Claude reads AGENTS.md directly in a supported runtime. No CLAUDE.md adapter. .claude/ assets are owned by Claude; Codex does not create or modify them.
- Native .claude/memory/ is reference-only for Codex. Do not modify or bulk-migrate it. No deployed blog-copy edits.
- Shared skills live in .agents/skills/. Shared role bodies live in .agents/agents/; runtime adapters remain thin.
- Read .agents/docs/harness-policy.md for the source registry and wiki/guides/releasing.md before release work.

## Public documentation
- Write README, usage guides, package materials and release notes for app users: download, use, supported formats, updates, troubleshooting, credits and terms.
- Keep agent operations, approvals, internal workflow, repair narratives and test reports out of user documents. Developer guides contain concise contributor procedures; operational history stays in its internal sources.
- Preserve attribution, actual limitations and legal terms. Do not rewrite external license originals. Run the public-document check with the repository checks.
## Filesystem cleanup
Before cleanup, inventory exact approved paths, Git/index state, active owners and recovery evidence. Preserve originals, customer files, credentials, evidence and backups. Use only a verified OS recycle/trash operation with permanent-deletion fallback disabled, record the actual recycle payload and verify restoration. If recycling or recovery cannot be proven, preserve the files and report blocked. Do not bypass a denied operation by changing flags, splitting paths or switching APIs. This standalone rule has no parent dependency; a managed checkout also follows the parent cleanup contract.
