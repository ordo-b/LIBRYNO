"""Sincronização bidirecional com OrdoB Core API."""
import threading
import time
from datetime import datetime
from typing import Optional
from src.auth.ordob_client import client
from src.auth.session import session
from src.core.database import DatabaseSession
from src.core.models import Book, Reader
from src.utils.logger import logger


class SyncManager:
    """
    Gerencia a sincronização bidirecional entre dados locais e a API OrdoB Core.
    
    - Upload: Envia alterações locais para a nuvem
    - Download: Recebe atualizações da nuvem
    - Resolução de conflitos: Last-write-wins por timestamp
    """

    def __init__(self):
        self._sync_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_sync = 0.0
        self._sync_interval = 300

    def should_sync(self) -> bool:
        """Verifica se o cliente deve sincronizar."""
        from src.config import Config
        return Config.SYNC_ENABLED and session.is_authenticated and session.token

    def sync_start(self, interval: int = 300):
        """Inicia a sincronização periódica em background."""
        if self._sync_thread and self._sync_thread.is_alive():
            return

        self._sync_interval = interval
        self._stop_event.clear()
        self._sync_thread = threading.Thread(
            target=self._sync_loop,
            daemon=True,
            name="SyncManager",
        )
        self._sync_thread.start()
        logger.info("Sync manager started (interval: {}s)", interval)

    def sync_stop(self):
        """Para a sincronização periódica."""
        self._stop_event.set()
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5)
        logger.info("Sync manager stopped")

    def _sync_loop(self):
        """Loop principal de sincronização."""
        while not self._stop_event.is_set():
            try:
                if self.should_sync():
                    self.sync_full()
            except Exception as e:
                logger.error("Sync error: {}", e)

            self._stop_event.wait(self._sync_interval)

    def sync_full(self) -> bool:
        """Executa uma sincronização completa (upload + download)."""
        if not self.should_sync():
            return False

        start_time = time.time()
        logger.info("Starting full sync...")

        upload_ok = self.sync_upload()
        download_ok = self.sync_download()

        self._last_sync = time.time()
        elapsed = self._last_sync - start_time
        logger.info("Sync completed in {:.2f}s (upload: {}, download: {})",
                     elapsed, upload_ok, download_ok)

        return upload_ok and download_ok

    def sync_upload(self) -> bool:
        """Envia alterações locais para a nuvem."""
        try:
            token = session.token
            if not token:
                return False

            local_books = self._get_local_books_updated_after(self._last_sync)
            local_readers = self._get_local_readers_updated_after(self._last_sync)

            for book in local_books:
                client.session.headers["Authorization"] = f"Bearer {token}"
                client.session.post(
                    f"{client.base_url}/v1/libryno/books",
                    json={
                        "n_tombo": book["n_tombo"],
                        "isbn": book["isbn"],
                        "titulo": book["titulo"],
                        "autor": book["autor"],
                        "editora": book["editora"],
                        "ano_edicao": book["ano_edicao"],
                        "classificacao": book["classificacao"],
                        "n_folhas": book["n_folhas"],
                        "volume": book["volume"],
                        "data_cadastro": book["data_cadastro"],
                        "assunto": book["assunto"],
                    },
                    timeout=10,
                )
                logger.debug("Uploaded book: {}", book["n_tombo"])

            for reader in local_readers:
                client.session.headers["Authorization"] = f"Bearer {token}"
                client.session.post(
                    f"{client.base_url}/v1/libryno/readers",
                    json={
                        "nome": reader["nome"],
                        "telefone": reader["telefone"],
                        "email": reader["email"],
                        "cpf": reader["cpf"],
                        "identidade": reader["identidade"],
                        "cep": reader["cep"],
                        "escolaridade": reader["escolaridade"],
                        "data_nascimento": reader["data_nascimento"],
                        "endereco": reader["endereco"],
                        "data_cadastro": reader["data_cadastro"],
                    },
                    timeout=10,
                )
                logger.debug("Uploaded reader: {}", reader["cpf"])

            return True
        except Exception as e:
            logger.error("Sync upload error: {}", e)
            return False

    def sync_download(self) -> bool:
        """Baixa atualizações da nuvem para o cliente local."""
        try:
            if not session.token:
                return False

            last_sync_iso = datetime.fromtimestamp(self._last_sync).isoformat() if self._last_sync else None

            response = client.session.get(
                f"{client.base_url}/v1/libryno/sync",
                params={"since": last_sync_iso, "product": "libryno"},
                timeout=30,
            )

            if response.status_code != 200:
                logger.warning("Sync download failed: {}", response.status_code)
                return False

            data = response.json()
            books = data.get("books", [])
            readers = data.get("readers", [])

            with DatabaseSession() as db:
                for book_data in books:
                    existing = db.query(Book).filter_by(n_tombo=book_data["n_tombo"]).first()
                    if existing:
                        for k, v in book_data.items():
                            if hasattr(existing, k) and v is not None:
                                setattr(existing, k, v)
                    else:
                        book = Book(**{k: v for k, v in book_data.items() if k in {
                            "n_tombo", "isbn", "editora", "ano_edicao", "classificacao",
                            "n_folhas", "titulo", "autor", "volume", "data_cadastro", "assunto"
                        }})
                        db.add(book)

                for reader_data in readers:
                    existing = db.query(Reader).filter_by(cpf=reader_data["cpf"]).first()
                    if existing:
                        for k, v in reader_data.items():
                            if hasattr(existing, k) and v is not None:
                                setattr(existing, k, v)
                    else:
                        reader = Reader(**{k: v for k, v in reader_data.items() if k in {
                            "nome", "telefone", "email", "cpf", "identidade", "cep",
                            "escolaridade", "data_nascimento", "endereco", "data_cadastro"
                        }})
                        db.add(reader)

            logger.info("Sync downloaded: {} books, {} readers", len(books), len(readers))
            return True
        except Exception as e:
            logger.error("Sync download error: {}", e)
            return False

    def _get_local_books_updated_after(self, timestamp: float) -> list[dict]:
        """Retorna livros modificados após o timestamp."""
        with DatabaseSession() as db:
            if timestamp:
                cutoff = datetime.fromtimestamp(timestamp)
                books = db.query(Book).filter(Book.created_at >= cutoff).all()
            else:
                books = db.query(Book).all()

            return [
                {
                    "id": b.id, "n_tombo": b.n_tombo, "isbn": b.isbn,
                    "editora": b.editora, "ano_edicao": b.ano_edicao,
                    "classificacao": b.classificacao, "n_folhas": b.n_folhas,
                    "titulo": b.titulo, "autor": b.autor, "volume": b.volume,
                    "data_cadastro": b.data_cadastro, "assunto": b.assunto,
                    "created_at": b.created_at.isoformat() if b.created_at else "",
                }
                for b in books
            ]

    def _get_local_readers_updated_after(self, timestamp: float) -> list[dict]:
        """Retorna leitores modificados após o timestamp."""
        with DatabaseSession() as db:
            if timestamp:
                cutoff = datetime.fromtimestamp(timestamp)
                readers = db.query(Reader).filter(Reader.created_at >= cutoff).all()
            else:
                readers = db.query(Reader).all()

            return [
                {
                    "id": r.id, "nome": r.nome, "telefone": r.telefone,
                    "email": r.email, "cpf": r.cpf, "identidade": r.identidade,
                    "cep": r.cep, "escolaridade": r.escolaridade,
                    "data_nascimento": r.data_nascimento, "endereco": r.endereco,
                    "data_cadastro": r.data_cadastro,
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                }
                for r in readers
            ]


sync_manager = SyncManager()
