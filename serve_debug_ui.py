#!/usr/bin/env python3
"""
Simple HTTP server to serve the debug UI and test run data.
Usage: python serve_debug_ui.py [--port PORT] [--test-runs-dir DIR]
"""

import argparse
import http.server
import json
import os
import socketserver
from pathlib import Path
from urllib.parse import urlparse, unquote


class DebugUIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, test_runs_dir=None, **kwargs):
        self.test_runs_dir = Path(test_runs_dir) if test_runs_dir else Path.cwd() / "test_runs"
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)

        if path == '/' or path == '/debug_ui.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_path = Path(__file__).parent / 'debug_ui.html'
            if html_path.exists():
                with open(html_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'<h1>debug_ui.html not found</h1>')
            return

        if path.startswith('/test_runs/'):
            file_path = self.test_runs_dir / path[11:]
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if file_path.suffix == '.json':
                    self.send_header('Content-type', 'application/json')
                elif file_path.suffix in ['.png', '.jpg', '.jpeg']:
                    self.send_header('Content-type', f'image/{file_path.suffix[1:]}')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
            return

        if path == '/list_runs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            runs = []
            if self.test_runs_dir.exists():
                for run_dir in sorted(self.test_runs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                    if run_dir.is_dir():
                        metadata_path = run_dir / 'metadata.json'
                        if metadata_path.exists():
                            try:
                                with open(metadata_path) as f:
                                    metadata = json.load(f)
                                runs.append({
                                    'name': run_dir.name,
                                    'path': f'/test_runs/{run_dir.name}',
                                    'goal': metadata.get('goal', ''),
                                    'success': metadata.get('success', False),
                                    'start_time': metadata.get('start_time', ''),
                                })
                            except:
                                runs.append({
                                    'name': run_dir.name,
                                    'path': f'/test_runs/{run_dir.name}',
                                    'goal': '',
                                    'success': False,
                                    'start_time': '',
                                })
            self.wfile.write(json.dumps(runs).encode())
            return

        super().do_GET()

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description='Serve Android World Debug UI')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on (default: 8000)')
    parser.add_argument('--test-runs-dir', type=str, default=None,
                       help='Directory containing test runs (default: ./test_runs)')
    args = parser.parse_args()

    test_runs_dir = Path(args.test_runs_dir) if args.test_runs_dir else Path.cwd() / "test_runs"

    handler = lambda *args, **kwargs: DebugUIHandler(*args, test_runs_dir=test_runs_dir, **kwargs)

    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"🚀 Debug UI server running at http://localhost:{args.port}/")
        print(f"📁 Serving test runs from: {test_runs_dir}")
        print(f"💡 Open http://localhost:{args.port}/ in your browser")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")


if __name__ == '__main__':
    main()

