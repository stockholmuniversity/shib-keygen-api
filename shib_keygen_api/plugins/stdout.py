from flask import current_app

from shib_keygen_api.plugins import PEM, Plugin


class Stdout(Plugin):
    @classmethod
    def export(cls, pem: PEM) -> bool:
        current_app.logger.info("%r", pem)
        return True

    @classmethod
    def status(cls) -> bool:
        return True
