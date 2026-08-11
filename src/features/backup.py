"""Sistema de backup automático (PREMIUM)."""
import zipfile
from datetime import datetime
from pathlib import Path

from src.config import DATA_DIR
from src.core.database import DatabaseSession
from src.core.models import BackupRecord
from src.utils.logger import logger

BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


class BackupManager:
    @staticmethod
    def create_backup(name: str = "") -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = name or f"libryno_backup_{timestamp}"
            zip_path = BACKUP_DIR / f"{filename}.zip"

            db_path = DATA_DIR / "libryno.db"
            if not db_path.exists():
                logger.warning("Database file not found for backup")
                return ""

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(db_path, "libryno.db")
                for f in DATA_DIR.glob("*.json"):
                    zf.write(f, f.name)

            size = zip_path.stat().st_size
            with DatabaseSession() as session:
                record = BackupRecord(filename=zip_path.name, size_bytes=size)
                session.add(record)

            logger.info("Backup created: {} ({} bytes)", zip_path.name, size)
            return str(zip_path)
        except Exception as e:
            logger.error("Error creating backup: {}", e)
            return ""

    @staticmethod
    def restore_backup(zip_path: str) -> bool:
        try:
            src = Path(zip_path)
            if not src.exists():
                return False

            with zipfile.ZipFile(src, "r") as zf:
                for name in zf.namelist():
                    if name == "libryno.db":
                        dest = DATA_DIR / "libryno.db"
                        with open(dest, "wb") as f:
                            f.write(zf.read(name))
                        logger.info("Database restored from: {}", zip_path)
                        return True
            return False
        except Exception as e:
            logger.error("Error restoring backup: {}", e)
            return False

    @staticmethod
    def list_backups() -> list[dict]:
        try:
            with DatabaseSession() as session:
                records = session.query(BackupRecord).order_by(
                    BackupRecord.created_at.desc()
                ).all()
                return [
                    {
                        "id": r.id, "filename": r.filename,
                        "size_bytes": r.size_bytes,
                        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
                    }
                    for r in records
                ]
        except Exception as e:
            logger.error("Error listing backups: {}", e)
            return []

    @staticmethod
    def delete_backup(backup_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                record = session.query(BackupRecord).filter_by(id=backup_id).first()
                if not record:
                    return False
                filepath = BACKUP_DIR / record.filename
                if filepath.exists():
                    filepath.unlink()
                session.delete(record)
                return True
        except Exception as e:
            logger.error("Error deleting backup: {}", e)
            return False
