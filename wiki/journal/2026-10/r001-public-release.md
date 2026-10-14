# r001: 공개 개발 저장소와 0.1.0 기준 릴리스

| 항목 | 값 |
|---|---|
| 문서리비전 | r001-public-release |
| 작성일시 | 2026-10-14 10:25 (KST) |
| 작성모델 | GPT-6 기반 Codex 메인 |
| 담당에이전트 | Director |

## 요약

[Issue #1](https://github.com/plcmanjp/excel-cad-label-maker/issues/1)에 따라 공개 개발 및 배포 저장소를 구성하고 v0.1.0을 공개했다. 900 스타터의 중립 규칙, 역할 정본, Codex 어댑터, SessionStart와 회귀 검사를 재사용했다. Claude 전용 설정은 구성하지 않았다. 로컬 절대경로 hooks.json, 기존 EXE, ZIP과 QC 원본은 Git에서 제외했다.

원개발자 ‘직장인’과 Fork 및 후속 개발자 plcmanjp를 구분하고 관리자의 원본 공개 재배포 허락을 확인했다. 구체적인 오픈소스 라이선스는 확인되지 않아 임의로 부여하지 않았다. 원본 GitHub 주소가 없어 네트워크 fork로 표현하지 않았다.

## 커밋 (이번 세션)

- 3db049041a3849a4b5c12ca071d33d0adc495c80: 공개 개발 하네스와 0.1.0 원본 배포 구성.
- v0.1.0은 위 commit을 가리킨다. 완료 기록 commit은 git log -- wiki/journal/2026-10/r001-public-release.md로 확인한다.

## 검증

- Python 3.14.3 및 Windows PowerShell에서 하네스 fixture 22개와 합성 릴리스 경계 검사 6개가 통과했다. 원본 소스는 문법 손상 상태를 그대로 보존하며 제품 build 대상으로 검사하지 않았다.
- 실제 절대 등록 훅의 root/subcwd 및 startup/resume 4조건에서 출력 일치, 4096 UTF-8 bytes 이하와 파일, HEAD 및 index 보존을 확인했다.
- 공개 경계, BOM, 원본 SHA-256, 규칙 import, TOML과 표시 구두점 검사가 통과했다. 독립 code-reviewer의 낮음 2건(배포 문서 링크, 어댑터의 이전 제품명)을 보정하고 delta 검수를 통과했다.
- 정확한 제목의 실제 Excel_Cad_Label.exe 창을 확인했다. 첫 오대상 UIA 결과는 무효이며 이후 실제 EXE 경로와 PID를 확인했다. 캡처는 다른 창이 가려 시각 품질 근거로 쓰지 않았다.
- 원본 EXE와 ZIP 내부 EXE의 SHA-256: 215a2e3a179bc20153fac6b014898ea85667a1d6a9229f9177c342a72465db14.
- 공개 ZIP 재다운로드 SHA-256: c37cdf49f41a07e87bd339cbfb72675dee89dc3fb64cba354c35af249d05a7e4. GitHub 자산 digest 및 SHA256SUMS.txt와 일치한다.
- 초기 main CI 38495346833 및 tag CI 38495451633이 성공했다. 릴리스는 draft 및 prerelease가 아니다.

## 다음 우선순위

[Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)가 소스 복구, 합성 자료 변환 회귀 검사, 재현 가능한 Windows 빌드와 외부 라이브러리 고지를 소유한다. 기존 0.1.0 자산은 교체하지 않는다. 실제 CAD 호환성과 DWG 변환 수용 결과는 별도 검증한다.

## 자가점검 회고

공개 배포 경계에서 독립 읽기 전용 검수와 자산 재다운로드 검증을 수행했다. 제품 코드의 추정 복구와 재빌드 주장은 하지 않았다. 부모 저장소와 기존 공개 프로젝트, 고객 자료 및 원본 폴더를 수정하지 않았다.
