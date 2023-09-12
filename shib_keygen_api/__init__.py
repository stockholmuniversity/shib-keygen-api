import importlib.metadata as importlib_metadata
import sys
from importlib.metadata import entry_points
from typing import Any, Dict, Tuple

from flask import Flask

app = Flask(__name__)


__metadata__ = importlib_metadata.metadata(__name__)
__version__ = __metadata__["Version"]

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
        "plugin": repr(output_plugin),
        "output": repr(output),
        "export": output.export() if output else "no plugin",
    }


@app.route("/status")
def status() -> Tuple[Dict[str, Any], int]:
    code = 200
    try:
        plugin_status = output_plugin.status() if output_plugin else None
    except Exception as ex:  # pylint: disable=broad-exception-caught
        code = 500
        plugin_status = False
        app.logger.info(
            "Caught exception %r while trying to get status from plugin %r",
            ex,
            output_plugin,
        )
    plugin_name = output_plugin_class.name if output_plugin_class else None

    return {
        "plugin": {"name": plugin_name, "status": plugin_status},
        "version": __version__,
        "output": repr(output_plugin),
        "export": output_plugin.export() if output_plugin else "no plugin",
    }, code
