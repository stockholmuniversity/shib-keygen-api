from flask import current_app

from shib_keygen_api.plugins import CSR, PEM


def openssl(csr: CSR) -> PEM:
    current_app.logger.info("%r", csr)
    public, private = ("lol", "lol")
    return PEM(private, public)
