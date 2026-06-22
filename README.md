# 재획용

[![GitHub](https://img.shields.io/badge/download-재획용_v1.0.zip-blue?logo=github)](https://github.com/woid0309/webbrowser/raw/main/재획용_v1.0.zip)

PySide6 기반 웹 브라우저 + 타이머 애플리케이션

## 기능

- **웹 브라우저**: Google, YouTube, 치지직, Netflix 버튼으로 바로 이동
- **타이머**: 1~120분 설정, 시간 경과 시 알림
- **투명도**: 슬라이더로 창 투명도 조절 (15%~100%)
- **항상 위**: 다른 창 위에 고정
- **테두리 없는 창**: 타이틀바 드래그로 이동, ✕ 버튼으로 닫기

## 실행

```bash
pip install -r requirements.txt
python main.py
```

## 다운로드

실행 파일이 포함된 zip 파일입니다. (Git LFS로 관리)

```bash
git lfs pull
```

또는 위 배지 링크를 클릭하여 직접 다운로드하세요.

## 빌드 (PyInstaller)

```bash
pip install pyinstaller
pyinstaller 재획용.spec
```

빌드 후: `dist/재획용/재획용.exe`
