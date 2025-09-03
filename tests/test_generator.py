from flask import Flask

from shib_keygen_api.generator import openssl
from shib_keygen_api.plugins import CSR, PEM


def test_openssl(app: Flask) -> None:
    with app.app_context():
        csr = CSR(common_name="test.example.com", path="test/example.com")
        pem = openssl(csr)
        assert isinstance(pem, PEM)
        assert pem.public.startswith("-----BEGIN CERTIFICATE-----")
        assert "-----END CERTIFICATE-----" in pem.public
        assert pem.private.startswith("-----BEGIN PRIVATE KEY-----")
        assert "-----END PRIVATE KEY-----" in pem.private
