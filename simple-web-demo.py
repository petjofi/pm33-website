#!/usr/bin/env python3

import http.server
import socketserver
import json
import urllib.request
from urllib.parse import parse_qs, urlparse
import webbrowser
import threading
import time

class StrategicAIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_main_page()
        elif self.path == "/api/test":
            self.test_backend()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == "/api/chat":
            self.handle_chat()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>PM33 Strategic AI Co-Pilot - Live Demo</title>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); 
                  color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .chat-area { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .message { margin-bottom: 20px; }
        .user-msg { text-align: right; }
        .user-msg .content { background: #007bff; color: white; padding: 15px; border-radius: 20px; 
                             display: inline-block; max-width: 70%; }
        .ai-msg .content { background: #f1f3f4; padding: 15px; border-radius: 20px; }
        .workflow { background: #e3f2fd; border: 2px solid #2196f3; border-radius: 10px; 
                    padding: 20px; margin-top: 15px; }
        .task { background: #fff; border-left: 4px solid #4caf50; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .task.high { border-left-color: #ff9800; }
        .task.critical { border-left-color: #f44336; }
        textarea { width: 100%; padding: 15px; border: 1px solid #ddd; border-radius: 10px; 
                   font-size: 16px; font-family: inherit; resize: vertical; }
        button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                 padding: 15px 30px; border-radius: 10px; font-size: 16px; cursor: pointer; 
                 width: 100%; margin-top: 15px; }
        button:hover { opacity: 0.9; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .loading { color: #666; font-style: italic; }
        .status { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; 
                  padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 PM33 Strategic AI Co-Pilot</h1>
            <p>Replace limited strategic capabilities consultants with AI strategic guidance</p>
            <p><strong>Live Demo - Day 2 MVP Complete</strong></p>
        </div>
        
        <div class="status">
            <strong>✅ Status:</strong> Backend API connected and ready | 
            <strong>🎯 AI Engine:</strong> Strategic workflow generation active
        </div>
        
        <div class="chat-area">
            <div id="messages">
                <div class="ai-msg">
                    <div class="content">
                        <strong>🎯 Strategic AI:</strong> Welcome! I'm your Strategic AI Co-Pilot. 
                        Ask me strategic questions like:
                        <ul style="margin-top: 10px;">
                            <li><em>"Our competitor launched X feature. How should we respond?"</em></li>
                            <li><em>"Should we hire engineers or invest in marketing?"</em></li>
                            <li><em>"How do we convert beta users to paid plans?"</em></li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <textarea id="questionInput" rows="4" placeholder="Ask your strategic question here..."></textarea>
                <button onclick="askStrategicAI()" id="askButton">Send Strategic Query</button>
            </div>
        </div>
    </div>
    
    <script>
        async function askStrategicAI() {
            const input = document.getElementById('questionInput');
            const button = document.getElementById('askButton');
            const messages = document.getElementById('messages');
            
            const question = input.value.trim();
            if (!question) return;
            
            // Add user message
            const userMsg = document.createElement('div');
            userMsg.className = 'message user-msg';
            userMsg.innerHTML = `<div class="content"><strong>You:</strong> ${question}</div>`;
            messages.appendChild(userMsg);
            
            // Add loading message
            const loadingMsg = document.createElement('div');
            loadingMsg.className = 'message ai-msg';
            loadingMsg.innerHTML = `<div class="content loading">🤔 Strategic AI is analyzing your question...</div>`;
            messages.appendChild(loadingMsg);
            
            // Clear input and disable button
            input.value = '';
            button.disabled = true;
            button.textContent = 'Analyzing...';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message: question,
                        context: { company_name: 'PM33', product_type: 'Strategic AI Co-Pilot' }
                    })
                });
                
                // Remove loading message
                messages.removeChild(loadingMsg);
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Add AI response
                    const aiMsg = document.createElement('div');
                    aiMsg.className = 'message ai-msg';
                    
                    let workflowHtml = '';
                    if (data.workflow) {
                        const tasksHtml = data.workflow.tasks.map(task => {
                            const priorityClass = task.priority === 'critical' ? 'critical' : 
                                                 task.priority === 'high' ? 'high' : '';
                            return `
                                <div class="task ${priorityClass}">
                                    <strong>${task.title}</strong><br>
                                    👤 ${task.assignee} | 
                                    🎯 ${task.priority.toUpperCase()} | 
                                    📅 ${new Date(task.due_date).toLocaleDateString()}
                                </div>
                            `;
                        }).join('');
                        
                        workflowHtml = `
                            <div class="workflow">
                                <h3>📋 ${data.workflow.name}</h3>
                                <p><strong>Objective:</strong> ${data.workflow.objective}</p>
                                <h4>Tasks (${data.workflow.tasks.length}):</h4>
                                ${tasksHtml}
                            </div>
                        `;
                    }
                    
                    aiMsg.innerHTML = `
                        <div class="content">
                            <strong>🎯 Strategic AI:</strong> ${data.response}
                            ${workflowHtml}
                        </div>
                    `;
                    messages.appendChild(aiMsg);
                    
                } else {
                    throw new Error('API Error');
                }
                
            } catch (error) {
                // Remove loading message
                if (loadingMsg.parentNode) {
                    messages.removeChild(loadingMsg);
                }
                
                const errorMsg = document.createElement('div');
                errorMsg.className = 'message ai-msg';
                errorMsg.innerHTML = `<div class="content">❌ Sorry, I encountered an error. Please try again.</div>`;
                messages.appendChild(errorMsg);
            }
            
            // Re-enable button
            button.disabled = false;
            button.textContent = 'Send Strategic Query';
            
            // Scroll to bottom
            messages.scrollTop = messages.scrollHeight;
        }
        
        // Enter key support
        document.getElementById('questionInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askStrategicAI();
            }
        });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            # Forward to backend API
            backend_response = urllib.request.urlopen(
                urllib.request.Request(
                    'http://127.0.0.1:8001/api/strategic/chat',
                    data=json.dumps(data).encode(),
                    headers={'Content-Type': 'application/json'}
                )
            )
            
            result = backend_response.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(result)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e), "response": "Sorry, connection to Strategic AI failed."})
            self.wfile.write(error_response.encode())
    
    def test_backend(self):
        try:
            response = urllib.request.urlopen('http://127.0.0.1:8001/health')
            result = response.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(result)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode())

def open_browser():
    time.sleep(2)  # Give server time to start
    webbrowser.open('http://localhost:8888')

if __name__ == "__main__":
    PORT = 8888
    
    with socketserver.TCPServer(("", PORT), StrategicAIHandler) as httpd:
        print("\n" + "="*80)
        print("🚀 PM33 Strategic AI Co-Pilot - Web Demo")
        print("="*80)
        print(f"✅ Demo Server: http://localhost:{PORT}")
        print(f"✅ Backend API: http://127.0.0.1:8001") 
        print(f"🎯 Opening browser automatically...")
        print("="*80)
        
        # Open browser automatically
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"\n🎯 Your Strategic AI Co-Pilot is ready!")
        print(f"Visit: http://localhost:{PORT}")
        print("\nPress Ctrl+C to stop")
        
        httpd.serve_forever()