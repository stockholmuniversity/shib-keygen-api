from pathlib import Path
from typing import Any, Dict

from flask import current_app

from shib_keygen_api.plugins import CSR, PEM, Plugin

CONFIG: Dict[Any, Any] = {}


class Dir(Plugin):
    @staticmethod
    def config() -> None:
        global CONFIG  # pylint: disable=global-statement

        if not CONFIG:
            CONFIG = current_app.config.get("PLUGIN_CONFIG", {}).get(
                __name__[__name__.rfind(".") + 1 :], {}
            )
            if path := CONFIG.get("path"):
                path = Path(path)
                path.mkdir(mode=0o700, parents=True, exist_ok=True)

    @classmethod
    def export(cls, pem: PEM, csr: CSR) -> bool:
        cls.config()
        if cert_path := CONFIG.get("path"):
            cert_path = Path(cert_path) / Path(csr.path)
            cert_path.mkdir(mode=0o700, parents=True, exist_ok=True)
            certificate = cert_path / (csr.common_name + "-cert.pem")
            key = cert_path / (csr.common_name + "-key.pem")
            if not certificate.exists():
                certificate.touch(mode=0o600)
                certificate.write_text(pem.public)
            if not key.exists():
                key.touch(mode=0o600)
                key.write_text(pem.private)
            current_app.logger.info(
                "Successfully stored certs for %r in %r", csr.common_name, cert_path
            )
            return True
        current_app.logger.error("No configured 'path' to store certificates in")
        return False

    @classmethod
    def status(cls) -> bool:
        cls.config()
        if path := CONFIG.get("path"):
            return Path(path).is_dir()
        return False
