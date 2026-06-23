import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QSlider, QLineEdit,
                               QMessageBox, QLabel, QFrame, QMenu)
from PySide6.QtCore import QTimer, Qt, QSettings
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView


# 일정 시간이 지나면 자동으로 닫히는 메시지 박스
class AutoClosingMessageBox(QMessageBox):
    def __init__(self, text, caption, timeout=2500):
        super().__init__()
        self.setWindowTitle(caption)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok)
        QTimer.singleShot(timeout, self.close)  # timeout(ms) 후 자동 종료

    @staticmethod
    def show(text, caption, timeout=2500):
        mb = AutoClosingMessageBox(text, caption, timeout)
        mb.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("재획용")
        # 항상 위에 고정 (다른 창에 가려지지 않음)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # 북마크 버튼 리스트 (__init__ 초반에 선언만)
        self.bookmark_buttons: list = []

        # 전체 창을 세로로 분할: 상단(title_bar) + 웹뷰
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === 상단 툴바 (타이머 + 사이트 버튼 + URL 입력 + 투명도) ===
        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("""
            #titleBar { background-color: #2c2c2c; }
            QLabel { color: white; }
            QLineEdit { color: white; background-color: #3c3c3c; }
        """)
        self.title_bar.setMaximumHeight(36)

        top = QHBoxLayout(self.title_bar)
        top.setContentsMargins(4, 2, 4, 2)
        top.setSpacing(2)

        # -- 카운트다운 타이머 --
        lbl_timer = QLabel("타이머")
        lbl_timer.setMaximumHeight(24)
        top.addWidget(lbl_timer)

        self.timer_input = QLineEdit("30")  # 기본 30분
        self.timer_input.setFixedWidth(45)
        self.timer_input.setMaximumHeight(24)
        top.addWidget(self.timer_input)

        self.btn_timer = QPushButton("시작")
        self.btn_timer.setMaximumWidth(40)
        self.btn_timer.setMaximumHeight(24)
        self.btn_timer.clicked.connect(self.start_timer)
        top.addWidget(self.btn_timer)

        self.timer_label = QLabel("")  # 남은 시간 표시 (예: 28:45)
        self.timer_label.setMaximumHeight(24)
        top.addWidget(self.timer_label)

        # 구분선 (타이머 영역 | 사이트 영역)
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setMaximumWidth(2)
        top.addWidget(sep)

        # -- 사이트 바로가기 버튼 --
        btn_google = QPushButton("Google")
        btn_google.setMaximumWidth(50)
        btn_google.setMaximumHeight(24)
        btn_google.clicked.connect(lambda: self.webview.setUrl("https://www.google.com"))
        top.addWidget(btn_google)

        btn_youtube = QPushButton("youtube")
        btn_youtube.setMaximumWidth(55)
        btn_youtube.setMaximumHeight(24)
        btn_youtube.clicked.connect(lambda: self.webview.setUrl("https://www.youtube.com"))
        top.addWidget(btn_youtube)

        btn_chzzk = QPushButton("Chzzk")
        btn_chzzk.setMaximumWidth(45)
        btn_chzzk.setMaximumHeight(24)
        btn_chzzk.clicked.connect(lambda: self.webview.setUrl("https://chzzk.naver.com"))
        top.addWidget(btn_chzzk)

        btn_netflix = QPushButton("Netflix")
        btn_netflix.setMaximumWidth(55)
        btn_netflix.setMaximumHeight(24)
        btn_netflix.clicked.connect(lambda: self.webview.setUrl("https://www.netflix.com"))
        top.addWidget(btn_netflix)

        # -- 사용자가 저장한 북마크 버튼들 --
        self.bookmark_container = QWidget()
        self.bookmark_layout = QHBoxLayout(self.bookmark_container)
        self.bookmark_layout.setContentsMargins(0, 0, 0, 0)
        self.bookmark_layout.setSpacing(2)
        top.addWidget(self.bookmark_container)

        # -- 직접 URL 입력 --
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL 입력")
        self.url_input.setMaximumHeight(24)
        self.url_input.returnPressed.connect(self.navigate_to_url)  # 엔터키로 이동
        top.addWidget(self.url_input)

        btn_go = QPushButton("이동")
        btn_go.setMaximumHeight(24)
        btn_go.clicked.connect(self.navigate_to_url)
        top.addWidget(btn_go)

        self.load_bookmarks()  # 저장된 북마크 불러와서 버튼 생성

        # 오른쪽 영역: 투명도 조절 + 닫기 버튼
        top.addStretch()

        lbl_opacity = QLabel("투명도")
        top.addWidget(lbl_opacity)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(15, 100)  # 15% ~ 100%
        self.opacity_slider.setValue(100)
        self.opacity_slider.setSingleStep(5)
        self.opacity_slider.setFixedWidth(70)
        self.opacity_slider.setMaximumHeight(20)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        top.addWidget(self.opacity_slider)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.clicked.connect(self.close)
        top.addWidget(btn_close)

        layout.addWidget(self.title_bar)

        # === 웹 브라우저 영역 ===
        self.webview = QWebEngineView()
        self.webview.setUrl("https://www.google.com")  # 시작 페이지
        layout.addWidget(self.webview)

        # 1초마다 timer_tick 실행 (카운트다운용)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_tick)
        self.remaining_seconds = 0  # 남은 초
        self.timer_minutes = 0      # 원래 설정한 분 (알림 메시지용)

        self.resize(1000, 600)

    # 슬라이더 값(15~100)을 0.15~1.0 비율로 창 투명도에 반영
    def change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)

    # 타이머 시작 / 중지 (버튼 토글)
    def start_timer(self):
        if self.timer.isActive():
            # 실행 중이면 중지
            self.timer.stop()
            self.btn_timer.setText("시작")
            self.timer_label.setText("")
            return

        try:
            minutes = int(self.timer_input.text())
            if 1 <= minutes <= 120:
                # 분 → 초 변환, 1초 간격 타이머 시작
                self.remaining_seconds = minutes * 60
                self.timer_minutes = minutes
                self.timer_label.setText(self._format_time(self.remaining_seconds))
                self.btn_timer.setText("중지")
                self.timer.start(1000)  # 1000ms = 1초마다 tick
            else:
                AutoClosingMessageBox.show("1부터 120까지 숫자를 입력하세요.", "오류", 2000)
        except ValueError:
            AutoClosingMessageBox.show("숫자를 입력하세요.", "오류", 2000)

    # 1초마다 호출, 남은 시간 감소 및 UI 갱신
    def timer_tick(self):
        if self.remaining_seconds <= 0:
            return  # 이미 종료된 타이머의 잔여 tick 무시

        self.remaining_seconds -= 1
        self.timer_label.setText(self._format_time(self.remaining_seconds))

        if self.remaining_seconds == 0:
            self.timer.stop()
            self.btn_timer.setText("시작")
            self.timer_label.setText("")
            AutoClosingMessageBox.show(
                f"{self.timer_minutes}분이 경과했습니다.", "알림", 2500
            )

    # 초 → "MM:SS" 형식 변환
    @staticmethod
    def _format_time(seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    # URL 입력창의 주소로 이동 + 북마크 저장
    def navigate_to_url(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if " " in url:
            AutoClosingMessageBox.show("올바른 URL을 입력하세요.", "오류", 2000)
            return
        # http:// 없으면 자동 추가
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.webview.setUrl(url)
        self.save_bookmark(url)
        self.url_input.clear()

    # 북마크 우클릭 메뉴
    def _show_bookmark_menu(self, pos, url):
        menu = QMenu()
        menu.addAction("삭제", lambda: self._delete_bookmark(url))
        menu.exec(self.bookmark_container.mapToGlobal(pos))

    # 북마크 삭제
    def _delete_bookmark(self, url):
        settings = QSettings("JaehoekYong", "JaehoekYong")
        bookmarks = settings.value("bookmarks", []) or []
        if url in bookmarks:
            bookmarks.remove(url)
        settings.setValue("bookmarks", bookmarks)
        self.rebuild_bookmark_buttons()

    # QSettings(레지스트리)에 북마크 저장 (최대 3개, 최신순)
    def save_bookmark(self, url):
        settings = QSettings("JaehoekYong", "JaehoekYong")
        bookmarks = settings.value("bookmarks", []) or []
        if url in bookmarks:
            bookmarks.remove(url)   # 중복 제거 후 맨 앞으로
        bookmarks.insert(0, url)
        if len(bookmarks) > 3:
            bookmarks = bookmarks[:3]
        settings.setValue("bookmarks", bookmarks)
        self.rebuild_bookmark_buttons()

    # 프로그램 시작 시 저장된 북마크 불러오기
    def load_bookmarks(self):
        settings = QSettings("JaehoekYong", "JaehoekYong")
        bookmarks = settings.value("bookmarks", []) or []
        self._create_bookmark_buttons(bookmarks)

    # 북마크 버튼 전체 갱신 (기존 버튼 제거 → 다시 생성)
    def rebuild_bookmark_buttons(self):
        for btn in self.bookmark_buttons:
            self.bookmark_layout.removeWidget(btn)
            btn.deleteLater()
        self.bookmark_buttons.clear()

        settings = QSettings("JaehoekYong", "JaehoekYong")
        bookmarks = settings.value("bookmarks", []) or []
        self._create_bookmark_buttons(bookmarks)

    # 북마크 목록을 버튼으로 생성 (도메인만 표시, 18자 제한)
    def _create_bookmark_buttons(self, bookmarks):
        self.bookmark_buttons.clear()
        for url in bookmarks:
            display = url.replace("https://", "").replace("http://", "").split("/")[0]
            if len(display) > 18:
                display = display[:16] + ".."
            btn = QPushButton(display)
            btn.setMaximumHeight(24)
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.clicked.connect(lambda checked, u=url: self.webview.setUrl(u))
            btn.customContextMenuRequested.connect(
                lambda pos, u=url: self._show_bookmark_menu(pos, u))
            self.bookmark_layout.addWidget(btn)
            self.bookmark_buttons.append(btn)

    # 창 닫을 때 타이머 정리
    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 다크 테마 적용 (Fusion 스타일 + 어두운 색상 팔레트)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#2c2c2c"))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor("#3c3c3c"))       # 입력창 배경
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor("#3c3c3c"))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor("#4a9eff"))  # 강조 파랑
    palette.setColor(QPalette.ToolTipBase, QColor("#2c2c2c"))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
