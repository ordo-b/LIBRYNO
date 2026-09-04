"""Auto-updater do Libryno — Verifica, baixa e aplica atualizações automaticamente."""
import os
import sys
import threading
import subprocess
import tempfile
import urllib.request
import shutil
from pathlib import Path
from typing import Optional, Callable
from src.config import Config
from src.utils.logger import logger


class UpdateProgress:
    """Callbacks de progresso para UI."""
    def __init__(
        self,
        on_start: Callable[[], None] = None,
        on_progress: Callable[[int, int], None] = None,
        on_complete: Callable[[bool, str], None] = None,
    ):
        self.on_start = on_start or (lambda: None)
        self.on_progress = on_progress or (lambda d, t: None)
        self.on_complete = on_complete or (lambda success, msg: None)


class AutoUpdater:
    """Gerenciador de atualizações automáticas."""

    def __init__(self):
        self._downloading = False
        self._cancelled = False

    def check_for_updates(self, callback: Optional[Callable[[dict], None]] = None) -> dict:
        """Verifica se há atualização disponível. Retorna info da release."""
        info = Config.get_update_info()

        if callback:
            try:
                callback(info)
            except Exception as e:
                logger.error("Erro no callback de update: {}", e)

        return info

    def check_and_notify(
        self,
        on_update_available: Callable[[dict], None],
        on_no_update: Callable[[], None] = None,
        on_error: Callable[[str], None] = None,
    ):
        """Verifica em background e chama callbacks apropriados."""
        def worker():
            info = self.check_for_updates()
            if info.get("update_available"):
                try:
                    on_update_available(info)
                except Exception as e:
                    logger.error("Erro no callback update_available: {}", e)
            elif info.get("reason") and info["reason"] != "auto_update_disabled":
                try:
                    if on_error:
                        on_error(info["reason"])
                except Exception as e:
                    logger.error("Erro no callback error: {}", e)
            else:
                try:
                    if on_no_update:
                        on_no_update()
                except Exception as e:
                    logger.error("Erro no callback no_update: {}", e)

        thread = threading.Thread(target=worker, daemon=True, name="UpdateCheck")
        thread.start()

    def download_update(
        self,
        download_url: str,
        progress: UpdateProgress,
    ) -> Optional[Path]:
        """Baixa o instalador/arquivo de atualização para um arquivo temporário."""
        if self._downloading:
            raise RuntimeError("Download já em andamento")

        self._downloading = True
        self._cancelled = False

        try:
            # Cria arquivo temporário
            suffix = Path(download_url).suffix or ".exe"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_path = Path(temp_file.name)
            temp_file.close()

            logger.info("Iniciando download de {} para {}", download_url, temp_path)

            def download_thread():
                try:
                    req = urllib.request.Request(
                        download_url,
                        headers={"User-Agent": f"{Config.APP_NAME}/{Config.APP_VERSION}"},
                    )
                    with urllib.request.urlopen(req, timeout=30) as response:
                        total_size = int(response.headers.get("Content-Length", 0))
                        downloaded = 0
                        chunk_size = 8192

                        progress.on_start()

                        with open(temp_path, "wb") as f:
                            while not self._cancelled:
                                chunk = response.read(chunk_size)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress.on_progress(downloaded, total_size)

                    if self._cancelled:
                        temp_path.unlink(missing_ok=True)
                        progress.on_complete(False, "Cancelado pelo usuário")
                    else:
                        progress.on_complete(True, str(temp_path))

                except Exception as e:
                    logger.error("Erro no download: {}", e)
                    temp_path.unlink(missing_ok=True)
                    progress.on_complete(False, f"Erro: {e}")

            thread = threading.Thread(target=download_thread, daemon=True, name="UpdateDownload")
            thread.start()
            return temp_path

        except Exception as e:
            self._downloading = False
            logger.error("Erro ao iniciar download: {}", e)
            progress.on_complete(False, f"Erro: {e}")
            return None

    def cancel_download(self):
        """Cancela download em andamento."""
        self._cancelled = True
        self._downloading = False

    def install_windows(self, installer_path: Path) -> bool:
        """Executa o instalador NSIS no Windows (modo silencioso)."""
        if sys.platform != "win32":
            return False

        try:
            logger.info("Executando instalador Windows: {}", installer_path)
            # /S = silencioso, /D=dir define diretório
            result = subprocess.run(
                [str(installer_path), "/S"],
                check=True,
                timeout=120,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error("Falha ao executar instalador Windows: {}", e)
            return False
        except Exception as e:
            logger.error("Erro inesperado ao instalar no Windows: {}", e)
            return False

    def install_linux_deb(self, deb_path: Path) -> bool:
        """Instala pacote .deb no Linux (Debian/Ubuntu)."""
        if sys.platform != "linux":
            return False

        try:
            logger.info("Instalando pacote .deb: {}", deb_path)
            # Usa pkexec para privilégios de root
            result = subprocess.run(
                ["pkexec", "dpkg", "-i", str(deb_path)],
                check=True,
                timeout=120,
            )
            # Corrige dependências se necessário
            subprocess.run(["pkexec", "apt-get", "install", "-f", "-y"], check=False)
            return True
        except Exception as e:
            logger.error("Falha ao instalar .deb: {}", e)
            return False

    def install_linux_appimage(self, appimage_path: Path, install_dir: Optional[Path] = None) -> bool:
        """Instala AppImage no Linux."""
        if sys.platform != "linux":
            return False

        try:
            if install_dir is None:
                install_dir = Path.home() / ".local" / "bin"

            install_dir.mkdir(parents=True, exist_ok=True)
            target = install_dir / f"{Config.APP_NAME.lower()}.AppImage"

            logger.info("Instalando AppImage em: {}", target)
            shutil.copy2(appimage_path, target)
            target.chmod(0o755)

            # Cria .desktop entry
            self._create_desktop_entry(target)

            return True
        except Exception as e:
            logger.error("Falha ao instalar AppImage: {}", e)
            return False

    def _create_desktop_entry(self, appimage_path: Path):
        """Cria arquivo .desktop para integração com menu de aplicações."""
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = desktop_dir / f"{Config.APP_NAME.lower()}.desktop"
        content = f"""[Desktop Entry]
Name={Config.APP_NAME}
Comment=Sistema de Gestão de Bibliotecas
Exec={appimage_path}
Icon={Config.APP_NAME.lower()}
Terminal=false
Type=Application
Categories=Office;Education;
StartupNotify=true
"""
        desktop_file.write_text(content)
        logger.info("Arquivo .desktop criado em: {}", desktop_file)

    def apply_update(
        self,
        info: dict,
        progress: UpdateProgress,
    ) -> bool:
        """Baixa e aplica a atualização baseada na plataforma."""
        download_urls = info.get("download_urls", {})
        system = sys.platform

        if system == "win32":
            url = download_urls.get("windows")
            if not url:
                progress.on_complete(False, "Instalador Windows não encontrado na release")
                return False

            installer_path = self.download_update(url, progress)
            if not installer_path:
                return False

            return self.install_windows(installer_path)

        elif system == "linux":
            # Tenta .deb primeiro, depois AppImage
            url = download_urls.get("linux_deb")
            if url:
                installer_path = self.download_update(url, progress)
                if installer_path:
                    return self.install_linux_deb(installer_path)

            url = download_urls.get("linux_appimage")
            if url:
                installer_path = self.download_update(url, progress)
                if installer_path:
                    return self.install_linux_appimage(installer_path)

            progress.on_complete(False, "Nenhum instalador Linux disponível")
            return False

        else:
            progress.on_complete(False, f"Plataforma não suportada: {system}")
            return False

    def check_and_auto_update(
        self,
        on_update_found: Callable[[dict], None],
        on_no_update: Callable[[], None] = None,
        on_error: Callable[[str], None] = None,
        on_update_complete: Callable[[bool, str], None] = None,
    ):
        """Verifica, baixa e instala atualização automaticamente (com confirmação do usuário)."""
        def check_worker():
            info = self.check_for_updates()
            if not info.get("update_available"):
                if on_no_update:
                    on_no_update()
                return

            # Update encontrado - notifica UI
            on_update_found(info)

            # A UI deve chamar apply_update quando usuário confirmar
            # Aqui apenas notifica que há update

        threading.Thread(target=check_worker, daemon=True, name="AutoUpdateCheck").start()


# Instância global
auto_updater = AutoUpdater()