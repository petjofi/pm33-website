#!/usr/bin/env python3
"""
PM33 Frontend Collaboration Agent

This agent coordinates between frontend engineers and the PM33 backend system.
It provides real-time API status, endpoint documentation, integration guidance,
and troubleshooting support for frontend-backend collaboration.

Usage:
    python3 pm33_frontend_collaboration_agent.py

Features:
- Real-time backend API status monitoring
- Interactive endpoint testing and documentation
- Frontend integration guidance
- Error debugging and resolution
- Development workflow coordination
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

class PM33FrontendCollaborationAgent:
    """Agent for coordinating frontend-backend development"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_status = {}
        self.integration_log = []
        self.last_health_check = None
        
    def get_backend_status(self) -> Dict[str, Any]:
        """Get comprehensive backend status for frontend team"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            health_data = response.json()
            self.last_health_check = datetime.now()
            
            return {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "timestamp": self.last_health_check.isoformat(),
                "backend_url": self.backend_url,
                "health_data": health_data,
                "available_endpoints": self._get_available_endpoints(),
                "ai_engines_status": health_data.get("ai_engines", {}),
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "backend_url": self.backend_url,
                "troubleshooting": self._get_backend_troubleshooting()
            }
    
    def _get_available_endpoints(self) -> List[Dict[str, Any]]:
        """Document available API endpoints for frontend integration"""
        return [
            {
                "path": "/health",
                "method": "GET",
                "purpose": "Backend health and AI engine status",
                "response_format": "JSON with health metrics and AI engine status",
                "example_usage": f"fetch('{self.backend_url}/health')",
                "expected_response_time": "< 100ms"
            },
            {
                "path": "/api/mock-strategic-response",
                "method": "POST",
                "purpose": "Strategic AI analysis with workflow generation",
                "request_body": {
                    "message": "Your strategic question or scenario"
                },
                "response_format": "JSON with AI response, workflow, and metadata",
                "example_usage": f"""fetch('{self.backend_url}/api/mock-strategic-response', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ message: "How should we prioritize features?" }})
}})""",
                "expected_response_time": "< 2000ms"
            },
            {
                "path": "/",
                "method": "GET",
                "purpose": "Full HTML dashboard interface (for reference)",
                "response_format": "Complete HTML dashboard with interactive elements",
                "example_usage": f"window.open('{self.backend_url}/', '_blank')",
                "expected_response_time": "< 500ms"
            }
        ]
    
    def _get_backend_troubleshooting(self) -> List[str]:
        """Provide troubleshooting steps for backend connection issues"""
        return [
            "1. Ensure backend is running: python3 pm33_multi_engine_demo.py",
            "2. Check port 8000 is not blocked by firewall",
            "3. Verify backend URL is correct: http://localhost:8000",
            "4. Test direct connection: curl http://localhost:8000/health",
            "5. Check for port conflicts: lsof -i :8000",
            "6. Restart backend if needed: kill process and restart"
        ]
    
    def test_endpoint(self, endpoint_path: str, method: str = "GET", payload: Dict = None) -> Dict[str, Any]:
        """Test specific backend endpoint for frontend team"""
        url = f"{self.backend_url}{endpoint_path}"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=payload or {}, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result = {
                "endpoint": endpoint_path,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "success": 200 <= response.status_code < 300,
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to parse JSON response
            try:
                result["response_data"] = response.json()
            except:
                result["response_text"] = response.text[:500] + "..." if len(response.text) > 500 else response.text
            
            # Add headers for debugging
            result["response_headers"] = dict(response.headers)
            
            # Log the test
            self.integration_log.append(result)
            
            return result
            
        except Exception as e:
            error_result = {
                "endpoint": endpoint_path,
                "method": method,
                "url": url,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "troubleshooting": self._get_endpoint_troubleshooting(endpoint_path)
            }
            
            self.integration_log.append(error_result)
            return error_result
    
    def _get_endpoint_troubleshooting(self, endpoint: str) -> List[str]:
        """Get specific troubleshooting for endpoint issues"""
        if endpoint == "/health":
            return [
                "Check if backend is running",
                "Verify port 8000 is accessible",
                "Backend might be starting up (wait 30 seconds)"
            ]
        elif endpoint == "/api/mock-strategic-response":
            return [
                "Ensure request has Content-Type: application/json header",
                "Verify request body has 'message' field",
                "Check if AI engines are initialized (may take 60 seconds on first start)"
            ]
        else:
            return ["Check endpoint path spelling", "Verify backend is fully initialized"]
    
    def get_integration_guidance(self, frontend_framework: str = "nextjs") -> Dict[str, Any]:
        """Provide framework-specific integration guidance"""
        
        base_integration = {
            "backend_url": self.backend_url,
            "cors_enabled": True,
            "authentication": "None required for demo endpoints",
            "rate_limiting": "None currently implemented",
            "error_handling": "Backend provides graceful fallbacks"
        }
        
        if frontend_framework.lower() == "nextjs":
            return {
                **base_integration,
                "framework": "Next.js",
                "api_integration_example": """
// Create API route: app/api/strategic/route.ts
export async function POST(request: Request) {
  const { message } = await request.json()
  
  try {
    const response = await fetch('http://localhost:8000/api/mock-strategic-response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    return Response.json(
      { error: 'Backend connection failed', details: error.message },
      { status: 500 }
    )
  }
}""",
                "client_usage_example": """
// Client component usage
const [response, setResponse] = useState(null)
const [loading, setLoading] = useState(false)

const askStrategicQuestion = async (question) => {
  setLoading(true)
  try {
    const res = await fetch('/api/strategic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question })
    })
    
    const data = await res.json()
    setResponse(data)
  } catch (error) {
    console.error('Strategic analysis failed:', error)
    setResponse({ error: 'Analysis unavailable' })
  } finally {
    setLoading(false)
  }
}"""
            }
        elif frontend_framework.lower() == "react":
            return {
                **base_integration,
                "framework": "React",
                "api_integration_example": """
// Custom hook for PM33 backend integration
import { useState, useCallback } from 'react'

export const usePM33Strategic = () => {
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const askQuestion = useCallback(async (message) => {
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch('http://localhost:8000/api/mock-strategic-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      
      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`)
      }
      
      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err.message)
      console.error('PM33 strategic analysis failed:', err)
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { response, loading, error, askQuestion }
}""",
                "client_usage_example": """
// Component usage
function StrategicDashboard() {
  const { response, loading, error, askQuestion } = usePM33Strategic()
  
  const handleSubmit = (e) => {
    e.preventDefault()
    const question = e.target.question.value
    askQuestion(question)
  }
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input name="question" placeholder="Ask strategic question..." />
        <button disabled={loading}>
          {loading ? 'Analyzing...' : 'Ask PM33'}
        </button>
      </form>
      
      {error && <div className="error">Error: {error}</div>}
      {response && (
        <div className="response">
          <h3>Strategic Analysis</h3>
          <p>{response.response}</p>
          {response.workflow && (
            <div className="workflow">
              <h4>Generated Workflow</h4>
              <p>{response.workflow.strategic_objective}</p>
              <ul>
                {response.workflow.tasks.map(task => (
                  <li key={task.id}>{task.title}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}"""
            }
        
        return base_integration
    
    def get_development_status(self) -> Dict[str, Any]:
        """Get current development status for coordination"""
        backend_status = self.get_backend_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "backend_status": backend_status,
            "integration_readiness": {
                "backend_healthy": backend_status["status"] == "healthy",
                "endpoints_available": len(self._get_available_endpoints()),
                "ai_engines_ready": len(backend_status.get("health_data", {}).get("ai_engines", {}).get("engines", {})) > 0,
                "recommended_next_steps": self._get_next_steps(backend_status)
            },
            "recent_tests": self.integration_log[-10:] if self.integration_log else [],
            "environment_info": {
                "backend_url": self.backend_url,
                "python_backend_running": self._check_backend_process(),
                "suggested_frontend_port": "3000 (to avoid conflicts)"
            }
        }
    
    def _get_next_steps(self, backend_status: Dict) -> List[str]:
        """Get recommended next steps based on current status"""
        if backend_status["status"] != "healthy":
            return [
                "1. Start the PM33 backend: python3 pm33_multi_engine_demo.py",
                "2. Wait for initialization (30-60 seconds)",
                "3. Test health endpoint: curl http://localhost:8000/health",
                "4. Contact backend team if issues persist"
            ]
        
        return [
            "1. Backend is healthy - ready for frontend integration",
            "2. Test strategic endpoint with sample question",
            "3. Implement API integration using provided examples",
            "4. Add error handling for backend unavailability",
            "5. Test workflow generation and display"
        ]
    
    def _check_backend_process(self) -> bool:
        """Check if backend process is running"""
        try:
            result = subprocess.run(['lsof', '-i', ':8000'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

# Collaboration API Server
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend development

# Initialize the collaboration agent
agent = PM33FrontendCollaborationAgent()

@app.route('/agent/status')
def get_status():
    """Get current development and backend status"""
    return jsonify(agent.get_development_status())

@app.route('/agent/test-endpoint', methods=['POST'])
def test_endpoint():
    """Test specific backend endpoint"""
    data = request.json or {}
    endpoint = data.get('endpoint', '/health')
    method = data.get('method', 'GET')
    payload = data.get('payload')
    
    result = agent.test_endpoint(endpoint, method, payload)
    return jsonify(result)

@app.route('/agent/integration-guide')
def get_integration_guide():
    """Get integration guidance for frontend framework"""
    framework = request.args.get('framework', 'nextjs')
    guide = agent.get_integration_guidance(framework)
    return jsonify(guide)

@app.route('/agent/backend-status')
def get_backend_status():
    """Get detailed backend status"""
    status = agent.get_backend_status()
    return jsonify(status)

@app.route('/agent/logs')
def get_logs():
    """Get integration test logs"""
    limit = int(request.args.get('limit', 50))
    logs = agent.integration_log[-limit:] if agent.integration_log else []
    return jsonify({
        "logs": logs,
        "total_tests": len(agent.integration_log),
        "latest_timestamp": logs[-1]["timestamp"] if logs else None
    })

if __name__ == "__main__":
    print("🤝 PM33 Frontend Collaboration Agent Starting...")
    print("📊 Agent Dashboard: http://localhost:5001/agent/status")
    print("🔧 Test Endpoints: POST http://localhost:5001/agent/test-endpoint")
    print("📚 Integration Guide: http://localhost:5001/agent/integration-guide")
    print("🎯 Backend Status: http://localhost:5001/agent/backend-status")
    print("📋 Test Logs: http://localhost:5001/agent/logs")
    print()
    
    # Initial backend check
    initial_status = agent.get_backend_status()
    if initial_status["status"] == "healthy":
        print("✅ Backend is healthy - ready for frontend integration!")
        ai_count = len(initial_status.get("health_data", {}).get("ai_engines", {}).get("engines", {}))
        print(f"🤖 {ai_count} AI engines detected")
    else:
        print("⚠️ Backend not ready - check troubleshooting guide")
        print("🔧 Run: python3 pm33_multi_engine_demo.py")
    
    print("\n🚀 Collaboration agent ready for frontend team!")
    
    # Start the collaboration API
    app.run(host='0.0.0.0', port=5001, debug=True)