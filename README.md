# 재획용

[![Release](https://img.shields.io/badge/release-v1.0-blue?logo=github)](https://github.com/woid0309/webbrowser/releases/tag/v1.0)

PySide6 기반 웹 브라우저 + 카운트다운 타이머 오버레이 애플리케이션

## 기능

- **웹 브라우저**: Google, YouTube, 치지직(Chzzk), Netflix 버튼으로 바로 이동
- **URL 입력**: 직접 주소 입력 + 엔터 or [이동] 버튼으로 탐색
- **북마크**: 입력한 URL 자동 저장 (최대 3개), 우클릭으로 삭제
- **카운트다운 타이머**: 1~120분 설정, 실시간 MM:SS 표시, 시작/중지 토글
- **투명도**: 슬라이더로 창 투명도 조절 (15%~100%)
- **항상 위**: 다른 창 위에 고정 (WindowStaysOnTopHint)
- **다크 테마**: Fusion 스타일 + 어두운 색상 팔레트

## 실행

```bash
pip install -r requirements.txt
python main.py
```

## 빌드 (PyInstaller)

```bash
pip install pyinstaller
pyinstaller 재획용.spec
```

빌드 후: `dist/재획용/재획용.exe`
