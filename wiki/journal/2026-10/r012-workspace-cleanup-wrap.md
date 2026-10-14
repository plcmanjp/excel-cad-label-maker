# r012 워크스페이스 청소와 세션 마무리

| 항목 | 값 |
|---|---|
| 문서리비전 | r012-workspace-cleanup-wrap |
| 작성일시 | 2026-10-14 17:55 (KST) |
| 작성모델 | GPT-6 (Codex) |
| 담당에이전트 | Codex Director와 읽기 전용 검수 Specialist |

## 요약

- 사용자 지시에 따라 완료한 QC 및 작업 부산물, 임시 빌드와 재생성 가능한 Python bytecode 캐시를 휴지통으로 옮겼다.
- 정확한 허용 목록577개, 파일23,772개, 1,502,120,015바이트를 정리했다. 원래 경로와 일치하는 휴지통577개 항목을 대조했고 미일치0개다.
- 병합 브랜치7개를 일반 삭제했다. 로컬 및 원격 main 하나, 등록 워크트리1개와 잔여 워크트리 메타데이터0개를 확인했다.

## 결정/판단 근거

- Git 추적 제외와 ignore, 실제 경로 포함 관계 및 조상과 하위 링크, 프로세스와 보존 경계 및 재생성 근거를 먼저 확인했다. 기존 cleanup 엔진의 고정 manifest가 이 저장소에는 없어 별도 허용 목록으로 관측했다. 스캔이 삭제 권한을 부여한다고 해석하지 않았다.
- 실행 직전 최초 목록과 파일 수 및 byte가 같아야 진행했고 symlink 및 junction과 cloud 이외 reparse tag를 거부했다. 각 휴지통 이동은 Microsoft.VisualBasic.FileIO의 명시적 SendToRecycleBin 4인수 호출을 사용했다. 광역 git clean과 영구 삭제 또는 권한 변경은 사용하지 않았다.
- 일회성 원시 QC 로그와 실행본 및 합성 파일은 정리했고 Git에 저장된 검사 요약과 원본 및 정식 배포 자산은 보존했다. 기존 QC 기록의 private_evidence는 완료 당시의 경로이며 원시 부산물은 이번 청소로 휴지통에 있다.

## 정리 범위

- .local의 완료 QC 폴더: centered-docs-qc, download-v0.1.0, drag-qc, flatten-qc, layout-qc, qc, release-qc, release-v021, runtime-qc, update-qc.
- .local의 임시 전송 및 조회 파일: commit-message.txt, completion-file.json, issue-files.json, issue2-before-rename.json, verify_registered.py.
- project/build와 project/dist.
- release/artifacts의 중복 출력: baseline-build, Excel_CAD_Label, flat-qc-d6ca19a, layout-qc-4971446, runtime-qc-3557071.
- 원본 .py가 있는 Python bytecode 캐시555개: .venv419개, uia-qc-env135개와 PyInstaller hook1개. 삭제 후 잔여0개다.

## 보존 범위

- 모든 Git 추적 파일, 원본 소스와 원본 EXE, 아이콘과 외부 법적 고지 및 기존 journal과 release QC.
- 정식 v0.1.0, v0.2.0, v0.2.1, v0.2.2의 ZIP과 체크섬. 청소 전후 보존 hash183개가 일치한다.
- .venv와 .local/uia-qc-env의 환경 본체. 원본 패키징이 사용하는 .local/baseline/Excel_Cad_Label.exe도 남긴다.

## 검증

- 독립 청소 계획 검수 PASS, 수정 필요 finding0개. 후보는 보존 대상과 겹치지 않았다.
- 휴지통 이동 로그와 실제577개 항목 및 원래 경로를 대조했다. 각 대상의 원래 경로가 없어졌고 보존 hash183개는 일치한다.
- 저장소 경로의 실행 프로세스0개. 검증 앱2개와 보이는 임시 Explorer2개를 정상 종료했다.
- 개발환경의 앱 및 빌드 의존성 import와 pip check PASS. 재사용 UIA 환경은 실제 pyvenv.cfg와 일치하는 Python3.13.15이며 pywinauto import PASS다.
- 저장소 구조와 링크 및 인코딩과 원본 provenance, 공개 문서 경계 검사 PASS. 제품 소스와 정식 배포 파일은 변경하지 않았다.
- branch7개 모두 origin/main의 조상임을 확인해 git branch -d로 삭제했다. 원격 refs/heads는 main만 존재하고 worktree prune dry-run의 잔여 항목은 없다.

## 커밋 (이번 세션)

- 기준 commit90cc7fe1d767aeb9fb5274d70a74053d8f04a05c에서 청소했고 제품 소스를 변경하지 않았다.
- 이 journal과 CURRENT의 마무리 기록은 별도 commit으로 main에 저장한다. 파일 삭제는 Git 추적 제외 자료에만 적용했다.

## 작업번호

- [Issue #19](https://github.com/plcmanjp/excel-cad-label-maker/issues/19): 워크스페이스 부산물과 병합 브랜치 정리 및 세션 마무리.

## 다음 우선순위

1. 새 작업 시 현재 main과 해당 Issue에서 시작한다. 필요할 때 빌드와 QC 부산물을 다시 생성한다.
2. Issue #14의 실제 CAD와 별도 PC 및 원본 대응과 이용 조건은 미검증 범위를 유지한다.

## 자가점검 회고

- 후보 관측과 독립 계획 검수, 실제 휴지통 이동 및 보존 대조를 별도 근거로 확인했다. 저장소 밖 자료와 다른 세션의 실행 환경을 청소 범위에 넣지 않았다.
- 기존 공개 자산과 원본, 재사용 환경은 유지하고 완료한 원시 부산물은 휴지통에서 복구할 수 있게 정리했다.
