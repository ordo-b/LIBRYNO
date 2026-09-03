"""Autenticação Google OAuth para desktop via servidor local.

Fluxo:
1. Servidor local escuta em porta aleatória
2. Abre Google OAuth no navegador (via OrdoB)
3. Após auth, Google redireciona para OrdoB
4. OrdoB processa e redireciona para ordob.com
5. Usuário copia token da página e cola no app

Alternativa: servidor local captura callback se OrdoB suportar redirect customizado.
"""
import json
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode

from src.auth.ordob_client import client
from src.utils.logger import logger

# URL do Google OAuth via OrdoB
ORDOB_GOOGLE_AUTH_URL = "https://api.ordob.com/api/v1/auth/google"
ORDOB_LOGIN_URL = "https://ordob.com/login"
ORDOB_CADASTRO_URL = "https://ordob.com/cadastro"


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler para capturar callback do OAuth."""

    token_received = None  # threading.Event
    received_token = None  # list para armazenar token

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "token" in params:
            _OAuthCallbackHandler.received_token[0] = params["token"][0]
            _OAuthCallbackHandler.token_received.set()
            self._respond_ok("✅ Autenticado! Voltando ao Libryno...")
        elif "access_token" in params:
            _OAuthCallbackHandler.received_token[0] = params["access_token"][0]
            _OAuthCallbackHandler.token_received.set()
            self._respond_ok("✅ Autenticado! Voltando ao Libryno...")
        elif "code" in params:
            # Temos um code, mas precisamos trocar por token
            _OAuthCallbackHandler.received_token[0] = f"code:{params['code'][0]}"
            _OAuthCallbackHandler.token_received.set()
            self._respond_ok("✅ Código recebido! Processando...")
        else:
            self._respond_error("Parâmetro 'token' não encontrado na URL.")

    def _respond_ok(self, message: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Libryno - Autenticado</title>
<style>
body {{ background: #1a1a2e; color: #5CE1E6; font-family: sans-serif;
       display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
.box {{ text-align: center; padding: 40px; }}
h1 {{ font-size: 48px; }}
p {{ font-size: 18px; color: #a0a0a0; }}
</style></head>
<body><div class="box"><h1>✅</h1><p>{message}</p></div></body></html>"""
        self.wfile.write(html.encode("utf-8"))

    def _respond_error(self, message: str):
        self.send_response(400)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Libryno - Erro</title>
<style>
body {{ background: #1a1a2e; color: #ff4444; font-family: sans-serif;
       display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
.box {{ text-align: center; padding: 40px; }}
</style></head>
<body><div class="box"><h1>❌</h1><p>{message}</p></div></body></html>"""
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP


class GoogleOAuthManager:
    """Gerencia fluxo Google OAuth para desktop."""

    def __init__(self):
        self._server = None
        self._thread = None
        self._port = None
        self._stop_event = threading.Event()

    def start_server(self, timeout: int = 120) -> tuple[bool, str]:
        """Inicia servidor local e abre Google OAuth.

        Retorna (sucesso, token_ou_erro).
        """
        import socket

        # Encontrar porta disponível
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        self._port = sock.getsockname()[1]
        sock.close()

        # Configurar handler
        _OAuthCallbackHandler.token_received = threading.Event()
        _OAuthCallbackHandler.received_token = [None]

        # Criar servidor
        self._server = HTTPServer(("localhost", self._port), _OAuthCallbackHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

        logger.info("OAuth server started on port {}", self._port)

        # Abrir Google OAuth no navegador via OrdoB
        webbrowser.open(ORDOB_GOOGLE_AUTH_URL)

        # Esperar token ou timeout
        _OAuthCallbackHandler.token_received.wait(timeout=timeout)

        # Parar servidor
        self._server.shutdown()
        self._server.server_close()

        token = _OAuthCallbackHandler.received_token[0]
        if token:
            logger.info("OAuth token received")
            return True, token
        else:
            logger.warning("OAuth timeout - no token received")
            return False, "Tempo esgotado. Tente novamente."

    def get_auth_url(self) -> str:
        """Retorna URL de autenticação Google via OrdoB."""
        return ORDOB_GOOGLE_AUTH_URL

    def get_login_url(self) -> str:
        """Retorna URL de login OrdoB."""
        return ORDOB_LOGIN_URL

    def get_cadastro_url(self) -> str:
        """Retorna URL de cadastro OrdoB."""
        return ORDOB_CADASTRO_URL


# Instância global
google_auth = GoogleOAuthManager()
