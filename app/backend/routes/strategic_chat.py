from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategic_workflow_engine import StrategicWorkflowEngine

router = APIRouter(prefix="/api/strategic", tags=["strategic"])

class StrategyQuery(BaseModel):
    query: str
    context: Dict[str, Any] = {}

class ChatMessage(BaseModel):
    message: str
    context: Dict[str, Any] = {}

@router.post("/chat")
async def strategic_chat(message: ChatMessage):
    """Strategic AI chat with workflow generation"""
    engine = StrategicWorkflowEngine()
    
    # Generate strategic response
    workflow = await engine.generate_strategic_workflow(
        message.message, 
        message.context
    )
    
    return {
        "response": f"Here's your strategic analysis with executable plan:",
        "workflow": {
            "id": workflow.id,
            "name": workflow.name,
            "objective": workflow.strategic_objective,
            "tasks": [
                {
                    "title": task.title,
                    "assignee": task.assignee_role,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat()
                } for task in workflow.tasks[:5]  # First 5 tasks
            ]
        }
    }

@router.post("/workflow/generate")
async def generate_workflow(query: StrategyQuery):
    """Generate executable workflow from strategic query"""
    engine = StrategicWorkflowEngine()
    workflow = await engine.generate_strategic_workflow(query.query, query.context)
    
    return {
        "workflow_id": workflow.id,
        "name": workflow.name,
        "strategic_objective": workflow.strategic_objective,
        "total_tasks": len(workflow.tasks),
        "tasks": [
            {
                "title": task.title,
                "description": task.description,
                "assignee": task.assignee_role,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat(),
                "strategic_rationale": task.strategic_rationale
            } for task in workflow.tasks
        ]
    }