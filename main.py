import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QSlider, QLineEdit,
                               QMessageBox, QLabel)
from PySide6.QtCore import QTimer, Qt, QEvent, QPoint
from PySide6.QtWebEngineWidgets import QWebEngineView


class AutoClosingMessageBox(QMessageBox):
    def __init__(self, text, caption, timeout=2500):
        super().__init__()
        self.setWindowTitle(caption)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok)
        QTimer.singleShot(timeout, self.close)

    @staticmethod
    def show(text, caption, timeout=2500):
        mb = AutoClosingMessageBox(text, caption, timeout)
        mb.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("재획용")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("#titleBar { background-color: #2c2c2c; }")
        self.title_bar.installEventFilter(self)

        top = QHBoxLayout(self.title_bar)
        top.setContentsMargins(8, 4, 8, 4)
        top.setSpacing(4)

        self.timer_input = QLineEdit("30")
        self.timer_input.setFixedWidth(60)
        top.addWidget(self.timer_input)

        btn_timer = QPushButton("타이머")
        btn_timer.clicked.connect(self.start_timer)
        top.addWidget(btn_timer)

        btn_google = QPushButton("Google")
        btn_google.clicked.connect(lambda: self.webview.setUrl("https://www.google.com"))
        top.addWidget(btn_google)

        btn_youtube = QPushButton("YouTube")
        btn_youtube.clicked.connect(lambda: self.webview.setUrl("https://www.youtube.com"))
        top.addWidget(btn_youtube)

        btn_chzzk = QPushButton("치지직")
        btn_chzzk.clicked.connect(lambda: self.webview.setUrl("https://chzzk.naver.com"))
        top.addWidget(btn_chzzk)

        btn_netflix = QPushButton("Netflix")
        btn_netflix.clicked.connect(lambda: self.webview.setUrl("https://www.netflix.com"))
        top.addWidget(btn_netflix)

        top.addStretch()

        lbl_opacity = QLabel("투명도")
        top.addWidget(lbl_opacity)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(15, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setSingleStep(5)
        self.opacity_slider.setFixedWidth(100)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        top.addWidget(self.opacity_slider)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.clicked.connect(self.close)
        top.addWidget(btn_close)

        layout.addWidget(self.title_bar)

        self.webview = QWebEngineView()
        self.webview.setUrl("https://www.google.com")
        layout.addWidget(self.webview)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_tick)
        self.timer_duration = 0

        self.dragging = False
        self.drag_pos = QPoint()

        self.resize(821, 595)

    def change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)

    def eventFilter(self, obj, event):
        if obj is self.title_bar:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.dragging = True
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_pos)
                return True
            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.dragging = False
                return True
        return super().eventFilter(obj, event)

    def start_timer(self):
        try:
            duration = int(self.timer_input.text())
            if 0 < duration < 121:
                self.timer_duration = duration
                self.timer.start(duration * 60000)
            elif duration == 141:
                QMessageBox.information(self, "어허", "어허")
            else:
                QMessageBox.warning(self, "오류", "1부터 120까지 숫자를 입력하세요.")
        except ValueError:
            QMessageBox.warning(self, "오류", "숫자를 입력하세요.")

    def timer_tick(self):
        self.timer.stop()
        AutoClosingMessageBox.show(
            f"{self.timer_duration}분이 경과했습니다.", "알림", 2500
        )

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
