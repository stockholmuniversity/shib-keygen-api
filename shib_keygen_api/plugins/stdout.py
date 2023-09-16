from flask import current_app

from shib_keygen_api.plugins import CSR, PEM, Plugin


class Stdout(Plugin):
    @classmethod
    def export(cls, pem: PEM, _csr: CSR) -> bool:
        current_app.logger.info("%r", pem)
        return True

    @classmethod
    def status(cls) -> bool:
        return True
