# mypy: disable-error-code="union-attr"
from pathlib import Path
from typing import Any, Dict

import hvac
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
            CLIENT = hvac.Client(**CONFIG["client"])
            CLIENT.kv.default_kv_version = 1
            getattr(CLIENT.auth, CONFIG["auth_method"]).login(
                **CONFIG["auth_method_params"]
            )

    @classmethod
    def export(cls, pem: PEM, csr: CSR) -> bool:
        cls.config()
        cert_path = CONFIG["path"]
        cert_path = Path(cert_path) / Path(csr.path)
        certs = CLIENT.kv.list_secrets(cert_path)
        current_app.logger.info("%r", certs)
        certificate = cert_path / (csr.common_name + "-cert.pem")
        key = cert_path / (csr.common_name + "-key.pem")
        cert_exists = certificate.name in certs["data"]["keys"]
        current_app.logger.debug("cert_exists: %r", cert_exists)

        if not cert_exists:
            CLIENT.kv.create_or_update_secret(
                certificate, method="POST", secret={"binaryData": pem.public}
            )
            CLIENT.kv.create_or_update_secret(
                key, method="POST", secret={"binaryData": pem.private}
            )
            current_app.logger.info(
                "Successfully stored certs for %r in %r", csr.common_name, cert_path
            )
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
