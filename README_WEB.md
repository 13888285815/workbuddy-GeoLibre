# GeoLibre Web UI 使用指南

## 🌍 概述

GeoLibre 现在支持通过 Web UI 进行访问，无需 Jupyter Notebook 即可使用地图功能。

## 📋 前置要求

- Python 3.8+
- FastAPI
- Uvicorn

## 🚀 快速开始

### 方式 1: 使用启动脚本（推荐）

```bash
chmod +x start_web.sh
./start_web.sh
```

### 方式 2: 手动启动 API 服务器

```bash
cd python
pip install fastapi uvicorn python-multipart
python -m geolibre.web_app
```

访问 http://localhost:8000

### 方式 3: 使用 uvicorn（开发模式）

```bash
uvicorn geolibre.web_app:app --host 0.0.0.0 --port 8000 --reload
```

### 方式 4: 纯静态 HTML（无 API）

直接在浏览器中打开 `web-ui.html` 文件。

## 📡 API 端点

### 健康检查
```
GET /api/health
```

### 项目管理
```
GET  /api/project       # 获取当前项目
POST /api/project       # 保存项目
```

### 图层管理
```
POST   /api/layers/geojson     # 添加 GeoJSON 图层
POST   /api/layers/tile        # 添加瓦片图层
DELETE /api/layers/{layer_id}  # 删除图层
```

### 文件上传
```
POST /api/files/upload   # 上传文件
```

## 📖 API 文档

启动服务器后访问 http://localhost:8000/docs 查看交互式 API 文档（Swagger UI）。

## 🎨 Web UI 功能

### GeoJSON 图层
- 输入 GeoJSON 数据
- 自定义图层名称
- 添加到地图

### 瓦片图层
- 支持标准 XYZ 瓦片
- 自定义 URL 模板
- 设置归属信息

### 地图配置
- 设置地图中心
- 调整缩放级别
- 切换主题（浅色/深色）

### 项目管理
- 保存当前项目
- 加载已保存项目
- 图层列表管理

## 🔧 开发说明

### 添加新的 API 端点

编辑 `python/src/geolibre/web_app.py`:

```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"message": "Custom endpoint"}
```

### 自定义 Web UI

编辑 `web-ui.html` 文件，修改样式和功能。

### 集成现有 GeoLibre 功能

```python
from geolibre import Map

# 创建地图
m = Map(center=[116.4074, 39.9042], zoom=10)

# 添加图层
m.add_geojson("data.geojson")
m.add_tile_layer("https://tile.openstreetmap.org/{z}/{x}/{y}.png")

# 获取项目状态
project = m.to_project()
```

## 🌐 生产部署

### 使用 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY python /app/python
RUN pip install -e /app/python

EXPOSE 8000
CMD ["python", "-m", "geolibre.web_app"]
```

```bash
docker build -t geolibre-web .
docker run -p 8000:8000 geolibre-web
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name geolibre.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用 HTTPS

```bash
uvicorn geolibre.web_app:app \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

## 🔐 安全注意事项

1. **CORS**: 生产环境请修改 `allow_origins` 为具体域名
2. **认证**: 添加用户认证（JWT、OAuth 等）
3. **数据持久化**: 使用数据库代替内存存储
4. **文件上传**: 限制文件类型和大小

## 📝 示例代码

### 使用 JavaScript 调用 API

```javascript
// 添加 GeoJSON 图层
async function addLayer() {
    const response = await fetch('http://localhost:8000/api/layers/geojson', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: 'My Layer',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [116.4074, 39.9042]
                },
                properties: {}
            }
        })
    });
    
    const result = await response.json();
    console.log(result);
}
```

### 使用 curl 测试 API

```bash
# 健康检查
curl http://localhost:8000/api/health

# 添加图层
curl -X POST http://localhost:8000/api/layers/geojson \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Layer",
    "data": {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [0, 0]
      },
      "properties": {}
    }
  }'

# 获取项目
curl http://localhost:8000/api/project
```

## 🐛 故障排除

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000

# 使用其他端口
python -m geolibre.web_app --port 8001
```

### 模块未找到
```bash
# 确保在正确目录
cd python
pip install -e .
```

### CORS 错误
检查浏览器控制台，确保 API 服务器正在运行。

## 📚 相关文档

- [GeoLibre 官方文档](https://geolibre.app)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)

## 💡 提示

1. **开发模式**: 使用 `--reload` 参数自动重载代码
2. **调试**: 访问 `/docs` 查看交互式 API 文档
3. **性能**: 生产环境使用 Gunicorn + Uvicorn
4. **监控**: 添加日志和健康检查端点

## 📞 获取帮助

- GitHub Issues: https://github.com/opengeos/GeoLibre/issues
- 文档: https://geolibre.app
