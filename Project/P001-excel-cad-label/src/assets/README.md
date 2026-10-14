# 앱 아이콘

흰색 라벨지에 진한 ABC를 적은 Excel CAD Label Maker 개발 앱 아이콘입니다. [Issue #5](https://github.com/plcmanjp/excel-cad-label-maker/issues/5)의 사용자 지시로 생성했습니다.

- 생성 도구: 내장 `image_gen`, CLI 또는 API 키를 사용하지 않았습니다.
- `app-icon.png`: 생성된 투명 배경 PNG 원본입니다. 흰색 라벨은 불투명합니다.
- `app-icon.ico`: PNG 프레임을 담은 16, 20, 24, 32, 40, 48, 64, 96, 128, 256px Windows 아이콘입니다.
- `manifest.json`: 원본과 ICO의 SHA-256 및 프레임 크기를 기록합니다.

ICO 변환은 Windows의 System.Drawing을 사용하는 `scripts/make-app-icon.ps1`로 재현합니다. 이미지의 내용은 바꾸지 않고 크기와 형식을 변환합니다. 추가 Python 패키지는 필요하지 않습니다.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/make-app-icon.ps1 -Force
~~~

ICO는 PyInstaller EXE 리소스 및 `_internal/assets/`에 포함되고 Tk 창의 기본 아이콘으로 사용됩니다. 원본 0.1.0 EXE에는 적용하지 않습니다.

## 최종 생성 프롬프트

~~~text
Use case: logo-brand
Asset type: Windows desktop app icon for an Excel-to-CAD duct label maker.
Primary request: a simple white label paper with the exact text "ABC" prominently printed on it, symbolic of making labels.
Subject: one clean white rectangular adhesive label sheet, rounded corners, subtle paper thickness and a very small lifted corner. No additional objects.
Style: polished, restrained desktop application icon, clean bold silhouette, crisp high contrast, almost flat with slight edge depth, no busy texture.
Composition: square 1024x1024 canvas, centered label filling about 86 percent of width and 70 percent of height, nearly front-facing with only minimal perspective. Safe transparent margin. The label is white and has a clear medium gray edge so it stays visible on a light desktop.
Text (verbatim): "ABC". Exactly three uppercase letters A B C, centered across the white label. Large bold simple sans-serif type in near-black, thick strokes, perfectly legible, text occupies most of the label. No other text.
Background: genuinely transparent alpha, no colored tile or background, no checkerboard baked into pixels.
Constraints: Readable as a 16 to 32 pixel application icon. No Microsoft/Excel logos, no CAD logos, no watermark, no tiny details, no extra symbols. White paper must remain opaque.
~~~
