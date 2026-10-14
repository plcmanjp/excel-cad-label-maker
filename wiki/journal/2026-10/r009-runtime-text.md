# r009 런타임 경량화와 텍스트 안내 완료

| 항목 | 값 |
|---|---|
| 문서리비전 | r009-runtime-text |
| 작성일시 | 2026-10-14 15:54 (KST) |
| 작성모델 | GPT-6 Codex |
| 담당에이전트 | Director 및 읽기 전용 제품 Reviewer |

## 요약

[Issue #12](https://github.com/plcmanjp/excel-cad-label-maker/issues/12)의 TXT 출력과 런타임 의존성 경량화를 완료하고 [PR #13](https://github.com/plcmanjp/excel-cad-label-maker/pull/13)을 main에 병합했다. pandas 대신 기존 Excel 엔진을 직접 읽고 Windows x64 및 Tk 8.6용 TkDnD만 수집한다. numpy 등 ezdxf 필수 의존성은 유지했다.

사용자 안내는 UTF-8 일반 텍스트로 변환하고 외부 고지는 byte를 보존하며 TXT 이름과 provenance를 맞춘다. Windows 대소문자 규칙에 따른 파일명 중복, 기존 대상과 provenance 충돌을 쓰기 전에 거부한다. 출력에 Markdown이 남으면 정식 패키저가 거부한다.

## 검증

로컬 project39 + release16 + harness22는 76 PASS, native symlink 권한 부족 1 SKIP이다. 브랜치, PR과 main Windows CI는 모두 77 PASS 및 0 SKIP이다. 개발 및 업데이트 QC와 clean main 정식 빌드, 아이콘과 TXT 및 receipt와 압축 해제 파일 hash를 확인했다.

기존 reader와 합성 workbook 49개의 라벨 묶음이 일치했다. XLS 날짜 반올림 경계와 고지 이름 충돌을 독립 검수에서 찾아 수정했고 해당 hunk와 회귀 검사에 한정한 delta 검수를 통과했다.

최종 ZIP의 실제 EXE에서 Explorer 드롭과 DXF 저장을 확인했다. 라벨 4개, TEXT와 LWPOLYLINE 각 7개의 글자와 위치 및 스타일이 기존 구현과 같고 AC1024 및 mm와 audit 오류 0건이다. 업데이트 QC 앱은 실제 GitHub API로 새 버전 팝업과 나중에 버튼을 확인했다. UIA selector 저장 readback과 Computer Use의 시각 확인을 구분해 기록했다.

폴더는 87,078,780 bytes에서 65,536,735 bytes로 24.7%, ZIP은 39,863,064 bytes에서 29,500,045 bytes로 26.0% 감소했다. 20,000셀 읽기 5회 중앙값은 0.1163초에서 0.1102초, converter import 교차 7회 중앙값은 0.6929초에서 0.5856초다. 디스크 캐시를 비우지 않았으며 실제 frozen GUI 시작 시간의 측정 결과가 아니다.

빌드와 ZIP 및 EXE hash, 원시 측정값과 CI ID는 [공개 QC 기록](../../../project/qc/runtime-optimization-results.json)에 있다. 원시 GUI 및 경로 자료는 Git에서 제외되는 .local/runtime-qc에 둔다. 새 ZIP은 로컬 검증용이며 공개 v0.1.0 및 v0.2.0은 보존한다. 원본과 아이콘 및 외부 고지와 공개 ZIP 68개 hash를 재확인했다.

## 커밋 (이번 세션)

- 구현 66bb0af247a09c197d37dd131b48defe3e5df485
- PR #13 병합 및 최종 빌드 기준 35570717c4563740cea128cc53a1597276f17128
- 이후 QC 및 문서 기록 커밋은 Git 이력을 따른다. 기록 변경 때문에 검증된 구현 EXE를 다시 빌드했다고 표현하지 않는다.

## 미해결 이슈

[Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)는 실제 CAD, Python 없는 별도 PC와 원본 EXE 및 소스 대응과 구체적인 수정, 상업 및 추가 재배포 조건 확인이 남아 OPEN이다. DWG 직접 출력은 미지원이다.

## 다음 우선순위

- 실제 CAD와 Python 없는 별도 PC 검증을 Issue #2에 연결한다.
- 원본 빌드 정보 및 세부 이용 조건을 확인하고 다음 공개 버전을 정한다.

## 자가점검 회고

CURRENT의 이전 한국어 전송 손상을 UTF-8 파일 편집으로 복구하고 실제 hook 파서의 문서 구조 검사를 추가했다. 한국어 문서를 PowerShell 파이프로 Python stdin에 전달하는 방식은 피한다. 고지의 확장자 변환은 원문 hash뿐 아니라 변환 후 이름의 충돌까지 검증해야 한다.
