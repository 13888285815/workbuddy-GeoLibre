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
from typing import Any, Optional, Union

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

_HERE = pathlib.Path(__file__).parent

# Look for static files in several places
_STATIC_PATHS = [
    _HERE.parent.parent.parent / "web",             # project root /web directory
    _HERE / "static",                              # bundled with package
    _HERE.parent.parent.parent / "web-ui.html",    # project root (web-ui.html) - legacy
]

# Find the first existing static directory
def _resolve_static():
    """Resolve the static assets location."""
    # Check /web directory first (new structure)
    for p in _STATIC_PATHS:
        if p.is_dir() and (p / "index.html").exists():
            return p
    # Check /web directory without index.html check
    for p in _STATIC_PATHS:
        if p.is_dir() and p.name == "web":
            return p
    # Check static directory
    for p in _STATIC_PATHS:
        if p.is_dir():
            return p
    # Fallback to first path
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
    style: Optional[dict[str, Any]] = None


class TileLayer(BaseModel):
    name: str
    url: str
    tile_size: int = 256
    attribution: Optional[str] = None
    style: Optional[dict[str, Any]] = None


class ProjectState(BaseModel):
    project: dict[str, Any]


# In-memory project storage (use database in production)
_current_project: dict[str, Any] = {}

# File storage directory
_UPLOAD_DIR = _HERE.parent.parent.parent / "uploads"
_UPLOAD_DIR.mkdir(exist_ok=True)

# Projects storage directory
_PROJECTS_DIR = _HERE.parent.parent.parent / "projects"
_PROJECTS_DIR.mkdir(exist_ok=True)


# ── Web UI Routes ─────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page (index.html)."""
    if _HTML_FILE.exists():
        html_content = _HTML_FILE.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)

    # Fallback: try to serve from static directory
    index_path = _STATIC_DIR / "index.html"
    if index_path.exists():
        html_content = index_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)

    raise HTTPException(
        status_code=404,
        detail="index.html not found. Please ensure the static files are present.",
    )


# ── API Routes ────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "GeoLibre Web", "version": "1.0.0"}


@app.get("/api/project")
async def get_project():
    """Get the current project state."""
    # Try to load from file
    project_file = _PROJECTS_DIR / "current_project.json"
    if project_file.exists():
        try:
            content = project_file.read_text(encoding="utf-8")
            return JSONResponse(content=json.loads(content))
        except Exception:
            pass

    # Fallback to in-memory
    return JSONResponse(content=_current_project)


@app.post("/api/project")
async def save_project(project: ProjectState):
    """Save the current project state."""
    global _current_project
    _current_project = project.project

    # Save to file
    try:
        project_file = _PROJECTS_DIR / "current_project.json"
        project_file.write_text(
            json.dumps(_current_project, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"Warning: Could not save project to file: {e}")

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

    # Save GeoJSON to file
    try:
        geojson_file = _UPLOAD_DIR / f"{layer_data['id']}.geojson"
        geojson_file.write_text(
            json.dumps(layer.data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"Warning: Could not save GeoJSON to file: {e}")

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

            # Remove associated file if exists
            geojson_file = _UPLOAD_DIR / f"{layer_id}.geojson"
            if geojson_file.exists():
                geojson_file.unlink()

            return {"status": "success", "message": f"Layer {layer_id} removed"}

    raise HTTPException(status_code=404, detail=f"Layer {layer_id} not found")


@app.post("/api/layers/{layer_id}/style")
async def update_layer_style(layer_id: str, style: dict[str, Any]):
    """Update layer style."""
    global _current_project

    if "layers" not in _current_project:
        raise HTTPException(status_code=404, detail="No layers found")

    for layer in _current_project["layers"]:
        if layer.get("id") == layer_id:
            layer["style"] = style
            return {"status": "success", "message": f"Style updated for {layer_id}"}

    raise HTTPException(status_code=404, detail=f"Layer {layer_id} not found")


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (GeoJSON, GeoTIFF, etc.)."""
    try:
        content = await file.read()

        # Save file
        file_path = _UPLOAD_DIR / (file.filename or "unknown")
        file_path.write_bytes(content)

        # Try to parse GeoJSON
        if file.filename and file.filename.endswith(('.geojson', '.json')):
            try:
                geojson_data = json.loads(content.decode('utf-8'))

                # Validate GeoJSON
                if _validate_geojson(geojson_data):
                    return {
                        "status": "success",
                        "filename": file.filename,
                        "size": len(content),
                        "type": "geojson",
                        "data": geojson_data,
                    }
            except json.JSONDecodeError:
                pass

        return {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "url": f"/api/files/{file.filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/files/{filename}")
async def get_file(filename: str):
    """Get uploaded file."""
    file_path = _UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/api/bookmarks")
async def get_bookmarks():
    """Get all bookmarks."""
    bookmarks_file = _PROJECTS_DIR / "bookmarks.json"
    if not bookmarks_file.exists():
        return []
    try:
        content = bookmarks_file.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return []


@app.post("/api/bookmarks")
async def add_bookmark(bookmark: dict[str, Any]):
    """Add a bookmark."""
    bookmarks_file = _PROJECTS_DIR / "bookmarks.json"

    bookmarks = []
    if bookmarks_file.exists():
        try:
            content = bookmarks_file.read_text(encoding="utf-8")
            bookmarks = json.loads(content)
        except Exception:
            bookmarks = []

    bookmark["id"] = f"bookmark_{len(bookmarks)}"
    bookmark["timestamp"] = bookmark.get("timestamp", "")
    bookmarks.append(bookmark)

    try:
        bookmarks_file.write_text(
            json.dumps(bookmarks, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return {"status": "success", "bookmark_id": bookmark["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save bookmark: {str(e)}")


def _validate_geojson(data: dict) -> bool:
    """Validate GeoJSON structure."""
    valid_types = ['Feature', 'FeatureCollection', 'Point', 'LineString', 'Polygon',
                   'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']

    if not isinstance(data, dict):
        return False

    if "type" not in data or data["type"] not in valid_types:
        return False

    return True


# Mount static directory for any other static assets
if _STATIC_DIR.exists():
    # Check if it's the web directory with subdirectories
    css_dir = _STATIC_DIR / "css"
    js_dir = _STATIC_DIR / "js"
    img_dir = _STATIC_DIR / "img"

    # Mount main static directory
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # Also mount subdirectories if they exist
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    if img_dir.exists():
        app.mount("/img", StaticFiles(directory=str(img_dir)), name="img")


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

    print(f"\n📁 Static files directory: {_STATIC_DIR}")
    print(f"📁 Uploads directory: {_UPLOAD_DIR}")
    print(f"📁 Projects directory: {_PROJECTS_DIR}\n")

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
