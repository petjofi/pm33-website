#!/usr/bin/env python3
"""
PM33 Strategic Workflow Engine
Bridges AI strategic intelligence with executable workflows
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import anthropic
from dotenv import load_dotenv

load_dotenv()

class WorkflowType(Enum):
    COMPETITIVE_RESPONSE = "competitive_response"
    FEATURE_PRIORITIZATION = "feature_prioritization"
    MARKET_EXPANSION = "market_expansion"
    RISK_MITIGATION = "risk_mitigation"
    STRATEGIC_PLANNING = "strategic_planning"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class StrategicTask:
    id: str
    title: str
    description: str
    assignee_role: str
    estimated_hours: int
    priority: TaskPriority
    strategic_rationale: str
    success_criteria: str
    dependencies: List[str]
    due_date: datetime

@dataclass
class StrategicWorkflow:
    id: str
    name: str
    description: str
    workflow_type: WorkflowType
    strategic_objective: str
    success_metrics: List[str]
    tasks: List[StrategicTask]
    created_at: datetime
    estimated_completion: datetime

class StrategicWorkflowEngine:
    """Converts AI strategic recommendations into executable workflows"""
    
    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.workflow_templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> Dict[WorkflowType, Dict]:
        """Load workflow templates for different strategic scenarios"""
        return {
            WorkflowType.COMPETITIVE_RESPONSE: {
                "standard_tasks": [
                    "Competitive feature analysis",
                    "Customer impact assessment", 
                    "Technical feasibility review",
                    "Marketing response planning",
                    "Resource allocation analysis",
                    "Timeline planning",
                    "Risk assessment",
                    "Success metrics definition"
                ],
                "typical_duration": 14,  # days
                "critical_roles": ["Product Manager", "Engineering Lead", "Marketing Lead", "Research Lead"]
            },
            WorkflowType.FEATURE_PRIORITIZATION: {
                "standard_tasks": [
                    "ROI analysis completion",
                    "Technical complexity assessment",
                    "User impact analysis",
                    "Resource requirement planning",
                    "Timeline estimation",
                    "Risk identification",
                    "Success criteria definition",
                    "Stakeholder alignment"
                ],
                "typical_duration": 7,  # days
                "critical_roles": ["Product Manager", "Engineering Lead", "UX Research", "Data Analyst"]
            },
            WorkflowType.MARKET_EXPANSION: {
                "standard_tasks": [
                    "Market opportunity analysis",
                    "Competitive landscape review",
                    "Customer segment validation",
                    "Go-to-market planning",
                    "Resource requirement analysis",
                    "Partnership evaluation",
                    "Risk assessment",
                    "Success metrics definition"
                ],
                "typical_duration": 21,  # days
                "critical_roles": ["Product Manager", "Marketing Lead", "Sales Lead", "Business Development"]
            }
        }
    
    async def generate_strategic_workflow(self, strategic_query: str, context: Dict[str, Any]) -> StrategicWorkflow:
        """Generate executable workflow from strategic AI recommendation"""
        
        # First, get strategic analysis and recommendation
        strategic_analysis = await self._get_strategic_analysis(strategic_query, context)
        
        # Determine workflow type
        workflow_type = await self._classify_workflow_type(strategic_query)
        
        # Generate specific workflow tasks
        workflow_tasks = await self._generate_workflow_tasks(strategic_analysis, workflow_type, context)
        
        # Create workflow object
        workflow = StrategicWorkflow(
            id=f"workflow_{int(datetime.now().timestamp())}",
            name=strategic_analysis.get("workflow_name", "Strategic Initiative"),
            description=strategic_analysis.get("description", ""),
            workflow_type=workflow_type,
            strategic_objective=strategic_analysis.get("objective", ""),
            success_metrics=strategic_analysis.get("success_metrics", []),
            tasks=workflow_tasks,
            created_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(days=self.workflow_templates[workflow_type]["typical_duration"])
        )
        
        return workflow
    
    async def _get_strategic_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive strategic analysis from Claude"""
        
        context_str = self._format_context(context)
        
        prompt = f"""
        Analyze this strategic product management question and provide comprehensive guidance:
        
        Question: {query}
        
        Company Context:
        {context_str}
        
        Provide strategic analysis including:
        1. **Situation Assessment**: Current state and key factors
        2. **Strategic Recommendation**: Specific recommended approach
        3. **Success Metrics**: How to measure success (3-5 specific metrics)
        4. **Key Risks**: Primary risks and mitigation approaches
        5. **Resource Requirements**: Team roles and time estimates needed
        6. **Timeline**: Realistic timeline for execution
        7. **Workflow Name**: Concise name for the resulting workflow
        8. **Strategic Objective**: Clear objective statement
        
        Focus on actionable, specific guidance that can be translated into executable tasks.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response into structured data (simplified for MVP)
        analysis_text = response.content[0].text
        
        # Extract key components (would use more sophisticated parsing in production)
        return {
            "full_analysis": analysis_text,
            "workflow_name": self._extract_section(analysis_text, "Workflow Name"),
            "description": self._extract_section(analysis_text, "Situation Assessment"),
            "objective": self._extract_section(analysis_text, "Strategic Objective"),
            "success_metrics": self._extract_list(analysis_text, "Success Metrics"),
            "risks": self._extract_section(analysis_text, "Key Risks"),
            "timeline": self._extract_section(analysis_text, "Timeline")
        }
    
    async def _classify_workflow_type(self, query: str) -> WorkflowType:
        """Classify the type of workflow needed based on the strategic query"""
        
        classification_prompt = f"""
        Classify this product management query into one of these workflow types:
        - competitive_response: Responding to competitor actions
        - feature_prioritization: Deciding between features or initiatives  
        - market_expansion: Entering new markets or segments
        - risk_mitigation: Addressing identified risks or problems
        - strategic_planning: Long-term strategic planning and roadmapping
        
        Query: {query}
        
        Respond with just the workflow type (e.g., "competitive_response"):
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": classification_prompt}]
        )
        
        classification = response.content[0].text.strip().lower()
        
        # Map to enum (with fallback)
        type_mapping = {
            "competitive_response": WorkflowType.COMPETITIVE_RESPONSE,
            "feature_prioritization": WorkflowType.FEATURE_PRIORITIZATION,
            "market_expansion": WorkflowType.MARKET_EXPANSION,
            "risk_mitigation": WorkflowType.RISK_MITIGATION,
            "strategic_planning": WorkflowType.STRATEGIC_PLANNING
        }
        
        return type_mapping.get(classification, WorkflowType.STRATEGIC_PLANNING)
    
    async def _generate_workflow_tasks(self, strategic_analysis: Dict, workflow_type: WorkflowType, context: Dict) -> List[StrategicTask]:
        """Generate specific executable tasks from strategic analysis"""
        
        template = self.workflow_templates[workflow_type]
        
        task_generation_prompt = f"""
        Based on this strategic analysis, create a detailed task breakdown for execution:
        
        Strategic Analysis:
        {strategic_analysis.get('full_analysis', '')}
        
        Workflow Type: {workflow_type.value}
        Standard Tasks for this type: {template['standard_tasks']}
        
        For each task, provide:
        1. **Task Title**: Clear, actionable title
        2. **Description**: Specific deliverables and approach
        3. **Assignee Role**: Who should own this (Product Manager, Engineering Lead, etc.)
        4. **Estimated Hours**: Realistic time estimate
        5. **Priority**: Critical/High/Medium/Low
        6. **Strategic Rationale**: Why this task supports the strategic objective
        7. **Success Criteria**: How to know the task is complete
        8. **Dependencies**: Which other tasks must be completed first
        
        Generate 6-10 specific tasks that will execute this strategic recommendation.
        
        Format as JSON array with each task as an object.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": task_generation_prompt}]
        )
        
        # Parse tasks (simplified for MVP - would use structured JSON parsing)
        tasks_data = self._parse_tasks_from_response(response.content[0].text)
        
        # Convert to StrategicTask objects
        tasks = []
        base_date = datetime.now() + timedelta(days=1)  # Start tomorrow
        
        for i, task_data in enumerate(tasks_data):
            task = StrategicTask(
                id=f"task_{int(datetime.now().timestamp())}_{i}",
                title=task_data.get("title", f"Strategic Task {i+1}"),
                description=task_data.get("description", ""),
                assignee_role=task_data.get("assignee_role", "Product Manager"),
                estimated_hours=task_data.get("estimated_hours", 8),
                priority=TaskPriority(task_data.get("priority", "medium").lower()),
                strategic_rationale=task_data.get("strategic_rationale", ""),
                success_criteria=task_data.get("success_criteria", ""),
                dependencies=task_data.get("dependencies", []),
                due_date=base_date + timedelta(days=i*2)  # Stagger task due dates
            )
            tasks.append(task)
        
        return tasks
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format company context for AI analysis"""
        formatted_context = []
        
        if context.get("company_name"):
            formatted_context.append(f"Company: {context['company_name']}")
        
        if context.get("product_description"):
            formatted_context.append(f"Product: {context['product_description']}")
            
        if context.get("current_metrics"):
            metrics = context["current_metrics"]
            formatted_context.append(f"Key Metrics: {json.dumps(metrics, indent=2)}")
            
        if context.get("team_size"):
            formatted_context.append(f"Team Size: {context['team_size']} people")
            
        if context.get("current_tools"):
            formatted_context.append(f"Current Tools: {', '.join(context['current_tools'])}")
        
        return "\n".join(formatted_context) if formatted_context else "No additional context provided"
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from analysis text"""
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section_name.lower() in line.lower() and ('**' in line or '#' in line):
                in_section = True
                continue
            elif in_section and ('**' in line or line.startswith('#')):
                break
            elif in_section:
                section_content.append(line)
        
        return '\n'.join(section_content).strip()
    
    def _extract_list(self, text: str, section_name: str) -> List[str]:
        """Extract a list from a section"""
        section_text = self._extract_section(text, section_name)
        
        # Extract bullet points or numbered items
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or (line and line[0].isdigit()):
                # Remove bullet point or number prefix
                clean_line = line.lstrip('-*0123456789. ').strip()
                if clean_line:
                    items.append(clean_line)
        
        return items[:5]  # Limit to 5 items
    
    def _parse_tasks_from_response(self, response_text: str) -> List[Dict]:
        """Parse task details from AI response (simplified for MVP)"""
        
        # This is a simplified parser - in production would use structured JSON
        # For MVP, create standard tasks based on workflow type
        
        standard_tasks = [
            {
                "title": "Strategic Analysis and Planning",
                "description": "Complete detailed analysis of the strategic situation and create execution plan",
                "assignee_role": "Product Manager", 
                "estimated_hours": 16,
                "priority": "high",
                "strategic_rationale": "Foundation for all subsequent strategic actions",
                "success_criteria": "Comprehensive analysis document with clear recommendations",
                "dependencies": []
            },
            {
                "title": "Stakeholder Alignment and Communication",
                "description": "Align key stakeholders on strategic approach and get buy-in for execution plan",
                "assignee_role": "Product Manager",
                "estimated_hours": 8,
                "priority": "critical",
                "strategic_rationale": "Ensures organizational support for strategic initiative",
                "success_criteria": "Stakeholder sign-off on strategic approach",
                "dependencies": ["Strategic Analysis and Planning"]
            },
            {
                "title": "Resource Planning and Allocation",
                "description": "Determine resource requirements and allocate team capacity for execution",
                "assignee_role": "Engineering Lead",
                "estimated_hours": 12,
                "priority": "high",
                "strategic_rationale": "Ensures adequate resources for successful execution",
                "success_criteria": "Resource plan with clear allocations and timeline",
                "dependencies": ["Strategic Analysis and Planning"]
            },
            {
                "title": "Risk Assessment and Mitigation Planning",
                "description": "Identify potential risks and create mitigation strategies",
                "assignee_role": "Product Manager",
                "estimated_hours": 6,
                "priority": "medium",
                "strategic_rationale": "Proactive risk management ensures smoother execution",
                "success_criteria": "Risk registry with mitigation plans for top risks",
                "dependencies": ["Strategic Analysis and Planning"]
            },
            {
                "title": "Success Metrics and Tracking Setup",
                "description": "Define success metrics and set up tracking and reporting mechanisms",
                "assignee_role": "Data Analyst",
                "estimated_hours": 10,
                "priority": "medium",
                "strategic_rationale": "Enables measurement of strategic initiative success",
                "success_criteria": "Metrics dashboard with baseline measurements",
                "dependencies": ["Strategic Analysis and Planning"]
            },
            {
                "title": "Execution Kick-off and Initial Implementation",
                "description": "Begin execution of strategic initiative with initial implementation phase",
                "assignee_role": "Product Manager",
                "estimated_hours": 20,
                "priority": "critical",
                "strategic_rationale": "Translates strategy into concrete action and momentum",
                "success_criteria": "First milestone of strategic initiative completed",
                "dependencies": ["Stakeholder Alignment and Communication", "Resource Planning and Allocation"]
            }
        ]
        
        return standard_tasks
    
    async def sync_workflow_to_external_tools(self, workflow: StrategicWorkflow, integration_config: Dict) -> Dict[str, Any]:
        """Sync generated workflow to external PM tools (Jira, Linear, etc.)"""
        
        sync_results = {}
        
        # Example integration with Jira (would be implemented based on specific tool APIs)
        if integration_config.get("jira_enabled"):
            jira_project_key = integration_config.get("jira_project_key")
            
            # Create epic for strategic workflow
            epic_data = {
                "summary": workflow.name,
                "description": f"Strategic Objective: {workflow.strategic_objective}\n\n{workflow.description}",
                "issuetype": {"name": "Epic"},
                "project": {"key": jira_project_key}
            }
            
            # Create individual tasks as stories under epic
            task_sync_results = []
            for task in workflow.tasks:
                story_data = {
                    "summary": task.title,
                    "description": f"Strategic Rationale: {task.strategic_rationale}\n\nSuccess Criteria: {task.success_criteria}\n\n{task.description}",
                    "issuetype": {"name": "Story"},
                    "project": {"key": jira_project_key},
                    "priority": {"name": task.priority.value.title()},
                    "duedate": task.due_date.strftime("%Y-%m-%d")
                }
                task_sync_results.append({"task_id": task.id, "jira_data": story_data})
            
            sync_results["jira"] = {
                "epic": epic_data,
                "stories": task_sync_results
            }
        
        return sync_results

# Example usage
async def example_strategic_workflow():
    """Example of how the strategic workflow engine works"""
    
    engine = StrategicWorkflowEngine()
    
    # Example strategic query
    query = "Our main competitor just launched a feature similar to ours but with better UX. How should we respond?"
    
    # Company context
    context = {
        "company_name": "PM33",
        "product_description": "AI-native product management platform",
        "current_metrics": {
            "monthly_users": 1200,
            "churn_rate": "3%",
            "nps": 67
        },
        "team_size": 8,
        "current_tools": ["Jira", "Slack", "Mixpanel"]
    }
    
    # Generate strategic workflow
    workflow = await engine.generate_strategic_workflow(query, context)
    
    print(f"Generated Workflow: {workflow.name}")
    print(f"Strategic Objective: {workflow.strategic_objective}")
    print(f"Number of tasks: {len(workflow.tasks)}")
    
    for i, task in enumerate(workflow.tasks[:3]):  # Show first 3 tasks
        print(f"\nTask {i+1}: {task.title}")
        print(f"Assignee: {task.assignee_role}")
        print(f"Priority: {task.priority.value}")
        print(f"Strategic Rationale: {task.strategic_rationale}")

if __name__ == "__main__":
    asyncio.run(example_strategic_workflow())