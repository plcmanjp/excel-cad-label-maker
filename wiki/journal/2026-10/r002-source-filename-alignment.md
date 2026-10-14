# r002: 원본 소스 파일명과 경로 정합

| 항목 | 값 |
|---|---|
| 문서리비전 | r002-source-filename-alignment |
| 작성일시 | 2026-10-14 10:54 (KST) |
| 작성모델 | GPT-6 기반 Codex 메인 |
| 담당에이전트 | Director |

## 요약

저장소 관리자가 지정한 excel_cad_label.py 파일명을 유지했다. manifest의 source_path, 원본 바이트 보존 Git 속성, 개발 안내와 원본 README를 현재 경로에 맞췄다. 원본 파일 내용은 수정하지 않았으며, 공개된 v0.1.0 태그와 릴리스 자산을 교체하거나 재포장하지 않았다.

## 커밋 (이번 세션)

- 기준 HEAD: 913939281151b33d0b49a09f8c4c7d8398346a40.
- 파일명과 참조 갱신 commit은 이 journal 경로의 git log로 확인한다.

## 검증

- 현재 경로: Project/P001-excel-cad-label/original/excel_cad_label.py.
- 소스 SHA-256은 1af3c494969671cce72186c4ebd464d7eecc06c22926ceb9f0e7807f5265e2f0으로 원본과 같다.
- Git blob fbfb003121422c58f321d2774d851e673be6c273가 이전 HEAD의 원본 blob과 일치한다.
- 저장소 공개 경계, 인코딩, 원본 hash와 import/TOML 검사 PASS. 개발 파일에서 이전 파일명 참조는 0건이다.
- v0.1.0 ZIP SHA-256 c37cdf49f41a07e87bd339cbfb72675dee89dc3fb64cba354c35af249d05a7e4를 보존했다.
- 원본 Python의 문법 손상 상태도 그대로다. 이 변경은 복구 구현이나 재빌드가 아니다.

## 다음 우선순위

[Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)의 현재 경로를 따라 정상 원본, 소스 복구와 재현 가능한 빌드를 확인한다.

## 자가점검 회고

사용자가 직접 수행하고 명시한 파일명 변경을 보존했다. 연결된 경로와 Git 속성을 함께 갱신하고 파일 내용 및 기존 릴리스의 무변경을 hash로 검증했다.