#!/usr/bin/env python3
"""天地图瓦片代理服务器 + 静态文件服务
天地图WAF会拒绝带有Origin/Referer头的请求。浏览器跨域加载瓦片时自动携带Origin头，
导致MapLibre无法直接加载天地图瓦片。本服务器作为中间代理：
- 静态文件请求：直接返回
- /tile-proxy/?url=<encoded_url>：转发到天地图，剥离Origin/Referer头
"""
import http.server
import http.client
import urllib.parse
import ssl
import os
import sys
import signal

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9091
DIR = os.path.dirname(os.path.abspath(__file__))

# 允许代理的目标域名
ALLOWED_HOSTS = [
    't0.tianditu.gov.cn', 't1.tianditu.gov.cn', 't2.tianditu.gov.cn',
    't3.tianditu.gov.cn', 't4.tianditu.gov.cn', 't5.tianditu.gov.cn',
    't6.tianditu.gov.cn', 't7.tianditu.gov.cn',
]


class TileProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/tile-proxy/':
            self._proxy_tile(parsed)
        else:
            super().do_GET()

    def end_headers(self):
        # 静态文件禁用缓存，确保开发时拿到最新版本
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def _proxy_tile(self, parsed):
        params = urllib.parse.parse_qs(parsed.query)
        target_url = params.get('url', [None])[0]

        if not target_url:
            self.send_error(400, 'Missing url parameter')
            return

        target_parsed = urllib.parse.urlparse(target_url)
        if target_parsed.hostname not in ALLOWED_HOSTS:
            self.send_error(403, f'Host not allowed: {target_parsed.hostname}')
            return

        try:
            # 建立HTTPS连接并发送请求（不带Origin/Referer）
            ctx = ssl.create_default_context()
            conn = http.client.HTTPSConnection(
                target_parsed.hostname,
                timeout=10,
                context=ctx
            )

            path_with_query = target_parsed.path
            if target_parsed.query:
                path_with_query += '?' + target_parsed.query

            headers = {
                'User-Agent': 'TileProxy/1.0',
                'Accept': 'image/png,image/*,*/*',
            }

            conn.request('GET', path_with_query, headers=headers)
            resp = conn.getresponse()
            body = resp.read()

            # 返回瓦片，添加CORS头
            self.send_response(resp.status)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.send_header('Content-Type', resp.getheader('Content-Type', 'image/png'))
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            conn.close()

        except Exception as e:
            self.send_error(502, f'Proxy error: {str(e)}')

    def log_message(self, format, *args):
        # 静默日志（瓦片请求太多）
        if '/tile-proxy/' in str(args):
            return
        super().log_message(format, *args)


if __name__ == '__main__':
    def shutdown(sig, frame):
        print('\nServer stopped.')
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    server = http.server.HTTPServer(('', PORT), TileProxyHandler)
    print(f'代理服务器启动: http://localhost:{PORT}')
    print(f'静态文件目录: {DIR}')
    print(f'瓦片代理已启用（天地图）')
    server.serve_forever()
