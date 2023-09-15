import shlex
import subprocess
import tempfile

from flask import current_app

from shib_keygen_api.plugins import CSR, PEM

DAYS = 10 * 365


def openssl(csr: CSR) -> PEM:
    timeout = 5
    with tempfile.NamedTemporaryFile(buffering=0) as ssl_config:
        # From https://git.shibboleth.net/view/?p=cpp-sp.git;a=blob;f=configs/keygen.sh
        ssl_config.write(
            f"""
# OpenSSL configuration file for creating keypair
[req]
prompt=no
default_bits=3072
encrypt_key=no
default_md=sha256
distinguished_name=dn
# PrintableStrings only
string_mask=MASK:0002
x509_extensions=ext
[dn]
CN={csr.common_name}
[ext]
subjectAltName=DNS:{csr.common_name}
subjectKeyIdentifier=hash
        """.encode()
        )
        command = list(
            shlex.split(
                f"openssl req -config {ssl_config.name} -new -x509 -days {DAYS} -keyout {csr.common_name}-key.pem -out {csr.common_name}-cert.pem"
            )
        )
        with subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
        ) as process:
            try:
                (_, stderr) = process.communicate(timeout=timeout)
                # Strip out irrelevant dhparam(?) output
                stderr = stderr.lstrip("*.+-\n")
                current_app.logger.debug("stderr: %r", stderr)
                current_app.logger.debug("Process returncode: %r", process.returncode)
                if process.returncode != 0:
                    raise RuntimeError(stderr)
            except subprocess.TimeoutExpired as ex:
                raise RuntimeError(r"Hit timeout after {timeout}s") from ex
            finally:
                process.kill()

            current_app.logger.info(
                "Successfully generated certificate and key for %r", csr.common_name
            )

    current_app.logger.info("%r", csr)
    public, private = ("lol", "lol")
    return PEM(private, public)
