"""Tela de Login - Integrada com OrdoB API."""
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.auth.license import check_existing_license
from src.auth.ordob_client import client
from src.auth.session import session
from src.config import Config
from src.ui.i18n.translator import t


class LoginScreen(QMainWindow):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle(t("login.title"))
        self.setFixedSize(700, 450)
        self.setWindowIcon(QtGui.QIcon(Config.resource_path("img/icon.png")))
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        left = QFrame()
        left.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16213e, stop:1 #0f3460);
                border-radius: 0px;
            }
        """)
        left_layout = QVBoxLayout(left)
        left_layout.setAlignment(Qt.AlignCenter)

        logo = QLabel("📚")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 64px; background: transparent;")
        left_layout.addWidget(logo)

        app_name = QLabel("LIBRYNO")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #5CE1E6; "
            "background: transparent; margin-top: 10px;"
        )
        left_layout.addWidget(app_name)

        subtitle = QLabel(t("login.login_with_ordob"))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            "font-size: 14px; color: #a0a0a0; background: transparent;"
        )
        left_layout.addWidget(subtitle)

        layout.addWidget(left, 1)

        right = QFrame()
        right.setStyleSheet("QFrame { background-color: #1a1a2e; }")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(40, 60, 40, 40)
        right_layout.setSpacing(16)

        title = QLabel(t("login.title"))
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #ffffff; "
            "background: transparent; margin-bottom: 10px;"
        )
        right_layout.addWidget(title)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText(t("login.email"))
        self.input_email.setFixedHeight(44)
        right_layout.addWidget(self.input_email)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText(t("login.password"))
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setFixedHeight(44)
        self.input_pass.returnPressed.connect(self._do_login)
        right_layout.addWidget(self.input_pass)

        right_layout.addSpacing(10)

        btn_login = QPushButton(t("login.enter"))
        btn_login.setFixedHeight(44)
        btn_login.clicked.connect(self._do_login)
        right_layout.addWidget(btn_login)

        btn_register = QPushButton(t("login.register"))
        btn_register.setFixedHeight(44)
        btn_register.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: #5CE1E6;
            }
            QPushButton:hover { background-color: #1a4a80; }
        """)
        btn_register.clicked.connect(self._do_register)
        right_layout.addWidget(btn_register)

        right_layout.addStretch()

        version = QLabel(f"v{Config.APP_VERSION}")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #666666; font-size: 11px; background: transparent;")
        right_layout.addWidget(version)

        layout.addWidget(right, 1)

    def _do_login(self):
        email = self.input_email.text().strip()
        password = self.input_pass.text().strip()

        if not email or not password:
            QMessageBox.warning(self, t("messages.warning"), t("messages.fields_required"))
            return

        result = client.login(email, password)
        if result:
            token = result.get("token", "")
            user = result.get("user", {})
            session.login(token, user)

            if client.health_check():
                check_existing_license()

            QMessageBox.information(self, t("messages.success"), t("login.success"))
            self.close()
            if self.on_success:
                self.on_success()
        else:
            QMessageBox.critical(self, t("messages.error"), t("login.error"))

    def _do_register(self):
        self.register_screen = RegisterScreen(self)
        self.register_screen.show()
        self.hide()

    def closeEvent(self, event):
        if not session.is_authenticated:
            reply = QMessageBox.question(
                self, "Sair", "Deseja realmente sair?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class RegisterScreen(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_screen = parent
        self.setWindowTitle(t("register.title"))
        self.setFixedSize(850, 550)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        title = QLabel(t("register.title"))
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #5CE1E6;")
        layout.addWidget(title)

        form = QHBoxLayout()
        form.setSpacing(20)

        left_form = QVBoxLayout()
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(t("register.name"))
        self.input_name.setFixedHeight(40)
        left_form.addWidget(self.input_name)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText(t("register.email"))
        self.input_email.setFixedHeight(40)
        left_form.addWidget(self.input_email)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText(t("register.password"))
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedHeight(40)
        left_form.addWidget(self.input_password)

        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText(t("register.confirm_password"))
        self.input_confirm.setEchoMode(QLineEdit.Password)
        self.input_confirm.setFixedHeight(40)
        left_form.addWidget(self.input_confirm)

        form.addLayout(left_form, 1)

        right_form = QVBoxLayout()
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText(t("register.phone"))
        self.input_phone.setFixedHeight(40)
        right_form.addWidget(self.input_phone)

        self.input_company = QLineEdit()
        self.input_company.setPlaceholderText(t("register.company"))
        self.input_company.setFixedHeight(40)
        right_form.addWidget(self.input_company)

        self.input_doc = QLineEdit()
        self.input_doc.setPlaceholderText(t("register.document"))
        self.input_doc.setFixedHeight(40)
        right_form.addWidget(self.input_doc)

        right_form.addStretch()
        form.addLayout(right_form, 1)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_back = QPushButton(t("register.back"))
        btn_back.setStyleSheet("QPushButton { background-color: #0f3460; color: #5CE1E6; }")
        btn_back.clicked.connect(self._go_back)
        btn_row.addWidget(btn_back)

        btn_row.addStretch()

        btn_register = QPushButton(t("register.register"))
        btn_register.setFixedWidth(200)
        btn_register.clicked.connect(self._do_register)
        btn_row.addWidget(btn_register)

        layout.addLayout(btn_row)

    def _do_register(self):
        name = self.input_name.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        confirm = self.input_confirm.text().strip()
        phone = self.input_phone.text().strip()
        company = self.input_company.text().strip()
        doc = self.input_doc.text().strip()

        if not name or not email or not password:
            QMessageBox.warning(self, t("messages.warning"), t("messages.fields_required"))
            return
        if password != confirm:
            QMessageBox.warning(self, t("messages.warning"), t("register.error"))
            return

        result = client.register(name, email, password, phone, company, doc)
        if result:
            QMessageBox.information(self, t("messages.success"), t("register.success"))
            self._go_back()
        else:
            QMessageBox.critical(self, t("messages.error"), t("register.error"))

    def _go_back(self):
        self.close()
        if self.parent_screen:
            self.parent_screen.show()
