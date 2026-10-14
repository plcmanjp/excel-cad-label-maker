# 아이콘 자산

흰 라벨지에 ABC가 적힌 앱 아이콘입니다.

- [PNG](../../project/src/assets/app-icon.png): 투명 배경 이미지
- [ICO](../../project/src/assets/app-icon.ico): 16, 20, 24, 32, 40, 48, 64, 96, 128, 256px 프레임을 포함한 Windows 아이콘
- [자산 정보](../../project/src/assets/manifest.json): 파일 SHA-256과 프레임 크기

ICO는 EXE 리소스와 Tk 창 아이콘에 사용됩니다. 저장된 PNG를 ICO로 변환하려면 저장소 루트에서 다음 명령을 실행하세요.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/make-app-icon.ps1 -Force
~~~
