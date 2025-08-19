#!/usr/bin/env python3
"""
PM33 Strategic AI Testing Suite
Comprehensive testing for strategic AI quality and functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

class StrategicAITester:
    def __init__(self, api_base="http://127.0.0.1:8001"):
        self.api_base = api_base
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        time_str = f"({response_time:.2f}s)" if response_time > 0 else ""
        print(f"{status} {test_name} {time_str}")
        if details and not passed:
            print(f"    Details: {details}")
    
    def test_api_health(self):
        """Test basic API connectivity and health"""
        print("\n🔧 Testing API Health...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_base}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("API Health Check", True, response_time=response_time)
                else:
                    self.log_test("API Health Check", False, f"Unhealthy status: {data}")
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
    
    def test_strategic_chat_basic(self):
        """Test basic strategic chat functionality"""
        print("\n💬 Testing Strategic Chat...")
        
        test_query = {
            "message": "Quick test: Should PM33 focus on new features or user acquisition?",
            "context": {"company_name": "PM33", "test_mode": True}
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/api/strategic/chat",
                json=test_query,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'response' in data and 'workflow' in data:
                    self.log_test("Strategic Chat Basic", True, 
                                "Response and workflow generated", response_time)
                    
                    # Check workflow structure
                    workflow = data['workflow']
                    if 'tasks' in workflow and len(workflow['tasks']) > 0:
                        self.log_test("Workflow Generation", True, 
                                    f"{len(workflow['tasks'])} tasks generated")
                    else:
                        self.log_test("Workflow Generation", False, "No tasks generated")
                        
                else:
                    self.log_test("Strategic Chat Basic", False, "Invalid response structure")
            else:
                self.log_test("Strategic Chat Basic", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Strategic Chat Basic", False, str(e))
    
    def test_context_awareness(self):
        """Test if AI uses PM33-specific context"""
        print("\n🎯 Testing Context Awareness...")
        
        # Query that should trigger PM33-specific context
        context_query = {
            "message": "Our main competitor Productboard just launched new AI features. How should we respond given our current situation?",
            "context": {
                "company_name": "PM33",
                "current_stage": "pre-revenue",
                "competitive_situation": "direct_feature_overlap"
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/api/strategic/chat",
                json=context_query,
                timeout=90
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '').lower()
                workflow_text = json.dumps(data.get('workflow', {})).lower()
                full_response = response_text + workflow_text
                
                # Check for PM33-specific context usage
                context_indicators = [
                    'pm33',
                    'strategic ai co-pilot',
                    'beta users',
                    'productboard',
                    '$97',
                    'week 1'
                ]
                
                context_found = sum(1 for indicator in context_indicators 
                                  if indicator in full_response)
                
                if context_found >= 2:
                    self.log_test("Context Awareness", True, 
                                f"Found {context_found} context indicators", response_time)
                else:
                    self.log_test("Context Awareness", False, 
                                f"Only {context_found} context indicators found")
                    
            else:
                self.log_test("Context Awareness", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Context Awareness", False, str(e))
    
    def test_strategic_scenarios(self):
        """Test key strategic scenarios PM33 users will face"""
        print("\n📊 Testing Strategic Scenarios...")
        
        scenarios = [
            {
                "name": "Resource Allocation",
                "query": "We have $10k budget. Should we hire a developer or invest in marketing to reach our 50 beta user goal?",
                "expected_elements": ["budget", "beta users", "timeline", "trade-offs"]
            },
            {
                "name": "Competitive Response", 
                "query": "A well-funded competitor just launched similar features. How should PM33 differentiate?",
                "expected_elements": ["differentiation", "competitive advantage", "strategic response"]
            },
            {
                "name": "Product Strategy",
                "query": "Should we add enterprise features or focus on SMB market first?",
                "expected_elements": ["market strategy", "product roadmap", "customer segment"]
            }
        ]
        
        for scenario in scenarios:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_base}/api/strategic/chat",
                    json={
                        "message": scenario["query"],
                        "context": {"company_name": "PM33", "scenario_type": scenario["name"]}
                    },
                    timeout=90
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    full_text = json.dumps(data).lower()
                    
                    # Check for expected strategic elements
                    elements_found = sum(1 for element in scenario["expected_elements"]
                                       if element.lower() in full_text)
                    
                    if elements_found >= len(scenario["expected_elements"]) // 2:
                        self.log_test(f"Scenario: {scenario['name']}", True, 
                                    f"Strategic elements present", response_time)
                    else:
                        self.log_test(f"Scenario: {scenario['name']}", False, 
                                    f"Missing strategic elements")
                else:
                    self.log_test(f"Scenario: {scenario['name']}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Scenario: {scenario['name']}", False, str(e))
    
    def test_performance_benchmarks(self):
        """Test response time and performance"""
        print("\n⚡ Testing Performance...")
        
        # Quick query for performance testing
        perf_query = {
            "message": "Quick strategic question for performance test",
            "context": {"company_name": "PM33"}
        }
        
        response_times = []
        
        for i in range(3):  # Test 3 times
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_base}/api/strategic/chat",
                    json=perf_query,
                    timeout=60
                )
                response_time = time.time() - start_time
                response_times.append(response_time)
                
            except Exception as e:
                print(f"    Performance test {i+1} failed: {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            # Performance benchmarks
            if avg_time < 30:
                self.log_test("Average Response Time", True, f"Average: {avg_time:.2f}s")
            else:
                self.log_test("Average Response Time", False, f"Too slow: {avg_time:.2f}s")
            
            if max_time < 60:
                self.log_test("Max Response Time", True, f"Max: {max_time:.2f}s")
            else:
                self.log_test("Max Response Time", False, f"Too slow: {max_time:.2f}s")
        else:
            self.log_test("Performance Test", False, "All requests failed")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("🎯 PM33 Strategic AI Test Report")
        print("="*80)
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   • {result['test_name']}: {result['details']}")
        
        print(f"\n🚀 Strategic AI Status:")
        if passed_tests / total_tests >= 0.8:
            print("   ✅ READY FOR DEVELOPMENT")
        elif passed_tests / total_tests >= 0.6:
            print("   ⚠️  NEEDS ATTENTION - Some issues found")
        else:
            print("   ❌ NOT READY - Major issues need fixing")
        
        print("="*80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests,
            'total_time': total_time,
            'ready_for_development': passed_tests / total_tests >= 0.8
        }
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting PM33 Strategic AI Test Suite...")
        print(f"⏰ Start Time: {self.start_time.strftime('%H:%M:%S')}")
        
        # Run all test categories
        self.test_api_health()
        self.test_strategic_chat_basic()
        self.test_context_awareness()
        self.test_strategic_scenarios()
        self.test_performance_benchmarks()
        
        # Generate final report
        return self.generate_test_report()

def main():
    """Main testing function"""
    print("🎯 PM33 Strategic AI Co-Pilot - Development Testing Suite")
    print("Testing strategic AI quality and functionality...\n")
    
    tester = StrategicAITester()
    
    try:
        report = tester.run_all_tests()
        
        # Exit code based on test results
        if report['ready_for_development']:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()