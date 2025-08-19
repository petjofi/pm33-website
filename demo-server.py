#!/usr/bin/env python3

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
from urllib.error import HTTPError

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/strategic/chat':
            # Proxy the request to the actual API
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Forward to actual API
                req = urllib.request.Request(
                    'http://127.0.0.1:8001/api/strategic/chat',
                    data=post_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = response.read()
                
                # Send response back
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(result)
                
            except HTTPError as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = json.dumps({"error": f"API Error: {str(e)}"})
                self.wfile.write(error_response.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json') 
                self.end_headers()
                error_response = json.dumps({"error": f"Server Error: {str(e)}"})
                self.wfile.write(error_response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8090
    os.chdir('/Users/ssaper/Desktop/my-projects/pm33-claude-execution')
    
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print(f"🚀 PM33 Strategic AI Co-Pilot Demo Server")
        print(f"📍 Running at: http://localhost:{PORT}")
        print(f"🎯 Demo URL: http://localhost:{PORT}/demo-strategic-chat.html")
        print(f"📡 API Proxy: http://localhost:{PORT}/api/strategic/chat")
        print(f"🔄 Backend: http://127.0.0.1:8001")
        print(f"\n✅ Ready! Open http://localhost:{PORT}/demo-strategic-chat.html")
        httpd.serve_forever()