# Wiki Management

## Roles
| Path | Content |
|---|---|
| `wiki/INDEX.md` | Navigation index and durable registry for low-frequency fixed information and entry points |
| `wiki/journal/CURRENT.md` | Work journal and single work-state SSOT injected at SessionStart |
| `wiki/meta/` | Product/project what, why, boundaries, decisions, risks, and roadmap |
| `wiki/specs/` | Per-feature `summary / plan / checklist` specifications |
| `wiki/poc/` | Durable folder bundles for directly executed proofs of concept |
| `wiki/journal/YYYY-MM/r{NNN}-*.md` | Session journals |
| `wiki/troubleshooting/` | Recurrence-prevention KB |
| `wiki/guides/`, `wiki/reference/` | User and contributor guides and technical references |
| `.agents/docs/` | Agent operating policy and generation provenance |
| `project/original/`, `project/src/`, `project/tests/` | Preserved original, application source/assets, and unified product/build-guard tests. `project/INDEX.md` owns the flat single-app layout |
| `project/scripts/`, `project/tests/`, `project/qc/` | Development tools, build guards, and product QC assets |
| `release/` | Release configuration, package materials, preserved notices, packaging tools, and release QC. `release/INDEX.md` owns the layout |

This repository uses **1 workspace = 1 app** and a flat `project/` layout. Keep application source, original input, and tests directly under the paths above. Product planning documents belong in `wiki/`; GitHub Issues own work instructions. Do not add an implementation-lineage directory without an explicitly approved structural task.

## Readers and Published Copy

- README, usage guides, package README/NOTICE/CREDITS, bundled library explanations and release notes are user documents. Explain the product, download, use, supported formats, updates, relevant limitations, credits and terms.
- Exclude internal agent setup, approval conversations, repair history, workflow narratives and test reports from user documents. Do not link CURRENT, journals or harness policy from user entry points.
- Developer guides provide concise reproducible commands and technical references for contributors. Agent operating policy and asset-generation prompts belong in `.agents/docs/`.
- CURRENT, immutable journals and QC records remain internal continuity and evidence sources. Preserve their integrity and existing external legal originals; do not disguise an unverified capability as supported.
- `.agents/scripts/check_public_docs.py` enforces the current user-document boundary through repository checks. Add newly introduced user entry points to its manifest.

## Work Journal (CURRENT.md)

- `wiki/journal/CURRENT.md` is the single work-state SSOT. The SessionStart hook injects a `SOURCE` raw fallback and a GOAL 1, STATE 2, OPEN 2, NEXT 3 compressed brief. It derives the previous journal pointer from the filesystem automatically; do not maintain that pointer manually.
- Update it immediately for every material state change: requirements, design decisions, actual file changes, verification results, or blocks. Replace current state instead of accumulating turns or chronology.
- Do not copy session retrospectives or completion details into it. The `r{NNN}` snapshot is their SSOT; do not keep the same content in 2 places. Replace "다음 작업" during wrap-up instead of accumulating entries. Recommended limit: ≤10KB.
- **During wrap-up, refine CURRENT.md before writing the `r{NNN}` snapshot.**
- Body SSOT: `wiki/journal/README.md` §작업 저널 (CURRENT.md — 혼합형).
- Do not put work state in `wiki/INDEX.md`.

## Journal
`wiki/journal/YYYY-MM/r{NNN}-{slug}.md`: **the journal itself is history; do not add an index or mapping table.**
For monthly r001 numbering, top-level H1, 4 visible metadata fields, no YAML frontmatter, and required sections, follow `wiki/journal/README.md`.

## Meta

`wiki/meta/meta-{NNN}-{category}-{slug}.md` records product/project what, why, boundaries, decisions, risks, and roadmap. `wiki/meta/INDEX.md` is the SSOT for immutable, never-reused, globally increasing 3-digit numbering and classification rules.

## Specs

`wiki/specs/{category}/S{NNNN}-{slug}-{summary|plan|checklist}.md` is a per-feature 3-document set. `wiki/specs/INDEX.md` is the SSOT for immutable, never-reused, globally increasing 4-digit numbering, 1-level categories, promotion from 구상중, and required structures for each document type.

## PoC

`wiki/poc/poc-{NNN}-{slug}/` preserves current state, reproduction assets, results, and decisions for a directly executed proof of concept as a durable folder bundle. The root `README.md` is its current-state SSOT. Create only needed category folders. `wiki/poc/INDEX.md` is the SSOT for numbering, structure, state, and sensitive-information rules.

## Work Management

GitHub Issues in plcmanjp/excel-cad-label-maker own work instructions. Read the exact assigned Issue and verify authentication and repository identity. Do not copy Issue bodies into local orders. CURRENT contains progress and pointers only. For non-ASCII mutations on Windows, follow wiki/guides/releasing.md safe body-file transport and exact API readback.

## Troubleshooting
Use `wiki/troubleshooting/TS-{NNN}-{slug}.md` for recurring problems and document them autonomously right after resolution.
Follow `wiki/troubleshooting/INDEX.md` for numbering, required sections, and authoring triggers. For recurrence prevention, consider permanent rules or hooks first.
