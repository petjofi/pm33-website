#!/usr/bin/env python3
"""
Test PM33 Orchestration System
Generate first daily briefing and test agent interactions
"""

import asyncio
import sys
import os

# Add orchestration path
sys.path.append(os.path.join(os.getcwd(), 'pm33-orchestration'))

from master_orchestrator import PM33MasterOrchestrator
from human_interface.daily_briefing import HumanDecisionInterface

async def test_orchestration():
    print("🎯 Testing PM33 Orchestration System")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = PM33MasterOrchestrator()
    
    # Initialize human interface
    human_interface = HumanDecisionInterface(orchestrator)
    
    # Generate daily briefing
    print("\n📊 Generating Daily Briefing...")
    briefing = await orchestrator.generate_daily_briefing()
    
    # Send briefing to human
    await human_interface.send_daily_briefing(briefing)
    
    # Test scope optimization
    print("\n🔄 Testing Scope Optimization...")
    scope_review = await orchestrator.conduct_scope_review()
    
    print(f"Scope suggestions available: {len(scope_review)}")
    
    # Test agent interactions
    print("\n🤖 Testing Agent Interactions...")
    
    # Test technical agent decision
    tech_decision = await orchestrator.technical_agent.make_decision({
        "type": "api_endpoint_development",
        "endpoint": "/api/strategic/multi-ai",
        "purpose": "Multi-AI team coordination for PM33"
    })
    
    print(f"Technical decision: {tech_decision['decision']}")
    
    # Test strategy agent decision
    strategy_decision = await orchestrator.strategy_agent.make_decision({
        "type": "competitive_analysis",
        "competitive_context": "New AI PM tool launched"
    })
    
    print(f"Strategy decision: {strategy_decision['decision']}")
    
    print("\n✅ Orchestration system test completed successfully!")
    print("📁 Check pm33-orchestration/daily-briefings/ for detailed briefing")

if __name__ == "__main__":
    asyncio.run(test_orchestration())