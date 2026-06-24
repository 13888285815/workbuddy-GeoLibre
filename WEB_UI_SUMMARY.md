# GeoLibre Web UI 修改总结

## 修改内容

### 1. 重写 `python/src/geolibre/web_app.py`
- **FastAPI 后端**：完整的 RESTful API
- **静态文件服务**：自动从 `python/src/geolibre/static/` 提供 `web-ui.html`
- **CLI 入口**：支持 `--host`, `--port`, `--reload` 参数
- **自动路径解析**：能自动在包内和项目根目录查找静态文件
- 服务访问: `http://localhost:8000` (前端), `http://localhost:8000/docs` (API 文档)

### 2. 重写 `python/src/geolibre/static/index.html` + `web-ui.html`
- 用 **Leaflet** 替换外部 iframe，不再依赖 `viewer.geolibre.app`
- 内置地图渲染，支持：
  - 📍 添加/删除 GeoJSON 图层（带弹窗属性展示）
  - 🗺️ 添加/删除瓦片图层
  - 🎯 飞往指定坐标
  - 💾 保存/加载项目
  - 📊 API 健康状态检测
  - 🖱️ 鼠标坐标实时显示
- 离线降级：后端不可用时前端仍可用（本地添加图层）

### 3. 重写 `start_web.sh`
- 自动检测 Python 环境
- 自动安装缺失依赖（fastapi, uvicorn, python-multipart）
- 交互式菜单（启动服务器 / 打开静态HTML / 退出）
- 更好的输出格式

### 4. 更新 `Dockerfile.web`
- 复制静态 HTML 到包目录
- 使用 urllib 替代 requests 做健康检查（减少依赖）

### 5. 更新 `test_web_api.py`
- 修复了删除测试的递归 bug
- 用标准库 `urllib` 替代 `requests`（零依赖）

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/` | Web UI HTML 页面 |
| GET  | `/api/health` | 健康检查 |
| GET  | `/api/project` | 获取项目状态 |
| POST | `/api/project` | 保存项目 |
| POST | `/api/layers/geojson` | 添加 GeoJSON 图层 |
| POST | `/api/layers/tile` | 添加瓦片图层 |
| DELETE | `/api/layers/{id}` | 删除图层 |
| POST | `/api/files/upload` | 上传文件 |

## 启动方式

```bash
# 方式 1: 启动脚本
./start_web.sh

# 方式 2: 直接运行
cd python
pip install fastapi uvicorn python-multipart
PYTHONPATH=src python -m geolibre.web_app

# 方式 3: 开发模式（热重载）
PYTHONPATH=src python -m geolibre.web_app --reload

# 方式 4: Docker
docker build -f Dockerfile.web -t geolibre-web .
docker run -p 8000:8000 geolibre-web
```
