from __future__ import annotations
from typing import Any
import tempfile
import hashlib
import shutil
from pathlib import Path

from ...embedded_config.embedded_config import EmbeddedConfig
from ...input_output import file_util
from ...oxt_logger import OxtLogger
from ..download import Download
from ..pip_installers.base_installer import BaseInstaller
from ..progress import Progress


class EmbeddedInstall(BaseInstaller):
    """Install embedded"""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx=ctx)
        self._embedded_config = EmbeddedConfig()

    def _get_logger(self) -> OxtLogger:
        return OxtLogger(log_name=__name__)

    def needs_install(self) -> bool:
        """Check if needs install"""
        if not self._config.is_win:
            return False
        try:
            import _sqlite3
        except ImportError:
            return True
        return False

    def install(self) -> None:
        """Install embedded"""
        if not self.needs_install():
            self._logger.info("sqlite3 is already installed.")
            return
        try:
            eb_itm = self._embedded_config.get_config()
        except Exception as err:
            self._logger.error(f"Unable to get embedded config: {err}")
            return
        progress: Progress | None = None
        if self.config.show_progress:
            self._logger.debug("Starting Progress Window")
            msg = self.resource_resolver.resolve_string("msg08")
            title = self.resource_resolver.resolve_string("title01") or self.config.lo_implementation_name
            progress = Progress(start_msg=f"{msg} sqlite3", title=title)
            progress.start()
        else:
            self._logger.debug("Progress Window is disabled")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Do something with the temporary directory
                # print(f"Temporary directory created at {temp_dir}")
                path_embedded = Path(temp_dir)

                url = str(eb_itm["url"])
                filename = path_embedded / "embedded_py.zip"
                dl = Download()
                data, _, err = dl.url_open(url, verify=False)
                if err:
                    self._logger.error("Unable to download embedded python file")
                    return
                dl.save_binary(pth=filename, data=data)

                if filename.exists():
                    self._logger.info("embedded_py.zip file has been saved")
                else:
                    self._logger.error("Unable to copy embedded_py.zip file")
                    return

                if md5_str := str(eb_itm["md5"]):
                    if not self._verify_file(filename=filename, md5_str=md5_str):
                        self._logger.error("MD5 verification failed")
                        return
                    else:
                        self._logger.info("MD5 verification passed")
                unzip_path = path_embedded / "embedded_py"
                if not unzip_path.exists():
                    unzip_path.mkdir()
                self._unzip(filename=filename, dst=unzip_path)
                files = {"_sqlite3.pyd", "sqlite3.dll"}
                for f in files:
                    eb_file = unzip_path / f
                    if not eb_file.exists():
                        self._logger.error(f"Unable to find {eb_file.name} file")
                        return
                    self._copy_file(src=eb_file, dst=self._embedded_config.install_dir / f)

                self._copy_sqlite3_dir(path=unzip_path)

        finally:
            if progress:
                self._logger.debug("Ending Progress Window")
                progress.kill()

    def _copy_sqlite3_dir(self, path: Path) -> None:
        """Copy sqlite3 directory"""
        # sourcery skip: raise-specific-error
        # There is only one zip file in the directory
        try:
            zip_files = list(path.glob("python*.zip"))
            if not zip_files:
                self._logger.error("No zip files found")
                return
            zip_file = zip_files[0]
            unzip_path = path / "internal_py"
            if not unzip_path.exists():
                unzip_path.mkdir()
            self._unzip(filename=zip_file, dst=unzip_path)
            sql_dir = unzip_path / "sqlite3"
            dst = self._embedded_config.install_dir / "sqlite3"
            shutil.copytree(sql_dir, dst)
            if dst.exists():
                self._logger.debug(f"Directory has been copied to {dst}")
            else:
                self._logger.error("Directory has not been copied")
                raise Exception("Directory has not been copied")

        except Exception as err:
            self._logger.error(f"Unable to copy directory: {err}", exc_info=True)
            raise

    def _copy_file(self, src: Path, dst: Path) -> None:
        """Copy file"""
        # sourcery skip: raise-specific-error
        try:
            shutil.copy(src, dst)
            if dst.exists():
                self._logger.debug(f"File has been copied to {dst}")
            else:
                self._logger.error("File has not been copied")
                raise Exception("File has not been copied")
        except Exception as err:
            self._logger.error(f"Unable to copy file: {err}", exc_info=True)
            raise

    def _verify_file(self, filename: Path, md5_str: str) -> bool:
        result = hashlib.md5(open(filename, "rb").read()).hexdigest()
        return result == md5_str

    def _unzip(self, filename: Path, dst: str | Path) -> None:
        """Unzip the downloaded wheel file"""
        # sourcery skip: raise-specific-error
        if isinstance(dst, str):
            dst = Path(dst)
        try:
            file_util.unzip_file(filename, dst)
            if dst.exists():
                self._logger.debug(f"File has been unzipped to {dst}")
            else:
                self._logger.error("File has not been unzipped")
                raise Exception("File has not been unzipped")
        except Exception as err:
            self._logger.error(f"Unable to unzip file: {err}", exc_info=True)
            raise
