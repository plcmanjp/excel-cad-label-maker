# r008 - 앱 개발 경로 평면화

| 항목 | 값 |
|---|---|
| 문서리비전 | r008-flat-project |
| 작성일시 | 2026-10-14 14:57 (KST) |
| 작성모델 | GPT-6 (Codex) |
| 담당에이전트 | Codex Director /root |

## 요약

사용자 지시에 따라 project의 앱 계층을 평면화했다. 원본과 구현은 project/original 및 project/src에서 관리하고 제품 테스트는 기존 project/tests의 빌드 보호 검사와 통합한다. 제거된 계층의 빈 디렉터리는 삭제하지 않고 Git에서 제외되는 로컬 검수 경로로 이동했다.

실행, 개발 및 정식 빌드와 별도 QC 진입점, 아이콘 도구, receipt와 패키저, baseline manifest 및 현재 문서와 하네스의 경로를 갱신했다. CI는 통합 project/tests35를 빌드에서 한 번 실행하며 release/tests12와 하네스22를 합해 검사69개를 유지한다.

## 커밋 (이번 세션)

- `0557c7d150e966880657cedfaf159b95faf560a3`: 평면화와 운영 경로 및 CI 수정.
- `d6ca19a83589fbb5e6e2b738d6675df2e580bdeb`: 검증된 PR #11의 main 병합.
- 완료 결과와 이 스냅샷은 후속 한국어 문서 commit으로 기록한다.

## 검증

- 로컬 검사68 PASS, native symlink1은 권한 부족 SKIP다. branch run38518873448, PR run38518918434 및 병합 main run38519150398의 Windows CI에서69개 모두 통과했고 native 검사도 실행됐다.
- 이동한 원본, 구현과 테스트 및 아이콘13개 파일의 hash와 기준 Git byte가 일치했다. 기존 보호 파일68개의 hash도 평면화 경로로 대조해 보존을 확인했다.
- 통합 검사, 저장소 및 문서 링크, 개발 및 정식 Windows 빌드, flat source/assets receipt 대조와 QC 진입점 import가 PASS다.
- 누적 diff의 독립 읽기 전용 검수에서 원본 안내의 옛 계층 설명1건을 수정했다. 보정 문장만 delta 검수해 해소를 확인했다.
- 깨끗한 병합 main에서 정식 빌드와 ZIP을 실제 생성했다. receipt의 source_dirty=false 및 main commit, project/src 진입점과 source/assets 경로 및 내부1,905개 파일 hash를 대조했다. 검증 ZIP은 release/artifacts/flat-qc-d6ca19a에만 보관하며 공개하지 않았다.
- GitHub v0.1.0과 v0.2.0의 기존 자산 ID, 크기 및 digest를 보존했다. 과거 QC JSON과 journal 및 공개 릴리스 파일은 수정하지 않았다.

상세는 project/qc/flat-project-results.json, 원시 로그와 이동 전 hash는 Git에서 제외되는 .local/flatten-qc에 있다.

## 작업번호

- [Issue #10](https://github.com/plcmanjp/excel-cad-label-maker/issues/10): 평면화 완료, CLOSED.
- [PR #11](https://github.com/plcmanjp/excel-cad-label-maker/pull/11): 독립 검수와 CI 통과 후 main 병합 완료.

## 다음 우선순위

Issue #2의 실제 CAD, Python 없는 별도 Windows PC 실행 및 원본 이용 조건 확인을 이어간다. 경로와 패키징 검증을 해당 미검증 항목의 PASS로 확대하지 않는다.

## 자가점검 회고

기존 tests 디렉터리와 이름 충돌을 확인한 뒤 바이트를 보존하며 통합했다. 실행 도구와 CI 및 정본 경로 규칙을 함께 수정했고 제품 검사를 중복 실행하지 않도록 검수했다. 과거 근거의 경로는 현재 경로와 구분해 보존했다.
