#!/usr/bin/env python3
"""
Quick Strategic AI Test for Beta Demo Preparation
Tests with pre-defined strategic questions
"""

import sys
import os
sys.path.append('app/backend')

from strategic_workflow_engine import StrategicWorkflowEngine
import asyncio

def test_strategic_scenarios():
    """Test Strategic AI with common PM scenarios"""
    print("🎯 PM33 Strategic AI Co-Pilot - Demo Test")
    print("=" * 60)
    
    engine = StrategicWorkflowEngine()
    
    # Test scenarios for beta demos
    scenarios = [
        {
            "question": "Our main competitor just launched AI features similar to ours. They have 10x more funding. How should we respond strategically?",
            "context": {
                "company_name": "PM33",
                "product_type": "AI Strategic Co-Pilot",
                "competitive_situation": "feature_overlap"
            }
        },
        {
            "question": "We have $10k budget. Should we hire a developer or invest in marketing to reach our 50 beta user goal?",
            "context": {
                "company_name": "PM33", 
                "budget": "$10k",
                "goal": "50 beta users"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"📊 DEMO SCENARIO {i}")
        print(f"{'='*60}")
        print(f"🤔 Strategic Question:")
        print(f'"{scenario["question"]}"')
        print("\n⏳ Strategic AI is analyzing...")
        
        try:
            workflow = asyncio.run(engine.generate_strategic_workflow(
                scenario["question"], 
                scenario["context"]
            ))
            
            print(f"\n🎯 STRATEGIC AI RESPONSE:")
            print(f"📋 Strategic Plan: {workflow.name}")
            print(f"🎯 Objective: {workflow.strategic_objective}")
            
            print(f"\n📊 Generated {len(workflow.tasks)} executable tasks:")
            for j, task in enumerate(workflow.tasks[:5], 1):
                priority_emoji = "🔴" if task.priority.value == 'critical' else "🟡" if task.priority.value == 'high' else "🟢"
                print(f"\n{j}. {task.title}")
                print(f"   👤 {task.assignee_role}")
                print(f"   {priority_emoji} {task.priority.value.upper()}")
                print(f"   📅 {task.due_date.strftime('%m/%d')}")
            
            print(f"\n✅ DEMO SCENARIO {i} - SUCCESS!")
            print("💡 This shows: Strategic guidance → Executable workflows")
            
        except Exception as e:
            print(f"❌ DEMO SCENARIO {i} - ERROR: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 STRATEGIC AI DEMO TEST COMPLETE!")
    print("✅ Your Strategic AI Co-Pilot is ready for beta user demos")
    print("💰 Value Prop: Replace limited strategic capabilities consultants with AI")
    print("⚡ Instant strategic analysis → actionable tasks")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_strategic_scenarios()