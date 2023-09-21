# mypy: disable-error-code="union-attr"
import base64
from pathlib import Path
from typing import Any, Dict

import hvac  # type: ignore
from flask import current_app

from shib_keygen_api.plugins import CSR, PEM, Plugin

CONFIG: Dict[Any, Any] = {}

CLIENT = None


class Vault(Plugin):
    @staticmethod
    def config() -> None:
        global CONFIG, CLIENT  # pylint: disable=global-statement

        if not CONFIG:
            CONFIG = current_app.config.get("PLUGIN_CONFIG", {}).get(
                __name__[__name__.rfind(".") + 1 :], {}
            )
        if not CLIENT:
            try:
                CLIENT = hvac.Client(**CONFIG["client"])
                CLIENT.kv.default_kv_version = 1
                getattr(CLIENT.auth, CONFIG["auth_method"]).login(
                    **CONFIG["auth_method_params"]
                )
            except hvac.exceptions.VaultError as ex:
                raise RuntimeError("Can't configure Vault") from ex

    @classmethod
    def export(cls, pem: PEM, csr: CSR) -> bool:
        cls.config()
        cert_path = CONFIG["path"]
        cert_path = Path(cert_path) / Path(csr.path)
        try:
            certs = CLIENT.kv.list_secrets(cert_path)
        except hvac.exceptions.VaultError as ex:
            raise RuntimeError("Can't list certificates in Vault") from ex
        current_app.logger.info("%r", certs)
        certificate = cert_path / (csr.common_name + "-cert.pem")
        key = cert_path / (csr.common_name + "-key.pem")
        cert_exists = certificate.name in certs["data"]["keys"]
        current_app.logger.debug("cert_exists: %r", cert_exists)

        if not cert_exists:
            public: Any = pem.public
            private: Any = pem.private
            storage_method = CONFIG.get("storage_method", "raw")
            if storage_method == "base64":
                public = base64.b64encode(public.encode())
                private = base64.b64encode(private.encode())
            elif storage_method == "binarylist":
                public = [ord(c) for c in public]
                private = [ord(c) for c in private]
            elif storage_method == "raw":
                pass
            else:
                current_app.logger.error(
                    "Incorrect 'storage_method'  %r using 'raw' instead.",
                    storage_method,
                )

            current_app.logger.debug("storage_method: %r", storage_method)
            try:
                CLIENT.kv.create_or_update_secret(
                    certificate, method="POST", secret={"binaryData": public}
                )
                CLIENT.kv.create_or_update_secret(
                    key, method="POST", secret={"binaryData": private}
                )
                current_app.logger.info(
                    "Successfully stored certs for %r in %r", csr.common_name, cert_path
                )
            except hvac.exceptions.VaultError as ex:
                raise RuntimeError("Can't export certificates to Vault") from ex
        else:
            current_app.logger.info(
                "Successfully found certs for %r in %r", csr.common_name, cert_path
            )

        return True

    @classmethod
    def status(cls) -> bool:
        cls.config()
        health_status: bool = CLIENT.sys.read_health_status().ok
        current_app.logger.debug("health_status: %r", health_status)
        is_authenticated: bool = CLIENT.is_authenticated()
        current_app.logger.debug("is_authenticated: %r", is_authenticated)
        return health_status and is_authenticated
