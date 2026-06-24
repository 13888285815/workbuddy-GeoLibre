#!/usr/bin/env python3
"""Test script for GeoLibre Web UI API."""

import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_URL = "http://localhost:8000/api"


def _req(method, path, data=None):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def test_health():
    try:
        r = _req("GET", "health")
        print(f"✅ Health check: {r}")
        return True
    except URLError as e:
        print(f"❌ Server unreachable: {e.reason}")
        return False


def test_add_geojson():
    data = {
        "name": "Beijing Point",
        "data": {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [116.4, 39.9]},
            "properties": {"name": "Beijing", "population": 21_540_000},
        },
    }
    r = _req("POST", "layers/geojson", data)
    print(f"✅ Added GeoJSON layer: id={r.get('layer_id')}")
    return r["layer_id"]


def test_add_tile():
    data = {
        "name": "OSM",
        "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "© OpenStreetMap contributors",
    }
    r = _req("POST", "layers/tile", data)
    print(f"✅ Added tile layer: id={r.get('layer_id')}")
    return r["layer_id"]


def test_get_project():
    r = _req("GET", "project")
    n = len(r.get("layers", []))
    print(f"✅ Project: {n} layer(s)")
    return r


def test_del_layer(layer_id):
    r = _req("DELETE", f"layers/{layer_id}")
    print(f"✅ Deleted layer {layer_id}: {r}")
    return r


def main():
    print("─" * 45)
    print("🌍  GeoLibre Web UI — API 测试")
    print("─" * 45)

    if not test_health():
        print("\n❌ 服务器未启动。请先运行:")
        print("   cd python && python -m geolibre.web_app")
        sys.exit(1)

    print()
    gid = test_add_geojson()
    print()
    tid = test_add_tile()
    print()
    test_get_project()
    print()
    test_del_layer(gid)
    test_del_layer(tid)
    print()
    print("✅ 全部测试通过!")


if __name__ == "__main__":
    main()
