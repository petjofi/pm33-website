# PM33 Agent Integration Guide

## For Claude Code Development Agents

This guide helps other Claude Code agents integrate with the PM33 backend system for strategic analysis, workflow generation, and development coordination.

## Quick Start

### 1. Import the Helper
```python
from pm33_agent_collaboration_helper import PM33AgentHelper, ensure_pm33_ready, test_pm33_strategic

# Quick status check
if ensure_pm33_ready():
    result = test_pm33_strategic("How should we prioritize features?")
    print(f"Strategic analysis: {result['success']}")
```

### 2. Basic Integration Pattern
```python
from pm33_agent_collaboration_helper import PM33AgentHelper

def integrate_with_pm33():
    helper = PM33AgentHelper()
    
    # Check if backend is ready
    status = helper.get_backend_status()
    if status["status"] != "healthy":
        print("❌ PM33 backend not ready")
        return False
    
    # Test strategic endpoint
    result = helper.test_strategic_endpoint("What should we build next?")
    if result["success"]:
        print(f"✅ Strategic analysis working: {result['ai_response']}")
        return True
    
    return False
```

## Core Functions

### Status Checking
```python
# Get comprehensive status
helper = PM33AgentHelper()
status = helper.get_backend_status()

# Quick status check
quick_status = helper.get_quick_status_summary()
print(quick_status)  # "✅ PM33 Backend: Healthy | AI Engines: 1 | Ready for integration"

# Wait for backend to be ready
is_ready = helper.wait_for_backend_ready(max_wait_seconds=60)
```

### Strategic Analysis Testing
```python
# Test strategic analysis
result = helper.test_strategic_endpoint("How should we approach market expansion?")

if result["success"]:
    print(f"Response: {result['ai_response']}")
    print(f"Tasks generated: {result['tasks_count']}")
    print(f"Framework used: {result['framework_used']}")
    print(f"Engine: {result['engine_used']}")
```

### Health Monitoring
```python
# Test health endpoint
health = helper.test_health_endpoint()

if health["success"]:
    print(f"Backend initialized: {health['backend_initialized']}")
    print(f"AI engines: {health['healthy_engines']}/{health['ai_engines_count']}")
    print(f"Components healthy: {health['components_healthy']}")
```

## Integration Patterns for Different Agent Types

### 1. Frontend Development Agent
```python
from pm33_agent_collaboration_helper import PM33AgentHelper

class FrontendAgent:
    def __init__(self):
        self.pm33 = PM33AgentHelper()
    
    def check_api_integration(self):
        """Check if backend APIs are ready for frontend integration"""
        status = self.pm33.get_integration_status()
        
        if status["integration_ready"]:
            print("✅ Backend ready for frontend integration")
            return True
        
        print("❌ Backend not ready:")
        for rec in status["agent_recommendations"]:
            print(f"  {rec}")
        return False
    
    def test_frontend_apis(self):
        """Test the APIs that frontend will use"""
        tests = [
            self.pm33.test_health_endpoint(),
            self.pm33.test_strategic_endpoint("Test frontend integration")
        ]
        
        return all(test["success"] for test in tests)
```

### 2. Backend Development Agent
```python
class BackendAgent:
    def __init__(self):
        self.pm33 = PM33AgentHelper()
    
    def verify_backend_changes(self):
        """Verify backend changes don't break existing functionality"""
        # Test core endpoints still work
        health_ok = self.pm33.test_health_endpoint()["success"]
        strategic_ok = self.pm33.test_strategic_endpoint("Test backend changes")["success"]
        
        return health_ok and strategic_ok
    
    def get_performance_metrics(self):
        """Get backend performance metrics"""
        result = self.pm33.test_strategic_endpoint("Performance test")
        return {
            "response_time_ms": result.get("response_time_ms", 0),
            "engine_used": result.get("engine_used", "unknown"),
            "success": result.get("success", False)
        }
```

### 3. Testing Agent
```python
class TestingAgent:
    def __init__(self):
        self.pm33 = PM33AgentHelper()
    
    def run_integration_tests(self):
        """Run comprehensive integration tests"""
        test_cases = [
            "How should we prioritize our roadmap?",
            "What is our competitive advantage?", 
            "How should we allocate engineering resources?",
            "What market opportunities should we pursue?"
        ]
        
        results = []
        for question in test_cases:
            result = self.pm33.test_strategic_endpoint(question)
            results.append({
                "question": question,
                "success": result["success"],
                "response_time": result.get("response_time_ms", 0),
                "tasks_generated": result.get("tasks_count", 0)
            })
        
        return results
    
    def validate_workflow_generation(self):
        """Validate that workflows are properly generated"""
        result = self.pm33.test_strategic_endpoint("Create a strategic plan")
        
        if not result["success"]:
            return False
        
        # Check workflow structure
        return (
            result.get("workflow_generated", False) and
            result.get("tasks_count", 0) > 0 and
            result.get("framework_used", "") != ""
        )
```

## Error Handling Patterns

### Graceful Degradation
```python
def safe_strategic_analysis(question: str) -> Dict[str, Any]:
    """Strategic analysis with graceful fallback"""
    helper = PM33AgentHelper()
    
    # Try to ensure backend is ready
    if not helper.ensure_backend_running():
        return {
            "success": False,
            "error": "PM33 backend unavailable",
            "fallback_message": "Strategic analysis temporarily unavailable"
        }
    
    # Test the endpoint
    result = helper.test_strategic_endpoint(question)
    
    if result["success"]:
        return result
    
    # Fallback response
    return {
        "success": False,
        "error": result.get("error", "Unknown error"),
        "fallback_message": "Using cached strategic frameworks",
        "question": question
    }
```

### Retry Logic
```python
def strategic_analysis_with_retry(question: str, max_retries: int = 3) -> Dict[str, Any]:
    """Strategic analysis with automatic retry"""
    helper = PM33AgentHelper()
    
    for attempt in range(max_retries):
        result = helper.test_strategic_endpoint(question)
        
        if result["success"]:
            return result
        
        if attempt < max_retries - 1:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return {
        "success": False,
        "error": f"Failed after {max_retries} attempts",
        "question": question
    }
```

## Development Workflow Integration

### Pre-Development Check
```python
def pre_development_check() -> bool:
    """Run before starting development work"""
    helper = PM33AgentHelper()
    helper.print_agent_coordination_info()
    
    status = helper.get_integration_status()
    if not status["integration_ready"]:
        print("🚨 PM33 backend not ready for development")
        return False
    
    print("✅ PM33 backend ready - proceeding with development")
    return True
```

### Post-Development Validation
```python
def post_development_validation() -> bool:
    """Run after making changes to validate integration"""
    helper = PM33AgentHelper()
    
    # Test core functionality
    health_test = helper.test_health_endpoint()
    strategic_test = helper.test_strategic_endpoint("Validate development changes")
    
    if not (health_test["success"] and strategic_test["success"]):
        print("❌ Development changes broke PM33 integration")
        return False
    
    print("✅ PM33 integration validated after development changes")
    return True
```

## Quick Reference Commands

### Status Checks
```python
from pm33_agent_collaboration_helper import pm33_quick_status, ensure_pm33_ready

# One-liner status
print(pm33_quick_status())

# Ensure ready with wait
if ensure_pm33_ready():
    print("Ready for integration")
```

### Direct Testing
```python
from pm33_agent_collaboration_helper import test_pm33_strategic

# Quick strategic test
result = test_pm33_strategic("Test question")
print(f"Success: {result['success']}")
```

### Full Status Report
```python
from pm33_agent_collaboration_helper import get_pm33_status

status = get_pm33_status()
print(f"Backend: {status['status']}")
print(f"AI Engines: {status['ai_engines']['healthy_count']}")
```

## Backend API Reference

### Available Endpoints

1. **Health Check**
   - `GET http://localhost:8002/health`
   - Returns backend and AI engine status

2. **Strategic Analysis**
   - `POST http://localhost:8002/api/mock-strategic-response`
   - Body: `{"message": "your strategic question"}`
   - Returns AI analysis + workflow

3. **Dashboard Interface**
   - `GET http://localhost:8002/`
   - Full HTML dashboard for reference

### Response Formats

#### Health Response
```json
{
  "initialized": true,
  "components": {
    "ai_manager": "healthy",
    "context_manager": "healthy"
  },
  "ai_engines": {
    "healthy_count": 1,
    "total_count": 4,
    "engines": {
      "groq": "healthy",
      "openai": "error: quota exceeded",
      "together": "error: type union error",
      "anthropic": "available_untested"
    }
  }
}
```

#### Strategic Analysis Response
```json
{
  "response": "Strategic analysis text...",
  "workflow": {
    "strategic_objective": "...",
    "framework_used": "Strategic Analysis Framework",
    "tasks": [
      {
        "id": "t001",
        "title": "Task title",
        "assignee": "Product Manager",
        "priority": "critical"
      }
    ]
  },
  "meta": {
    "engine": "groq",
    "response_time": 0.5,
    "context_chars": 909
  }
}
```

## Troubleshooting

### Backend Not Responding
```python
helper = PM33AgentHelper()
status = helper.get_backend_status()

if status["status"] == "unreachable":
    print("Backend not running. Start with:")
    print("python3 pm33_multi_engine_demo.py")
```

### AI Engines Down
```python
status = helper.get_backend_status()
ai_count = status["ai_engines"]["healthy_count"]

if ai_count == 0:
    print("AI engines degraded - using fallback mode")
    print("Strategic analysis still functional with frameworks")
```

### Port Conflicts
```bash
# Check what's running on port 8002
lsof -i :8002

# Kill if needed
kill $(lsof -ti :8002)
```

## Best Practices for Agent Integration

1. **Always check backend status first**
2. **Use graceful fallbacks for strategic analysis**
3. **Test critical endpoints before proceeding**
4. **Handle AI engine degradation gracefully**
5. **Log integration test results for debugging**

## Example Integration Script

```python
#!/usr/bin/env python3
"""Example agent integration with PM33"""

from pm33_agent_collaboration_helper import PM33AgentHelper

def main():
    # Initialize helper
    helper = PM33AgentHelper()
    
    # Print status
    helper.print_agent_coordination_info()
    
    # Ensure backend is ready
    if not helper.ensure_backend_running():
        print("❌ Cannot proceed - PM33 backend not available")
        return
    
    # Test strategic analysis
    result = helper.test_strategic_endpoint("What should we focus on this quarter?")
    
    if result["success"]:
        print(f"✅ Strategic analysis: {result['ai_response']}")
        print(f"📋 Generated {result['tasks_count']} tasks")
    else:
        print(f"❌ Strategic analysis failed: {result['error']}")
    
    # Get integration recommendations
    integration = helper.get_integration_status()
    for rec in integration["agent_recommendations"]:
        print(rec)

if __name__ == "__main__":
    main()
```

This helper system is designed for **Python script integration** rather than server deployment, making it perfect for agent-to-agent coordination in the PM33 development ecosystem.