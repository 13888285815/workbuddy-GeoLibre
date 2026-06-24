/**
 * GeoLibre Web GIS - Main Application
 */

// Configuration
const CONFIG = {
    apiBase: '/api',
    mapCenter: [105, 35],
    mapZoom: 4
};

// Application State
const state = {
    map: null,
    layers: [],
    activeTool: null,
    theme: localStorage.getItem('geolibre_theme') || 'light'
};

/**
 * Initialize application
 */
function initApp() {
    console.log('🌍 GeoLibre Web GIS Initializing...');

    initTheme();
    initMap();
    initUI();
    checkAPI();

    console.log('✅ GeoLibre Web GIS Initialized');
    showNotification('GeoLibre Web GIS 已加载', 'success');
}

/**
 * Initialize theme
 */
function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = state.theme === 'dark'
            ? '<i class="fas fa-sun"></i>'
            : '<i class="fas fa-moon"></i>';

        themeToggle.addEventListener('click', () => {
            state.theme = state.theme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', state.theme);
            localStorage.setItem('geolibre_theme', state.theme);

            themeToggle.innerHTML = state.theme === 'dark'
                ? '<i class="fas fa-sun"></i>'
                : '<i class="fas fa-moon"></i>';
        });
    }
}

/**
 * Initialize map
 */
function initMap() {
    state.map = new maplibregl.Map({
        container: 'map',
        style: {
            version: 8,
            sources: {
                'osm': {
                    type: 'raster',
                    tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '© OpenStreetMap contributors'
                }
            },
            layers: [{
                id: 'osm',
                type: 'raster',
                source: 'osm'
            }]
        },
        center: CONFIG.mapCenter,
        zoom: CONFIG.mapZoom
    });

    // Add navigation control
    state.map.addControl(new maplibregl.NavigationControl(), 'top-right');

    // Map event listeners
    state.map.on('mousemove', (e) => {
        updateCoords(e.lngLat.lng, e.lngLat.lat);
    });

    state.map.on('moveend', () => {
        updateMapInfo();
    });

    state.map.on('load', () => {
        console.log('Map loaded');
        updateMapInfo();
    });
}

/**
 * Initialize UI
 */
function initUI() {
    // Sidebar tabs
    document.querySelectorAll('.sidebar-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });

    // Add layer options
    document.querySelectorAll('.add-option').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const type = e.currentTarget.dataset.type;
            showAddForm(type);
        });
    });

    // Add GeoJSON button
    const addGeoJSONBtn = document.getElementById('addGeoJSONBtn');
    if (addGeoJSONBtn) {
        addGeoJSONBtn.addEventListener('click', addGeoJSONLayer);
    }

    // Add Tile button
    const addTileBtn = document.getElementById('addTileBtn');
    if (addTileBtn) {
        addTileBtn.addEventListener('click', addTileLayer);
    }

    // Toggle left sidebar
    const toggleLeft = document.getElementById('toggleLeftSidebar');
    if (toggleLeft) {
        toggleLeft.addEventListener('click', () => {
            const sidebar = document.getElementById('leftSidebar');
            sidebar.classList.toggle('collapsed');
        });
    }

    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchLocation(e.target.value);
            }
        });
    }
}

/**
 * Switch tab
 */
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.sidebar-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    const activeTab = document.querySelector(`.sidebar-tab[data-tab="${tabName}"]`);
    if (activeTab) activeTab.classList.add('active');

    // Update tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    const activePanel = document.getElementById(`tab-${tabName}`);
    if (activePanel) activePanel.classList.add('active');
}

/**
 * Show add form
 */
function showAddForm(type) {
    // Hide all forms
    document.querySelectorAll('.add-form').forEach(form => {
        form.classList.remove('active');
        form.classList.add('hidden');
    });

    // Show selected form
    const form = document.getElementById(`form-${type}`);
    if (form) {
        form.classList.remove('hidden');
        form.classList.add('active');
    }
}

/**
 * Add GeoJSON layer
 */
function addGeoJSONLayer() {
    const nameInput = document.getElementById('geojsonName');
    const dataInput = document.getElementById('geojsonData');

    const name = nameInput?.value || 'GeoJSON Layer';
    const dataStr = dataInput?.value?.trim();

    if (!dataStr) {
        showNotification('请输入 GeoJSON 数据', 'error');
        return;
    }

    let data;
    try {
        data = JSON.parse(dataStr);
    } catch (error) {
        showNotification('JSON 格式错误: ' + error.message, 'error');
        return;
    }

    // Add to map
    addGeoJSONToMap(name, data);

    // Save to backend
    fetch(`${CONFIG.apiBase}/layers/geojson`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, data, style: {} })
    }).catch(err => console.log('Backend save failed', err));

    showNotification(`✅ 图层 "${name}" 添加成功`, 'success');

    // Clear inputs
    if (nameInput) nameInput.value = '';
    if (dataInput) dataInput.value = '';
}

/**
 * Add GeoJSON to map
 */
function addGeoJSONToMap(name, data) {
    const map = state.map;
    const layerId = 'geojson_' + Date.now();

    // Add source
    map.addSource(layerId, {
        type: 'geojson',
        data: data
    });

    // Add layer
    map.addLayer({
        id: layerId,
        type: 'circle',
        source: layerId,
        paint: {
            'circle-radius': 8,
            'circle-color': '#3b82f6',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#1e40ab'
        }
    });

    // Store layer info
    state.layers.push({
        id: layerId,
        name: name,
        type: 'geojson',
        visible: true
    });

    renderLayers();
    updateFooter();

    // Fit to bounds
    try {
        const bounds = getGeoJSONBounds(data);
        if (bounds) {
            map.fitBounds(bounds, { padding: 50 });
        }
    } catch (e) {
        console.log('Could not fit to bounds', e);
    }
}

/**
 * Add tile layer
 */
function addTileLayer() {
    const nameInput = document.getElementById('tileName');
    const urlInput = document.getElementById('tileUrl');

    const name = nameInput?.value || 'Tile Layer';
    const url = urlInput?.value?.trim();

    if (!url) {
        showNotification('请输入瓦片 URL', 'error');
        return;
    }

    const map = state.map;
    const sourceId = 'tile_' + Date.now();
    const layerId = 'tile_layer_' + Date.now();

    // Add source
    map.addSource(sourceId, {
        type: 'raster',
        tiles: [url],
        tileSize: 256
    });

    // Add layer
    map.addLayer({
        id: layerId,
        type: 'raster',
        source: sourceId
    });

    // Store layer info
    state.layers.push({
        id: layerId,
        name: name,
        type: 'tile',
        visible: true,
        sourceId: sourceId
    });

    renderLayers();
    updateFooter();

    showNotification(`✅ 瓦片图层 "${name}" 添加成功`, 'success');
}

/**
 * Render layers list
 */
function renderLayers() {
    const container = document.getElementById('layerList');
    if (!container) return;

    if (state.layers.length === 0) {
        container.innerHTML = '<div class="layer-empty"><p>暂无图层</p></div>';
        return;
    }

    container.innerHTML = state.layers.map((layer, index) => `
        <div class="layer-item">
            <i class="fas ${layer.type === 'geojson' ? 'fa-map-marker-alt' : 'fa-th'}"></i>
            <span>${layer.name}</span>
            <button onclick="removeLayer(${index})" class="btn-icon">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
}

/**
 * Remove layer
 */
function removeLayer(index) {
    const layer = state.layers[index];
    if (!layer) return;

    const map = state.map;

    // Remove from map
    if (map.getLayer(layer.id)) {
        map.removeLayer(layer.id);
    }
    if (layer.sourceId && map.getSource(layer.sourceId)) {
        map.removeSource(layer.sourceId);
    } else if (map.getSource(layer.id)) {
        map.removeSource(layer.id);
    }

    // Remove from state
    state.layers.splice(index, 1);

    renderLayers();
    updateFooter();

    showNotification(`🗑️ 图层已删除`, 'success');
}

/**
 * Update coordinates display
 */
function updateCoords(lng, lat) {
    const coordsEl = document.getElementById('mapCoords');
    if (coordsEl) {
        coordsEl.textContent = `经度: ${lng.toFixed(4)} 纬度: ${lat.toFixed(4)}`;
    }
}

/**
 * Update map info in footer
 */
function updateMapInfo() {
    const map = state.map;
    if (!map) return;

    const center = map.getCenter();
    const zoom = map.getZoom();

    const centerEl = document.getElementById('footerCenter');
    const zoomEl = document.getElementById('footerZoom');

    if (centerEl) {
        centerEl.textContent = `${center.lat.toFixed(2)}, ${center.lng.toFixed(2)}`;
    }
    if (zoomEl) {
        zoomEl.textContent = `缩放: ${zoom.toFixed(1)}`;
    }
}

/**
 * Update footer
 */
function updateFooter() {
    const layersEl = document.getElementById('footerLayers');
    if (layersEl) {
        layersEl.textContent = `图层: ${state.layers.length}`;
    }
}

/**
 * Get GeoJSON bounds
 */
function getGeoJSONBounds(data) {
    if (data.type === 'FeatureCollection') {
        const bounds = new maplibregl.LngLatBounds();
        data.features.forEach(feature => {
            extendBounds(bounds, feature.geometry);
        });
        return bounds;
    } else if (data.type === 'Feature') {
        const bounds = new maplibregl.LngLatBounds();
        extendBounds(bounds, data.geometry);
        return bounds;
    }
    return null;
}

/**
 * Extend bounds with geometry
 */
function extendBounds(bounds, geometry) {
    if (geometry.type === 'Point') {
        bounds.extend(geometry.coordinates);
    } else if (geometry.type === 'LineString' || geometry.type === 'MultiPoint') {
        geometry.coordinates.forEach(coord => bounds.extend(coord));
    }
}

/**
 * Search location
 */
async function searchLocation(query) {
    if (!query || query.length < 3) return;

    try {
        showNotification('搜索中...', 'info', 1000);

        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
        );
        const results = await response.json();

        if (results.length > 0) {
            const result = results[0];
            const lat = parseFloat(result.lat);
            const lon = parseFloat(result.lon);

            state.map.flyTo({
                center: [lon, lat],
                zoom: 12,
                duration: 2000
            });

            showNotification(`已定位到: ${result.display_name}`, 'success');
        } else {
            showNotification('未找到相关位置', 'error');
        }
    } catch (error) {
        showNotification('搜索失败: ' + error.message, 'error');
    }
}

/**
 * Check API health
 */
async function checkAPI() {
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('apiStatusLabel');

    try {
        const response = await fetch(`${CONFIG.apiBase}/health`);
        if (response.ok) {
            dot.className = 'status-dot online';
            label.textContent = '已连接 ✅';
        } else {
            throw new Error('API not ok');
        }
    } catch (error) {
        dot.className = 'status-dot offline';
        label.textContent = '离线 ❌';
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 4000) {
    const container = document.getElementById('notifications');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    container.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', initApp);
