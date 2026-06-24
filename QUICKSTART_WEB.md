# 🚀 GeoLibre Web UI 快速启动指南

## ⚡ 3 分钟快速开始

### 方式 1: 使用 Python（推荐）

```bash
# 1. 进入项目目录
cd /Users/zzx/Desktop/ai源码/workbuddy-GeoLibre/python

# 2. 安装依赖（首次运行）
pip install fastapi uvicorn python-multipart

# 3. 启动服务器
python -m geolibre.web_app

# 4. 打开浏览器
# 访问 http://localhost:8000
```

### 方式 2: 直接打开 HTML（无需服务器）

```bash
# 在项目根目录
open web-ui.html
```

### 方式 3: 使用 Docker

```bash
# 构建镜像
docker build -f Dockerfile.web -t geolibre-web .

# 运行容器
docker run -p 8000:8000 geolibre-web
```

## 📋 验证安装

打开浏览器访问：

- **Web UI**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## 🧪 测试 API

### 使用 Python 测试脚本

```bash
python test_web_api.py
```

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/api/health

# 添加 GeoJSON 图层
curl -X POST http://localhost:8000/api/layers/geojson \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Point",
    "data": {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [116.4, 39.9]},
      "properties": {"name": "Beijing"}
    }
  }'

# 获取项目状态
curl http://localhost:8000/api/project
```

## 🎯 功能演示

运行示例脚本：

```bash
cd examples
python web_ui_examples.py
```

## 🔧 配置选项

### 修改端口

```bash
# 方式 1: 使用 Python
python -m geolibre.web_app --port 9000

# 方式 2: 使用 uvicorn
uvicorn geolibre.web_app:app --port 9000
```

### 允许外部访问

```bash
# 绑定到所有网络接口
python -m geolibre.web_app --host 0.0.0.0 --port 8000
```

### 使用自定义配置

创建配置文件 `config.py`:

```python
# geolibre_config.py
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
DEBUG = True
```

然后启动：

```bash
python -m geolibre.web_app --config geolibre_config.py
```

## 📦 依赖安装

### 最小依赖

```bash
pip install fastapi uvicorn
```

### 完整依赖

```bash
pip install -r requirements-web.txt
```

## 🐛 故障排除

### 问题 1: 端口被占用

```bash
# 查找占用进程
lsof -i :8000

# 终止进程
kill -9 <PID>

# 或使用其他端口
python -m geolibre.web_app --port 8001
```

### 问题 2: 模块未找到

```bash
# 确保在正确目录
cd python

# 安装包
pip install -e .
```

### 问题 3: CORS 错误

检查 `web_app.py` 中的 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 修改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 4: 静态文件 404

确保已构建前端资源：

```bash
# 在项目根目录
npm install
npm run build:embed
```

## 🌐 生产部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker geolibre.web_app:app
```

### 使用 Systemd

创建服务文件 `/etc/systemd/system/geolibre-web.service`:

```ini
[Unit]
Description=GeoLibre Web UI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/geolibre/python
ExecStart=/usr/bin/python3 -m geolibre.web_app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl start geolibre-web
sudo systemctl enable geolibre-web
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📚 下一步

- 查看 [Web UI 完整文档](README_WEB.md)
- 阅读 [API 文档](http://localhost:8000/docs)
- 运行 [示例代码](examples/web_ui_examples.py)
- 了解 [GeoLibre 官方文档](https://geolibre.app)

## 💡 提示

1. **开发模式**: 使用 `--reload` 自动重载代码
2. **调试**: 查看 `/docs` 页面测试 API
3. **日志**: 添加 `--log-level debug` 查看详细日志
4. **性能**: 生产环境使用 Gunicorn + 多进程

## 🆘 获取帮助

- GitHub: https://github.com/opengeos/GeoLibre
- 文档: https://geolibre.app
- 问题反馈: https://github.com/opengeos/GeoLibre/issues
