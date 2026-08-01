# plugins/__init__.py

from .nrp_plugin import NRPPlugin

PLUGIN_REGISTRY = {
    "nrp": NRPPlugin,
}
