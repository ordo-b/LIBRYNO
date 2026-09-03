"""Constantes do aplicativo LIBRYNO."""

APP_FULL_NAME = "LIBRYNO - Sistema de Gestão de Biblioteca"
APP_AUTHOR = "OrdoB"
APP_ORG = "OrdoB"
APP_CNPJ = ""

MIN_NAME_LEN = 3
MIN_USERNAME_LEN = 3
MIN_PASSWORD_LEN = 5

ROLE_ADMIN = "admin"
ROLE_COLLABORATOR = "collaborator"
ROLE_CONSULTANT = "consultant"

LOAN_STATUS_ACTIVE = "active"
LOAN_STATUS_RETURNED = "returned"
LOAN_STATUS_OVERDUE = "overdue"

DEFAULT_LOAN_DAYS = 14
FINE_PER_DAY = 1.0

FREE_TIER_POPUP_INTERVAL = 10

# ─── FREE TIER LIMITS ────────────────────────────────────────────
# Limite de registros permitidos para usuários no plano FREE.
# Acima disso o CRUD bloqueia criação e exige upgrade para PREMIUM.
FREE_MAX_BOOKS = 50
FREE_MAX_READERS = 50
FREE_MAX_COLLABS = 3
FREE_MAX_COLLABORATORS = 3  # alias
FREE_MAX_EXPORTS_PER_DAY = 3

# ─── AUTH ENFORCEMENT ────────────────────────────────────────────
# O Libryno SÓ funciona com autenticação OrdoB.
# Se a API estiver inacessível no startup, o app deve mostrar
# aviso e permitir retry, mas NÃO liberar acesso offline.
AUTH_REQUIRE_API_ON_STARTUP = True
AUTH_TOKEN_VALIDATION_TIMEOUT = 10  # segundos
