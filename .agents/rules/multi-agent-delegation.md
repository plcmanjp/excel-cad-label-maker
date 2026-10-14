# Multi-Agent Delegation

## Principles
- **Main = only Director (depth 0).** The main owns planning, routing, state tracking, integration, gates, independent verification, and user conversation. Do not spawn a separate `workspace-manager` Agent.
- **Depth 1.** Only Director to Specialist is allowed. A Specialist does not spawn another Specialist and returns results to the main Director.
- **Least privilege.** Review requires read access; editing receives only the minimum write access needed.
- **Context firewall.** Put long exploration and audits in a subagent.
- **Direct work and delegation.** The Director may directly execute an approved plan when scope and acceptance criteria are explicit and the required evidence, tools, permissions, and verification are available. File count is an impact-review signal, not a delegation threshold. Select a Specialist when expertise, independent judgment, context isolation, or parallel execution has a concrete benefit. Direct work does not grant product decisions, external-operation approval, or broader permissions. Preserve independent verification at high-risk boundaries, approval gates, depth 1, one Writer per file, and read-only review mode. When `../AGENTS.md` exists, Read `../.agents/harness/rules_on_demand/agent-operation-standard.md` for the parent standard; otherwise this rule remains the standalone default.
- **Tool adapters.** Keep the same role names, with tool-specific definition files in `.codex/agents` and `.claude/agents`.

## Director 6 Steps
1. **Decompose**: split the goal into independent missions and approval gates.
2. **Select role**: choose the role SSOT for the mission, not a model name, and confirm current runtime Agent registration.
3. **Assign**: give the Specialist the 4 brief fields and least privilege.
4. **Track state**: record each mission as `완료`, `부분완료`, `실패`, or `차단`. Record the cause and resume condition for failures and blocks.
5. **Integrate**: combine returned results in the main context and decide conflicts.
6. **Verify independently**: do not trust reports alone. Recheck primary sources, diffs, and test results in the main context.

If the Codex execution surface has no named-Agent selector, Read the selected role SSOT and inject it into a general subagent brief. This fallback does not justify skipping role selection and does not change responsibility for depth, state tracking, or independent verification.

## Execution Cadence
- Apply the 6 steps to an approved plan/Phase with a fixed goal, write set, completion criteria, and deterministic checks. Do not apply them per user message, file, or micro-edit. One Writer owns implementation and self-verification for the same plan as one batch.
- Default sequence: `Writer 1회 일괄 구현 → 결정적 검사 → 누적 diff 검수 1회 → 지적 묶음 보정 1회 → 변경 hunk·기존 finding·실패 검사만 delta 재확인 → Director 최종 판정`. Between stages, repeat only deterministic checks that require no new model judgment.
- A separate Reviewer is not a default stage. Require one only for high-risk boundaries such as authentication, authorization, privacy, data loss, concurrency, PLC writes, schemas, public APIs, deployment, or external launch; plan scope drift; changed acceptance criteria; or a new deterministic-check failure. Split high-risk work by risk boundary, not by file.
- After corrections, do not rerun a full review, completed work, or a new Agent. Consider a new brief or Agent only when scope or acceptance criteria change, a new failure cause appears, or work enters a high-risk boundary.
- For bounded Codex Agent spawning, prefer `fork_turns="none"` and pass minimal history only when needed. Provide only the role SSOT pointer, 4 brief fields, file manifest, and exclusions. Limit the default final response to 8KiB and 12 findings. Exclude raw logs, full diffs, and duplicate rules from both input and return.

## Completion, Verification and Progress
- Continue an approved plan through implementation, relevant verification, and repair of failures caused by the change. Use the existing OUTPUT and HANDOFF for deliverables, checks, and stop conditions; do not create another work-instruction source.
- Select verification by changed behavior and risk. Record the change-type routing, cwd, command, environment, side effects, pass criteria, results, and unrun reasons in the repository-selected work system. Disposable local checks without production access may repeat within approval; device-global writes, external transmission, and deployment require their own authority.
- Repetition is a diagnostic signal, not a stop count. After two unsupported hypotheses fail, obtain a bounded measurement within scope. Stop a retry when the same failure repeats without new evidence, a changed hypothesis, or measurable progress; report the blocker and resumption condition. Productive edits, supported polling, and verification do not stop merely because of edit or tool-call counts. Honor explicit budgets, one-shot contracts, and runtime limits.
- Ask for missing decisions affecting scope, acceptance, authority, or irreversible effects and continue independent authorized work while waiting. Silence or elapsed time never supplies approval. Resolve routine implementation choices within approval and preserve completed valid work when instructions change.

## Specialist 공통 반환 계약
The Director tells every spawnable role to Read its role SSOT first. Spawnable-role SSOTs and tool adapters such as `.codex/agents/*.toml` point to this contract only. A Specialist returns the following 7 fields in this order. Put existing role-specific deliverables under `OUTPUT`. This contract does not force the format of the Director's final user response.

```
STATUS: 완료/부분 완료/실패/차단 — 한 줄 상태
SCOPE: 브리프 4요소 기준 실제 작업 범위와 제외 범위
EVIDENCE: 근거, 실제 diff, 실행한 검증과 결과
OUTPUT: 역할별 도메인 산출물, 변경 파일, 검증 결과
UNCERTAINTY: 확인하지 못한 사실과 가정
RISKS: 남은 위험, 영향, 승인 필요 여부
DIRECTOR CHECK: Director가 독립 확인하고 최종 판정할 항목
```

Do not summarize `부분 완료`, `실패`, or `차단` as complete.

## Roster Mapping
| Mission | Role | Note |
|---|---|---|
| Harness audit | `harness-auditor` | Read-only |
| Approved patch | `harness-engineer` | Write |
| Platform research | `platform-researcher` | Web allowed |
| Diff review | `code-reviewer` | Read-only |
| Exploration/planning | Tool built-in | explore/plan, etc. |

## 4 Brief Fields
```
GOAL / INPUT / OUTPUT / HANDOFF
```

## Parallelism and Isolation
Run independent work in parallel. Use a worktree only for experiments with high conflict risk, when the tool supports it.

## Prohibited
- Telling a Specialist to call another agent
- Using a write agent in review mode
- Vague spawning without a brief
- Choosing a model name before selecting a role
- Treating a Specialist report alone as completed verification
