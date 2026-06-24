"""GeoLibre for Jupyter: the full GeoLibre GIS app as an anywidget."""

from typing import Any

from .geolibre import Feature, Layer, Map

__version__ = "1.7.0"
__all__ = ["Feature", "Layer", "Map", "__version__", "run_web_server"]


def run_web_server(host: str = "0.0.0.0", port: int = 8000):
    """
    启动 GeoLibre Web UI 服务器
    
    Args:
        host: 服务器监听地址，默认 0.0.0.0（所有接口）
        port: 服务器端口，默认 8000
    
    Example:
        >>> from geolibre import run_web_server
        >>> run_web_server(port=8000)
    """
    from .web_app import run_server
    run_server(host=host, port=port)


def _jupyter_server_extension_points() -> list[dict[str, str]]:
    """Declare the Jupyter Server extension that serves the bundled app."""
    return [{"module": "geolibre"}]


def _load_jupyter_server_extension(serverapp: Any) -> None:
    """Entry point called by Jupyter Server when the extension loads."""
    from ._extension import load_jupyter_server_extension

    load_jupyter_server_extension(serverapp)
