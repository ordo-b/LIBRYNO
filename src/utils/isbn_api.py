"""Consulta de ISBN via BrasilAPI."""
import requests

from src.utils.logger import logger


def set_isbn(isbn: str) -> dict:
    """Consulta ISBN na BrasilAPI. Retorna dict com dados do livro."""
    try:
        resp = requests.get(
            f"https://brasilapi.com.br/api/isbn/v1/{isbn}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "title": data.get("title", ""),
                "subtitle": data.get("subtitle", ""),
                "authors": data.get("authors", []),
                "publisher": data.get("publisher", ""),
                "synopsis": data.get("synopsis", ""),
                "page_count": data.get("page_count", ""),
                "year": data.get("year", ""),
                "isbn": data.get("isbn13", isbn),
            }
        logger.warning("ISBN not found: {}", isbn)
        return {}
    except requests.RequestException as e:
        logger.error("ISBN API error: {}", e)
        return {}
