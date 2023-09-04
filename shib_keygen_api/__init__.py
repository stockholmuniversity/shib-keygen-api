import importlib.metadata as importlib_metadata

from flask import Flask

app = Flask(__name__)


__metadata__ = importlib_metadata.metadata(__name__)
__version__ = __metadata__["Version"]


@app.route("/")
def index():
    return {
        "fax": "data",
        "version": __version__,
    }
