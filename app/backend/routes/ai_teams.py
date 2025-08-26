# app/backend/routes/ai_teams.py
# FastAPI routes for PM33's 4 Agentic AI Teams coordination and orchestration
# Provides REST endpoints for Strategic Intelligence, Workflow Execution, Data Intelligence, Communication
# RELEVANT FILES: services/ai_service.py, ai_teams/orchestrator.py, main.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from services.ai_service import PM33ServiceIntegration
from ai_teams.base_team import BaseRequest, TaskPriority
from utils.logging import logger

router = APIRouter(prefix="/api/ai-teams", tags=["AI Teams"])

# Global service integration instance
ai_service = PM33ServiceIntegration()


# Pydantic models for API validation
class OrchestrationRequest(BaseModel):
    """Request for multi-AI team orchestration"""
    workflow_type: str = Field(..., description="Type of PMO workflow (strategic_planning, competitive_response, etc.)")
    query: str = Field(..., description="Primary strategic question or objective")
    context: Dict[str, Any] = Field(default_factory=dict, description="Company and situational context")
    orchestration_mode: str = Field(default="strategic_cascade", description="Coordination mode")
    required_teams: Optional[List[str]] = Field(default=None, description="AI teams to involve")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    stakeholders: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class StrategicIntelligenceRequest(BaseModel):
    """Request for Strategic Intelligence team"""
    query: str = Field(..., description="Strategic question or analysis request")
    framework: str = Field(default="ice", description="Strategic framework to use")
    context: Dict[str, Any] = Field(default_factory=dict)


class WorkflowGenerationRequest(BaseModel):
    """Request for Workflow Execution team"""
    strategic_objective: str = Field(..., description="Strategic objective to implement")
    timeline_weeks: int = Field(default=8, ge=1, le=52)
    team_size: int = Field(default=5, ge=1, le=20)
    pm_tool: str = Field(default="jira", description="PM tool integration")


class DataIntelligenceRequest(BaseModel):
    """Request for Data Intelligence team"""
    analysis_type: str = Field(..., description="Type of data analysis")
    data_sources: List[str] = Field(..., description="Data sources to analyze")
    context: Dict[str, Any] = Field(default_factory=dict)


class CommunicationRequest(BaseModel):
    """Request for Communication team"""
    communication_type: str = Field(..., description="Type of communication")
    audience: str = Field(..., description="Target audience")
    content: Dict[str, Any] = Field(..., description="Content to communicate")
    format_type: str = Field(default="email", description="Communication format")


# Multi-AI Orchestration Endpoints
@router.post("/orchestrate")
async def orchestrate_ai_teams(request: OrchestrationRequest, background_tasks: BackgroundTasks):
    """
    Orchestrate multiple AI teams for comprehensive PMO transformation
    
    This is the primary endpoint for leveraging PM33's 4 agentic AI teams:
    - Strategic Intelligence (Claude): Complex strategic reasoning and analysis
    - Workflow Execution (OpenAI): Task automation and PM tool integration
    - Data Intelligence (Together AI): Predictive analytics and pattern recognition
    - Communication (Claude/OpenAI): Stakeholder communication and alignment
    
    Supports multiple orchestration modes:
    - sequential: Teams work one after another with context passing
    - parallel: Teams work simultaneously for speed
    - collaborative: Teams iterate and refine together
    - strategic_cascade: Strategic → Workflow → Data → Communication flow
    """
    try:
        logger.info(f"Starting AI orchestration: {request.workflow_type}")
        
        result = await ai_service.orchestrate_ai_teams(
            workflow_type=request.workflow_type,
            query=request.query,
            context=request.context,
            orchestration_mode=request.orchestration_mode,
            required_teams=request.required_teams
        )
        
        # Track successful orchestration
        background_tasks.add_task(
            log_orchestration_success, 
            request.workflow_type, 
            request.orchestration_mode,
            result.get("success_probability", 0.0)
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "orchestration_result": result,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid orchestration request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Orchestration failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI orchestration failed")


@router.get("/orchestration/{request_id}/status")
async def get_orchestration_status(request_id: str):
    """Get status of ongoing orchestration"""
    try:
        status = await ai_service.get_orchestration_status(request_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Orchestration not found")
        
        return JSONResponse(content=status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Status check failed")


# Individual AI Team Endpoints
@router.post("/strategic-intelligence")
async def query_strategic_intelligence(request: StrategicIntelligenceRequest):
    """
    Query Strategic Intelligence AI Team directly
    
    Uses Anthropic Claude for complex strategic reasoning including:
    - Strategic framework analysis (ICE, RICE, Porter's Five Forces)
    - Competitive intelligence and response strategies
    - Market opportunity assessment
    - Risk analysis and mitigation planning
    """
    try:
        result = await ai_service.query_strategic_intelligence(
            query=request.query,
            framework=request.framework,
            context=request.context
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Strategic intelligence query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Strategic intelligence query failed")


@router.post("/workflow-execution")
async def generate_workflow(request: WorkflowGenerationRequest):
    """
    Generate executable workflow using Workflow Execution AI Team
    
    Uses OpenAI for structured workflow generation including:
    - Automated task creation and assignment
    - Cross-functional coordination
    - PM tool integration (Jira, Linear, Monday, Asana)
    - Timeline management and dependency tracking
    """
    try:
        result = await ai_service.generate_workflow(
            strategic_objective=request.strategic_objective,
            timeline_weeks=request.timeline_weeks,
            team_size=request.team_size,
            pm_tool=request.pm_tool
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Workflow generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Workflow generation failed")


@router.post("/data-intelligence")
async def analyze_data_intelligence(request: DataIntelligenceRequest):
    """
    Perform data analysis using Data Intelligence AI Team
    
    Uses Together AI for cost-effective bulk processing including:
    - Predictive analytics and forecasting
    - Pattern recognition and trend analysis
    - Performance optimization recommendations
    - Customer behavior analysis
    """
    try:
        result = await ai_service.analyze_data_intelligence(
            analysis_type=request.analysis_type,
            data_sources=request.data_sources,
            context=request.context
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Data intelligence analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Data intelligence analysis failed")


@router.post("/communication")
async def generate_communication(request: CommunicationRequest):
    """
    Generate stakeholder communication using Communication AI Team
    
    Uses Claude/OpenAI for high-quality communication including:
    - Executive summaries and strategic presentations
    - Stakeholder-specific updates and reports
    - Cross-team alignment facilitation
    - Professional documentation generation
    """
    try:
        result = await ai_service.generate_communication(
            communication_type=request.communication_type,
            audience=request.audience,
            content=request.content,
            format_type=request.format_type
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Communication generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Communication generation failed")


# System Health and Monitoring Endpoints
@router.get("/health")
async def health_check():
    """
    Comprehensive health check for all AI teams and services
    
    Checks status of:
    - 4 AI teams (Strategic, Workflow, Data, Communication)
    - 8 integrated services (Railway, Pinecone, Supabase, Claude, OpenAI, Together AI, PostHog, Resend)
    - Multi-AI orchestration system
    """
    try:
        health = await ai_service.health_check()
        
        status_code = 200 if health.get("overall_status") == "healthy" else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "service": "PM33 AI Teams",
                "health": health,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "PM33 AI Teams",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/capabilities")
async def get_ai_teams_capabilities():
    """
    Get comprehensive list of AI team capabilities
    
    Returns detailed information about what each AI team can do:
    - Strategic Intelligence: Framework analysis, competitive intelligence, strategic planning
    - Workflow Execution: Task automation, PM tool integration, coordination
    - Data Intelligence: Predictive analytics, pattern recognition, optimization
    - Communication: Stakeholder communication, documentation, alignment
    """
    try:
        capabilities = {
            "strategic_intelligence": ai_service.orchestrator.teams["strategic_intelligence"].get_capabilities(),
            "workflow_execution": ai_service.orchestrator.teams["workflow_execution"].get_capabilities(),
            "data_intelligence": ai_service.orchestrator.teams["data_intelligence"].get_capabilities(),
            "communication": ai_service.orchestrator.teams["communication"].get_capabilities()
        }
        
        return JSONResponse(content={
            "ai_teams": capabilities,
            "orchestration_modes": [
                "sequential",
                "parallel", 
                "collaborative",
                "strategic_cascade"
            ],
            "workflow_types": [
                "strategic_planning",
                "competitive_response",
                "feature_prioritization",
                "market_expansion",
                "performance_optimization",
                "stakeholder_alignment"
            ],
            "integrated_services": [
                "Railway PostgreSQL",
                "Pinecone Vector DB",
                "Supabase BaaS",
                "Anthropic Claude",
                "OpenAI",
                "Together AI",
                "PostHog Analytics",
                "Resend Email"
            ]
        })
        
    except Exception as e:
        logger.error(f"Capabilities query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Capabilities query failed")


@router.get("/metrics")
async def get_ai_teams_metrics():
    """Get AI teams performance and usage metrics"""
    try:
        # This would integrate with actual metrics collection
        # For now, return simulated metrics
        metrics = {
            "total_orchestrations": 150,
            "successful_orchestrations": 142,
            "success_rate": 94.7,
            "average_processing_time_ms": 2500,
            "team_utilization": {
                "strategic_intelligence": 85,
                "workflow_execution": 78,
                "data_intelligence": 62,
                "communication": 71
            },
            "popular_workflows": {
                "strategic_planning": 45,
                "competitive_response": 32,
                "feature_prioritization": 28,
                "market_expansion": 18
            },
            "orchestration_modes": {
                "strategic_cascade": 58,
                "collaborative": 25,
                "parallel": 12,
                "sequential": 5
            }
        }
        
        return JSONResponse(content={
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
            "period": "last_30_days"
        })
        
    except Exception as e:
        logger.error(f"Metrics query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics query failed")


# Background task functions
async def log_orchestration_success(workflow_type: str, mode: str, success_probability: float):
    """Log successful orchestration for analytics"""
    logger.info(f"Orchestration completed - Type: {workflow_type}, Mode: {mode}, Success: {success_probability:.2f}")


# Application lifecycle events
@router.on_event("startup")
async def startup_event():
    """Initialize AI service on startup"""
    logger.info("Initializing PM33 AI Teams service...")
    # AI service is already initialized in global scope


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup AI service on shutdown"""
    logger.info("Shutting down PM33 AI Teams service...")
    await ai_service.close()