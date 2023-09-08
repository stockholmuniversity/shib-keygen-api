import importlib.metadata as importlib_metadata
import sys
from importlib.metadata import entry_points

from flask import Flask

app = Flask(__name__)


__metadata__ = importlib_metadata.metadata(__name__)
__version__ = __metadata__["Version"]

DEFAULT_PLUGIN = "stdout"
PLUGIN_GROUP = "shib_keygen_api.plugins"
PLUGIN = app.config.get("OUTPUT_PLUGIN", DEFAULT_PLUGIN)
output_plugin = next(
    iter(
        [
            ep
            for ep in entry_points().get(PLUGIN_GROUP, [])
            if ep.name == PLUGIN and ep.group == PLUGIN_GROUP
        ],
    ),
    None,
)
if not output_plugin:
    app.logger.fatal(
        "Tried to load plugin %r but failed to find it",
        PLUGIN,
    )
    sys.exit(1)

app.logger.info("Loaded output plugin %r", output_plugin.name)

output = output_plugin.load() if output_plugin else None
@app.route("/")
def index():
    return {
        "fax": "data",
        "version": __version__,
        "plugin": repr(output_plugin),
        "output": repr(output),
        "export": output.export() if output else "no plugin",
    }
