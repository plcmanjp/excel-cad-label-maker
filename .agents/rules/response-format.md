# Response Format

## Language and Tone
- Use Korean for user responses and human-facing documents.
- Do not use enclosed alphanumeric glyphs. Use `1.`, `(1)`, or `-`.

## Structure
- Be accurate and concise. Use bullets, tables, or `코드` when useful.
- Label speculation as speculation.

## Q123
```
**Q1.** 질문내용

**Q2.** 질문내용

**Q3.** 질문내용
```
- Bold only the Q label, leave 1 blank line, and do not use HTML
- Do not offer a choice that can cause loss or reverse completed work. Omit when none are useful

## Audit Report
```
# 점검 — YYYY-MM-DD
## 요약: PASS N / 이슈 M
## 이슈
| 항목 | 심각도 | 근거 | 제안 |
## 미결 질문
```
Do not auto-fix. In a Specialist return, place this format under `OUTPUT`. Return contract: `multi-agent-delegation.md §Specialist 공통 반환 계약`.
