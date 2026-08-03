"""Cliente HTTP para a API OrdoB Core."""
import json
import time
import threading
from typing import Optional, Callable
from urllib.parse import urljoin
import requests
from src.config import Config
from src.utils.logger import logger


class OrdoBClient:
    """Cliente HTTP com retry exponencial, health check e SSE para tempo real."""

    MAX_RETRIES = 5
    BASE_DELAY = 1.0
    MAX_DELAY = 60.0
    TIMEOUT = 15

    def __init__(self):
        self.base_url = Config.get_api_url()
        self.product_slug = Config.ORDOB_PRODUCT_SLUG
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Product": self.product_slug,
        })

    def set_token(self, token: str):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        self.session.headers.pop("Authorization", None)

    def _request_with_retry(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Executa requisição HTTP com retry exponencial e backoff."""
        kwargs.setdefault("timeout", self.TIMEOUT)
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = self.session.request(method, url, **kwargs)
                if resp.status_code < 500:
                    return resp
                delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)
                logger.warning("Server error {} (attempt {}/{}), retrying in {}s",
                               resp.status_code, attempt + 1, self.MAX_RETRIES, delay)
                time.sleep(delay)
            except requests.RequestException as e:
                logger.warning("Request error (attempt {}/{}): {}",
                               attempt + 1, self.MAX_RETRIES, e)
                if attempt < self.MAX_RETRIES - 1:
                    delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)
                    time.sleep(delay)
                else:
                    logger.error("Max retries exceeded for {} {}", method, url)
                    return None
        return None

    def health_check(self) -> bool:
        try:
            resp = requests.get(
                f"{self.base_url.replace('/api', '')}/api/health",
                timeout=self.TIMEOUT,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def ping(self) -> dict:
        """Verifica latência e status do servidor."""
        start = time.time()
        if self.health_check():
            return {"online": True, "latency_ms": int((time.time() - start) * 1000)}
        return {"online": False, "latency_ms": 0}

    def login(self, email: str, password: str) -> Optional[dict]:
        try:
            resp = self._request_with_retry(
                "POST",
                f"{self.base_url}/v1/auth/login",
                json={"email": email, "password": password},
            )
            if resp and resp.status_code == 200:
                data = resp.json()
                logger.info("Login successful for: {}", email)
                return data
            if resp:
                logger.warning("Login failed for: {} - Status {}", email, resp.status_code)
            return None
        except Exception as e:
            logger.error("Login request error: {}", e)
            return None

    def register(self, name: str, email: str, password: str,
                 phone: str = "", company: str = "", document: str = "") -> Optional[dict]:
        try:
            payload = {"name": name, "email": email, "password": password}
            if phone:
                payload["phone"] = phone
            if company:
                payload["company_name"] = company
            if document:
                payload["document"] = document

            resp = self._request_with_retry(
                "POST",
                f"{self.base_url}/v1/auth/register",
                json=payload,
            )
            if resp and resp.status_code == 201:
                data = resp.json()
                logger.info("Registration successful for: {}", email)
                return data
            if resp:
                logger.warning("Registration failed: {} - {}", resp.status_code, resp.text)
            return None
        except Exception as e:
            logger.error("Registration request error: {}", e)
            return None

    def logout(self, token: str) -> bool:
        try:
            self.set_token(token)
            resp = self._request_with_retry(
                "POST",
                f"{self.base_url}/v1/auth/logout",
            )
            self.clear_token()
            return resp is not None and resp.status_code == 200
        except Exception:
            self.clear_token()
            return False

    def get_user(self, token: str) -> Optional[dict]:
        try:
            self.set_token(token)
            resp = self._request_with_retry("GET", f"{self.base_url}/v1/user")
            if resp and resp.status_code == 200:
                return resp.json().get("user")
            return None
        except Exception as e:
            logger.error("Get user error: {}", e)
            return None

    def validate_license(self, license_key: str) -> Optional[dict]:
        try:
            resp = self._request_with_retry(
                "POST",
                f"{self.base_url}/v1/license/validate",
                json={
                    "license_key": license_key,
                    "product": self.product_slug,
                },
            )
            if resp and resp.status_code == 200:
                data = resp.json()
                logger.info("License validation: valid={}", data.get("valid"))
                return data
            return None
        except Exception as e:
            logger.error("License validation error: {}", e)
            return None

    def get_licenses(self, token: str) -> Optional[list]:
        try:
            self.set_token(token)
            resp = self._request_with_retry("GET", f"{self.base_url}/v1/licenses")
            if resp and resp.status_code == 200:
                return resp.json().get("licenses", [])
            return None
        except Exception as e:
            logger.error("Get licenses error: {}", e)
            return None

    def create_ticket(self, token: str, subject: str, description: str,
                      category: str = "suporte", priority: str = "media") -> Optional[dict]:
        try:
            self.set_token(token)
            resp = self._request_with_retry(
                "POST",
                f"{self.base_url}/v1/tickets",
                json={
                    "subject": subject,
                    "description": description,
                    "category": category,
                    "priority": priority,
                },
            )
            if resp and resp.status_code == 201:
                return resp.json().get("ticket")
            return None
        except Exception as e:
            logger.error("Create ticket error: {}", e)
            return None

    def stream_notifications(self, token: str, on_message: Callable, on_error: Callable = None) -> threading.Event:
        """
        Conecta via Server-Sent Events (SSE) e mantém conexão em tempo real.
        Retorna um threading.Event para cancelar o streaming.
        """
        from src.utils.sse_client import SSEClient

        sse = SSEClient(
            base_url=self.base_url.replace("/api", ""),
            token=token,
            endpoint="/api/v1/notifications/stream",
            on_message=on_message,
            on_error=on_error,
        )
        stop_event = sse.start()
        return stop_event


client = OrdoBClient()
