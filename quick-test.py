#!/usr/bin/env python3
"""
Quick Development Test - PM33 Strategic AI
Fast testing during development iterations
"""

import requests
import json
import time
from datetime import datetime

def quick_test():
    """Quick 30-second test for development workflow"""
    print("⚡ PM33 Strategic AI - Quick Development Test")
    print("=" * 50)
    
    api_base = "http://127.0.0.1:8001"
    start_time = time.time()
    
    # Test 1: API Health (5 seconds)
    print("1️⃣  Testing API Health...")
    try:
        response = requests.get(f"{api_base}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is responding")
        else:
            print(f"   ❌ API unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        return False
    
    # Test 2: Strategic Chat Basic (20 seconds)
    print("2️⃣  Testing Strategic AI...")
    test_query = {
        "message": "Quick test: Our competitor launched similar features. Should PM33 pivot strategy?",
        "context": {
            "company_name": "PM33",
            "current_stage": "Day 2 MVP",
            "priority": "50 beta users"
        }
    }
    
    try:
        query_start = time.time()
        response = requests.post(
            f"{api_base}/api/strategic/chat",
            json=test_query,
            timeout=25
        )
        query_time = time.time() - query_start
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            if 'response' in data and 'workflow' in data:
                task_count = len(data.get('workflow', {}).get('tasks', []))
                print(f"   ✅ Strategic response generated ({task_count} tasks)")
                print(f"   ⏱️  Response time: {query_time:.1f}s")
                
                # Quick context check
                response_text = json.dumps(data).lower()
                context_found = any(keyword in response_text for keyword in 
                                  ['pm33', 'beta users', 'strategic', 'competitor'])
                
                if context_found:
                    print("   ✅ Context awareness detected")
                else:
                    print("   ⚠️  Limited context awareness")
                
                return True
            else:
                print("   ❌ Invalid response structure")
                return False
        else:
            print(f"   ❌ Strategic AI failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Strategic AI error: {e}")
        return False
    
    finally:
        total_time = time.time() - start_time
        print(f"\n⏱️  Total test time: {total_time:.1f}s")

def main():
    """Main function"""
    success = quick_test()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 QUICK TEST PASSED - Ready for development!")
        print("🚀 Strategic AI Co-Pilot is functional")
    else:
        print("⚠️  QUICK TEST FAILED - Check API status")
        print("🔧 Debug: Ensure backend server is running")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    main()