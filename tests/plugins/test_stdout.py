import pytest
from flask import Flask

from shib_keygen_api.generator import openssl
from shib_keygen_api.plugins import CSR
from shib_keygen_api.plugins.stdout import Stdout


def test_stdout(app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    with app.app_context():
        csr = CSR(common_name="test.example.com", path="test/example.com")
        pem = openssl(csr)
        stdout = Stdout()
        with caplog.at_level("INFO"):
            assert stdout.export(pem, csr)
            assert "-----BEGIN PRIVATE KEY-----" in caplog.text
            assert "-----BEGIN CERTIFICATE-----" in caplog.text
