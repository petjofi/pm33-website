#!/usr/bin/env python3
"""
Base Agent Class for PM33 Orchestration
Provides context loading, escalation logic, and scope optimization capabilities
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, shared_context: Dict, relevant_context_files: Dict):
        self.shared_context = shared_context
        self.relevant_context_files = relevant_context_files
        self.project_root = Path("/Users/ssaper/Desktop/my-projects/pm33-claude-execution")
        
        # Agent-specific configuration (to be set by subclasses)
        self.role = ""
        self.autonomous_decisions = []
        self.must_escalate = []
        
        # Load only relevant context
        self.agent_context = self.load_relevant_context()
        
        # Track performance for scope optimization
        self.decision_history = []
        self.escalation_history = []
        self.efficiency_metrics = {}
    
    def load_relevant_context(self) -> Dict:
        """Load only the context files relevant to this agent"""
        context = {}
        
        for category, files in self.relevant_context_files.items():
            context[category] = {}
            
            for file_path in files:
                full_path = self.project_root / file_path
                
                if full_path.is_file():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            context[category][file_path] = f.read()
                    except Exception as e:
                        context[category][file_path] = f"Error reading file: {e}"
                        
                elif full_path.is_dir():
                    # Load directory contents (for app/frontend/, etc.)
                    context[category][file_path] = self.scan_directory(full_path)
        
        return context
    
    def scan_directory(self, directory: Path) -> Dict:
        """Scan directory for relevant files"""
        structure = {}
        
        try:
            for item in directory.rglob("*"):
                if item.is_file() and item.suffix in ['.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md']:
                    relative_path = str(item.relative_to(directory))
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            # Only read first 100 lines to avoid huge context
                            lines = f.readlines()[:100]
                            structure[relative_path] = ''.join(lines)
                            if len(lines) == 100:
                                structure[relative_path] += "\n... (truncated)"
                    except Exception as e:
                        structure[relative_path] = f"Error reading: {e}"
        except Exception as e:
            structure["error"] = f"Error scanning directory: {e}"
        
        return structure
    
    async def should_escalate(self, decision_type: str, context: Dict = None) -> bool:
        """Check if decision requires human escalation"""
        
        # Check explicit escalation keywords
        for escalation_keyword in self.must_escalate:
            if escalation_keyword.lower() in decision_type.lower():
                return True
        
        # Check if this is an autonomous decision first (takes precedence)
        for autonomous_keyword in self.autonomous_decisions:
            if autonomous_keyword.lower() in decision_type.lower():
                return False  # This is autonomous, don't escalate
        
        # Check context-specific escalation criteria
        if context:
            # High business impact decisions
            if context.get("business_impact", 0) >= 8:
                return True
            
            # Day 3 critical path decisions
            if any(keyword in str(context).lower() for keyword in ["day_3", "beta_launch", "demo_critical"]):
                return True
            
            # Strategic positioning changes (but not competitive_analysis)
            if any(keyword in str(context).lower() for keyword in ["value_prop", "positioning"]):
                return True
            
            # Competitive changes (but not competitive_analysis)  
            if "competitive" in str(context).lower() and "competitive_analysis" not in decision_type.lower():
                return True
        
        return False
    
    async def make_decision(self, decision_context: Dict):
        """Main decision-making method"""
        decision_start = datetime.now()
        
        if await self.should_escalate(decision_context["type"], decision_context):
            result = await self.prepare_escalation(decision_context)
            self.escalation_history.append({
                "timestamp": decision_start,
                "decision_type": decision_context["type"],
                "escalated": True,
                "reason": result.get("escalation_reason")
            })
        else:
            result = await self.autonomous_decision(decision_context)
            self.decision_history.append({
                "timestamp": decision_start,
                "decision_type": decision_context["type"],
                "escalated": False,
                "duration_seconds": (datetime.now() - decision_start).total_seconds()
            })
        
        return result
    
    async def prepare_escalation(self, context: Dict):
        """Format escalation for human review"""
        return {
            "agent": self.role,
            "decision_needed": context.get("summary", "Decision required"),
            "pm33_strategic_context": await self.extract_pm33_context(context),
            "impact_analysis": await self.analyze_impact(context),
            "recommendation": await self.get_recommendation(context),
            "alternatives": await self.get_alternatives(context),
            "urgency": await self.assess_urgency(context),
            "escalation_reason": await self.explain_escalation_reason(context)
        }
    
    @abstractmethod
    async def autonomous_decision(self, context: Dict):
        """Make autonomous decision - implemented by subclasses"""
        pass
    
    async def extract_pm33_context(self, context: Dict) -> Dict:
        """Extract PM33-specific context for decision"""
        agentic_impact = self.assess_ai_teams_impact(context)
        if hasattr(agentic_impact, '__await__'):
            agentic_impact = await agentic_impact
        
        return {
            "strategic_alignment": self.assess_strategic_alignment(context),
            "day_3_impact": self.assess_day_3_impact(context),
            "agentic_ai_impact": agentic_impact,
            "competitive_implications": self.assess_competitive_impact(context)
        }
    
    def assess_strategic_alignment(self, context: Dict) -> str:
        """Assess alignment with PM33 strategic vision"""
        strategic_keywords = ["pmo transformation", "agentic ai", "strategic automation", "product-led growth"]
        
        context_text = str(context).lower()
        alignment_score = sum(1 for keyword in strategic_keywords if keyword in context_text)
        
        if alignment_score >= 3:
            return "HIGH - directly supports PM33 strategic vision"
        elif alignment_score >= 1:
            return "MEDIUM - partially aligned with strategic goals"
        else:
            return "LOW - limited strategic alignment"
    
    def assess_day_3_impact(self, context: Dict) -> str:
        """Assess impact on Day 3 beta launch"""
        day_3_keywords = ["demo", "beta", "launch", "signup", "conversion"]
        
        context_text = str(context).lower()
        impact_score = sum(1 for keyword in day_3_keywords if keyword in context_text)
        
        if impact_score >= 2:
            return "CRITICAL - directly affects Day 3 success"
        elif impact_score >= 1:
            return "MEDIUM - may impact Day 3 timeline"
        else:
            return "LOW - minimal Day 3 impact"
    
    async def suggest_scope_improvements(self) -> Dict:
        """Analyze performance and suggest scope optimizations"""
        
        # Analyze decision patterns
        decision_analysis = self.analyze_decision_patterns()
        
        # Identify bottlenecks
        bottlenecks = self.identify_current_bottlenecks()
        
        # Generate suggestions
        suggestions = {
            "authority_requests": await self.identify_authority_expansion_opportunities(),
            "efficiency_improvements": await self.identify_efficiency_improvements(),
            "cross_agent_collaboration": await self.identify_collaboration_opportunities(),
            "scope_expansion_justification": {
                "current_limitations": bottlenecks,
                "performance_data": decision_analysis,
                "estimated_efficiency_gains": await self.estimate_efficiency_gains()
            }
        }
        
        return suggestions
    
    def analyze_decision_patterns(self) -> Dict:
        """Analyze historical decision patterns"""
        total_decisions = len(self.decision_history)
        escalated_decisions = len(self.escalation_history)
        
        if total_decisions == 0:
            return {"status": "insufficient_data"}
        
        escalation_rate = escalated_decisions / (total_decisions + escalated_decisions)
        
        return {
            "total_decisions": total_decisions,
            "escalation_rate": escalation_rate,
            "avg_decision_time": self.calculate_avg_decision_time(),
            "most_common_escalation_types": self.get_common_escalation_types()
        }
    
    def identify_current_bottlenecks(self) -> List[str]:
        """Identify current process bottlenecks"""
        bottlenecks = []
        
        # High escalation rate indicates over-restrictive scope
        if len(self.escalation_history) > 0:
            escalation_rate = len(self.escalation_history) / max(1, len(self.decision_history) + len(self.escalation_history))
            if escalation_rate > 0.3:  # >30% escalation rate
                bottlenecks.append("High escalation rate suggests over-restrictive autonomous authority")
        
        # Common escalation types suggest scope expansion opportunities
        common_escalations = self.get_common_escalation_types()
        if common_escalations:
            bottlenecks.append(f"Frequent escalations for: {', '.join(common_escalations)}")
        
        return bottlenecks
    
    def get_common_escalation_types(self) -> List[str]:
        """Get most common types of escalations"""
        escalation_types = {}
        
        for escalation in self.escalation_history:
            decision_type = escalation.get("decision_type", "unknown")
            escalation_types[decision_type] = escalation_types.get(decision_type, 0) + 1
        
        # Return top 3 most common
        return sorted(escalation_types.keys(), key=lambda x: escalation_types[x], reverse=True)[:3]
    
    @abstractmethod
    async def get_pending_approvals(self) -> List[Dict]:
        """Get items pending human approval - implemented by subclasses"""
        pass
    
    @abstractmethod
    async def get_progress_summary(self) -> Dict:
        """Get progress summary - implemented by subclasses"""
        pass