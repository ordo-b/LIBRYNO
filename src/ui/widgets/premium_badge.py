"""Widget de badge premium/free."""
from PyQt5 import QtWidgets, QtCore


class PremiumBadge(QtWidgets.QLabel):
    """Badge que mostra status Premium/Free."""

    def __init__(self, is_premium: bool = False, parent=None):
        super().__init__(parent)
        self._premium = is_premium
        self.setFixedSize(90, 28)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.update_style()

    def set_premium(self, value: bool):
        self._premium = value
        self.update_style()

    def update_style(self):
        if self._premium:
            self.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FFD700, stop:1 #FFA500);
                    color: #1a1a2e;
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
            self.setText("★ PREMIUM")
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #0f3460;
                    color: #5CE1E6;
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
            self.setText("FREE")
