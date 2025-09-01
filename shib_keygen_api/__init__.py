import importlib.metadata as importlib_metadata
import logging.config
import sys
from importlib.metadata import entry_points
from typing import Any, Dict, Optional, Tuple

from flask import Flask, request
from flask.logging import default_handler
from werkzeug.exceptions import HTTPException

from shib_keygen_api.generator import openssl
from shib_keygen_api.plugins import CSR

app = Flask(__name__)

try:
    app.config.from_envvar("FLASK_CONFIG", silent=False)
except (FileNotFoundError, RuntimeError) as ex:
    logging.error("Couldn't read config file: %s", ex)
app.config.from_prefixed_env()

__metadata__ = importlib_metadata.metadata(__name__)
__version__ = __metadata__["Version"]

logging.config.dictConfig({**{"version": 1}, **app.config.get("LOGGING", {})})

# Set Flasks logging handler to all loggers and enable them all
for logger in [
    logging.getLogger(name)
    for name in logging.root.manager.loggerDict  # pylint: disable=no-member
]:
    logger.handlers = [default_handler]
    logger.disabled = False

DEFAULT_PLUGIN = "stdout"
PLUGIN_GROUP = "shib_keygen_api.plugins"
PLUGIN = app.config.get("OUTPUT_PLUGIN", DEFAULT_PLUGIN)
output_plugin_class = next(
    iter(
        [
            ep
            for ep in entry_points().get(PLUGIN_GROUP, [])
            if ep.name == PLUGIN and ep.group == PLUGIN_GROUP
        ],
    ),
    None,
)
if not output_plugin_class:
    app.logger.fatal(
        "Tried to load plugin %r but failed to find it",
        PLUGIN,
    )
    sys.exit(1)

app.logger.info("Loaded output plugin %r", output_plugin_class.name)

output_plugin = output_plugin_class.load()


@app.route("/")
def index() -> Dict[str, str]:
    return {
        "fax": "data",
        "version": __version__,
        "plugin_class": repr(output_plugin_class),
        "output": repr(output_plugin),
    }


@app.post("/generate")
def generate() -> Any:
    code: Optional[int] = 200
    response: Any = {}
    try:
        csr_json = request.get_json(force=True)
        app.logger.debug("%r", csr_json)
        csr = CSR(**csr_json)
        app.logger.debug("%r", csr)
        cert = openssl(csr)
        export_status = output_plugin.export(cert, csr)
        app.logger.debug(
            "Export plugin %r export_status: %r",
            output_plugin,
            export_status,
        )
        response = {"status": export_status}
    except HTTPException as ex:  # pylint: disable=redefined-outer-name
        app.logger.exception("wat")
        code = ex.code
        response = {"error": {"code": code, "message": str(ex)}}
    except TypeError as ex:
        app.logger.exception("wat")
        code = 400
        response = {"error": {"code": code, "message": str(ex)}}
    except RuntimeError:
        message = "Error generating certificate and key"
        app.logger.exception(message)
        code = 500
        response = {"error": {"code": code, "message": message}}

    return response, code


@app.route("/status")
def status() -> Tuple[Dict[str, Any], int]:
    code = 200
    try:
        plugin_status = output_plugin.status() if output_plugin else None
    except Exception:  # pylint: disable=broad-exception-caught,redefined-outer-name
        code = 500
        plugin_status = False
        app.logger.exception(
            "Caught exception while trying to get status from plugin %r",
            output_plugin,
        )
    plugin_name = output_plugin_class.name if output_plugin_class else None

    return {
        "plugin": {"name": plugin_name, "status": plugin_status},
        "version": __version__,
        "output": repr(output_plugin),
    }, code
