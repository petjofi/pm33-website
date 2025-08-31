# PM33 Frontend Collaboration Agent

## Quick Start for Frontend Engineer

### 1. Start the Collaboration Agent
```bash
python3 pm33_frontend_collaboration_agent.py
```

### 2. Access Agent Dashboard
- **Main Dashboard**: http://localhost:5000/agent/status
- **Backend Health**: http://localhost:5000/agent/backend-status
- **Integration Guide**: http://localhost:5000/agent/integration-guide?framework=nextjs
- **Test Logs**: http://localhost:5000/agent/logs

## Available API Endpoints

### Get Development Status
```bash
GET http://localhost:5000/agent/status
```
Returns complete status of backend, AI engines, and integration readiness.

### Test Backend Endpoints
```bash
POST http://localhost:5000/agent/test-endpoint
Content-Type: application/json

{
  "endpoint": "/api/mock-strategic-response",
  "method": "POST",
  "payload": {
    "message": "How should we prioritize our roadmap?"
  }
}
```

### Get Integration Examples
```bash
GET http://localhost:5000/agent/integration-guide?framework=nextjs
# or
GET http://localhost:5000/agent/integration-guide?framework=react
```

## Backend Integration Points

### 1. Health Check
```javascript
// Check if backend is ready
const healthCheck = async () => {
  const response = await fetch('http://localhost:8000/health')
  const health = await response.json()
  return health.components.ai_manager === 'healthy'
}
```

### 2. Strategic Analysis
```javascript
// Ask strategic questions
const askStrategic = async (question) => {
  const response = await fetch('http://localhost:8000/api/mock-strategic-response', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: question })
  })
  
  const result = await response.json()
  return {
    aiResponse: result.response,
    workflow: result.workflow,
    metadata: result.meta
  }
}
```

## Next.js Integration Example

### API Route (`app/api/strategic/route.ts`)
```typescript
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
      { error: 'Backend unavailable', fallback: true },
      { status: 500 }
    )
  }
}
```

### Client Component
```tsx
'use client'
import { useState } from 'react'

export default function StrategicChat() {
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const question = formData.get('question') as string
    
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
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="p-6">
      <form onSubmit={handleSubmit} className="mb-6">
        <input 
          name="question"
          placeholder="Ask PM33 a strategic question..."
          className="w-full p-3 border rounded"
          disabled={loading}
        />
        <button 
          type="submit" 
          disabled={loading}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
        >
          {loading ? 'Analyzing...' : 'Ask PM33'}
        </button>
      </form>
      
      {response && (
        <div className="bg-gray-50 p-4 rounded">
          <h3 className="font-bold mb-2">PM33 Strategic Analysis</h3>
          <p className="mb-4">{response.response}</p>
          
          {response.workflow && (
            <div>
              <h4 className="font-semibold mb-2">Generated Workflow</h4>
              <p className="text-sm mb-2">{response.workflow.strategic_objective}</p>
              <ul className="list-disc pl-4">
                {response.workflow.tasks.map((task, i) => (
                  <li key={i}>{task.title} - {task.assignee}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

## Real-Time Collaboration

### Test Endpoints
```bash
# Test health
curl http://localhost:5000/agent/test-endpoint \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/health", "method": "GET"}'

# Test strategic analysis
curl http://localhost:5000/agent/test-endpoint \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/api/mock-strategic-response",
    "method": "POST",
    "payload": {"message": "What is our competitive advantage?"}
  }'
```

### Monitor Backend Health
```javascript
// Real-time health monitoring
const monitorBackend = async () => {
  try {
    const response = await fetch('http://localhost:5000/agent/backend-status')
    const status = await response.json()
    
    console.log('Backend Status:', status.status)
    console.log('AI Engines:', status.health_data?.ai_engines?.healthy_count)
    console.log('Response Time:', status.response_time_ms, 'ms')
    
    return status.status === 'healthy'
  } catch (error) {
    console.error('Backend unreachable:', error)
    return false
  }
}

// Check every 30 seconds
setInterval(monitorBackend, 30000)
```

## Error Handling

### Graceful Fallbacks
```javascript
const safeStrategicCall = async (question) => {
  try {
    // Primary: Direct backend call
    const response = await fetch('http://localhost:8000/api/mock-strategic-response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question })
    })
    
    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.warn('Direct backend failed, using fallback')
  }
  
  // Fallback: Through Next.js API route
  try {
    const response = await fetch('/api/strategic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question })
    })
    
    return await response.json()
  } catch (error) {
    // Ultimate fallback
    return {
      response: "Strategic analysis temporarily unavailable. Please try again.",
      workflow: null,
      error: true
    }
  }
}
```

## Troubleshooting

### Backend Not Responding
1. Check if backend is running: `lsof -i :8000`
2. Start backend: `python3 pm33_multi_engine_demo.py`
3. Test health: `curl http://localhost:8000/health`

### CORS Issues
- Backend has CORS enabled for all origins during development
- If issues persist, use Next.js API routes as proxy

### AI Engines Down
- Backend provides fallback responses even when AI engines are unavailable
- Workflows are still generated using strategic frameworks

## Communication Channels

### For Issues:
1. Check agent dashboard: http://localhost:5000/agent/status
2. Review test logs: http://localhost:5000/agent/logs
3. Test specific endpoints via agent API

### For New Features:
1. Backend API is stable and ready
2. All strategic analysis endpoints functional
3. Workflow generation working with task breakdown

## Development Status: ✅ READY

**Backend Status**: Healthy and operational  
**AI Engines**: Groq active (ultra-fast responses)  
**API Endpoints**: All strategic endpoints functional  
**Frontend Integration**: Ready with examples and agent support  

**Next Steps**: Implement frontend components using provided examples and test via collaboration agent.