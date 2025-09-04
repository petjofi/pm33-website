#!/usr/bin/env python3
"""
PM33 Deployment Agent - Claude Code Integration
Registers the PM33 deployment agent with Claude Code for native integration
"""

import sys
import json
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from .pm33_deployment_agent import PM33DeploymentAgent
except ImportError:
    # Handle hyphenated filename
    import importlib.util
    spec = importlib.util.spec_from_file_location("pm33_deployment_agent", Path(__file__).parent / "pm33-deployment-agent.py")
    pm33_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pm33_module)
    PM33DeploymentAgent = pm33_module.PM33DeploymentAgent


def register_pm33_deployment_agent():
    """Register PM33 deployment agent with Claude Code"""
    
    agent_metadata = PM33DeploymentAgent.register_with_claude()
    
    # Claude Code agent registration format
    claude_agent_info = {
        "agent_class": PM33DeploymentAgent,
        "metadata": agent_metadata,
        "handler": "handle_claude_request",
        "initialization": {
            "config_path": Path(__file__).parent / "deployment-config.yaml"
        }
    }
    
    return claude_agent_info


# ==================== CLAUDE CODE INTEGRATION ====================

async def invoke_pm33_deployment_agent(command: str, **kwargs):
    """
    Direct invocation interface for Claude Code
    
    Usage from Claude:
        result = await invoke_pm33_deployment_agent("deploy", environment="staging")
        result = await invoke_pm33_deployment_agent("validate", branch="feature/css-fixes")
        result = await invoke_pm33_deployment_agent("deploy-pipeline", branch="css-theme-fixes")
    """
    
    # Initialize agent
    config_path = Path(__file__).parent / "deployment-config.yaml"
    agent = PM33DeploymentAgent(str(config_path))
    
    try:
        # Execute command
        result = await agent.handle_claude_request(command, kwargs)
        
        # Ensure staging server is cleaned up
        if hasattr(agent, 'staging_server_process') and agent.staging_server_process:
            await agent.stop_staging_server()
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "pm33-deployment-agent",
            "command": command,
            "parameters": kwargs
        }


# ==================== CLAUDE COMMAND SHORTCUTS ====================

async def deploy_to_staging(branch: str = None):
    """Deploy to staging environment with validation"""
    return await invoke_pm33_deployment_agent("deploy", environment="staging", branch=branch)


async def deploy_to_production(branch: str = None):
    """Deploy to production environment"""
    return await invoke_pm33_deployment_agent("deploy", environment="production", branch=branch)


async def run_full_pipeline(branch: str = None):
    """Run full dev → staging → production pipeline"""
    return await invoke_pm33_deployment_agent("deploy-pipeline", branch=branch)


async def validate_current_branch(branch: str = None):
    """Run UX/UI validation on current or specified branch"""
    return await invoke_pm33_deployment_agent("validate", branch=branch)


async def start_staging_validation(port: int = 3001):
    """Start interactive staging validation server"""
    return await invoke_pm33_deployment_agent("staging-server", action="start", port=port)


async def get_deployment_status():
    """Get current deployment and environment status"""
    return await invoke_pm33_deployment_agent("status")


async def check_environment_health():
    """Check health of all environments"""
    return await invoke_pm33_deployment_agent("health")


# ==================== DIRECT EXECUTION SUPPORT ====================

def main():
    """Direct execution interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PM33 Deployment Agent")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--branch", help="Git branch to operate on")
    parser.add_argument("--environment", help="Target environment")
    parser.add_argument("--port", type=int, default=3001, help="Server port")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    # Map command line args to function parameters
    kwargs = {}
    if args.branch:
        kwargs["branch"] = args.branch
    if args.environment:
        kwargs["environment"] = args.environment
    if args.port != 3001:
        kwargs["port"] = args.port
    
    # Execute command
    result = asyncio.run(invoke_pm33_deployment_agent(args.command, **kwargs))
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✅ {result.get('message', 'Command completed successfully')}")
            if result.get("url"):
                print(f"🌐 URL: {result['url']}")
        else:
            print(f"❌ Error: {result.get('error', 'Command failed')}")
    
    return 0 if result.get("success") else 1


# ==================== AGENT METADATA EXPORT ====================

# Export agent information for Claude Code discovery
PM33_DEPLOYMENT_AGENT = register_pm33_deployment_agent()

__all__ = [
    'PM33DeploymentAgent',
    'invoke_pm33_deployment_agent',
    'deploy_to_staging',
    'deploy_to_production', 
    'run_full_pipeline',
    'validate_current_branch',
    'start_staging_validation',
    'get_deployment_status',
    'check_environment_health',
    'PM33_DEPLOYMENT_AGENT'
]


if __name__ == "__main__":
    sys.exit(main())