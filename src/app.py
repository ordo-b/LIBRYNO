"""Bootstrap do aplicativo LIBRYNO v2.0."""
import sys
from PyQt5 import QtWidgets, QtGui
from src.config import Config
from src.core.migrations import setup_database
from src.core.seed import seed_demo_data
from src.ui.themes.theme_manager import apply_theme, get_current_theme
from src.ui.i18n.translator import set_locale, _load_locale
from src.auth.session import session
from src.auth.license import check_existing_license
from src.ui.screens.login import LoginScreen
from src.ui.screens.home import HomeScreen
from src.utils.logger import logger


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
        home = HomeScreen()
        home.show()
    else:
        login = LoginScreen(on_success=lambda: _show_home(login))
        login.show()

    sys.exit(app.exec_())


def _show_home(login_screen):
    home = HomeScreen(login_screen=login_screen)
    home.show()
