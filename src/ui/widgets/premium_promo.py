"""Widget de promoção Premium — toast elegante e não-intrusivo.

Características:
- Aparece como toast no canto inferior direito
- Botão X para fechar (nunca bloqueia)
- Botão "Ver Planos" que abre ordob.com/libryno
- Auto-desaparece após 15 segundos
- Design elegante com gradiente dourado
"""
import webbrowser

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PremiumPromoToast(QWidget):
    """Toast de promoção Premium — flutuante, dismissável."""

    PLANS_URL = "https://ordob.com/libryno"

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(380)
        self._build_ui()
        self.hide()

        # Auto-hide timer
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)

    def _build_ui(self):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2a1f0a, stop:1 #1a1520);
                border: 1px solid #FFD700;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        icon = QLabel("⭐")
        icon.setStyleSheet("font-size: 20px; background: transparent;")
        header.addWidget(icon)

        title = QLabel("Desbloqueie o Premium")
        title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #FFD700; "
            "background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent; color: #888; border: none;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { color: #FFD700; }
        """)
        btn_close.clicked.connect(self.fade_out)
        header.addWidget(btn_close)

        layout.addLayout(header)

        # Message
        self._msg_label = QLabel()
        self._msg_label.setWordWrap(True)
        self._msg_label.setStyleSheet(
            "font-size: 12px; color: #cccccc; background: transparent; "
            "line-height: 1.4;"
        )
        layout.addWidget(self._msg_label)

        # Feature highlights
        self._features_label = QLabel()
        self._features_label.setWordWrap(True)
        self._features_label.setStyleSheet(
            "font-size: 11px; color: #a0a0a0; background: transparent; "
            "margin-top: 4px;"
        )
        layout.addWidget(self._features_label)

        # Buttons
        btn_layout = QHBoxLayout()

        btn_plans = QPushButton("💎 Ver Planos")
        btn_plans.setFixedHeight(32)
        btn_plans.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFD700, stop:1 #FFA500);
                color: #1a1a2e; border: none; border-radius: 6px;
                font-size: 12px; font-weight: bold; padding: 0 16px;
            }
            QPushButton:hover { background: #FFA500; }
        """)
        btn_plans.clicked.connect(self._open_plans)
        btn_layout.addWidget(btn_plans)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

    def show_promo(self, message: str, features: str = "", duration_ms: int = 15000):
        """Mostra o toast com mensagem personalizada."""
        self._msg_label.setText(message)
        if features:
            self._features_label.setText(features)
            self._features_label.show()
        else:
            self._features_label.hide()

        # Posicionar no canto inferior direito do parent
        if self.parent():
            pw = self.parent().width()
            self.move(pw - self.width() - 20, self.parent().height() - self.height() - 20)

        self.show()
        self.raise_()

        # Auto-hide
        self._hide_timer.start(duration_ms)

    def fade_out(self):
        """Animação de saída suave."""
        self._hide_timer.stop()
        self.hide()

    def _open_plans(self):
        """Abre a página de planos no OrdoB."""
        webbrowser.open(self.PLANS_URL)
        self.fade_out()

    def show_limit_reached(self, entity: str, count: int, limit: int):
        """Mostra promo quando limite está próximo."""
        self.show_promo(
            message=(
                f"📊 Você já tem {count}/{limit} {entity}.\n"
                f"Upgrade para Premium e tenha ilimitado!"
            ),
            features="✨ Ilimitado • 📈 Relatórios • 💾 Backup",
            duration_ms=12000,
        )

    def show_feature_gate(self, feature_name: str):
        """Mostra promo quando feature premium é bloqueada."""
        self.show_promo(
            message=(
                f"🔒 {feature_name} é um recurso Premium.\n"
                "Ative sua chave OrdoB para acessar."
            ),
            features="💎 Acesso completo por apenas R$ 19,90/mês",
            duration_ms=10000,
        )

    def show_import_teaser(self):
        """Mostra após primeira importação."""
        self.show_promo(
            message=(
                "📥 Importação concluída!\n"
                "Com Premium, você pode importar Excel e mucho más."
            ),
            features="📊 Excel • 📋 Templates • 🔄 Backup automático",
            duration_ms=10000,
        )

    def show_welcome_tip(self):
        """Mostra dica de boas-vindas após 5 min."""
        self.show_promo(
            message=(
                "💡 Dica: Você está usando o plano FREE.\n"
                "Desbloqueie todos os recursos com o Premium!"
            ),
            features="📖 Empréstimos • 📈 Relatórios • 📥 Importação",
            duration_ms=15000,
        )
