from typing import Generator

import pytest
from flask import Flask

from shib_keygen_api import app as original_app


@pytest.fixture(name="app")
def flask_app() -> Generator[Flask, None, None]:
    app = original_app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here
