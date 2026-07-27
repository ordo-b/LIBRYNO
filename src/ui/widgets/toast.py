"""Widget de notificação toast (popup flutuante)."""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer


class ToastNotification(QtWidgets.QLabel):
    """Notificação toast que aparece e desaparece automaticamente."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(92, 225, 230, 0.95);
                color: #1a1a2e;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.fade_out)

    def show_toast(self, message: str, duration_ms: int = 3000):
        self.setText(message)
        self.adjustSize()
        if self.parent():
            pw = self.parent().width()
            ph = self.parent().height()
            self.move(
                (pw - self.width()) // 2,
                ph - self.height() - 40,
            )
        self.show()
        self.raise_()
        self._timer.start(duration_ms)

    def fade_out(self):
        self.hide()
