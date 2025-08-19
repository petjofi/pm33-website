#!/usr/bin/env python3
"""
PM33 Master Orchestrator
Coordinates specialized agents with relevant context mapping and scope optimization
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class EscalationLevel(Enum):
    IMMEDIATE = "immediate"
    DAILY = "daily" 
    WEEKLY = "weekly"

@dataclass
class Conflict:
    id: str
    agents_involved: List[str]
    conflict_type: str
    description: str
    business_impact: int  # 1-10
    urgency: EscalationLevel
    resolution_needed_by: datetime
    agent_positions: Dict[str, str]

@dataclass
class ScopeChange:
    agent: str
    change_type: str  # expand_authority, remove_escalation, add_collaboration
    description: str
    justification: str
    risk_level: str  # low, medium, high
    efficiency_gain: str

class PM33MasterOrchestrator:
    def __init__(self):
        self.project_root = Path("/Users/ssaper/Desktop/my-projects/pm33-claude-execution")
        self.shared_context = self.load_shared_context()
        self.conflict_log = []
        self.pending_escalations = []
        self.agent_contexts = self.define_agent_contexts()
        
        # Initialize agents with relevant context only
        from agents.technical_agent import TechnicalAgent
        from agents.strategy_agent import StrategyAgent  
        from agents.gtm_agent import GTMAgent
        from agents.ux_agent import UXAgent
        
        self.technical_agent = TechnicalAgent(self.shared_context, self.agent_contexts['technical'])
        self.strategy_agent = StrategyAgent(self.shared_context, self.agent_contexts['strategy'])
        self.gtm_agent = GTMAgent(self.shared_context, self.agent_contexts['gtm'])
        self.ux_agent = UXAgent(self.shared_context, self.agent_contexts['ux'])
    
    def define_agent_contexts(self) -> Dict:
        """Define relevant context files for each agent (not everything)"""
        return {
            "technical": {
                "core_requirements": [
                    "PROVEN_WORKFLOW_PATTERNS.md",
                    "PM33_DATA_REQUIREMENTS_ARCHITECTURE.md", 
                    "FINAL-SYSTEM-SUMMARY.md",
                    "app/frontend/package.json",
                    "app/backend/main.py"
                ],
                "ux_interface_specs": [
                    "PM33_UX_ARCHITECTURE_PLAN.md",
                    "PM33_CLICKABLE_DEMO_DESIGN.md"
                ],
                "demo_requirements": [
                    "DEVELOPMENT-TESTING-GUIDE.md",
                    "marketing/DAY3-BETA-OUTREACH-PLAN.md"
                ]
            },
            
            "ux": {
                "design_requirements": [
                    "PM33_UX_ARCHITECTURE_PLAN.md",
                    "PM33_CLICKABLE_DEMO_DESIGN.md", 
                    "DEMO-POSITIONING-GUIDE.md"
                ],
                "strategic_context": [
                    "INSTRUCTIONS-FOR-FUTURE-AGENTS.md",
                    "marketing/DAY3-BETA-OUTREACH-PLAN.md"
                ],
                "technical_constraints": [
                    "app/frontend/package.json",
                    "app/frontend/components/"
                ]
            },
            
            "strategy": {
                "core_strategic_docs": [
                    "INSTRUCTIONS-FOR-FUTURE-AGENTS.md",
                    "STRATEGIC-CONTEXT-REQUIREMENTS.md",
                    "pm33-session-manager.py"
                ],
                "competitive_intelligence": [
                    "strategy/competitive-analysis/",
                    "strategy/context/competitive/"
                ],
                "execution_context": [
                    "marketing/DAY3-BETA-OUTREACH-PLAN.md",
                    "PM33_CLICKABLE_DEMO_DESIGN.md"
                ],
                "revenue_strategy": [
                    "../PM33/pm33_100k_mrr_plan.md"
                ],
                "strategic_marketing_alignment": [
                    "../PM33/final drafts/",
                    "../PM33/Templates/"
                ]
            },
            
            "gtm": {
                "marketing_foundation": [
                    "marketing/",
                    "DEMO-POSITIONING-GUIDE.md",
                    "PM33_CLICKABLE_DEMO_DESIGN.md"
                ],
                "strategic_messaging": [
                    "INSTRUCTIONS-FOR-FUTURE-AGENTS.md",
                    "strategy/context/gtm/",
                    "strategy/context/company/"
                ],
                "competitive_context": [
                    "strategy/competitive-analysis/market-research-key-findings.md"
                ],
                "marketing_strategy_plan": [
                    "../PM33/pm33_100k_mrr_plan.md"
                ],
                "approved_marketing_content": [
                    "../PM33/final drafts/",
                    "../PM33/Templates/"
                ],
                "content_automation_framework": [
                    "../PM33/pm33_100k_mrr_plan.md"
                ]
            }
        }
    
    def load_shared_context(self):
        """Load PM33 shared context"""
        try:
            with open(self.project_root / "pm33-orchestration/state_management/shared_context.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.initialize_pm33_context()
    
    def initialize_pm33_context(self):
        """Initialize with PM33 strategic context"""
        return {
            "strategic_state": {
                "mission": "Transform PMs into PMOs through agentic AI teams",
                "value_proposition": "Transform PMs into PMOs through agentic AI teams - driving product-led growth via strategic automation and improved execution alignment",
                "target_market": "Senior PMs at Series A-C companies",
                "current_phase": "Day 3 beta launch preparation",
                "revenue_target": "$100K MRR by Dec 31, 2025"
            },
            "technical_progress": {
                "backend_status": "Multi-engine AI system operational",
                "frontend_status": "Next.js app with basic strategic chat",
                "integrations": "Jira sync patterns proven from Replit"
            },
            "day_3_requirements": {
                "beta_signups_target": 15,
                "demo_components": ["strategic_chat", "command_center", "ai_teams_demo"],
                "marketing_execution": "outreach_plan_ready"
            },
            "agentic_ai_teams": {
                "strategic_ai": "Multi-framework analysis capability",
                "workflow_ai": "Task generation and PM tool integration",
                "data_ai": "Company context learning and predictive analytics", 
                "comms_ai": "Stakeholder management and executive reporting"
            },
            "decisions_log": [],
            "conflicts_log": [],
            "last_updated": datetime.now().isoformat()
        }
    
    async def handle_conflict(self, conflict: Conflict):
        """Handle conflicts with PM33-specific resolution rules"""
        
        self.conflict_log.append({
            "timestamp": datetime.now(),
            "conflict": conflict,
            "resolution_method": None,
            "resolution": None
        })
        
        # PM33-specific conflict resolution
        if conflict.conflict_type == "technical_vs_ux":
            if "user_experience" in conflict.description.lower() or "conversion" in conflict.description.lower():
                resolution = await self.ux_agent.resolve_conflict(conflict)
            else:
                resolution = await self.technical_agent.resolve_conflict(conflict)
                
        elif conflict.conflict_type == "strategy_vs_gtm":
            if any(keyword in conflict.description.lower() for keyword in ["positioning", "value_prop", "competitive"]):
                resolution = await self.strategy_agent.resolve_conflict(conflict)
            else:
                resolution = await self.gtm_agent.resolve_conflict(conflict)
                
        elif conflict.urgency == EscalationLevel.IMMEDIATE or "day_3" in conflict.description.lower():
            await self.escalate_to_human(conflict)
            return
            
        else:
            resolution = await self.master_resolve_conflict(conflict)
        
        self.conflict_log[-1]["resolution"] = resolution
        await self.update_shared_context({"last_conflict_resolution": resolution})
    
    async def conduct_scope_review(self):
        """Weekly scope optimization review process"""
        
        # Get scope suggestions from each agent (based on relevant context only)
        scope_suggestions = {}
        
        for agent_name, agent in [("technical", self.technical_agent), 
                                 ("strategy", self.strategy_agent),
                                 ("gtm", self.gtm_agent), 
                                 ("ux", self.ux_agent)]:
            
            suggestions = await agent.suggest_scope_improvements()
            scope_suggestions[agent_name] = suggestions
        
        # Master agent analysis
        master_review = await self.analyze_scope_suggestions(scope_suggestions)
        
        # Package for human decision
        human_decision_package = await self.prepare_scope_decision_package(master_review)
        
        # Save for human review
        await self.save_scope_review(human_decision_package)
        
        return human_decision_package
    
    async def analyze_scope_suggestions(self, suggestions: Dict) -> Dict:
        """Master agent evaluates all scope suggestions"""
        
        return {
            "conflict_analysis": self.identify_authority_conflicts(suggestions),
            "efficiency_assessment": self.calculate_efficiency_gains(suggestions),
            "risk_evaluation": self.assess_scope_expansion_risks(suggestions),
            "pm33_strategic_alignment": self.assess_strategic_alignment(suggestions),
            "recommendations": {
                "high_priority": self.identify_high_impact_changes(suggestions),
                "approve": self.recommend_approvals(suggestions),
                "reject": self.recommend_rejections(suggestions),
                "clarify": self.identify_clarification_needs(suggestions)
            }
        }
    
    def identify_authority_conflicts(self, suggestions: Dict) -> Dict:
        """Identify potential authority conflicts between agents"""
        conflicts = []
        
        # Check for overlapping authority requests
        tech_agent_sugg = suggestions.get("technical", {})
        ux_agent_sugg = suggestions.get("ux", {})
        
        # Handle both old and new key names safely
        tech_requests = set()
        if isinstance(tech_agent_sugg, dict):
            if "authority_requests" in tech_agent_sugg and isinstance(tech_agent_sugg["authority_requests"], dict):
                tech_requests.update(tech_agent_sugg["authority_requests"].keys())
            if "authority_expansion_requests" in tech_agent_sugg and isinstance(tech_agent_sugg["authority_expansion_requests"], dict):
                tech_requests.update(tech_agent_sugg["authority_expansion_requests"].keys())
                
        ux_requests = set()
        if isinstance(ux_agent_sugg, dict):
            if "authority_requests" in ux_agent_sugg and isinstance(ux_agent_sugg["authority_requests"], dict):
                ux_requests.update(ux_agent_sugg["authority_requests"].keys())  
            if "authority_expansion_requests" in ux_agent_sugg and isinstance(ux_agent_sugg["authority_expansion_requests"], dict):
                ux_requests.update(ux_agent_sugg["authority_expansion_requests"].keys())
        
        overlaps = tech_requests.intersection(ux_requests)
        if overlaps:
            conflicts.append({
                "agents": ["technical", "ux"],
                "overlap": list(overlaps),
                "resolution_needed": True
            })
        
        return {"conflicts_found": conflicts, "requires_human_decision": len(conflicts) > 0}
    
    async def generate_daily_briefing(self) -> Dict:
        """Generate PM33-specific daily briefing"""
        
        return {
            "urgent_decisions_needed": [
                escalation for escalation in self.pending_escalations 
                if escalation.get("urgency") == EscalationLevel.IMMEDIATE
            ],
            "day_3_progress": await self.assess_day_3_progress(),
            "strategic_approvals": await self.strategy_agent.get_pending_approvals(),
            "ux_reviews": await self.ux_agent.get_pending_reviews(), 
            "gtm_strategy_items": await self.gtm_agent.get_pending_approvals(),
            "technical_progress": await self.technical_agent.get_progress_summary(),
            "conflicts_resolved": self.get_recent_conflicts(),
            "agentic_ai_teams_status": await self.get_ai_teams_status(),
            "scope_optimization_available": len(await self.check_pending_scope_suggestions()) > 0
        }
    
    async def assess_day_3_progress(self) -> Dict:
        """Assess progress toward Day 3 beta launch goals"""
        return {
            "beta_signups": {"target": 15, "actual": 0, "status": "not_started"},
            "demo_readiness": {
                "strategic_chat": "✅ operational",
                "command_center": "🔄 in_development", 
                "ai_teams_demo": "⏳ planned",
                "interactive_workflows": "⏳ planned"
            },
            "marketing_execution": {
                "outreach_plan": "✅ ready",
                "demo_positioning": "✅ updated",
                "viral_mechanics": "🔄 in_development"
            },
            "timeline_risk": "MEDIUM - Strategic Command Center critical path"
        }
    
    async def escalate_to_human(self, item):
        """Format escalation for human review with PM33 context"""
        
        urgency = item.get("urgency", "medium")
        if hasattr(urgency, 'value'):
            urgency = urgency.value
        
        escalation = {
            "id": f"escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": item.get("type", "decision_needed"),
            "priority": urgency,
            "summary": item.get("summary"),
            "pm33_context": {
                "strategic_impact": item.get("strategic_impact"),
                "day_3_impact": item.get("day_3_impact"),
                "competitive_implications": item.get("competitive_implications")
            },
            "recommendation": item.get("recommendation"),
            "alternatives": item.get("alternatives", []),
            "timeline": item.get("timeline"),
            "created_at": datetime.now()
        }
        
        self.pending_escalations.append(escalation)
        await self.send_escalation_notification(escalation)
        
        return escalation
    
    async def update_shared_context(self, updates: Dict):
        """Update shared context with changes"""
        self.shared_context.update(updates)
        self.shared_context["last_updated"] = datetime.now().isoformat()
        
        # Save to file
        os.makedirs(self.project_root / "pm33-orchestration/state_management", exist_ok=True)
        with open(self.project_root / "pm33-orchestration/state_management/shared_context.json", 'w') as f:
            json.dump(self.shared_context, f, indent=2, default=str)
    
    def get_recent_conflicts(self) -> List[Dict]:
        """Get recently resolved conflicts"""
        return self.conflict_log[-5:] if self.conflict_log else []
    
    async def get_ai_teams_status(self) -> Dict:
        """Get agentic AI teams status"""
        return self.shared_context.get("agentic_ai_teams", {})
    
    async def check_pending_scope_suggestions(self) -> List[Dict]:
        """Check for pending scope optimization suggestions"""
        return []  # Implementation would check for pending suggestions
    
    async def send_escalation_notification(self, escalation: Dict):
        """Send escalation notification (placeholder)"""
        print(f"🚨 ESCALATION: {escalation['summary']}")
    
    async def master_resolve_conflict(self, conflict):
        """Master agent conflict resolution"""
        return {"resolution": "master_orchestrator_resolution", "conflict_id": conflict.id}
    
    def calculate_efficiency_gains(self, suggestions: Dict) -> Dict:
        """Calculate efficiency gains from scope suggestions"""
        return {"estimated_gain": "25% faster decision making"}
    
    def assess_scope_expansion_risks(self, suggestions: Dict) -> Dict:
        """Assess risks of scope expansion"""
        return {"risk_level": "low", "risk_factors": ["Proven patterns reduce risk"]}
    
    def assess_strategic_alignment(self, suggestions: Dict) -> Dict:
        """Assess strategic alignment of scope suggestions"""
        return {"alignment_score": 85, "strategic_fit": "High alignment with PMO transformation"}
    
    def identify_high_impact_changes(self, suggestions: Dict) -> List[Dict]:
        """Identify high impact scope changes"""
        return [{"change": "Technical agent full database authority", "impact": "high"}]
    
    def recommend_approvals(self, suggestions: Dict) -> List[str]:
        """Recommend scope approvals"""
        return ["Technical database schema authority"]
    
    def recommend_rejections(self, suggestions: Dict) -> List[str]:
        """Recommend scope rejections"""
        return []
    
    def identify_clarification_needs(self, suggestions: Dict) -> List[str]:
        """Identify clarification needs"""
        return ["UX agent interaction pattern authority scope"]
    
    async def prepare_scope_decision_package(self, master_review: Dict) -> Dict:
        """Prepare scope decision package for human review"""
        return {"master_analysis": master_review, "decision_required": True}
    
    async def save_scope_review(self, decision_package: Dict) -> None:
        """Save scope review for human decision"""
        print(f"📋 Scope review saved for human decision: {len(decision_package)} items")

if __name__ == "__main__":
    orchestrator = PM33MasterOrchestrator()
    print("🎯 PM33 Master Orchestrator initialized")
    print(f"Strategic State: {orchestrator.shared_context['strategic_state']['current_phase']}")
    print(f"Agents: Technical, Strategy, GTM, UX")
    print("Ready for agent coordination and scope optimization")