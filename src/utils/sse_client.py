"""Cliente SSE (Server-Sent Events) para notificações em tempo real."""
import threading
import time
import requests
from typing import Callable, Optional
from src.utils.logger import logger


class SSEClient:
    """
    Cliente SSE que mantém conexão com o servidor para receber
    notificações em tempo real, com reconexão automática.
    """

    HEARTBEAT_TIMEOUT = 45
    RECONNECT_DELAY = 5
    MAX_RECONNECT_DELAY = 60

    def __init__(
        self,
        base_url: str,
        token: str,
        endpoint: str,
        on_message: Callable,
        on_error: Optional[Callable] = None,
    ):
        self.base_url = base_url
        self.token = token
        self.endpoint = endpoint
        self.on_message = on_message
        self.on_error = on_error
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_heartbeat = time.time()
        self._delay = self.RECONNECT_DELAY

    def start(self) -> threading.Event:
        """Inicia o listener SSE em uma thread separada."""
        if self._thread is not None and self._thread.is_alive():
            return self._stop_event

        self._thread = threading.Thread(
            target=self._listen,
            daemon=True,
            name="SSEListener",
        )
        self._thread.start()
        logger.info("SSE listener started for endpoint: {}", self.endpoint)
        return self._stop_event

    def _listen(self):
        """Loop principal do listener SSE."""
        url = f"{self.base_url}{self.endpoint}?token={self.token}"
        headers = {
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self.token}",
            "Cache-Control": "no-cache",
        }

        while not self._stop_event.is_set():
            try:
                with requests.get(
                    url,
                    headers=headers,
                    stream=True,
                    timeout=(10, 30),
                ) as resp:
                    if resp.status_code != 200:
                        logger.error("SSE connection failed: {} - {}",
                                     resp.status_code, resp.text[:100])
                        self._safe_error(f"HTTP {resp.status_code}")
                        continue

                    self._delay = self.RECONNECT_DELAY
                    self._last_heartbeat = time.time()
                    logger.info("SSE connected, listening for events...")

                    for line in resp.iter_lines(decode_unicode=True):
                        if self._stop_event.is_set():
                            break

                        if not line:
                            continue

                        self._last_heartbeat = time.time()

                        if line.startswith("data:"):
                            data = line[5:].strip()
                            if data and data != ": heartbeat":
                                try:
                                    import json
                                    parsed = json.loads(data)
                                    self._safe_message(parsed)
                                except json.JSONDecodeError:
                                    self._safe_message({"raw": data})
                        elif line.startswith("event:"):
                            event_type = line[6:].strip()
                            logger.debug("SSE event: {}", event_type)

                        if line.startswith(":"):
                            logger.debug("SSE heartbeat received")

            except requests.exceptions.RequestException as e:
                logger.warning("SSE connection error: {}, reconnecting in {}s",
                               e, self._delay)
                self._safe_error(str(e))
                self._delay = min(self._delay * 2, self.MAX_RECONNECT_DELAY)
            except Exception as e:
                logger.error("SSE unexpected error: {}", e)
                self._safe_error(str(e))
                self._delay = min(self._delay * 2, self.MAX_RECONNECT_DELAY)

            if not self._stop_event.is_set():
                self._stop_event.wait(self._delay)

    def _safe_message(self, data: dict):
        """Chama on_message com tratamento de exceções."""
        if self.on_message:
            try:
                self.on_message(data)
            except Exception as e:
                logger.error("Error in SSE on_message callback: {}", e)

    def _safe_error(self, error: str):
        """Chama on_error com tratamento de exceções."""
        if self.on_error:
            try:
                self.on_error(error)
            except Exception as e:
                logger.error("Error in SSE on_error callback: {}", e)

    def stop(self):
        """Para o listener SSE."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("SSE listener stopped")
