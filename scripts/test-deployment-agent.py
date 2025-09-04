#!/usr/bin/env python3
"""
PM33 Deployment Agent - Test Integration
Quick test script for validating deployment agent functionality
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add agents directory to path
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

try:
    import importlib.util
    
    # Load pm33-deployment-agent.py (with hyphens)
    spec = importlib.util.spec_from_file_location("pm33_deployment_agent", agents_dir / "pm33-deployment-agent.py")
    pm33_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pm33_module)
    PM33DeploymentAgent = pm33_module.PM33DeploymentAgent
    
    from validation_orchestrator import ValidationOrchestrator, quick_validation_check
    from staging_server_manager import StagingServerManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)


async def test_agent_registration():
    """Test Claude Code agent registration"""
    
    print("🧪 Testing Agent Registration...")
    
    try:
        # Test agent metadata registration
        metadata = PM33DeploymentAgent.register_with_claude()
        
        print(f"✅ Agent Registration: {metadata['name']}")
        print(f"📝 Description: {metadata['description']}")
        print(f"🛠️ Capabilities: {', '.join(metadata['capabilities'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Registration Failed: {e}")
        return False


async def test_validation_orchestrator():
    """Test validation orchestrator functionality"""
    
    print("\n🔍 Testing Validation Orchestrator...")
    
    try:
        project_root = Path(__file__).parent.parent
        
        # Quick validation check
        result = await quick_validation_check(str(project_root))
        
        print(f"✅ Validation Score: {result.get('overall_score', 0)}/100")
        print(f"🚀 Deployment Ready: {result.get('deployment_ready', False)}")
        
        if result.get('critical_issues'):
            print(f"⚠️ Critical Issues: {len(result['critical_issues'])}")
            
        return result.get('overall_score', 0) > 0
        
    except Exception as e:
        print(f"❌ Validation Test Failed: {e}")
        return False


async def test_staging_server_manager():
    """Test staging server manager (dry run)"""
    
    print("\n🚀 Testing Staging Server Manager...")
    
    try:
        project_root = Path(__file__).parent.parent
        manager = StagingServerManager(project_root, port=3099)  # Use different port for testing
        
        # Test status check
        status = await manager.get_server_status(run_health_check=False)
        
        print(f"✅ Server Status Check: {status['status']['status']}")
        print(f"🔗 Server URL: {status['status']['url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Staging Server Test Failed: {e}")
        return False


async def test_deployment_agent_commands():
    """Test deployment agent command handling"""
    
    print("\n⚙️ Testing Deployment Agent Commands...")
    
    try:
        config_path = Path(__file__).parent.parent / "agents" / "deployment-config.yaml"
        agent = PM33DeploymentAgent(str(config_path))
        
        # Test status command
        result = await agent.handle_claude_request("status", {})
        
        print(f"✅ Status Command: {result.get('success', False)}")
        
        if result.get('environment_status'):
            for env, status in result['environment_status'].items():
                print(f"  📁 {env}: {status}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Agent Command Test Failed: {e}")
        return False


async def test_full_integration():
    """Test complete deployment agent integration"""
    
    print("\n🔄 Testing Full Integration...")
    
    try:
        config_path = Path(__file__).parent.parent / "agents" / "deployment-config.yaml"
        agent = PM33DeploymentAgent(str(config_path))
        
        # Test validation workflow
        result = await agent.handle_claude_request("validate", {
            "environment": "development",
            "quick": True
        })
        
        print(f"✅ Integration Test: {result.get('success', False)}")
        
        if result.get('validation_results'):
            val_results = result['validation_results']
            print(f"🎯 Validation Score: {val_results.get('overall_score', 0)}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Integration Test Failed: {e}")
        return False


async def run_all_tests():
    """Run complete test suite"""
    
    print("🧪 PM33 Deployment Agent Test Suite")
    print("=" * 50)
    
    test_results = {
        "agent_registration": False,
        "validation_orchestrator": False,
        "staging_server_manager": False,
        "deployment_commands": False,
        "full_integration": False
    }
    
    # Run tests
    test_results["agent_registration"] = await test_agent_registration()
    test_results["validation_orchestrator"] = await test_validation_orchestrator()
    test_results["staging_server_manager"] = await test_staging_server_manager()
    test_results["deployment_commands"] = await test_deployment_agent_commands()
    test_results["full_integration"] = await test_full_integration()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Deployment agent is ready for use.")
        
        print("\n🚀 Usage Examples:")
        print("# Quick validation")
        print("python agents/__init__.py validate")
        
        print("\n# Start staging server")
        print("python agents/staging-server-manager.py start --interactive")
        
        print("\n# Full deployment pipeline")
        print("python agents/__init__.py deploy-pipeline --branch main")
        
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed_tests == total_tests


def main():
    """Main execution function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test PM33 Deployment Agent")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Run tests
    start_time = time.time()
    success = asyncio.run(run_all_tests())
    execution_time = time.time() - start_time
    
    if args.json:
        result = {
            "success": success,
            "execution_time": round(execution_time, 2),
            "timestamp": time.time()
        }
        print(json.dumps(result, indent=2))
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())