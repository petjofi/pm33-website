#!/usr/bin/env python3
"""
PM33 Cross-Agent Coordination System
Enterprise-grade multi-agent orchestration and coordination platform

This system orchestrates all PM33 agents (Strategic Consultant, UX Validator, 
Design Expert, API Evaluator, Cost Optimizer, etc.) to work together seamlessly
for comprehensive product management intelligence and decision support.

Key Features:
- Agent registry and capability discovery
- Task orchestration and workflow management  
- Inter-agent communication and data sharing
- Quality gates and validation checkpoints
- Performance monitoring and optimization
- Conflict resolution and consensus building
- Context sharing and knowledge management
- Automated agent collaboration patterns
"""

import json
import logging
import asyncio
import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Coroutine
from datetime import datetime, timedelta
import hashlib
import queue
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future
import subprocess
import sys

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pm33_cross_agent_coordinator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of PM33 agents in the coordination system"""
    STRATEGIC_CONSULTANT = "strategic_consultant"
    UX_WORKFLOW_VALIDATOR = "ux_workflow_validator"
    DESIGN_EXPERT = "design_expert"
    API_RESPONSE_EVALUATOR = "api_response_evaluator"
    LLM_COST_OPTIMIZER = "llm_cost_optimizer"
    PROMPT_ENGINEERING_SUITE = "prompt_engineering_suite"
    DECISION_VALIDATOR = "decision_validator"
    DATA_INTELLIGENCE = "data_intelligence"
    WORKFLOW_EXECUTION = "workflow_execution"
    COMMUNICATION = "communication"

class TaskType(Enum):
    """Types of tasks that can be coordinated across agents"""
    STRATEGIC_ANALYSIS = "strategic_analysis"
    DECISION_VALIDATION = "decision_validation"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    DESIGN_REVIEW = "design_review"
    UX_VALIDATION = "ux_validation"
    API_OPTIMIZATION = "api_optimization"
    COST_OPTIMIZATION = "cost_optimization"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    COMPREHENSIVE_REVIEW = "comprehensive_review"
    QUALITY_ASSURANCE = "quality_assurance"

class TaskPriority(Enum):
    """Task priority levels for coordination"""
    CRITICAL = "critical"     # Immediate attention required
    HIGH = "high"            # Complete within 1 hour
    MEDIUM = "medium"        # Complete within 4 hours  
    LOW = "low"             # Complete within 24 hours
    BACKGROUND = "background" # Complete when resources available

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_DEPENDENCY = "waiting_dependency"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(Enum):
    """Agent availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    ERROR = "error"

@dataclass
class AgentCapability:
    """Capability definition for an agent"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    processing_time_estimate: float  # seconds
    resource_requirements: Dict[str, Any]
    quality_metrics: List[str]
    dependencies: List[str] = field(default_factory=list)

@dataclass
class AgentInfo:
    """Agent information and status"""
    agent_id: str
    agent_type: AgentType
    name: str
    version: str
    capabilities: List[AgentCapability]
    status: AgentStatus
    current_load: float  # 0.0 to 1.0
    max_concurrent_tasks: int
    performance_metrics: Dict[str, float]
    last_heartbeat: datetime = field(default_factory=datetime.now)
    endpoint: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CoordinatedTask:
    """Task definition for cross-agent coordination"""
    task_id: str
    task_type: TaskType
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    required_agents: List[AgentType] = field(default_factory=list)
    assigned_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    workflow_id: Optional[str] = None

@dataclass
class WorkflowDefinition:
    """Multi-agent workflow definition"""
    workflow_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]  # Step definitions with agent assignments
    success_criteria: List[str]
    rollback_strategy: Optional[str] = None
    max_execution_time: Optional[int] = None  # seconds

@dataclass
class CoordinationResult:
    """Result from cross-agent coordination"""
    task_id: str
    success: bool
    results: Dict[str, Any]
    agent_contributions: Dict[str, Dict[str, Any]]
    execution_time: float
    quality_scores: Dict[str, float]
    recommendations: List[str]
    next_actions: List[str]
    confidence_score: float
    validation_results: Dict[str, Any]

class CrossAgentCoordinator:
    """
    Central coordination system for PM33 multi-agent collaboration
    
    Orchestrates complex workflows across multiple specialized agents,
    ensuring quality, consistency, and optimal resource utilization.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Cross-Agent Coordinator"""
        self.config = self._load_config(config_path)
        
        # Agent management
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_endpoints: Dict[AgentType, List[str]] = {}
        
        # Task management
        self.tasks: Dict[str, CoordinatedTask] = {}
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.active_tasks: Dict[str, Future] = {}
        
        # Workflow management
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_templates: Dict[str, WorkflowDefinition] = {}
        
        # Execution management
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.coordination_history: List[CoordinationResult] = []
        
        # Communication channels
        self.message_queues: Dict[str, queue.Queue] = {}
        self.shared_context: Dict[str, Any] = {}
        
        # Quality and performance tracking
        self.quality_metrics: Dict[str, List[float]] = {}
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
        # Initialize built-in workflows
        self._initialize_workflow_templates()
        
        # Start coordination engine
        self._start_coordination_engine()
        
        logger.info("PM33 Cross-Agent Coordinator initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load coordinator configuration"""
        default_config = {
            "heartbeat_interval": 30,  # seconds
            "task_timeout": 3600,      # seconds
            "max_retries": 3,
            "quality_threshold": 0.8,
            "coordination_patterns": {
                "sequential": {"max_parallel": 1},
                "parallel": {"max_parallel": 5},
                "pipeline": {"buffer_size": 3},
                "consensus": {"min_agreement": 0.7}
            },
            "agent_defaults": {
                "max_concurrent_tasks": 3,
                "heartbeat_timeout": 90,
                "performance_window": 100
            },
            "known_agents": {
                AgentType.STRATEGIC_CONSULTANT: {
                    "module": "pm33_strategic_consultant_agent",
                    "class": "PM33StrategicConsultant"
                },
                AgentType.UX_WORKFLOW_VALIDATOR: {
                    "module": "mcp_ux_workflow_validator",
                    "class": "UXWorkflowValidator"
                },
                AgentType.API_RESPONSE_EVALUATOR: {
                    "module": "pm33_api_response_evaluator",
                    "class": "APIResponseEvaluator"
                },
                AgentType.LLM_COST_OPTIMIZER: {
                    "module": "pm33_llm_cost_optimizer",
                    "class": "LLMCostOptimizer"
                },
                AgentType.DECISION_VALIDATOR: {
                    "module": "pm33_strategic_decision_validator",
                    "class": "StrategicDecisionValidator"
                },
                AgentType.PROMPT_ENGINEERING_SUITE: {
                    "module": "pm33_prompt_engineering_suite",
                    "class": "PromptEngineeringSuite"
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_workflow_templates(self):
        """Initialize built-in workflow templates"""
        
        # Comprehensive Product Decision Workflow
        product_decision_workflow = WorkflowDefinition(
            workflow_id="comprehensive_product_decision",
            name="Comprehensive Product Decision Analysis",
            description="End-to-end product decision validation using all PM33 agents",
            steps=[
                {
                    "step": 1,
                    "name": "Strategic Analysis",
                    "agent": AgentType.STRATEGIC_CONSULTANT,
                    "action": "analyze_decision_context",
                    "inputs": ["decision_context", "market_data"],
                    "outputs": ["strategic_analysis", "framework_recommendations"]
                },
                {
                    "step": 2,
                    "name": "Decision Validation",
                    "agent": AgentType.DECISION_VALIDATOR,
                    "action": "validate_decision",
                    "inputs": ["decision_context", "strategic_analysis"],
                    "outputs": ["validation_results", "risk_assessment"]
                },
                {
                    "step": 3,
                    "name": "Cost Impact Analysis",
                    "agent": AgentType.LLM_COST_OPTIMIZER,
                    "action": "analyze_cost_impact",
                    "inputs": ["decision_context", "implementation_plan"],
                    "outputs": ["cost_analysis", "optimization_recommendations"]
                },
                {
                    "step": 4,
                    "name": "UX Impact Validation",
                    "agent": AgentType.UX_WORKFLOW_VALIDATOR,
                    "action": "validate_ux_impact",
                    "inputs": ["decision_context", "user_workflows"],
                    "outputs": ["ux_validation", "workflow_recommendations"]
                },
                {
                    "step": 5,
                    "name": "Quality Gate Review",
                    "agent": AgentType.STRATEGIC_CONSULTANT,
                    "action": "synthesize_results",
                    "inputs": ["all_agent_outputs"],
                    "outputs": ["final_recommendation", "implementation_plan"]
                }
            ],
            success_criteria=[
                "All agents complete successfully",
                "Quality scores > 0.8 across all validations",
                "No critical risks identified",
                "Strategic alignment score > 0.75"
            ]
        )
        
        # API Quality Optimization Workflow
        api_optimization_workflow = WorkflowDefinition(
            workflow_id="api_quality_optimization",
            name="API Quality Optimization Pipeline",
            description="Comprehensive API response optimization using cost and quality analysis",
            steps=[
                {
                    "step": 1,
                    "name": "API Response Evaluation",
                    "agent": AgentType.API_RESPONSE_EVALUATOR,
                    "action": "evaluate_responses",
                    "inputs": ["api_responses", "quality_criteria"],
                    "outputs": ["quality_scores", "improvement_areas"]
                },
                {
                    "step": 2,
                    "name": "Cost Optimization",
                    "agent": AgentType.LLM_COST_OPTIMIZER,
                    "action": "optimize_llm_usage",
                    "inputs": ["api_responses", "cost_constraints"],
                    "outputs": ["cost_optimizations", "provider_recommendations"]
                },
                {
                    "step": 3,
                    "name": "Prompt Optimization",
                    "agent": AgentType.PROMPT_ENGINEERING_SUITE,
                    "action": "optimize_prompts",
                    "inputs": ["api_responses", "performance_targets"],
                    "outputs": ["optimized_prompts", "performance_predictions"]
                }
            ],
            success_criteria=[
                "API quality scores improved by >15%",
                "Cost reduced by >10% while maintaining quality",
                "Response time improved by >20%"
            ]
        )
        
        # Feature Design Review Workflow
        feature_design_workflow = WorkflowDefinition(
            workflow_id="feature_design_review",
            name="Feature Design Review Process",
            description="Comprehensive feature design validation across UX, design, and strategy",
            steps=[
                {
                    "step": 1,
                    "name": "Strategic Alignment",
                    "agent": AgentType.STRATEGIC_CONSULTANT,
                    "action": "validate_strategic_fit",
                    "inputs": ["feature_spec", "strategic_objectives"],
                    "outputs": ["alignment_analysis", "strategic_recommendations"]
                },
                {
                    "step": 2,
                    "name": "UX Workflow Validation",
                    "agent": AgentType.UX_WORKFLOW_VALIDATOR,
                    "action": "validate_user_workflows",
                    "inputs": ["feature_spec", "user_journeys"],
                    "outputs": ["ux_validation", "workflow_improvements"]
                },
                {
                    "step": 3,
                    "name": "Design Compliance Review",
                    "agent": AgentType.DESIGN_EXPERT,
                    "action": "validate_design_compliance",
                    "inputs": ["design_mockups", "design_system"],
                    "outputs": ["design_validation", "compliance_report"]
                }
            ],
            success_criteria=[
                "Strategic alignment score > 0.8",
                "UX validation passes all critical checks", 
                "Design compliance score > 0.9"
            ]
        )
        
        self.workflow_templates = {
            "comprehensive_product_decision": product_decision_workflow,
            "api_quality_optimization": api_optimization_workflow,
            "feature_design_review": feature_design_workflow
        }
        
        logger.info(f"Initialized {len(self.workflow_templates)} workflow templates")
    
    def register_agent(self, agent_info: AgentInfo) -> bool:
        """Register an agent with the coordination system"""
        
        try:
            # Validate agent info
            if not agent_info.agent_id or not agent_info.agent_type:
                raise ValueError("Agent ID and type are required")
            
            # Check for conflicts
            if agent_info.agent_id in self.agents:
                logger.warning(f"Agent {agent_info.agent_id} already registered, updating")
            
            # Store agent info
            self.agents[agent_info.agent_id] = agent_info
            
            # Update agent endpoints
            if agent_info.agent_type not in self.agent_endpoints:
                self.agent_endpoints[agent_info.agent_type] = []
            
            if agent_info.endpoint and agent_info.endpoint not in self.agent_endpoints[agent_info.agent_type]:
                self.agent_endpoints[agent_info.agent_type].append(agent_info.endpoint)
            
            # Create message queue for agent
            self.message_queues[agent_info.agent_id] = queue.Queue()
            
            logger.info(f"Registered agent: {agent_info.agent_id} ({agent_info.agent_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_info.agent_id}: {e}")
            return False
    
    def discover_agents(self) -> Dict[AgentType, List[str]]:
        """Discover and register available PM33 agents"""
        
        discovered = {}
        
        for agent_type, agent_config in self.config["known_agents"].items():
            try:
                # Attempt to import and instantiate agent
                module_name = agent_config["module"]
                class_name = agent_config["class"]
                
                # Check if module exists
                spec = None
                try:
                    import importlib.util
                    spec = importlib.util.find_spec(module_name)
                except ImportError:
                    continue
                
                if spec and spec.origin and Path(spec.origin).exists():
                    # Create agent info for discovered agent
                    agent_id = f"{agent_type.value}_001"
                    
                    # Define capabilities based on agent type
                    capabilities = self._get_default_capabilities(agent_type)
                    
                    agent_info = AgentInfo(
                        agent_id=agent_id,
                        agent_type=agent_type,
                        name=f"PM33 {agent_type.value.replace('_', ' ').title()}",
                        version="1.0.0",
                        capabilities=capabilities,
                        status=AgentStatus.AVAILABLE,
                        current_load=0.0,
                        max_concurrent_tasks=self.config["agent_defaults"]["max_concurrent_tasks"],
                        performance_metrics={}
                    )
                    
                    # Register discovered agent
                    if self.register_agent(agent_info):
                        if agent_type not in discovered:
                            discovered[agent_type] = []
                        discovered[agent_type].append(agent_id)
                
            except Exception as e:
                logger.warning(f"Failed to discover agent {agent_type.value}: {e}")
        
        logger.info(f"Discovered {sum(len(agents) for agents in discovered.values())} agents across {len(discovered)} types")
        return discovered
    
    def _get_default_capabilities(self, agent_type: AgentType) -> List[AgentCapability]:
        """Get default capabilities for agent type"""
        
        capability_definitions = {
            AgentType.STRATEGIC_CONSULTANT: [
                AgentCapability(
                    name="strategic_analysis",
                    description="Comprehensive strategic analysis using multiple frameworks",
                    input_types=["decision_context", "market_data", "competitive_intelligence"],
                    output_types=["strategic_analysis", "framework_scores", "recommendations"],
                    processing_time_estimate=60.0,
                    resource_requirements={"cpu": "high", "memory": "medium"},
                    quality_metrics=["accuracy", "completeness", "strategic_value"]
                ),
                AgentCapability(
                    name="framework_application",
                    description="Apply strategic frameworks (RICE, ICE, Porter's Five Forces)",
                    input_types=["decision_context", "framework_type"],
                    output_types=["framework_analysis", "scores", "recommendations"],
                    processing_time_estimate=30.0,
                    resource_requirements={"cpu": "medium", "memory": "low"},
                    quality_metrics=["accuracy", "relevance", "actionability"]
                )
            ],
            AgentType.DECISION_VALIDATOR: [
                AgentCapability(
                    name="decision_validation",
                    description="Validate strategic decisions against multiple criteria",
                    input_types=["decision_context", "validation_frameworks"],
                    output_types=["validation_results", "risk_assessment", "recommendations"],
                    processing_time_estimate=45.0,
                    resource_requirements={"cpu": "high", "memory": "medium"},
                    quality_metrics=["thoroughness", "accuracy", "risk_coverage"]
                )
            ],
            AgentType.UX_WORKFLOW_VALIDATOR: [
                AgentCapability(
                    name="ux_validation",
                    description="Validate user experience and workflow patterns",
                    input_types=["user_workflows", "ux_patterns", "design_specs"],
                    output_types=["ux_validation", "workflow_analysis", "improvements"],
                    processing_time_estimate=20.0,
                    resource_requirements={"cpu": "medium", "memory": "low"},
                    quality_metrics=["usability", "accessibility", "workflow_efficiency"]
                )
            ],
            AgentType.API_RESPONSE_EVALUATOR: [
                AgentCapability(
                    name="api_evaluation",
                    description="Evaluate API responses for quality and performance",
                    input_types=["api_responses", "quality_criteria", "performance_targets"],
                    output_types=["quality_scores", "performance_metrics", "improvements"],
                    processing_time_estimate=15.0,
                    resource_requirements={"cpu": "medium", "memory": "low"},
                    quality_metrics=["response_quality", "performance", "consistency"]
                )
            ],
            AgentType.LLM_COST_OPTIMIZER: [
                AgentCapability(
                    name="cost_optimization",
                    description="Optimize LLM usage for cost and performance",
                    input_types=["llm_requests", "cost_constraints", "quality_requirements"],
                    output_types=["cost_analysis", "optimization_plan", "provider_recommendations"],
                    processing_time_estimate=25.0,
                    resource_requirements={"cpu": "medium", "memory": "medium"},
                    quality_metrics=["cost_efficiency", "quality_maintained", "performance_impact"]
                )
            ],
            AgentType.PROMPT_ENGINEERING_SUITE: [
                AgentCapability(
                    name="prompt_optimization",
                    description="Optimize prompts for multiple LLM providers",
                    input_types=["prompts", "performance_targets", "provider_specs"],
                    output_types=["optimized_prompts", "performance_predictions", "ab_test_plans"],
                    processing_time_estimate=40.0,
                    resource_requirements={"cpu": "high", "memory": "medium"},
                    quality_metrics=["prompt_effectiveness", "cross_provider_consistency", "performance_gain"]
                )
            ]
        }
        
        return capability_definitions.get(agent_type, [])
    
    def create_task(
        self,
        task_type: TaskType,
        title: str,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        required_agents: Optional[List[AgentType]] = None,
        dependencies: Optional[List[str]] = None,
        deadline: Optional[datetime] = None,
        quality_gates: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new coordinated task"""
        
        task_id = f"task_{hashlib.md5(f'{task_type.value}_{title}_{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        # Auto-determine required agents if not specified
        if required_agents is None:
            required_agents = self._determine_required_agents(task_type, input_data)
        
        # Set default quality gates
        if quality_gates is None:
            quality_gates = self._get_default_quality_gates(task_type)
        
        task = CoordinatedTask(
            task_id=task_id,
            task_type=task_type,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            input_data=input_data,
            required_agents=required_agents,
            dependencies=dependencies or [],
            quality_gates=quality_gates,
            deadline=deadline,
            context=context or {}
        )
        
        self.tasks[task_id] = task
        
        # Add to task queue with priority
        priority_value = self._get_priority_value(priority)
        self.task_queue.put((priority_value, task_id))
        
        logger.info(f"Created task {task_id}: {title} (priority: {priority.value})")
        return task_id
    
    def _determine_required_agents(self, task_type: TaskType, input_data: Dict[str, Any]) -> List[AgentType]:
        """Automatically determine required agents for task type"""
        
        agent_mapping = {
            TaskType.STRATEGIC_ANALYSIS: [AgentType.STRATEGIC_CONSULTANT],
            TaskType.DECISION_VALIDATION: [AgentType.DECISION_VALIDATOR, AgentType.STRATEGIC_CONSULTANT],
            TaskType.WORKFLOW_OPTIMIZATION: [AgentType.UX_WORKFLOW_VALIDATOR],
            TaskType.UX_VALIDATION: [AgentType.UX_WORKFLOW_VALIDATOR, AgentType.DESIGN_EXPERT],
            TaskType.API_OPTIMIZATION: [AgentType.API_RESPONSE_EVALUATOR, AgentType.LLM_COST_OPTIMIZER],
            TaskType.COST_OPTIMIZATION: [AgentType.LLM_COST_OPTIMIZER],
            TaskType.PROMPT_OPTIMIZATION: [AgentType.PROMPT_ENGINEERING_SUITE],
            TaskType.COMPREHENSIVE_REVIEW: [
                AgentType.STRATEGIC_CONSULTANT,
                AgentType.DECISION_VALIDATOR,
                AgentType.UX_WORKFLOW_VALIDATOR
            ],
            TaskType.QUALITY_ASSURANCE: [
                AgentType.API_RESPONSE_EVALUATOR,
                AgentType.UX_WORKFLOW_VALIDATOR
            ]
        }
        
        base_agents = agent_mapping.get(task_type, [AgentType.STRATEGIC_CONSULTANT])
        
        # Add context-specific agents based on input data
        if "api_responses" in input_data:
            if AgentType.API_RESPONSE_EVALUATOR not in base_agents:
                base_agents.append(AgentType.API_RESPONSE_EVALUATOR)
        
        if "cost_constraints" in input_data or "llm_usage" in input_data:
            if AgentType.LLM_COST_OPTIMIZER not in base_agents:
                base_agents.append(AgentType.LLM_COST_OPTIMIZER)
        
        if "user_workflows" in input_data or "ux_requirements" in input_data:
            if AgentType.UX_WORKFLOW_VALIDATOR not in base_agents:
                base_agents.append(AgentType.UX_WORKFLOW_VALIDATOR)
        
        return base_agents
    
    def _get_default_quality_gates(self, task_type: TaskType) -> List[str]:
        """Get default quality gates for task type"""
        
        quality_gates = {
            TaskType.STRATEGIC_ANALYSIS: [
                "strategic_alignment_score > 0.8",
                "framework_coverage >= 3",
                "confidence_score > 0.7"
            ],
            TaskType.DECISION_VALIDATION: [
                "overall_validation_score > 75",
                "no_critical_risks_identified",
                "benchmark_compliance > 0.8"
            ],
            TaskType.UX_VALIDATION: [
                "accessibility_compliance = 100%",
                "usability_score > 0.85",
                "workflow_efficiency > 0.8"
            ],
            TaskType.API_OPTIMIZATION: [
                "performance_improvement > 15%",
                "cost_reduction > 10%",
                "quality_maintained >= 0.9"
            ],
            TaskType.COMPREHENSIVE_REVIEW: [
                "all_agents_complete_successfully",
                "quality_consensus > 0.8",
                "no_blocking_issues"
            ]
        }
        
        return quality_gates.get(task_type, ["quality_score > 0.8"])
    
    def _get_priority_value(self, priority: TaskPriority) -> int:
        """Convert priority enum to numeric value for queue ordering"""
        priority_values = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 4,
            TaskPriority.BACKGROUND: 5
        }
        return priority_values.get(priority, 3)
    
    def execute_workflow(
        self,
        workflow_template: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a predefined workflow template"""
        
        if workflow_template not in self.workflow_templates:
            raise ValueError(f"Workflow template {workflow_template} not found")
        
        template = self.workflow_templates[workflow_template]
        workflow_id = f"workflow_{hashlib.md5(f'{workflow_template}_{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        # Create workflow instance
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=template.name,
            description=template.description,
            steps=template.steps.copy(),
            success_criteria=template.success_criteria.copy(),
            rollback_strategy=template.rollback_strategy,
            max_execution_time=template.max_execution_time
        )
        
        self.workflows[workflow_id] = workflow
        
        # Create tasks for each step
        task_ids = []
        step_dependencies = []
        
        for i, step in enumerate(workflow.steps):
            step_task_id = self.create_task(
                task_type=TaskType.COMPREHENSIVE_REVIEW,  # Default task type for workflow steps
                title=f"{workflow.name} - {step['name']}",
                description=f"Step {step['step']}: {step.get('description', step['name'])}",
                input_data={**input_data, "workflow_step": step},
                required_agents=[step["agent"]] if "agent" in step else None,
                dependencies=step_dependencies.copy() if i > 0 else None,
                context={**(context or {}), "workflow_id": workflow_id, "step_number": step["step"]},
                priority=TaskPriority.HIGH
            )
            
            task_ids.append(step_task_id)
            step_dependencies.append(step_task_id)  # Sequential execution by default
        
        logger.info(f"Created workflow {workflow_id} with {len(task_ids)} steps")
        return workflow_id
    
    def coordinate_agents(self, task_id: str) -> CoordinationResult:
        """Coordinate multiple agents to complete a task"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Check dependencies
            if not self._check_dependencies(task):
                task.status = TaskStatus.WAITING_DEPENDENCY
                return self._create_coordination_result(task, False, "Dependencies not satisfied")
            
            # Assign agents
            assigned_agents = self._assign_agents(task)
            if not assigned_agents:
                task.status = TaskStatus.FAILED
                return self._create_coordination_result(task, False, "No suitable agents available")
            
            task.assigned_agents = assigned_agents
            
            # Execute task with assigned agents
            agent_results = {}
            execution_start = time.time()
            
            # Execute agents in optimal order
            execution_plan = self._create_execution_plan(task, assigned_agents)
            
            for execution_step in execution_plan:
                step_results = self._execute_agent_step(task, execution_step)
                agent_results.update(step_results)
                
                # Update shared context with intermediate results
                self._update_shared_context(task_id, step_results)
            
            execution_time = time.time() - execution_start
            
            # Validate quality gates
            quality_validation = self._validate_quality_gates(task, agent_results)
            
            if quality_validation["passed"]:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                success = True
                
                # Store results in task
                task.output_data = {
                    "agent_results": agent_results,
                    "quality_validation": quality_validation,
                    "execution_time": execution_time
                }
            else:
                task.status = TaskStatus.FAILED
                success = False
            
            # Create coordination result
            result = CoordinationResult(
                task_id=task_id,
                success=success,
                results=agent_results,
                agent_contributions={agent_id: {"results": agent_results.get(agent_id, {})} for agent_id in assigned_agents},
                execution_time=execution_time,
                quality_scores=quality_validation.get("scores", {}),
                recommendations=self._extract_recommendations(agent_results),
                next_actions=self._generate_next_actions(task, agent_results),
                confidence_score=quality_validation.get("confidence", 0.0),
                validation_results=quality_validation
            )
            
            # Store in history
            self.coordination_history.append(result)
            
            logger.info(f"Completed coordination for task {task_id}: {'SUCCESS' if success else 'FAILED'}")
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            logger.error(f"Coordination failed for task {task_id}: {e}")
            return self._create_coordination_result(task, False, str(e))
    
    def _check_dependencies(self, task: CoordinatedTask) -> bool:
        """Check if task dependencies are satisfied"""
        
        for dep_task_id in task.dependencies:
            if dep_task_id not in self.tasks:
                return False
            
            dep_task = self.tasks[dep_task_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _assign_agents(self, task: CoordinatedTask) -> List[str]:
        """Assign optimal agents to task"""
        
        assigned = []
        
        for required_agent_type in task.required_agents:
            # Find available agents of required type
            available_agents = [
                agent_id for agent_id, agent_info in self.agents.items()
                if (agent_info.agent_type == required_agent_type and
                    agent_info.status == AgentStatus.AVAILABLE and
                    agent_info.current_load < 0.8)
            ]
            
            if not available_agents:
                logger.warning(f"No available agents of type {required_agent_type.value} for task {task.task_id}")
                continue
            
            # Select best agent based on performance metrics
            best_agent = self._select_best_agent(available_agents, task)
            assigned.append(best_agent)
        
        return assigned
    
    def _select_best_agent(self, available_agents: List[str], task: CoordinatedTask) -> str:
        """Select best agent from available options"""
        
        if len(available_agents) == 1:
            return available_agents[0]
        
        # Score agents based on performance metrics and current load
        agent_scores = {}
        
        for agent_id in available_agents:
            agent_info = self.agents[agent_id]
            
            # Base score from performance metrics
            performance_score = sum(agent_info.performance_metrics.values()) / max(len(agent_info.performance_metrics), 1)
            
            # Load penalty
            load_penalty = agent_info.current_load * 0.3
            
            # Task type compatibility bonus
            compatibility_bonus = 0.1 if self._is_agent_compatible(agent_info, task) else 0.0
            
            final_score = performance_score - load_penalty + compatibility_bonus
            agent_scores[agent_id] = final_score
        
        # Return agent with highest score
        best_agent = max(agent_scores.keys(), key=lambda x: agent_scores[x])
        return best_agent
    
    def _is_agent_compatible(self, agent_info: AgentInfo, task: CoordinatedTask) -> bool:
        """Check if agent is particularly compatible with task"""
        
        # Check if agent has capabilities matching task requirements
        for capability in agent_info.capabilities:
            if any(input_type in task.input_data for input_type in capability.input_types):
                return True
        
        return False
    
    def _create_execution_plan(self, task: CoordinatedTask, assigned_agents: List[str]) -> List[Dict[str, Any]]:
        """Create optimal execution plan for assigned agents"""
        
        # For now, simple sequential execution
        # In future, could implement parallel, pipeline, or consensus patterns
        
        execution_plan = []
        
        for i, agent_id in enumerate(assigned_agents):
            agent_info = self.agents[agent_id]
            
            # Determine inputs for this agent
            agent_inputs = self._prepare_agent_inputs(task, agent_info, i)
            
            execution_step = {
                "step": i + 1,
                "agent_id": agent_id,
                "agent_type": agent_info.agent_type,
                "inputs": agent_inputs,
                "expected_outputs": self._get_expected_outputs(agent_info, task),
                "timeout": 300  # 5 minutes default timeout
            }
            
            execution_plan.append(execution_step)
        
        return execution_plan
    
    def _prepare_agent_inputs(self, task: CoordinatedTask, agent_info: AgentInfo, step_index: int) -> Dict[str, Any]:
        """Prepare inputs for specific agent"""
        
        # Start with task input data
        agent_inputs = task.input_data.copy()
        
        # Add context
        agent_inputs["task_context"] = {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "priority": task.priority.value,
            "step_index": step_index
        }
        
        # Add shared context from previous agents
        shared_context = self.shared_context.get(task.task_id, {})
        agent_inputs["shared_context"] = shared_context
        
        # Add agent-specific context
        agent_inputs["agent_context"] = {
            "agent_id": agent_info.agent_id,
            "capabilities": [cap.name for cap in agent_info.capabilities]
        }
        
        return agent_inputs
    
    def _get_expected_outputs(self, agent_info: AgentInfo, task: CoordinatedTask) -> List[str]:
        """Get expected outputs from agent based on capabilities"""
        
        expected_outputs = []
        
        for capability in agent_info.capabilities:
            # Check if capability is relevant to task
            if any(input_type in task.input_data for input_type in capability.input_types):
                expected_outputs.extend(capability.output_types)
        
        return list(set(expected_outputs))  # Remove duplicates
    
    def _execute_agent_step(self, task: CoordinatedTask, execution_step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent step"""
        
        agent_id = execution_step["agent_id"]
        agent_info = self.agents[agent_id]
        
        try:
            # Update agent load
            agent_info.current_load += 0.3
            
            # Simulate agent execution (in production, this would call actual agent)
            step_results = self._simulate_agent_execution(agent_info, execution_step)
            
            # Update agent performance metrics
            self._update_agent_performance(agent_id, step_results)
            
            return {agent_id: step_results}
            
        except Exception as e:
            logger.error(f"Agent step execution failed for {agent_id}: {e}")
            return {agent_id: {"error": str(e), "success": False}}
        finally:
            # Restore agent load
            agent_info.current_load = max(0.0, agent_info.current_load - 0.3)
    
    def _simulate_agent_execution(self, agent_info: AgentInfo, execution_step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent execution (replace with actual agent calls in production)"""
        
        agent_type = agent_info.agent_type
        inputs = execution_step["inputs"]
        
        # Simulate processing time
        processing_time = 2.0  # Default 2 seconds
        if agent_info.capabilities:
            processing_time = agent_info.capabilities[0].processing_time_estimate / 10  # Scale down for simulation
        
        time.sleep(min(processing_time, 5.0))  # Cap at 5 seconds for simulation
        
        # Generate simulated results based on agent type
        if agent_type == AgentType.STRATEGIC_CONSULTANT:
            return {
                "strategic_analysis": {
                    "frameworks_analyzed": ["RICE", "ICE", "Porter's Five Forces"],
                    "strategic_score": 85.2,
                    "recommendations": [
                        "Focus on high-impact, low-effort initiatives",
                        "Consider competitive positioning",
                        "Validate assumptions through customer research"
                    ]
                },
                "confidence": 0.87,
                "processing_time": processing_time,
                "success": True
            }
            
        elif agent_type == AgentType.DECISION_VALIDATOR:
            return {
                "validation_results": {
                    "overall_score": 78.5,
                    "recommendation": "CONDITIONAL_APPROVE",
                    "risk_level": "MEDIUM"
                },
                "risk_assessment": [
                    {
                        "category": "Execution Risk",
                        "level": "MEDIUM",
                        "probability": 0.4,
                        "impact": 6.5
                    }
                ],
                "confidence": 0.82,
                "processing_time": processing_time,
                "success": True
            }
            
        elif agent_type == AgentType.UX_WORKFLOW_VALIDATOR:
            return {
                "ux_validation": {
                    "overall_score": 0.89,
                    "accessibility_compliance": 0.95,
                    "usability_score": 0.87,
                    "workflow_efficiency": 0.91
                },
                "recommendations": [
                    "Improve keyboard navigation",
                    "Add loading states for better UX",
                    "Simplify complex workflows"
                ],
                "confidence": 0.91,
                "processing_time": processing_time,
                "success": True
            }
            
        elif agent_type == AgentType.API_RESPONSE_EVALUATOR:
            return {
                "quality_evaluation": {
                    "overall_quality": 0.84,
                    "performance_score": 0.78,
                    "consistency_score": 0.92
                },
                "improvement_areas": [
                    "Response time optimization",
                    "Error handling enhancement",
                    "API documentation updates"
                ],
                "confidence": 0.86,
                "processing_time": processing_time,
                "success": True
            }
            
        elif agent_type == AgentType.LLM_COST_OPTIMIZER:
            return {
                "cost_analysis": {
                    "current_cost": 245.50,
                    "optimized_cost": 198.20,
                    "savings": 47.30,
                    "savings_percentage": 19.3
                },
                "optimization_plan": [
                    "Switch low-complexity queries to Together AI",
                    "Optimize prompt length for cost efficiency",
                    "Implement intelligent caching"
                ],
                "confidence": 0.88,
                "processing_time": processing_time,
                "success": True
            }
            
        else:
            return {
                "generic_result": {
                    "analysis_completed": True,
                    "quality_score": 0.80
                },
                "confidence": 0.75,
                "processing_time": processing_time,
                "success": True
            }
    
    def _update_shared_context(self, task_id: str, step_results: Dict[str, Any]):
        """Update shared context with step results"""
        
        if task_id not in self.shared_context:
            self.shared_context[task_id] = {}
        
        self.shared_context[task_id].update(step_results)
    
    def _update_agent_performance(self, agent_id: str, step_results: Dict[str, Any]):
        """Update agent performance metrics"""
        
        if agent_id not in self.agents:
            return
        
        agent_info = self.agents[agent_id]
        
        # Extract performance data from results
        if step_results.get("success", False):
            confidence = step_results.get("confidence", 0.8)
            processing_time = step_results.get("processing_time", 10.0)
            
            # Update performance metrics with moving average
            if "accuracy" not in agent_info.performance_metrics:
                agent_info.performance_metrics["accuracy"] = confidence
            else:
                agent_info.performance_metrics["accuracy"] = (
                    agent_info.performance_metrics["accuracy"] * 0.8 + confidence * 0.2
                )
            
            if "avg_processing_time" not in agent_info.performance_metrics:
                agent_info.performance_metrics["avg_processing_time"] = processing_time
            else:
                agent_info.performance_metrics["avg_processing_time"] = (
                    agent_info.performance_metrics["avg_processing_time"] * 0.8 + processing_time * 0.2
                )
            
            agent_info.performance_metrics["success_rate"] = agent_info.performance_metrics.get("success_rate", 1.0)
        else:
            # Update failure rate
            current_success_rate = agent_info.performance_metrics.get("success_rate", 1.0)
            agent_info.performance_metrics["success_rate"] = current_success_rate * 0.9  # Decay on failure
    
    def _validate_quality_gates(self, task: CoordinatedTask, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality gates for task completion"""
        
        validation_result = {
            "passed": True,
            "scores": {},
            "confidence": 1.0,
            "failed_gates": [],
            "warnings": []
        }
        
        try:
            for gate in task.quality_gates:
                gate_result = self._evaluate_quality_gate(gate, agent_results, task)
                
                if not gate_result["passed"]:
                    validation_result["passed"] = False
                    validation_result["failed_gates"].append({
                        "gate": gate,
                        "reason": gate_result["reason"]
                    })
                
                if gate_result["score"] is not None:
                    validation_result["scores"][gate] = gate_result["score"]
                
                # Update overall confidence
                validation_result["confidence"] *= gate_result.get("confidence", 0.9)
        
        except Exception as e:
            logger.error(f"Quality gate validation error: {e}")
            validation_result["passed"] = False
            validation_result["failed_gates"].append({"gate": "validation_error", "reason": str(e)})
        
        return validation_result
    
    def _evaluate_quality_gate(self, gate: str, agent_results: Dict[str, Any], task: CoordinatedTask) -> Dict[str, Any]:
        """Evaluate a specific quality gate"""
        
        # Parse gate condition (simplified parser)
        if ">" in gate:
            metric, threshold_str = gate.split(">")
            metric = metric.strip()
            threshold = float(threshold_str.strip())
            operator = ">"
        elif ">=" in gate:
            metric, threshold_str = gate.split(">=")
            metric = metric.strip()
            threshold = float(threshold_str.strip())
            operator = ">="
        elif "=" in gate:
            metric, threshold_str = gate.split("=")
            metric = metric.strip()
            threshold_str = threshold_str.strip()
            if threshold_str.replace(".", "").replace("%", "").isdigit():
                threshold = float(threshold_str.replace("%", ""))
            else:
                threshold = threshold_str
            operator = "="
        else:
            # Boolean gate
            return self._evaluate_boolean_gate(gate, agent_results, task)
        
        # Extract metric value from agent results
        metric_value = self._extract_metric_value(metric, agent_results)
        
        if metric_value is None:
            return {
                "passed": False,
                "reason": f"Metric {metric} not found in agent results",
                "score": None,
                "confidence": 0.0
            }
        
        # Evaluate condition
        if operator == ">":
            passed = metric_value > threshold
        elif operator == ">=":
            passed = metric_value >= threshold
        elif operator == "=":
            if isinstance(threshold, str):
                passed = str(metric_value) == threshold
            else:
                passed = abs(metric_value - threshold) < 0.01
        else:
            passed = False
        
        return {
            "passed": passed,
            "reason": f"{metric} ({metric_value}) {'meets' if passed else 'fails'} threshold {operator} {threshold}",
            "score": metric_value if isinstance(metric_value, (int, float)) else None,
            "confidence": 0.9
        }
    
    def _evaluate_boolean_gate(self, gate: str, agent_results: Dict[str, Any], task: CoordinatedTask) -> Dict[str, Any]:
        """Evaluate boolean quality gates"""
        
        if gate == "all_agents_complete_successfully":
            all_successful = all(
                result.get("success", False) 
                for result in agent_results.values()
            )
            return {
                "passed": all_successful,
                "reason": "All agents completed successfully" if all_successful else "Some agents failed",
                "score": None,
                "confidence": 1.0
            }
        
        elif gate == "no_critical_risks_identified":
            # Check for critical risks in results
            critical_risks = []
            for result in agent_results.values():
                if "risk_assessment" in result:
                    risks = result["risk_assessment"]
                    if isinstance(risks, list):
                        critical_risks.extend([r for r in risks if r.get("level") == "CRITICAL"])
            
            no_critical_risks = len(critical_risks) == 0
            return {
                "passed": no_critical_risks,
                "reason": f"Found {len(critical_risks)} critical risks" if critical_risks else "No critical risks identified",
                "score": None,
                "confidence": 0.95
            }
        
        elif gate == "no_blocking_issues":
            # Check for blocking issues
            blocking_issues = []
            for result in agent_results.values():
                if not result.get("success", True):
                    blocking_issues.append(result.get("error", "Unknown error"))
            
            no_blocking = len(blocking_issues) == 0
            return {
                "passed": no_blocking,
                "reason": f"Found {len(blocking_issues)} blocking issues" if blocking_issues else "No blocking issues",
                "score": None,
                "confidence": 1.0
            }
        
        else:
            return {
                "passed": False,
                "reason": f"Unknown boolean gate: {gate}",
                "score": None,
                "confidence": 0.0
            }
    
    def _extract_metric_value(self, metric: str, agent_results: Dict[str, Any]) -> Optional[Union[float, str]]:
        """Extract metric value from nested agent results"""
        
        # Common metric mappings
        metric_mappings = {
            "strategic_alignment_score": ["strategic_analysis", "strategic_score"],
            "overall_validation_score": ["validation_results", "overall_score"],
            "quality_score": ["quality_evaluation", "overall_quality"],
            "accessibility_compliance": ["ux_validation", "accessibility_compliance"],
            "usability_score": ["ux_validation", "usability_score"],
            "confidence_score": ["confidence"],
            "framework_coverage": ["strategic_analysis", "frameworks_analyzed"],
            "performance_improvement": ["cost_analysis", "savings_percentage"],
            "cost_reduction": ["cost_analysis", "savings_percentage"],
            "quality_maintained": ["quality_evaluation", "overall_quality"]
        }
        
        # Try direct lookup first
        for agent_result in agent_results.values():
            if metric in agent_result:
                value = agent_result[metric]
                if isinstance(value, (int, float)):
                    return value
                elif isinstance(value, list):
                    return len(value)  # Return count for lists
                else:
                    return value
        
        # Try mapped lookup
        if metric in metric_mappings:
            path = metric_mappings[metric]
            for agent_result in agent_results.values():
                value = agent_result
                for key in path:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                
                if value is not None:
                    if isinstance(value, list) and metric == "framework_coverage":
                        return len(value)
                    return value
        
        return None
    
    def _extract_recommendations(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from agent results"""
        
        recommendations = []
        
        for agent_result in agent_results.values():
            if "recommendations" in agent_result:
                if isinstance(agent_result["recommendations"], list):
                    recommendations.extend(agent_result["recommendations"])
                else:
                    recommendations.append(str(agent_result["recommendations"]))
            
            # Check nested locations
            for key, value in agent_result.items():
                if isinstance(value, dict) and "recommendations" in value:
                    if isinstance(value["recommendations"], list):
                        recommendations.extend(value["recommendations"])
                    else:
                        recommendations.append(str(value["recommendations"]))
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations[:10]  # Limit to top 10
    
    def _generate_next_actions(self, task: CoordinatedTask, agent_results: Dict[str, Any]) -> List[str]:
        """Generate next actions based on task results"""
        
        next_actions = []
        
        # Based on task status and results
        if task.status == TaskStatus.COMPLETED:
            next_actions.extend([
                "Review and approve implementation plan",
                "Communicate results to stakeholders",
                "Begin implementation of recommendations"
            ])
        elif task.status == TaskStatus.FAILED:
            next_actions.extend([
                "Address identified issues and risks",
                "Gather additional information for failed validations",
                "Consider alternative approaches"
            ])
        
        # Extract action items from agent results
        for agent_result in agent_results.values():
            if "next_steps" in agent_result:
                if isinstance(agent_result["next_steps"], list):
                    next_actions.extend(agent_result["next_steps"])
            
            if "action_items" in agent_result:
                if isinstance(agent_result["action_items"], list):
                    next_actions.extend(agent_result["action_items"])
        
        return next_actions[:8]  # Limit to 8 actions
    
    def _create_coordination_result(self, task: CoordinatedTask, success: bool, error_message: str = "") -> CoordinationResult:
        """Create coordination result for failed tasks"""
        
        return CoordinationResult(
            task_id=task.task_id,
            success=success,
            results={},
            agent_contributions={},
            execution_time=0.0,
            quality_scores={},
            recommendations=[],
            next_actions=["Address task execution issues", "Review task requirements"],
            confidence_score=0.0,
            validation_results={"error": error_message} if error_message else {}
        )
    
    def _start_coordination_engine(self):
        """Start the coordination engine for task processing"""
        
        def process_task_queue():
            """Process tasks from the queue"""
            while True:
                try:
                    if not self.task_queue.empty():
                        priority, task_id = self.task_queue.get(timeout=1)
                        
                        if task_id in self.tasks:
                            task = self.tasks[task_id]
                            
                            # Check if task is ready to execute
                            if task.status == TaskStatus.PENDING and self._check_dependencies(task):
                                # Submit task for coordination
                                future = self.executor.submit(self.coordinate_agents, task_id)
                                self.active_tasks[task_id] = future
                    
                    # Clean up completed tasks
                    completed_tasks = []
                    for task_id, future in self.active_tasks.items():
                        if future.done():
                            completed_tasks.append(task_id)
                    
                    for task_id in completed_tasks:
                        del self.active_tasks[task_id]
                    
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                    
                except queue.Empty:
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Task queue processing error: {e}")
                    time.sleep(5)
        
        # Start task processing thread
        task_thread = threading.Thread(target=process_task_queue, daemon=True)
        task_thread.start()
        
        logger.info("Coordination engine started")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Agent status summary
        agent_summary = {}
        for agent_type in AgentType:
            agents_of_type = [a for a in self.agents.values() if a.agent_type == agent_type]
            if agents_of_type:
                agent_summary[agent_type.value] = {
                    "count": len(agents_of_type),
                    "available": len([a for a in agents_of_type if a.status == AgentStatus.AVAILABLE]),
                    "busy": len([a for a in agents_of_type if a.status == AgentStatus.BUSY]),
                    "avg_load": sum(a.current_load for a in agents_of_type) / len(agents_of_type)
                }
        
        # Task status summary
        task_summary = {}
        for status in TaskStatus:
            count = len([t for t in self.tasks.values() if t.status == status])
            if count > 0:
                task_summary[status.value] = count
        
        # Performance metrics
        recent_results = self.coordination_history[-50:]  # Last 50 results
        if recent_results:
            avg_execution_time = sum(r.execution_time for r in recent_results) / len(recent_results)
            success_rate = sum(1 for r in recent_results if r.success) / len(recent_results)
            avg_confidence = sum(r.confidence_score for r in recent_results) / len(recent_results)
        else:
            avg_execution_time = 0.0
            success_rate = 0.0
            avg_confidence = 0.0
        
        return {
            "system_health": "healthy" if success_rate > 0.8 else "degraded" if success_rate > 0.5 else "critical",
            "agents": agent_summary,
            "tasks": task_summary,
            "active_workflows": len(self.workflows),
            "performance_metrics": {
                "avg_execution_time": avg_execution_time,
                "success_rate": success_rate,
                "avg_confidence": avg_confidence,
                "total_coordinations": len(self.coordination_history)
            },
            "resource_utilization": {
                "task_queue_size": self.task_queue.qsize(),
                "active_tasks": len(self.active_tasks),
                "shared_context_size": len(self.shared_context)
            }
        }
    
    def shutdown(self):
        """Gracefully shutdown the coordinator"""
        
        logger.info("Shutting down Cross-Agent Coordinator")
        
        # Wait for active tasks to complete (with timeout)
        for task_id, future in self.active_tasks.items():
            try:
                future.result(timeout=30)  # 30 second timeout per task
            except Exception as e:
                logger.warning(f"Task {task_id} did not complete cleanly: {e}")
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Cross-Agent Coordinator shutdown complete")

def main():
    """Example usage of PM33 Cross-Agent Coordinator"""
    
    # Initialize coordinator
    coordinator = CrossAgentCoordinator()
    
    # Discover and register agents
    discovered_agents = coordinator.discover_agents()
    print(f"Discovered agents: {discovered_agents}")
    
    # Create a comprehensive product decision task
    task_id = coordinator.create_task(
        task_type=TaskType.COMPREHENSIVE_REVIEW,
        title="Evaluate AI Assistant Feature Addition",
        description="Comprehensive evaluation of adding AI assistant to PM dashboard",
        input_data={
            "decision_context": {
                "feature": "AI Assistant Integration",
                "strategic_importance": 8.5,
                "budget_impact": -150000,
                "timeline": "6 months"
            },
            "market_data": {
                "competitive_landscape": "High AI adoption in PM tools",
                "customer_demand": "Strong interest in AI capabilities"
            }
        },
        priority=TaskPriority.HIGH,
        required_agents=[
            AgentType.STRATEGIC_CONSULTANT,
            AgentType.DECISION_VALIDATOR,
            AgentType.UX_WORKFLOW_VALIDATOR,
            AgentType.LLM_COST_OPTIMIZER
        ]
    )
    
    print(f"Created task: {task_id}")
    
    # Wait a moment for coordination to complete
    time.sleep(10)
    
    # Check system status
    status = coordinator.get_system_status()
    print(f"System Status: {status}")
    
    # Execute a predefined workflow
    workflow_id = coordinator.execute_workflow(
        workflow_template="comprehensive_product_decision",
        input_data={
            "decision_context": {
                "initiative": "Enhanced PM Dashboard",
                "strategic_goals": ["Increase user engagement", "Improve decision quality"]
            }
        }
    )
    
    print(f"Started workflow: {workflow_id}")
    
    # Shutdown
    coordinator.shutdown()

if __name__ == "__main__":
    main()