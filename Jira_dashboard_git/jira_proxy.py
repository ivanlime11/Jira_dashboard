#!/usr/bin/env python3
"""
Jira Dashboard Proxy Server
Serves the dashboard HTML and proxies Jira API requests to bypass CORS.
Run: python3 jira_proxy.py
Then open: http://localhost:8765
"""

import http.server
import json
import os
import urllib.request
import urllib.parse
import base64
import threading
from pathlib import Path

PORT = 8765
DASHBOARD_DIR = Path(__file__).parent

class JiraProxyHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/jira'):
            self.handle_jira_proxy()
        else:
            # Remap / to the dashboard
            if self.path == '/':
                self.path = '/updated_dashboard.html'
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/jira'):
            self.handle_jira_proxy()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_jira_proxy(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            jira_url = self.headers.get('X-Jira-Url', '').rstrip('/')
            jira_email = self.headers.get('X-Jira-Email', '')
            jira_token = self.headers.get('X-Jira-Token', '')

            if not jira_url or not jira_email or not jira_token:
                self.send_json_error(400, "Missing Jira credentials in headers")
                return

            # Build target URL: strip /api/jira prefix, append rest to jira_url
            jira_path = self.path[len('/api/jira'):]
            target_url = jira_url + jira_path

            credentials = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()

            req = urllib.request.Request(
                target_url,
                data=body,
                headers={
                    'Authorization': f'Basic {credentials}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                method=self.command
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')
            self.send_response(e.code)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(error_body.encode())
        except Exception as e:
            self.send_json_error(500, str(e))

    def send_json_error(self, code, message):
        self.send_response(code)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Jira-Url, X-Jira-Email, X-Jira-Token')

    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {format % args}")


if __name__ == '__main__':
    import webbrowser
    server = http.server.ThreadingHTTPServer(('localhost', PORT), JiraProxyHandler)
    print(f"\n✅ Jira Dashboard Proxy running at http://localhost:{PORT}")
    print(f"   Serving files from: {DASHBOARD_DIR}")
    print(f"   Press Ctrl+C to stop.\n")
    try:
        threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        server.shutdown()
