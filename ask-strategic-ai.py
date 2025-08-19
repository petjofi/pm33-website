#!/usr/bin/env python3

import requests
import json

def ask_strategic_ai():
    print("🎯 PM33 Strategic AI Co-Pilot")
    print("Ask me any strategic question!\n")
    
    question = input("Your strategic question: ")
    
    if not question.strip():
        print("Please enter a question!")
        return
    
    print("\n⏳ Strategic AI is analyzing...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/strategic/chat",
            json={
                "message": question,
                "context": {"company_name": "PM33", "product_type": "Strategic AI Co-Pilot"}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🎯 STRATEGIC AI RESPONSE:")
            print(f"💡 {data['response']}\n")
            
            if 'workflow' in data and data['workflow']:
                workflow = data['workflow']
                print(f"📋 Generated Workflow: {workflow['name']}")
                print(f"🎯 Objective: {workflow['objective']}")
                print(f"\n📝 Tasks ({len(workflow['tasks'])}):")
                
                for i, task in enumerate(workflow['tasks'], 1):
                    priority_emoji = "🔴" if task['priority'] == 'critical' else "🟡" if task['priority'] == 'high' else "🟢"
                    print(f"{i}. {task['title']} ({task['assignee']}) {priority_emoji}")
        else:
            print(f"❌ Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Make sure backend API is running on http://127.0.0.1:8001")

if __name__ == "__main__":
    ask_strategic_ai()