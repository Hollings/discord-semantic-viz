#!/usr/bin/env python3
"""
Simple HTTP server for the visualization
Copies viz_data.json to frontend/ and starts a server
"""

import http.server
import socketserver
import webbrowser
import shutil
import os
from pathlib import Path

PORT = int(os.environ.get('PORT', 8080))
HOST = os.environ.get('HOST', '0.0.0.0')
NO_BROWSER = os.environ.get('NO_BROWSER', '').lower() in ('1', 'true', 'yes')

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / 'frontend'
OUTPUT_DIR = BASE_DIR / 'output'

def main():
    # Copy viz_data.json to frontend directory
    viz_data_src = OUTPUT_DIR / 'viz_data.json'
    viz_data_dst = FRONTEND_DIR / 'viz_data.json'

    if not viz_data_src.exists():
        print(f"Error: {viz_data_src} not found")
        print("Run the pipeline first to generate visualization data")
        return

    print(f"Copying {viz_data_src} to {viz_data_dst}...")
    shutil.copy(viz_data_src, viz_data_dst)

    # Change to frontend directory
    os.chdir(FRONTEND_DIR)

    # Start server
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop")

        # Open browser (skip in Docker)
        if not NO_BROWSER:
            try:
                webbrowser.open(url)
            except Exception:
                pass  # Ignore browser errors in headless environments

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == '__main__':
    main()
