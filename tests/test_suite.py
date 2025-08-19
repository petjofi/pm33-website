#!/usr/bin/env python3
"""
PM33 Comprehensive Testing Suite
Tests all core components and their integration
"""

import sys
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append('app/backend')

def print_test_header(test_name):
    print(f"\n{'='*50}")
    print(f"🧪 {test_name}")
    print(f"{'='*50}")

def print_test_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   📋 {details}")

def test_environment():
    """Test environment and configuration"""
    print_test_header("Environment Configuration Test")
    
    load_dotenv()
    
    # Test required environment variables
    required_vars = [
        'ANTHROPIC_API_KEY',
        'DATABASE_URL', 
        'RESEND_API_KEY',
        'PINECONE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_test_result("Environment Variables", False, f"Missing: {missing_vars}")
        return False
    else:
        print_test_result("Environment Variables", True, f"All {len(required_vars)} variables loaded")
        return True

def test_context_manager():
    """Test Strategic Context Manager"""
    print_test_header("Strategic Context Manager Test")
    
    try:
        from context_manager import StrategicContextManager
        
        # Initialize context manager
        cm = StrategicContextManager()
        print_test_result("Context Manager Import", True)
        
        # Test context loading
        context = cm.get_relevant_context("competitor strategy")
        print_test_result("Context Loading", len(context) > 0, f"{len(context)} characters loaded")
        
        # Test different query types
        test_queries = [
            ("competitive analysis", "competitor"),
            ("budget allocation", "budget"), 
            ("product strategy", "strategy"),
            ("market positioning", "market")
        ]
        
        all_passed = True
        for query, expected_keyword in test_queries:
            context = cm.get_relevant_context(query)
            has_relevant_content = len(context) > 100  # Should have substantial context
            print_test_result(f"Query: {query}", has_relevant_content, f"{len(context)} chars")
            if not has_relevant_content:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test_result("Context Manager", False, str(e))
        return False

def test_ai_api_connection():
    """Test direct AI API connection"""
    print_test_header("AI API Connection Test")
    
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print_test_result("API Key", False, "ANTHROPIC_API_KEY not found")
            return False
        
        client = anthropic.Anthropic(api_key=api_key)
        print_test_result("Client Initialization", True)
        
        # Test basic API call
        start_time = time.time()
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": "Respond with exactly: 'PM33 API test successful'"}]
        )
        api_time = time.time() - start_time
        
        response_text = response.content[0].text
        is_correct = "PM33 API test successful" in response_text
        
        print_test_result("Basic API Call", is_correct, f"Response time: {api_time:.2f}s")
        print_test_result("Response Content", is_correct, response_text[:100])
        
        # Test with strategic context
        start_time = time.time()
        strategic_response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[{
                "role": "user", 
                "content": "You are PM33's Strategic AI. Respond to: 'How should we compete?' with exactly 2 sentences."
            }]
        )
        strategic_time = time.time() - start_time
        
        strategic_text = strategic_response.content[0].text
        has_strategic_content = len(strategic_text.split('.')) >= 2
        
        print_test_result("Strategic Query", has_strategic_content, f"Time: {strategic_time:.2f}s")
        
        return is_correct and has_strategic_content
        
    except Exception as e:
        print_test_result("AI API Connection", False, str(e))
        return False

def test_strategic_workflow_engine():
    """Test Strategic Workflow Engine"""
    print_test_header("Strategic Workflow Engine Test")
    
    try:
        from strategic_workflow_engine import StrategicWorkflowEngine
        import asyncio
        
        engine = StrategicWorkflowEngine()
        print_test_result("Engine Import", True)
        
        # Test workflow generation
        test_context = {
            "company_name": "PM33",
            "stage": "Beta",
            "current_priorities": "50 beta users"
        }
        
        test_questions = [
            "Our competitor launched similar features. How should we respond?",
            "We have $15k budget. Should we hire or invest in marketing?",
            "How do we reach 50 beta users by month end?"
        ]
        
        all_passed = True
        for question in test_questions:
            try:
                start_time = time.time()
                workflow = asyncio.run(engine.generate_strategic_workflow(question, test_context))
                generation_time = time.time() - start_time
                
                # Validate workflow structure
                has_name = hasattr(workflow, 'name') and workflow.name
                has_objective = hasattr(workflow, 'strategic_objective') and workflow.strategic_objective
                has_tasks = hasattr(workflow, 'tasks') and len(workflow.tasks) > 0
                
                workflow_valid = has_name and has_objective and has_tasks
                
                print_test_result(
                    f"Workflow: {question[:30]}...", 
                    workflow_valid, 
                    f"Time: {generation_time:.2f}s, Tasks: {len(workflow.tasks) if has_tasks else 0}"
                )
                
                if not workflow_valid:
                    all_passed = False
                    
            except Exception as e:
                print_test_result(f"Workflow Generation", False, str(e))
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test_result("Strategic Workflow Engine", False, str(e))
        return False

def test_integration():
    """Test full integration: Context + AI + Workflow"""
    print_test_header("Full Integration Test")
    
    try:
        from context_manager import StrategicContextManager
        from strategic_workflow_engine import StrategicWorkflowEngine
        import asyncio
        
        # Initialize components
        cm = StrategicContextManager()
        engine = StrategicWorkflowEngine()
        
        # Test full pipeline
        question = "Our competitor Productboard just raised $100M. Strategic response?"
        
        # Step 1: Get relevant context
        start_time = time.time()
        context = cm.get_relevant_context(question)
        context_time = time.time() - start_time
        
        print_test_result("Context Retrieval", len(context) > 0, f"{len(context)} chars in {context_time:.2f}s")
        
        # Step 2: Build full context
        full_context = {
            "company_context": context,
            "company_name": "PM33",
            "stage": "Beta",
            "current_priorities": "50 beta users by Aug 25"
        }
        
        # Step 3: Generate workflow with context
        workflow_start = time.time()
        workflow = asyncio.run(engine.generate_strategic_workflow(question, full_context))
        workflow_time = time.time() - workflow_start
        
        # Validate full workflow
        total_time = context_time + workflow_time
        workflow_complete = (
            hasattr(workflow, 'name') and workflow.name and
            hasattr(workflow, 'tasks') and len(workflow.tasks) > 0 and
            hasattr(workflow, 'strategic_objective') and workflow.strategic_objective
        )
        
        print_test_result("Full Workflow Generation", workflow_complete, 
                         f"Total time: {total_time:.2f}s, Tasks: {len(workflow.tasks)}")
        
        # Test performance requirement (should complete under 30 seconds)
        performance_ok = total_time < 30
        print_test_result("Performance Requirement", performance_ok, 
                         f"Target: <30s, Actual: {total_time:.2f}s")
        
        return workflow_complete and performance_ok
        
    except Exception as e:
        print_test_result("Integration Test", False, str(e))
        return False

def test_file_structure():
    """Test required files and directories exist"""
    print_test_header("File Structure Test")
    
    required_files = [
        'app/backend/strategic_workflow_engine.py',
        'app/backend/context_manager.py',
        'strategy/context/company/company-profile.md',
        'strategy/context/gtm/ideal-customer-profile.md',
        '.env',
        'templates/mockup_demo.html'
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print_test_result(f"File: {file_path}", exists)
        if not exists:
            all_exist = False
    
    return all_exist

def run_full_test_suite():
    """Run complete test suite"""
    print("🎯 PM33 Comprehensive Test Suite")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Testing all components for PM demo readiness...")
    
    # Run all tests
    tests = [
        ("Environment Configuration", test_environment),
        ("File Structure", test_file_structure),
        ("Context Manager", test_context_manager),
        ("AI API Connection", test_ai_api_connection),
        ("Strategic Workflow Engine", test_strategic_workflow_engine),
        ("Full Integration", test_integration)
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            results[test_name] = result
            if result:
                passed_tests += 1
        except Exception as e:
            print_test_result(test_name, False, f"Test crashed: {str(e)}")
            results[test_name] = False
    
    # Final results
    print_test_header("Test Suite Results")
    print(f"📊 Passed: {passed_tests}/{total_tests} tests")
    print(f"📈 Success rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - System ready for PM demos!")
    else:
        print("⚠️ Some tests failed - System needs fixes before demos")
        print("\n🔍 Failed tests:")
        for test_name, passed in results.items():
            if not passed:
                print(f"  ❌ {test_name}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_full_test_suite()
    exit(0 if success else 1)