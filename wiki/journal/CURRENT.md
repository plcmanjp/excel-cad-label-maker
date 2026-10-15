# 작업 저널 (CURRENT)

## 목표

- MIT와 Arial 기본값을 포함한 0.4.1의 정식 배포를 완료하고 남은 현장 검증 범위를 유지한다.

## 현재 상태

- [PR #25](https://github.com/plcmanjp/excel-cad-label-maker/pull/25)를 main의 673d7a6에 병합했고 #24와 #26은 CLOSED다. [v0.4.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.1)은 정식 latest이며 공개 ZIP/체크섬을 재다운로드해 byte 일치를 확인했다.
- 소스 권리 양도에 대한 관리자의 명시적 확인을 근거로 MIT를 적용했다. GitHub도 MIT로 인식한다. 원개발자 직장인과 외부 고지는 유지하며 보관 원본 EXE 0.1.0은 새 MIT 선언에서 제외한다. 계약의 법적 효력을 독립 감정했다고 표현하지 않는다.
- 원격과 두 독립 checkout은 main을 사용한다. 원래 OneDrive checkout의 예상 밖 변경과 중복 worktree는 보존 상태이며 정리/동기화 완료로 판정하지 않는다.

## 주요 결정

- LICENSE.txt는 저장소 LICENSE와 byte 일치해야 하며 누락/변조/충돌한 배포물은 거부한다. 새 설정은 Arial이고 기존 마지막 설정/프리셋의 명시적 글꼴은 보존한다.
- tag v0.4.1과 공개 자산의 제품 commit은 673d7a6이다. 이후 내부 결과 기록 commit은 tag와 공개 자산을 바꾸지 않는다.

## 검증 결과

- [배포 결과](../../../project/qc/release041-results.json): 제품 128개, 하네스 22개, 원격 배포 보호 18개와 CI 및 독립 소스/실제 패키지 검수 PASS. 로컬 배포 보호는 17 PASS/1 symlink 권한 SKIP로 구분한다.
- fresh clean main 정식 ZIP의 1,130멤버와 LICENSE 원문/외부 고지 63개를 검증했다. 실제 EXE의 버전/Arial, 합성 한글 3라벨/8칸 입력과 DXF 저장/재읽기, ARIAL 스타일과 문자/좌표 일치, 원본 불변 및 audit 오류/수정 0을 확인했다.
- 실제 이전 공개 0.4.0 EXE의 최신 0.4.1 알림과 키보드 닫기, 공개 tag/latest/본문/두 자산 및 재다운로드 byte 일치를 확인했다.

## 미해결 사항

- 실제 Explorer 간 드롭과 독립 AutoCAD 렌더링은 이번 artifact에서 미검증이다. 파일 선택 입력과 DXF 문자열/스타일 검증 및 사용자 CAD의 Arial/굴림 정상 보고를 별도 근거로 유지한다.
- #20의 초보 사용자/실제 OS 배율과 #14의 CAD/별도 PC/원본 빌드 대응이 OPEN이다. #14의 소스 권리 조건은 관리자 확인과 MIT 적용 범위로 갱신했다.
- 원래 OneDrive checkout은 변경 소유권과 중복 worktree 및 복구 자료 확인 후에만 동기화/정리를 재개한다.

## 다음 작업

1. #20의 실제 사용자와 OS 배율 및 Explorer 드롭을 확인한다.
2. #14의 CAD/별도 PC/원본 빌드 대응을 해당 환경의 근거로 확인한다.
3. 원래 OneDrive checkout의 예상 밖 변경을 보존하면서 복구 범위를 확정한다.
