from flask import Flask

from shib_keygen_api.generator import openssl
from shib_keygen_api.plugins import CSR, PEM


def test_csr() -> None:
    csr = CSR(common_name="test.example.com", path="/test/example.com")
    assert csr.common_name == "test.example.com"
    assert csr.path == "test/example.com"


def test_pem(app: Flask) -> None:
    with app.app_context():
        csr = CSR(common_name="test.example.com", path="test/example.com")
        pem = openssl(csr)
        assert isinstance(pem, PEM)
        assert hasattr(pem, "public")
        assert hasattr(pem, "private")
