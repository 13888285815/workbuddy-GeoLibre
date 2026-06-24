"""Standalone web application for GeoLibre.

This module provides a FastAPI-based web server that allows GeoLibre to be
accessed through a web browser without requiring Jupyter notebook. It serves
the bundled web-ui.html and provides REST API endpoints for map operations.

Usage:
    python -m geolibre.web_app
    or
    uvicorn geolibre.web_app:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

_HERE = pathlib.Path(__file__).parent

# Look for web-ui.html / static/index.html in several places
_STATIC_PATHS = [
    _HERE / "static",                              # bundled with package
    _HERE.parent.parent.parent / "web-ui.html",    # project root (web-ui.html)
]

# Find the first existing static directory or file
def _resolve_static():
    """Resolve the static assets or web-ui.html location."""
    # Check static directory with index.html first
    for p in _STATIC_PATHS:
        if p.is_dir() and (p / "index.html").exists():
            return p
    # Check direct web-ui.html
    for p in _STATIC_PATHS:
        if p.is_file():
            return p.parent
    return _STATIC_PATHS[0]

_STATIC_DIR = _resolve_static()
_HTML_FILE = _STATIC_DIR / "index.html"

app = FastAPI(
    title="GeoLibre Web",
    description="A free and open-source, lightweight, cloud-native GIS platform",
    version="1.0.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API Models ─────────────────────────────────────────────────────

class GeoJSONLayer(BaseModel):
    name: str
    data: dict[str, Any]
    style: dict[str, Any] | None = None


class TileLayer(BaseModel):
    name: str
    url: str
    tile_size: int = 256
    attribution: str | None = None
    style: dict[str, Any] | None = None


class ProjectState(BaseModel):
    project: dict[str, Any]


# In-memory project storage (use database in production)
_current_project: dict[str, Any] = {}


# ── Web UI Routes ─────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page (web-ui.html)."""
    if _HTML_FILE.exists():
        html_content = _HTML_FILE.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    raise HTTPException(
        status_code=404,
        detail="web-ui.html not found. Please ensure the static file is present.",
    )


# ── API Routes ────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "GeoLibre Web", "version": "1.0.0"}


@app.get("/api/project")
async def get_project():
    """Get the current project state."""
    return JSONResponse(content=_current_project)


@app.post("/api/project")
async def save_project(project: ProjectState):
    """Save the current project state."""
    global _current_project
    _current_project = project.project
    return {"status": "success", "message": "Project saved", "layers": len(_current_project.get("layers", []))}


@app.post("/api/layers/geojson")
async def add_geojson_layer(layer: GeoJSONLayer):
    """Add a GeoJSON layer to the project."""
    global _current_project

    if "layers" not in _current_project:
        _current_project["layers"] = []

    layer_data = {
        "id": f"geojson_{len(_current_project['layers'])}",
        "type": "geojson",
        "name": layer.name,
        "data": layer.data,
        "style": layer.style or {},
    }
    _current_project["layers"].append(layer_data)

    return {"status": "success", "layer_id": layer_data["id"]}


@app.post("/api/layers/tile")
async def add_tile_layer(layer: TileLayer):
    """Add a tile layer to the project."""
    global _current_project

    if "layers" not in _current_project:
        _current_project["layers"] = []

    layer_data = {
        "id": f"tile_{len(_current_project['layers'])}",
        "type": "tile",
        "name": layer.name,
        "url": layer.url,
        "tile_size": layer.tile_size,
        "attribution": layer.attribution,
        "style": layer.style or {},
    }
    _current_project["layers"].append(layer_data)

    return {"status": "success", "layer_id": layer_data["id"]}


@app.delete("/api/layers/{layer_id}")
async def remove_layer(layer_id: str):
    """Remove a layer from the project."""
    global _current_project

    if "layers" not in _current_project:
        raise HTTPException(status_code=404, detail="No layers found")

    for i, layer in enumerate(_current_project["layers"]):
        if layer.get("id") == layer_id:
            _current_project["layers"].pop(i)
            return {"status": "success", "message": f"Layer {layer_id} removed"}

    raise HTTPException(status_code=404, detail=f"Layer {layer_id} not found")


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (GeoJSON, GeoTIFF, etc.)."""
    return {
        "status": "success",
        "filename": file.filename or "unknown",
        "size": file.size or 0,
        "url": f"/api/files/{file.filename}",
    }


# Mount static directory for any other static assets
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


# ── CLI Entry Point ───────────────────────────────────────────────

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the web server."""
    import uvicorn

    print("╔══════════════════════════════════════════════════╗")
    print("║       🌍  GeoLibre Web UI                       ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║   Local:   http://localhost:{port}                  ║")
    print(f"║   API:     http://localhost:{port}/docs             ║")
    print("║   Health:  http://localhost:{port}/api/health   ║".format(port=port))
    print("╠══════════════════════════════════════════════════╣")
    print("║   Press Ctrl+C to stop                          ║")
    print("╚══════════════════════════════════════════════════╝")
    uvicorn.run("geolibre.web_app:app", host=host, port=port, reload=reload)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="GeoLibre Web UI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
