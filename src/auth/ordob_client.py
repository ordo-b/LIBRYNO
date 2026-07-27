"""Cliente HTTP para a API OrdoB Core."""
import requests
from typing import Optional
from src.config import Config
from src.utils.logger import logger


class OrdoBClient:
    def __init__(self):
        self.base_url = Config.get_api_url()
        self.product_slug = Config.ORDOB_PRODUCT_SLUG
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def set_token(self, token: str):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        self.session.headers.pop("Authorization", None)

    def health_check(self) -> bool:
        try:
            resp = requests.get(
                f"{self.base_url.replace('/api', '')}/api/health",
                timeout=10,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def login(self, email: str, password: str) -> Optional[dict]:
        try:
            resp = self.session.post(
                f"{self.base_url}/v1/auth/login",
                json={"email": email, "password": password},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                logger.info("Login successful for: {}", email)
                return data
            logger.warning("Login failed for: {} - Status {}", email, resp.status_code)
            return None
        except requests.RequestException as e:
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

            resp = self.session.post(
                f"{self.base_url}/v1/auth/register",
                json=payload,
                timeout=15,
            )
            if resp.status_code == 201:
                data = resp.json()
                logger.info("Registration successful for: {}", email)
                return data
            logger.warning("Registration failed: {} - {}", resp.status_code, resp.text)
            return None
        except requests.RequestException as e:
            logger.error("Registration request error: {}", e)
            return None

    def logout(self, token: str) -> bool:
        try:
            self.set_token(token)
            resp = self.session.post(
                f"{self.base_url}/v1/auth/logout",
                timeout=10,
            )
            self.clear_token()
            return resp.status_code == 200
        except requests.RequestException:
            self.clear_token()
            return False

    def get_user(self, token: str) -> Optional[dict]:
        try:
            self.set_token(token)
            resp = self.session.get(
                f"{self.base_url}/v1/user",
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("user")
            return None
        except requests.RequestException as e:
            logger.error("Get user error: {}", e)
            return None

    def validate_license(self, license_key: str) -> Optional[dict]:
        try:
            resp = self.session.post(
                f"{self.base_url}/v1/license/validate",
                json={
                    "license_key": license_key,
                    "product": self.product_slug,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                logger.info("License validation: valid={}", data.get("valid"))
                return data
            return None
        except requests.RequestException as e:
            logger.error("License validation error: {}", e)
            return None

    def get_licenses(self, token: str) -> Optional[list]:
        try:
            self.set_token(token)
            resp = self.session.get(
                f"{self.base_url}/v1/licenses",
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("licenses", [])
            return None
        except requests.RequestException as e:
            logger.error("Get licenses error: {}", e)
            return None

    def create_ticket(self, token: str, subject: str, description: str,
                      category: str = "suporte", priority: str = "media") -> Optional[dict]:
        try:
            self.set_token(token)
            resp = self.session.post(
                f"{self.base_url}/v1/tickets",
                json={
                    "subject": subject,
                    "description": description,
                    "category": category,
                    "priority": priority,
                },
                timeout=15,
            )
            if resp.status_code == 201:
                return resp.json().get("ticket")
            return None
        except requests.RequestException as e:
            logger.error("Create ticket error: {}", e)
            return None


client = OrdoBClient()
