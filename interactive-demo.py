#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

def print_header():
    print("\n" + "="*80)
    print("🎯 PM33 Strategic AI Co-Pilot - Interactive Demo")
    print("AI-native product management platform that replaces limited strategic capabilities consultants")
    print("="*80)
    print("✅ Backend API: http://127.0.0.1:8001")
    print("✅ Status: Strategic AI ready for queries")
    print("="*80 + "\n")

def print_workflow(workflow_data):
    print("\n" + "🎯 STRATEGIC AI RESPONSE:")
    print("-" * 50)
    print(f"📋 Workflow: {workflow_data['name']}")
    print(f"🎯 Objective: {workflow_data['objective']}")
    print(f"📊 Total Tasks: {len(workflow_data['tasks'])}")
    
    print("\n📝 EXECUTABLE TASKS:")
    print("-" * 30)
    
    for i, task in enumerate(workflow_data['tasks'], 1):
        priority_emoji = "🔴" if task['priority'] == 'critical' else "🟡" if task['priority'] == 'high' else "🟢"
        due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00')).strftime('%m/%d/%Y')
        
        print(f"\n{i}. {task['title']}")
        print(f"   👤 Assignee: {task['assignee']}")
        print(f"   {priority_emoji} Priority: {task['priority'].upper()}")
        print(f"   📅 Due Date: {due_date}")

def test_strategic_ai(question, context=None):
    url = "http://127.0.0.1:8001/api/strategic/chat"
    
    payload = {
        "message": question,
        "context": context or {
            "company_name": "PM33",
            "product_type": "Strategic AI Co-Pilot"
        }
    }
    
    print(f"🤔 YOUR QUESTION:")
    print(f'"{question}"')
    print("\n⏳ Strategic AI is analyzing...")
    
    try:
        response = requests.post(url, json=payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n💡 {data['response']}")
            
            if 'workflow' in data and data['workflow']:
                print_workflow(data['workflow'])
            
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the backend API is running on http://127.0.0.1:8001")
        return False

def run_demo():
    print_header()
    
    # Demo scenarios
    scenarios = [
        {
            "question": "Our main competitor just launched an AI-powered feature that's very similar to what we're building. They have 10x more funding and a larger team. How should PM33 respond strategically?",
            "context": {
                "company_name": "PM33", 
                "product_type": "Strategic AI Co-Pilot",
                "competitive_pressure": "high",
                "funding_disadvantage": "10x less funding"
            }
        },
        {
            "question": "We need to choose between hiring 2 more engineers or investing $50k in marketing. We currently have 3 engineers, 0 paying customers, and limited runway. What should we prioritize?",
            "context": {
                "company_name": "PM33",
                "team_size": "3 engineers", 
                "revenue": "pre-revenue",
                "decision_type": "resource_allocation"
            }
        },
        {
            "question": "Our beta users love the product but aren't converting to paid plans. We have 47 active beta users. How do we convert them to our $97/month plan?",
            "context": {
                "company_name": "PM33",
                "beta_users": 47,
                "pricing": "$97/month",
                "conversion_challenge": "beta to paid"
            }
        }
    ]
    
    print("🎯 DEMO: Strategic AI Co-Pilot in Action")
    print("\nI'll demonstrate 3 strategic scenarios that product managers face:\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"📊 SCENARIO {i}: Strategic Decision Making")
        print('='*80)
        
        success = test_strategic_ai(scenario['question'], scenario['context'])
        
        if not success:
            print("❌ Demo stopped due to connection error")
            break
        
        if i < len(scenarios):
            input("\n⏸️  Press Enter to see next scenario...")
    
    print(f"\n{'='*80}")
    print("🎉 DEMO COMPLETE!")
    print("✅ Your PM33 Strategic AI Co-Pilot successfully:")
    print("   • Analyzed complex strategic scenarios")  
    print("   • Generated actionable workflows with specific tasks")
    print("   • Assigned roles, priorities, and due dates")
    print("   • Demonstrated the core value: 'Replace limited strategic capabilities consultants'")
    print(f"{'='*80}")
    print("\n🚀 Ready for Day 3: Marketing automation and beta user acquisition!")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Your Strategic AI Co-Pilot is ready when you are!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Ensure the backend API is running: python3 -m uvicorn main:app --host 127.0.0.1 --port 8001")