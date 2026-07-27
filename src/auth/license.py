"""Gerenciamento de licença premium via OrdoB."""
from typing import Optional, Tuple
from src.auth.ordob_client import client
from src.auth.session import session
from src.utils.logger import logger


def validate_license(license_key: str) -> Tuple[bool, str]:
    """Valida uma chave de licença. Retorna (is_valid, mensagem)."""
    result = client.validate_license(license_key)
    if result is None:
        return False, "Não foi possível conectar ao servidor OrdoB."

    if result.get("valid"):
        session.set_premium(True, license_key)
        org = result.get("organization", "")
        logger.info("License activated: {} for {}", license_key, org)
        return True, f"Licença ativada com sucesso!\nOrganização: {org}"

    error = result.get("error", "Licença inválida.")
    session.set_premium(False)
    logger.warning("License invalid: {} - {}", license_key, error)
    return False, error


def check_existing_license() -> bool:
    """Verifica se já existe uma licença salva na sessão."""
    if session.is_premium and session.license_key:
        result = client.validate_license(session.license_key)
        if result and result.get("valid"):
            return True
        session.set_premium(False)
        logger.info("Existing license expired or invalid, downgrading to free")
    return False


def deactivate_license():
    """Remove a licença premium da sessão."""
    session.set_premium(False)
    logger.info("License deactivated")


def get_license_info() -> Optional[dict]:
    """Retorna informações da licença atual."""
    if not session.is_premium or not session.license_key:
        return None
    return {
        "key": session.license_key,
        "status": "active",
        "user": session.user_name,
    }
