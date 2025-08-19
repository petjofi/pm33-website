#!/usr/bin/env python3
"""
Human Interface for PM33 Orchestration
Handles daily briefings, escalations, and human decision processing
"""

import json
import smtplib
from datetime import datetime
from typing import Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

class HumanDecisionInterface:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.project_root = Path("/Users/ssaper/Desktop/my-projects/pm33-claude-execution")
        
        # Human decision preferences (configurable)
        self.notification_preferences = {
            "email": True,
            "file_output": True,
            "console_output": True
        }
        
        self.decision_history = []
        
    async def send_daily_briefing(self, briefing: Dict):
        """Send daily strategic briefing to human"""
        
        formatted_briefing = await self.format_briefing_for_human(briefing)
        
        # Multiple output formats
        if self.notification_preferences["console_output"]:
            print(formatted_briefing["console"])
            
        if self.notification_preferences["file_output"]:
            await self.save_briefing_to_file(formatted_briefing["detailed"])
            
        if self.notification_preferences["email"]:
            await self.send_email_briefing(formatted_briefing["email"])
    
    async def format_briefing_for_human(self, briefing: Dict) -> Dict:
        """Format briefing in multiple formats for different consumption"""
        
        # Console format - quick overview
        console_format = f"""
🎯 PM33 DAILY STRATEGIC BRIEFING - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*70}

🚨 URGENT DECISIONS NEEDED: {len(briefing.get('urgent_decisions_needed', []))}
{self.format_urgent_items_brief(briefing.get('urgent_decisions_needed', []))}

📊 DAY 3 PROGRESS: {briefing.get('day_3_progress', {}).get('timeline_risk', 'UNKNOWN')}
{self.format_day_3_status_brief(briefing.get('day_3_progress', {}))}

🤖 AGENTIC AI TEAMS STATUS:
{self.format_ai_teams_status_brief(briefing.get('agentic_ai_teams_status', {}))}

⚙️  AGENT STATUS:
• Technical: {len(briefing.get('technical_progress', {}).get('completed_endpoints', []))} endpoints, {len(briefing.get('technical_progress', {}).get('completed_components', []))} components
• Strategy: {briefing.get('strategic_approvals', [])[:1] if briefing.get('strategic_approvals') else ['No pending items']}
• GTM: {len(briefing.get('gtm_strategy_items', []))} items pending
• UX: {len(briefing.get('ux_reviews', []))} reviews needed

🔄 SCOPE OPTIMIZATION: {'Available' if briefing.get('scope_optimization_available') else 'None pending'}

{'='*70}
📋 Full details saved to: pm33-orchestration/daily-briefings/
        """
        
        # Detailed format for file output
        detailed_format = await self.generate_detailed_briefing(briefing)
        
        # Email format - actionable items focus
        email_format = await self.generate_email_briefing(briefing)
        
        return {
            "console": console_format,
            "detailed": detailed_format, 
            "email": email_format
        }
    
    async def generate_detailed_briefing(self, briefing: Dict) -> str:
        """Generate comprehensive detailed briefing"""
        
        return f"""
# PM33 Daily Strategic Briefing
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Strategic Phase:** Day 3 Beta Launch Preparation

## Executive Summary
- **Overall Status:** {self.assess_overall_status(briefing)}
- **Critical Path:** {briefing.get('day_3_progress', {}).get('timeline_risk', 'Unknown')}
- **Urgent Decisions:** {len(briefing.get('urgent_decisions_needed', []))}

## Urgent Decisions Required

{self.format_urgent_decisions_detailed(briefing.get('urgent_decisions_needed', []))}

## Day 3 Launch Progress

### Demo Readiness
{self.format_demo_readiness(briefing.get('day_3_progress', {}).get('demo_readiness', {}))}

### Marketing Execution  
{self.format_marketing_progress(briefing.get('day_3_progress', {}).get('marketing_execution', {}))}

### Beta Signup Status
- **Target:** 15 signups
- **Actual:** {briefing.get('day_3_progress', {}).get('beta_signups', {}).get('actual', 0)}
- **Status:** {briefing.get('day_3_progress', {}).get('beta_signups', {}).get('status', 'Unknown')}

## Agent Progress & Pending Items

### Technical Agent
{self.format_technical_progress(briefing.get('technical_progress', {}))}

### Strategy Agent  
{self.format_strategy_progress(briefing.get('strategic_approvals', []))}

### GTM Agent
{self.format_gtm_progress(briefing.get('gtm_strategy_items', []))}

### UX Agent
{self.format_ux_progress(briefing.get('ux_reviews', []))}

## Agentic AI Teams Status
{self.format_agentic_teams_detailed(briefing.get('agentic_ai_teams_status', {}))}

## Conflicts Resolved
{self.format_conflicts_resolved(briefing.get('conflicts_resolved', []))}

## Scope Optimization Opportunities
{self.format_scope_optimization(briefing.get('scope_optimization_available', False))}

## Next 24 Hour Priorities
{await self.generate_next_24h_priorities(briefing)}

---
*Generated by PM33 Master Orchestrator*
*For decisions/approvals, update: pm33-orchestration/human_decisions.json*
        """
    
    async def save_briefing_to_file(self, detailed_briefing: str):
        """Save detailed briefing to file"""
        
        briefing_dir = self.project_root / "pm33-orchestration" / "daily-briefings"
        briefing_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"briefing-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        filepath = briefing_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(detailed_briefing)
        
        print(f"📁 Detailed briefing saved: {filepath}")
    
    async def process_human_decisions(self, decisions_file: str = None):
        """Process human decisions from file or direct input"""
        
        if not decisions_file:
            decisions_file = self.project_root / "pm33-orchestration" / "human_decisions.json"
        
        try:
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
        except FileNotFoundError:
            print(f"No decisions file found at {decisions_file}")
            return
        
        for decision in decisions.get("decisions", []):
            await self.process_single_decision(decision)
        
        # Archive processed decisions
        await self.archive_processed_decisions(decisions)
        
        print(f"✅ Processed {len(decisions.get('decisions', []))} human decisions")
    
    async def process_single_decision(self, decision: Dict):
        """Process a single human decision"""
        
        decision_id = decision.get("id")
        decision_type = decision.get("type")
        approval = decision.get("approval")  # approve, reject, modify
        
        if decision_type == "scope_change":
            await self.process_scope_change_decision(decision)
        elif decision_type == "strategic_approval":
            await self.process_strategic_approval(decision)
        elif decision_type == "ux_review":
            await self.process_ux_review_decision(decision)
        elif decision_type == "conflict_resolution":
            await self.process_conflict_resolution(decision)
        else:
            await self.process_general_decision(decision)
        
        # Log decision
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "processed": True
        })
        
        # Update shared context
        await self.orchestrator.update_shared_context({
            f"human_decision_{decision_id}": {
                "decision": decision,
                "processed_at": datetime.now().isoformat()
            }
        })
        
        # Notify relevant agents
        await self.notify_agents_of_decision(decision)
    
    async def process_scope_change_decision(self, decision: Dict):
        """Process human decision on agent scope changes"""
        
        agent_name = decision.get("agent")
        scope_changes = decision.get("scope_changes", {})
        approval = decision.get("approval")
        
        if approval == "approve":
            # Update agent authorities
            agent = getattr(self.orchestrator, f"{agent_name}_agent")
            
            if "new_autonomous_decisions" in scope_changes:
                agent.autonomous_decisions.extend(scope_changes["new_autonomous_decisions"])
            
            if "remove_escalations" in scope_changes:
                for escalation in scope_changes["remove_escalations"]:
                    if escalation in agent.must_escalate:
                        agent.must_escalate.remove(escalation)
            
            print(f"✅ Scope changes approved for {agent_name}_agent")
            
        elif approval == "reject":
            print(f"❌ Scope changes rejected for {agent_name}_agent: {decision.get('reason', 'No reason provided')}")
            
        elif approval == "modify":
            print(f"🔄 Scope changes require modification for {agent_name}_agent: {decision.get('modifications', 'No modifications specified')}")
    
    # Helper methods for formatting
    def format_urgent_items_brief(self, urgent_items: List[Dict]) -> str:
        if not urgent_items:
            return "• None"
        
        brief_items = []
        for item in urgent_items[:3]:  # Show top 3
            brief_items.append(f"• {item.get('summary', 'Unknown item')}")
        
        if len(urgent_items) > 3:
            brief_items.append(f"• ... and {len(urgent_items) - 3} more")
            
        return "\n".join(brief_items)
    
    def format_day_3_status_brief(self, day_3_progress: Dict) -> str:
        demo_status = day_3_progress.get("demo_readiness", {})
        ready_count = sum(1 for status in demo_status.values() if "✅" in str(status))
        total_count = len(demo_status)
        
        return f"• Demo Components: {ready_count}/{total_count} ready"
    
    def format_ai_teams_status_brief(self, ai_teams_status: Dict) -> str:
        if not ai_teams_status:
            return "• Status unknown"
        
        return f"• Strategic AI: {ai_teams_status.get('strategic_ai', 'Unknown')}\n• Workflow AI: {ai_teams_status.get('workflow_ai', 'Unknown')}"
    
    def assess_overall_status(self, briefing: Dict) -> str:
        """Assess overall project status"""
        
        urgent_count = len(briefing.get('urgent_decisions_needed', []))
        timeline_risk = briefing.get('day_3_progress', {}).get('timeline_risk', 'UNKNOWN')
        
        if urgent_count > 2 or timeline_risk == "HIGH":
            return "🔴 ATTENTION REQUIRED"
        elif urgent_count > 0 or timeline_risk == "MEDIUM":
            return "🟡 MONITORING NEEDED" 
        else:
            return "🟢 ON TRACK"

if __name__ == "__main__":
    print("PM33 Human Interface - Daily Briefing System")
    print("Use with master orchestrator for complete functionality")