"""Detecção automática de tema do sistema operacional."""

try:
    import darkdetect
    HAS_DARKDETECT = True
except ImportError:
    HAS_DARKDETECT = False


def get_system_theme() -> str | None:
    """
    Detecta o tema do sistema operacional.
    Retorna 'dark' ou 'light', ou None se não detectado.
    """
    if not HAS_DARKDETECT:
        return None

    try:
        mode = darkdetect.theme()
        if mode == "Dark":
            return "dark"
        elif mode == "Light":
            return "light"
        return None
    except Exception:
        return None


def listen_system_theme(callback):
    """
    Callback chamado quando o tema do sistema muda.
    Requer darkdetect instalado.
    """
    if not HAS_DARKDETECT:
        return False

    try:
        darkdetect.listener(callback)
        return True
    except Exception:
        return False
