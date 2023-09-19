# mypy: disable-error-code="union-attr"
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

    @classmethod
    def export(cls, pem: PEM, csr: CSR) -> bool:
        cls.config()
        return False

    @classmethod
    def status(cls) -> bool:
        cls.config()
        health_status: bool = CLIENT.sys.read_health_status().ok
        current_app.logger.debug("health_status: %r", health_status)
        is_authenticated: bool = CLIENT.is_authenticated()
        current_app.logger.debug("is_authenticated: %r", is_authenticated)
        return health_status and is_authenticated
