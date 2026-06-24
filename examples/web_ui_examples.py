"""
GeoLibre Web UI Example Scripts

This file demonstrates how to use GeoLibre Web UI programmatically.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"


def example_1_add_beijing_markers():
    """Example 1: Add markers for major cities in China"""
    print("📍 Example 1: Adding Chinese city markers...")
    
    cities = [
        {"name": "Beijing", "coords": [116.4074, 39.9042], "population": 21540000},
        {"name": "Shanghai", "coords": [121.4737, 31.2304], "population": 24280000},
        {"name": "Guangzhou", "coords": [113.2644, 23.1291], "population": 15300000},
        {"name": "Shenzhen", "coords": [114.0579, 22.5431], "population": 17560000},
        {"name": "Chengdu", "coords": [104.0665, 30.5728], "population": 16330000},
    ]
    
    for city in cities:
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": city["coords"]
            },
            "properties": {
                "name": city["name"],
                "population": city["population"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/layers/geojson",
            json={"name": city["name"], "data": geojson}
        )
        
        if response.status_code == 200:
            print(f"  ✅ Added {city['name']}")
        else:
            print(f"  ❌ Failed to add {city['name']}")
    
    print()


def example_2_add_china_boundary():
    """Example 2: Add China boundary polygon"""
    print("🗺️  Example 2: Adding China boundary...")
    
    # Simplified China boundary (approximate)
    china_boundary = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [73.5, 39.5],
                [80.0, 35.0],
                [87.0, 28.0],
                [97.0, 28.5],
                [106.0, 22.5],
                [108.0, 18.5],
                [110.0, 20.0],
                [117.0, 23.5],
                [120.0, 25.0],
                [122.0, 30.0],
                [124.0, 40.0],
                [130.0, 42.5],
                [135.0, 48.5],
                [127.0, 50.0],
                [120.0, 52.0],
                [100.0, 50.0],
                [87.0, 49.0],
                [73.5, 39.5]
            ]]
        },
        "properties": {
            "name": "China",
            "area_km2": 9596961
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/layers/geojson",
        json={
            "name": "China Boundary",
            "data": china_boundary,
            "style": {
                "fillColor": "#4CAF50",
                "fillOpacity": 0.3,
                "strokeColor": "#2E7D32",
                "strokeWidth": 2
            }
        }
    )
    
    if response.status_code == 200:
        print(f"  ✅ Added China boundary")
    else:
        print(f"  ❌ Failed to add China boundary")
    
    print()


def example_3_add_tile_layers():
    """Example 3: Add various tile layers"""
    print("🗺️  Example 3: Adding tile layers...")
    
    tile_layers = [
        {
            "name": "OpenStreetMap",
            "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "attribution": "© OpenStreetMap contributors"
        },
        {
            "name": "Satellite (ESRI)",
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attribution": "© Esri"
        },
        {
            "name": "Topographic",
            "url": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            "attribution": "© OpenTopoMap"
        }
    ]
    
    for tile in tile_layers:
        response = requests.post(
            f"{BASE_URL}/layers/tile",
            json=tile
        )
        
        if response.status_code == 200:
            print(f"  ✅ Added {tile['name']}")
        else:
            print(f"  ❌ Failed to add {tile['name']}")
    
    print()


def example_4_query_project():
    """Example 4: Query current project state"""
    print("📊 Example 4: Querying project state...")
    
    response = requests.get(f"{BASE_URL}/project")
    
    if response.status_code == 200:
        project = response.json()
        layer_count = len(project.get("layers", []))
        print(f"  ✅ Current project has {layer_count} layers")
        
        # Print layer details
        for i, layer in enumerate(project.get("layers", []), 1):
            print(f"     {i}. {layer.get('name')} ({layer.get('type')})")
    else:
        print(f"  ❌ Failed to query project")
    
    print()


def example_5_clear_all_layers():
    """Example 5: Clear all layers"""
    print("🗑️  Example 5: Clearing all layers...")
    
    # Get current project
    response = requests.get(f"{BASE_URL}/project")
    
    if response.status_code == 200:
        project = response.json()
        layers = project.get("layers", [])
        
        print(f"  Found {len(layers)} layers to delete...")
        
        for layer in layers:
            layer_id = layer.get("id")
            if layer_id:
                response = requests.delete(f"{BASE_URL}/layers/{layer_id}")
                if response.status_code == 200:
                    print(f"  ✅ Deleted {layer.get('name')}")
                else:
                    print(f"  ❌ Failed to delete {layer.get('name')}")
    else:
        print(f"  ❌ Failed to get project")
    
    print()


def main():
    print("\n" + "="*60)
    print("🌍 GeoLibre Web UI - Example Scripts")
    print("="*60 + "\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ Server is not running!")
        print("   Please start the server first:")
        print("   python -m geolibre.web_app\n")
        return
    
    # Run examples
    example_1_add_beijing_markers()
    example_2_add_china_boundary()
    example_3_add_tile_layers()
    example_4_query_project()
    
    # Ask user before clearing
    print("\n⚠️  Press Enter to clear all layers, or Ctrl+C to exit...")
    try:
        input()
        example_5_clear_all_layers()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("🌐 Open http://localhost:8000 to view the map")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
