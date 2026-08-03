"""Bootstrap do aplicativo LIBRYNO v2.0."""
import sys
from PyQt5 import QtWidgets, QtGui
from src.config import Config
from src.core.migrations import setup_database
from src.core.seed import seed_demo_data
from src.ui.themes.theme_manager import apply_theme, get_current_theme
from src.ui.i18n.translator import set_locale, _load_locale
from src.auth.session import session
from src.auth.license import check_existing_license, start_license_monitoring, stop_license_monitoring
from src.auth.ordob_client import client
from src.ui.screens.login import LoginScreen
from src.ui.screens.home import HomeScreen
from src.utils.logger import logger


_sse_stop_event = None


def run():
    logger.info("LIBRYNO v{} starting...", Config.APP_VERSION)

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.APP_VERSION)
    app.setWindowIcon(QtGui.QIcon("img/icon.png"))

    _load_locale("pt_BR")
    _load_locale("en")
    set_locale("pt_BR")

    apply_theme(app, get_current_theme() or "dark")

    setup_database()
    seed_demo_data()

    if session.is_authenticated:
        logger.info("Existing session found, verifying license...")
        check_existing_license()
        start_license_monitoring()
        _start_realtime_notifications()
        home = HomeScreen()
        home.show()
    else:
        login = LoginScreen(on_success=lambda: _show_home(login))
        login.show()

    sys.exit(app.exec_())


def _show_home(login_screen):
    global _sse_stop_event
    home = HomeScreen(login_screen=login_screen)
    home.show()
    start_license_monitoring()
    _sse_stop_event = _start_realtime_notifications()


def _on_notification(data: dict):
    """Callback para notificações SSE em tempo real."""
    logger.info("SSE notification received: {}", data.get("type") or "unknown")
    try:
        from src.features.notifications import NotificationsCRUD
        if data.get("type") == "unread_count":
            count = data.get("data", 0)
            NotificationsCRUD.create(
                titulo="Nova notificação",
                mensagem=f"Você tem {count} notificação(s) não lida(s).",
                tipo="sse_alert",
            )
        elif "ticket" in str(data.get("type", "")):
            NotificationsCRUD.create(
                titulo="Atualização de ticket",
                mensagem=data.get("data", {}).get("message_preview", "Nova mensagem"),
                tipo="sse_ticket",
            )
    except Exception as e:
        logger.error("Error processing SSE notification: {}", e)


def _start_realtime_notifications():
    """Inicia streaming SSE de notificações em tempo real."""
    global _sse_stop_event
    if session.is_authenticated and session.token:
        try:
            _sse_stop_event = client.stream_notifications(
                token=session.token,
                on_message=_on_notification,
                on_error=_on_sse_error,
            )
            logger.info("Realtime notifications started")
        except Exception as e:
            logger.error("Failed to start SSE: {}", e)
    return _sse_stop_event


def _on_sse_error(error: str):
    """Callback de erro para SSE."""
    logger.warning("SSE error: {}", error)


def cleanup():
    """Cleanup ao encerrar aplicativo."""
    stop_license_monitoring()
    if _sse_stop_event:
        _sse_stop_event.set()
    logger.info("LIBRYNO shutdown complete")
