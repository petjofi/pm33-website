#!/usr/bin/env python3
"""
PM33 Prompt Engineering Suite
Advanced multi-LLM prompt optimization system for strategic intelligence agents

This system provides intelligent prompt optimization across multiple LLM providers,
specialized templates for PM frameworks, and performance-driven prompt evolution.
Integrates with pm33_llm_cost_optimizer.py for comprehensive AI orchestration.

Key Features:
- Provider-specific prompt optimization (Claude, OpenAI, Together AI, Groq)
- PM-specific template library (RICE, ICE, JTBD, OKRs, Porter's Five Forces)
- A/B testing framework for prompt performance
- Dynamic prompt evolution based on success metrics
- Integration with PM33 Strategic Consultant Agent
- Performance tracking and cost-effectiveness analysis
"""

import json
import logging
import hashlib
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import re
from pathlib import Path

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pm33_prompt_engineering.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers with optimization characteristics"""
    ANTHROPIC_CLAUDE = "anthropic_claude"
    OPENAI_GPT = "openai_gpt" 
    TOGETHER_AI = "together_ai"
    GROQ_LLAMA = "groq_llama"

class PromptCategory(Enum):
    """PM33-specific prompt categories for strategic intelligence"""
    STRATEGIC_ANALYSIS = "strategic_analysis"
    FRAMEWORK_APPLICATION = "framework_application"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    PMO_TRANSFORMATION = "pmo_transformation"
    DECISION_VALIDATION = "decision_validation"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    STAKEHOLDER_COMMUNICATION = "stakeholder_communication"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"

class OptimizationStrategy(Enum):
    """Prompt optimization strategies based on provider capabilities"""
    VERBOSE_REASONING = "verbose_reasoning"  # Best for Claude
    STRUCTURED_OUTPUT = "structured_output"  # Best for OpenAI
    COST_EFFICIENT = "cost_efficient"       # Best for Together AI
    SPEED_OPTIMIZED = "speed_optimized"     # Best for Groq

class PerformanceMetric(Enum):
    """Key performance metrics for prompt effectiveness"""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACTIONABILITY = "actionability"
    COST_EFFICIENCY = "cost_efficiency"
    RESPONSE_TIME = "response_time"
    STRATEGIC_VALUE = "strategic_value"

@dataclass
class PromptTemplate:
    """Core prompt template with PM33 optimizations"""
    id: str
    category: PromptCategory
    name: str
    base_template: str
    provider_variants: Dict[LLMProvider, str] = field(default_factory=dict)
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)
    expected_output_format: str = "json"
    performance_requirements: Dict[PerformanceMetric, float] = field(default_factory=dict)
    industry_benchmarks: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_optimized: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    success_rate: float = 0.0

@dataclass
class PromptExecution:
    """Track individual prompt executions for optimization"""
    execution_id: str
    template_id: str
    provider: LLMProvider
    prompt_text: str
    variables: Dict[str, Any]
    response: str
    execution_time: float
    token_cost: float
    performance_scores: Dict[PerformanceMetric, float] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PromptOptimizationResult:
    """Results from prompt optimization analysis"""
    original_template_id: str
    optimized_prompt: str
    provider: LLMProvider
    optimization_strategy: OptimizationStrategy
    expected_improvements: Dict[PerformanceMetric, float]
    confidence_score: float
    reasoning: str
    estimated_cost_impact: float
    recommended_test_duration: int

@dataclass
class ABTestResult:
    """A/B testing results for prompt variants"""
    test_id: str
    variant_a_id: str
    variant_b_id: str
    sample_size: int
    duration_days: int
    performance_comparison: Dict[PerformanceMetric, Dict[str, float]]
    winner: str
    statistical_significance: float
    business_impact: Dict[str, float]
    recommendation: str

class PromptEngineeringSuite:
    """
    Advanced prompt engineering system for PM33 strategic intelligence agents
    
    Provides intelligent prompt optimization, A/B testing, and performance tracking
    across multiple LLM providers with PM-specific strategic focus.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Prompt Engineering Suite"""
        self.config = self._load_config(config_path)
        self.templates: Dict[str, PromptTemplate] = {}
        self.executions: List[PromptExecution] = []
        self.optimization_history: List[PromptOptimizationResult] = []
        self.ab_tests: Dict[str, ABTestResult] = {}
        
        # Performance tracking
        self.performance_cache: Dict[str, Dict[PerformanceMetric, float]] = {}
        self.provider_performance: Dict[LLMProvider, Dict[PerformanceMetric, float]] = {}
        
        # Load built-in PM33 templates
        self._initialize_pm33_templates()
        
        logger.info("PM33 Prompt Engineering Suite initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration for prompt engineering"""
        default_config = {
            "optimization_thresholds": {
                "accuracy": 0.85,
                "relevance": 0.90,
                "completeness": 0.80,
                "actionability": 0.85,
                "cost_efficiency": 0.75,
                "strategic_value": 0.80
            },
            "ab_test_settings": {
                "min_sample_size": 50,
                "significance_threshold": 0.05,
                "test_duration_days": 7
            },
            "provider_preferences": {
                LLMProvider.ANTHROPIC_CLAUDE: {
                    "strength": "deep_reasoning",
                    "optimization_focus": "accuracy_completeness"
                },
                LLMProvider.OPENAI_GPT: {
                    "strength": "structured_output",
                    "optimization_focus": "format_consistency"
                },
                LLMProvider.TOGETHER_AI: {
                    "strength": "cost_efficiency",
                    "optimization_focus": "cost_performance"
                },
                LLMProvider.GROQ_LLAMA: {
                    "strength": "speed",
                    "optimization_focus": "response_time"
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
    
    def _initialize_pm33_templates(self):
        """Initialize built-in PM33 strategic intelligence templates"""
        
        # RICE Framework Analysis Template
        rice_template = PromptTemplate(
            id="pm33_rice_analysis",
            category=PromptCategory.FRAMEWORK_APPLICATION,
            name="RICE Framework Analysis",
            base_template="""
As a strategic PM intelligence agent, conduct a comprehensive RICE analysis for the following initiative:

CONTEXT: {context}
INITIATIVE: {initiative_description}
OBJECTIVES: {objectives}
CONSTRAINTS: {constraints}

Please analyze using the RICE framework:

REACH: Estimate the number of users/stakeholders affected per time period
- Consider primary users, secondary stakeholders, and indirect impacts
- Provide quantitative estimates with confidence intervals

IMPACT: Assess the impact per user on strategic objectives  
- Rate on scale: 3 (massive), 2 (high), 1 (medium), 0.5 (low), 0.25 (minimal)
- Consider both quantitative metrics and qualitative strategic value
- Account for short-term and long-term impacts

CONFIDENCE: Evaluate certainty of reach and impact estimates
- Rate on scale: 100% (certain), 80% (high), 50% (medium), 20% (low)
- Identify key assumptions and risk factors
- Suggest validation approaches for low-confidence areas

EFFORT: Estimate person-months required for implementation
- Include development, testing, deployment, and maintenance
- Consider cross-functional effort (design, engineering, QA, PM)
- Account for technical complexity and resource constraints

FINAL RICE SCORE: Calculate (Reach × Impact × Confidence) / Effort

Provide strategic recommendations based on the analysis, including:
1. Priority ranking justification
2. Key risk factors and mitigation strategies  
3. Resource allocation recommendations
4. Success metrics and validation approach

Format as structured JSON with clear numerical scores and detailed reasoning.
""",
            required_variables=["context", "initiative_description", "objectives", "constraints"],
            expected_output_format="json",
            performance_requirements={
                PerformanceMetric.ACCURACY: 0.90,
                PerformanceMetric.COMPLETENESS: 0.85,
                PerformanceMetric.ACTIONABILITY: 0.90,
                PerformanceMetric.STRATEGIC_VALUE: 0.85
            }
        )
        
        # ICE Framework Template  
        ice_template = PromptTemplate(
            id="pm33_ice_analysis",
            category=PromptCategory.FRAMEWORK_APPLICATION,
            name="ICE Framework Analysis", 
            base_template="""
Conduct strategic ICE framework analysis for rapid prioritization:

INITIATIVES: {initiatives_list}
STRATEGIC_CONTEXT: {strategic_context}
RESOURCE_CONSTRAINTS: {resource_constraints}
TIME_HORIZON: {time_horizon}

For each initiative, analyze:

IMPACT (1-10): Potential positive effect on key metrics
- Consider user value, business metrics, strategic alignment
- Account for direct and indirect impacts
- Include risk-adjusted impact estimates

CONFIDENCE (1-10): Certainty that we can deliver the expected impact
- Based on team capabilities, technical feasibility, market validation
- Consider implementation complexity and external dependencies
- Include confidence intervals and key assumptions

EASE (1-10): How simple/quick to implement relative to other options
- Consider resource requirements, technical complexity, coordination needs
- Account for current team capacity and expertise
- Include time-to-value considerations

ICE SCORE: (Impact + Confidence + Ease) / 3

Provide strategic recommendations:
1. Prioritized initiative ranking with ICE scores
2. Resource allocation strategy
3. Risk mitigation for low-confidence initiatives
4. Quick wins and strategic bets identification
5. Implementation sequencing recommendations

Format as structured JSON with detailed scoring rationale.
""",
            required_variables=["initiatives_list", "strategic_context", "resource_constraints", "time_horizon"],
            expected_output_format="json"
        )
        
        # JTBD Analysis Template
        jtbd_template = PromptTemplate(
            id="pm33_jtbd_analysis", 
            category=PromptCategory.STRATEGIC_ANALYSIS,
            name="Jobs to Be Done Analysis",
            base_template="""
Conduct comprehensive Jobs to Be Done analysis for strategic product intelligence:

USER_SEGMENT: {user_segment}
CONTEXT: {context}
CURRENT_SOLUTIONS: {current_solutions}
PAIN_POINTS: {pain_points}

Analyze the core job:

FUNCTIONAL JOB: What practical task is the user trying to accomplish?
- Primary job statement: "When I [situation], I want to [motivation], so I can [expected outcome]"
- Supporting jobs and job steps
- Success criteria and constraints

EMOTIONAL JOB: How does the user want to feel during and after the job?
- Desired emotional outcomes
- Current emotional pain points
- Social and aspirational dimensions

SOCIAL JOB: How does the user want to be perceived by others?
- Identity and status considerations
- Social validation needs
- Community and belonging aspects

JOB STEPS: Break down the job into discrete steps
1. Beginning (motivation and context)
2. Middle (actual execution and obstacles)
3. End (outcomes and emotional payoff)

COMPETING SOLUTIONS: Analyze all ways users currently address this job
- Direct competitors
- Indirect alternatives
- Non-consumption scenarios
- Workarounds and hacks

OPPORTUNITY GAPS: Identify underserved or overserved aspects
- Unmet needs in current solutions
- Over-engineered aspects users don't value
- Emerging job variations

STRATEGIC IMPLICATIONS:
1. Product positioning recommendations
2. Feature prioritization guidance  
3. Market segmentation insights
4. Innovation opportunities
5. Competitive differentiation strategies

Format as structured JSON with actionable insights.
""",
            required_variables=["user_segment", "context", "current_solutions", "pain_points"],
            expected_output_format="json"
        )
        
        # Competitive Intelligence Template
        competitive_template = PromptTemplate(
            id="pm33_competitive_intelligence",
            category=PromptCategory.COMPETITIVE_INTELLIGENCE,
            name="Strategic Competitive Analysis",
            base_template="""
Conduct strategic competitive intelligence analysis:

COMPETITORS: {competitors}
MARKET_CONTEXT: {market_context}  
OUR_POSITION: {our_position}
ANALYSIS_FOCUS: {analysis_focus}

Perform comprehensive competitive analysis:

COMPETITIVE LANDSCAPE:
- Direct competitors (same solution, same job)
- Indirect competitors (different solution, same job)
- Potential disruptors (emerging solutions)
- Substitute solutions and non-consumption

COMPETITOR DEEP-DIVE for each major competitor:
- Value proposition and positioning
- Product capabilities and limitations
- Pricing strategy and business model
- Target customer segments
- Go-to-market approach
- Recent developments and trajectory

STRATEGIC POSITIONING ANALYSIS:
- Market positioning map
- Feature comparison matrix
- Pricing competitiveness
- Customer satisfaction analysis
- Brand strength and recognition

OPPORTUNITY IDENTIFICATION:
- Underserved market segments
- Feature gaps in competitor offerings
- Pricing inefficiencies
- Distribution channel opportunities
- Partnership potential

THREAT ASSESSMENT:
- Competitive threats to our position
- Potential market disruptors
- Pricing pressure risks
- Feature parity challenges
- Customer churn risks

STRATEGIC RECOMMENDATIONS:
1. Competitive differentiation strategy
2. Feature prioritization based on competitive gaps
3. Pricing strategy recommendations
4. Go-to-market positioning
5. Partnership and ecosystem opportunities
6. Defensive strategies for key threats

Format as structured JSON with actionable strategic insights.
""",
            required_variables=["competitors", "market_context", "our_position", "analysis_focus"],
            expected_output_format="json"
        )
        
        # PMO Transformation Template
        pmo_template = PromptTemplate(
            id="pm33_pmo_transformation",
            category=PromptCategory.PMO_TRANSFORMATION,
            name="PMO Transformation Analysis",
            base_template="""
Analyze PMO transformation requirements and strategy:

CURRENT_STATE: {current_state}
TARGET_PMO_CAPABILITIES: {target_capabilities}
ORGANIZATIONAL_CONTEXT: {organizational_context}
TRANSFORMATION_TIMELINE: {timeline}

Conduct comprehensive PMO transformation analysis:

CAPABILITY ASSESSMENT:
- Current PM/PMO maturity level (1-5 scale)
- Existing processes and tools
- Team skills and competencies
- Organizational readiness for change

PMO FRAMEWORK DESIGN:
- Governance structure and decision rights
- Process standardization requirements
- Tool and technology stack
- Measurement and reporting framework
- Risk and issue management approach

TRANSFORMATION ROADMAP:
Phase 1: Foundation (months 1-3)
- Core process definition
- Tool implementation
- Team training and onboarding
- Quick wins and early value demonstration

Phase 2: Optimization (months 4-6) 
- Process refinement and automation
- Advanced capability development
- Cross-functional integration
- Performance optimization

Phase 3: Scaling (months 7-12)
- Enterprise-wide rollout
- Advanced analytics and insights
- Continuous improvement culture
- Strategic value demonstration

CHANGE MANAGEMENT STRATEGY:
- Stakeholder engagement plan
- Communication and training approach
- Resistance management tactics
- Success measurement and celebration

VALUE REALIZATION PLAN:
- KPIs and success metrics
- ROI calculation methodology
- Value tracking and reporting
- Continuous improvement process

RISK MITIGATION:
- Key transformation risks
- Mitigation strategies
- Contingency planning
- Success factors and dependencies

Provide actionable transformation strategy with timeline, resources, and success metrics.

Format as structured JSON with detailed implementation guidance.
""",
            required_variables=["current_state", "target_capabilities", "organizational_context", "timeline"],
            expected_output_format="json"
        )
        
        # Store templates
        for template in [rice_template, ice_template, jtbd_template, competitive_template, pmo_template]:
            self.templates[template.id] = template
            
        # Generate provider-specific variants
        self._generate_provider_variants()
        
        logger.info(f"Initialized {len(self.templates)} PM33 strategic templates")
    
    def _generate_provider_variants(self):
        """Generate provider-optimized variants of base templates"""
        
        for template in self.templates.values():
            
            # Claude variant - emphasizes deep reasoning and comprehensive analysis
            claude_variant = template.base_template.replace(
                "Provide strategic recommendations",
                """Think through this analysis step-by-step with deep reasoning:

1. First, consider the broader strategic context and implications
2. Analyze each component with systematic rigor  
3. Consider multiple perspectives and potential counterarguments
4. Synthesize insights into actionable recommendations

Provide strategic recommendations"""
            )
            
            # OpenAI variant - emphasizes structured output and consistency
            openai_variant = template.base_template + """

IMPORTANT: Structure your response as valid JSON with these exact keys:
- "analysis": detailed analysis object
- "scores": numerical scores object  
- "recommendations": array of recommendation objects
- "confidence": overall confidence score (0-1)
- "reasoning": step-by-step reasoning array

Ensure all numerical values are properly formatted and all objects follow consistent schemas."""
            
            # Together AI variant - emphasizes efficiency and key insights
            together_variant = template.base_template.replace(
                "comprehensive", "focused"
            ).replace(
                "detailed", "key"
            ) + "\n\nFocus on the most impactful insights and actionable recommendations. Be concise but thorough."
            
            # Groq variant - emphasizes speed and clarity
            groq_variant = template.base_template + """

Provide a clear, fast analysis focusing on:
1. Key insights and critical factors
2. Clear numerical scores with brief justification
3. Top 3 most important recommendations
4. Critical success factors and risks

Keep analysis efficient while maintaining strategic depth."""
            
            template.provider_variants = {
                LLMProvider.ANTHROPIC_CLAUDE: claude_variant,
                LLMProvider.OPENAI_GPT: openai_variant,
                LLMProvider.TOGETHER_AI: together_variant,
                LLMProvider.GROQ_LLAMA: groq_variant
            }
    
    def optimize_prompt(
        self,
        template_id: str,
        provider: LLMProvider,
        performance_history: Optional[List[PromptExecution]] = None,
        target_metrics: Optional[Dict[PerformanceMetric, float]] = None
    ) -> PromptOptimizationResult:
        """
        Optimize a prompt template for specific provider and performance targets
        
        Args:
            template_id: ID of template to optimize
            provider: Target LLM provider
            performance_history: Historical execution data for analysis
            target_metrics: Desired performance targets
            
        Returns:
            PromptOptimizationResult with optimized prompt and analysis
        """
        
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Get historical performance data
        if performance_history is None:
            performance_history = [
                e for e in self.executions 
                if e.template_id == template_id and e.provider == provider
            ]
        
        # Analyze current performance
        current_performance = self._analyze_performance(performance_history)
        
        # Determine optimization strategy based on provider and performance gaps
        optimization_strategy = self._select_optimization_strategy(
            provider, current_performance, target_metrics
        )
        
        # Generate optimized prompt
        optimized_prompt = self._apply_optimization_strategy(
            template, provider, optimization_strategy, current_performance
        )
        
        # Calculate expected improvements
        expected_improvements = self._estimate_improvements(
            optimization_strategy, current_performance, target_metrics
        )
        
        # Generate optimization reasoning
        reasoning = self._generate_optimization_reasoning(
            template, provider, optimization_strategy, current_performance, expected_improvements
        )
        
        result = PromptOptimizationResult(
            original_template_id=template_id,
            optimized_prompt=optimized_prompt,
            provider=provider,
            optimization_strategy=optimization_strategy,
            expected_improvements=expected_improvements,
            confidence_score=self._calculate_optimization_confidence(
                performance_history, optimization_strategy
            ),
            reasoning=reasoning,
            estimated_cost_impact=self._estimate_cost_impact(optimization_strategy),
            recommended_test_duration=self.config["ab_test_settings"]["test_duration_days"]
        )
        
        self.optimization_history.append(result)
        logger.info(f"Generated optimization for {template_id} on {provider.value}")
        
        return result
    
    def _analyze_performance(
        self, 
        executions: List[PromptExecution]
    ) -> Dict[PerformanceMetric, float]:
        """Analyze performance metrics from execution history"""
        
        if not executions:
            return {metric: 0.0 for metric in PerformanceMetric}
        
        performance = {}
        
        for metric in PerformanceMetric:
            scores = [
                e.performance_scores.get(metric, 0.0) 
                for e in executions 
                if metric in e.performance_scores
            ]
            
            if scores:
                performance[metric] = statistics.mean(scores)
            else:
                performance[metric] = 0.0
        
        # Calculate derived metrics
        performance[PerformanceMetric.COST_EFFICIENCY] = self._calculate_cost_efficiency(executions)
        performance[PerformanceMetric.RESPONSE_TIME] = statistics.mean([e.execution_time for e in executions])
        
        return performance
    
    def _select_optimization_strategy(
        self,
        provider: LLMProvider,
        current_performance: Dict[PerformanceMetric, float],
        target_metrics: Optional[Dict[PerformanceMetric, float]]
    ) -> OptimizationStrategy:
        """Select optimal optimization strategy based on provider and performance gaps"""
        
        provider_preferences = self.config["provider_preferences"][provider]
        
        # Identify biggest performance gaps
        thresholds = self.config["optimization_thresholds"]
        gaps = {}
        
        for metric, threshold in thresholds.items():
            metric_enum = PerformanceMetric(metric)
            current = current_performance.get(metric_enum, 0.0)
            gaps[metric_enum] = max(0, threshold - current)
        
        # Select strategy based on provider strengths and performance gaps
        if provider == LLMProvider.ANTHROPIC_CLAUDE:
            if gaps.get(PerformanceMetric.ACCURACY, 0) > 0.1 or gaps.get(PerformanceMetric.COMPLETENESS, 0) > 0.1:
                return OptimizationStrategy.VERBOSE_REASONING
        elif provider == LLMProvider.OPENAI_GPT:
            if gaps.get(PerformanceMetric.RELEVANCE, 0) > 0.1:
                return OptimizationStrategy.STRUCTURED_OUTPUT
        elif provider == LLMProvider.TOGETHER_AI:
            return OptimizationStrategy.COST_EFFICIENT
        elif provider == LLMProvider.GROQ_LLAMA:
            return OptimizationStrategy.SPEED_OPTIMIZED
        
        return OptimizationStrategy.VERBOSE_REASONING  # Default fallback
    
    def _apply_optimization_strategy(
        self,
        template: PromptTemplate,
        provider: LLMProvider,
        strategy: OptimizationStrategy,
        current_performance: Dict[PerformanceMetric, float]
    ) -> str:
        """Apply optimization strategy to generate improved prompt"""
        
        base_prompt = template.provider_variants.get(provider, template.base_template)
        
        if strategy == OptimizationStrategy.VERBOSE_REASONING:
            return self._apply_verbose_reasoning(base_prompt, current_performance)
        elif strategy == OptimizationStrategy.STRUCTURED_OUTPUT:
            return self._apply_structured_output(base_prompt, template.expected_output_format)
        elif strategy == OptimizationStrategy.COST_EFFICIENT:
            return self._apply_cost_efficiency(base_prompt)
        elif strategy == OptimizationStrategy.SPEED_OPTIMIZED:
            return self._apply_speed_optimization(base_prompt)
        
        return base_prompt
    
    def _apply_verbose_reasoning(self, prompt: str, performance: Dict[PerformanceMetric, float]) -> str:
        """Apply verbose reasoning optimization for Claude"""
        
        reasoning_enhancement = """
Before providing your analysis, think through the problem systematically:

1. CONTEXT ANALYSIS: What are the key contextual factors and constraints?
2. FRAMEWORK APPLICATION: How should the strategic framework be applied in this specific situation?
3. MULTIPLE PERSPECTIVES: What different viewpoints should be considered?
4. TRADE-OFFS: What are the key trade-offs and decision factors?
5. VALIDATION: How can we validate our analysis and assumptions?

Then provide your comprehensive analysis:
"""
        
        return reasoning_enhancement + prompt + """

End with a confidence assessment:
- High confidence areas and supporting evidence
- Medium confidence areas and key assumptions
- Low confidence areas requiring further validation
- Recommended next steps for uncertainty resolution"""
    
    def _apply_structured_output(self, prompt: str, output_format: str) -> str:
        """Apply structured output optimization for OpenAI"""
        
        if output_format == "json":
            structure_guide = """
CRITICAL: Your response must be valid JSON with exactly this structure:

{
  "analysis": {
    "summary": "Brief executive summary",
    "key_insights": ["insight1", "insight2", "insight3"],
    "framework_scores": {
      "metric1": value,
      "metric2": value
    }
  },
  "recommendations": [
    {
      "priority": "high|medium|low",
      "title": "Recommendation title",
      "description": "Detailed description",
      "impact": "Expected business impact",
      "effort": "Implementation effort",
      "timeline": "Recommended timeline"
    }
  ],
  "risks": [
    {
      "risk": "Risk description",
      "probability": "high|medium|low", 
      "impact": "high|medium|low",
      "mitigation": "Mitigation strategy"
    }
  ],
  "confidence": 0.85,
  "next_steps": ["step1", "step2", "step3"]
}

Ensure all numerical values are numbers (not strings) and follow JSON formatting exactly.
"""
        else:
            structure_guide = f"""
Format your response as structured {output_format} with clear sections:
- Executive Summary
- Detailed Analysis  
- Recommendations (prioritized)
- Risk Assessment
- Next Steps
- Confidence Level
"""
        
        return prompt + "\n\n" + structure_guide
    
    def _apply_cost_efficiency(self, prompt: str) -> str:
        """Apply cost efficiency optimization for Together AI"""
        
        efficiency_guide = """
Optimize for efficiency while maintaining quality:

1. Focus on the most impactful insights and recommendations
2. Prioritize actionable conclusions over comprehensive background
3. Use clear, direct language without unnecessary elaboration
4. Highlight the top 3 most critical points in each section
5. Provide specific, quantified recommendations where possible

Be thorough in analysis but concise in presentation.
"""
        
        # Simplify the prompt while maintaining core requirements
        simplified_prompt = prompt.replace("comprehensive", "focused").replace("detailed", "key")
        
        return efficiency_guide + simplified_prompt + """

Structure your response for maximum value:
- Lead with key insights and critical factors
- Provide specific, quantified recommendations  
- Include only the most important risks and mitigation strategies
- End with clear next steps and success metrics"""
    
    def _apply_speed_optimization(self, prompt: str) -> str:
        """Apply speed optimization for Groq"""
        
        speed_guide = """
Provide rapid strategic analysis focusing on:

CRITICAL INSIGHTS: Top 3 most important findings
KEY METRICS: Essential numbers and scores with brief justification  
TOP RECOMMENDATIONS: 3 highest-impact actions with clear priorities
SUCCESS FACTORS: Critical elements for implementation success

Be direct and actionable while maintaining strategic depth.
"""
        
        # Streamline prompt for faster processing
        streamlined_prompt = prompt.replace("conduct comprehensive", "provide focused").replace("detailed analysis", "key analysis")
        
        return speed_guide + streamlined_prompt + """

Format for speed and clarity:
1. Executive summary (2-3 sentences)
2. Core insights with quantified impact
3. Prioritized recommendations with timelines
4. Critical success factors and key risks"""
    
    def create_ab_test(
        self,
        variant_a_id: str,
        variant_b_id: str, 
        test_duration_days: Optional[int] = None,
        target_metrics: Optional[List[PerformanceMetric]] = None
    ) -> str:
        """
        Create A/B test for comparing prompt variants
        
        Args:
            variant_a_id: Template ID for variant A
            variant_b_id: Template ID for variant B  
            test_duration_days: Duration of test in days
            target_metrics: Metrics to focus on for comparison
            
        Returns:
            Test ID for tracking
        """
        
        test_id = f"ab_test_{hashlib.md5(f'{variant_a_id}_{variant_b_id}_{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        if test_duration_days is None:
            test_duration_days = self.config["ab_test_settings"]["test_duration_days"]
        
        if target_metrics is None:
            target_metrics = [
                PerformanceMetric.ACCURACY,
                PerformanceMetric.RELEVANCE, 
                PerformanceMetric.ACTIONABILITY,
                PerformanceMetric.COST_EFFICIENCY
            ]
        
        # Initialize test tracking
        test_data = {
            "test_id": test_id,
            "variant_a_id": variant_a_id,
            "variant_b_id": variant_b_id,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=test_duration_days),
            "target_metrics": target_metrics,
            "variant_a_executions": [],
            "variant_b_executions": [],
            "status": "active"
        }
        
        # Store test data (in production, this would be in a database)
        self.ab_tests[test_id] = test_data
        
        logger.info(f"Created A/B test {test_id} comparing {variant_a_id} vs {variant_b_id}")
        
        return test_id
    
    def analyze_ab_test(self, test_id: str) -> ABTestResult:
        """
        Analyze A/B test results and determine winner
        
        Args:
            test_id: ID of test to analyze
            
        Returns:
            ABTestResult with statistical analysis and recommendations
        """
        
        if test_id not in self.ab_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test_data = self.ab_tests[test_id]
        
        # Get executions for both variants
        variant_a_executions = [
            e for e in self.executions 
            if e.template_id == test_data["variant_a_id"]
            and e.timestamp >= test_data["start_date"]
            and e.timestamp <= test_data["end_date"]
        ]
        
        variant_b_executions = [
            e for e in self.executions
            if e.template_id == test_data["variant_b_id"] 
            and e.timestamp >= test_data["start_date"]
            and e.timestamp <= test_data["end_date"]
        ]
        
        # Analyze performance for both variants
        variant_a_performance = self._analyze_performance(variant_a_executions)
        variant_b_performance = self._analyze_performance(variant_b_executions)
        
        # Calculate performance comparison
        performance_comparison = {}
        for metric in test_data["target_metrics"]:
            performance_comparison[metric] = {
                "variant_a": variant_a_performance.get(metric, 0.0),
                "variant_b": variant_b_performance.get(metric, 0.0),
                "difference": variant_b_performance.get(metric, 0.0) - variant_a_performance.get(metric, 0.0),
                "improvement_pct": (
                    (variant_b_performance.get(metric, 0.0) - variant_a_performance.get(metric, 0.0)) /
                    max(variant_a_performance.get(metric, 0.0), 0.01) * 100
                )
            }
        
        # Determine winner based on overall performance
        variant_a_score = sum(variant_a_performance.get(m, 0.0) for m in test_data["target_metrics"])
        variant_b_score = sum(variant_b_performance.get(m, 0.0) for m in test_data["target_metrics"])
        
        winner = test_data["variant_b_id"] if variant_b_score > variant_a_score else test_data["variant_a_id"]
        
        # Calculate statistical significance (simplified)
        sample_size = len(variant_a_executions) + len(variant_b_executions)
        min_sample = self.config["ab_test_settings"]["min_sample_size"]
        statistical_significance = min(1.0, sample_size / min_sample) if sample_size > 0 else 0.0
        
        # Calculate business impact
        business_impact = self._calculate_business_impact(performance_comparison, sample_size)
        
        # Generate recommendation
        recommendation = self._generate_ab_test_recommendation(
            winner, performance_comparison, statistical_significance, business_impact
        )
        
        result = ABTestResult(
            test_id=test_id,
            variant_a_id=test_data["variant_a_id"],
            variant_b_id=test_data["variant_b_id"],
            sample_size=sample_size,
            duration_days=test_data.get("duration_days", 7),
            performance_comparison=performance_comparison,
            winner=winner,
            statistical_significance=statistical_significance,
            business_impact=business_impact,
            recommendation=recommendation
        )
        
        logger.info(f"Analyzed A/B test {test_id}: Winner is {winner}")
        
        return result
    
    def get_optimal_template(
        self,
        category: PromptCategory,
        provider: LLMProvider,
        performance_requirements: Optional[Dict[PerformanceMetric, float]] = None
    ) -> Tuple[str, float]:
        """
        Get optimal template for given category, provider and requirements
        
        Args:
            category: Prompt category needed
            provider: Target LLM provider
            performance_requirements: Minimum performance requirements
            
        Returns:
            Tuple of (template_id, confidence_score)
        """
        
        candidates = [
            (template_id, template) 
            for template_id, template in self.templates.items()
            if template.category == category
        ]
        
        if not candidates:
            raise ValueError(f"No templates found for category {category}")
        
        # Score candidates based on historical performance and requirements
        scored_candidates = []
        
        for template_id, template in candidates:
            # Get historical performance for this template + provider
            template_executions = [
                e for e in self.executions
                if e.template_id == template_id and e.provider == provider
            ]
            
            if template_executions:
                performance = self._analyze_performance(template_executions)
                confidence = statistics.mean([e.performance_scores.get(PerformanceMetric.ACCURACY, 0.0) for e in template_executions[-10:]])
            else:
                # Use template's expected performance for new templates
                performance = template.performance_requirements
                confidence = 0.7  # Default confidence for untested templates
            
            # Check if meets requirements
            meets_requirements = True
            if performance_requirements:
                for metric, min_value in performance_requirements.items():
                    if performance.get(metric, 0.0) < min_value:
                        meets_requirements = False
                        break
            
            if meets_requirements:
                # Calculate overall score
                score = (
                    performance.get(PerformanceMetric.ACCURACY, 0.0) * 0.3 +
                    performance.get(PerformanceMetric.RELEVANCE, 0.0) * 0.2 + 
                    performance.get(PerformanceMetric.ACTIONABILITY, 0.0) * 0.2 +
                    performance.get(PerformanceMetric.STRATEGIC_VALUE, 0.0) * 0.2 +
                    confidence * 0.1
                )
                
                scored_candidates.append((template_id, score, confidence))
        
        if not scored_candidates:
            # Fallback to first available template
            template_id = candidates[0][0]
            return template_id, 0.5
        
        # Return highest scoring template
        best_candidate = max(scored_candidates, key=lambda x: x[1])
        return best_candidate[0], best_candidate[2]
    
    def track_execution(
        self,
        template_id: str,
        provider: LLMProvider,
        prompt_text: str,
        variables: Dict[str, Any],
        response: str,
        execution_time: float,
        token_cost: float,
        performance_scores: Optional[Dict[PerformanceMetric, float]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> str:
        """
        Track prompt execution for optimization and analysis
        
        Args:
            template_id: ID of template used
            provider: LLM provider used
            prompt_text: Final prompt sent to LLM
            variables: Variables used in template
            response: LLM response
            execution_time: Response time in seconds
            token_cost: Cost in tokens or dollars
            performance_scores: Quality scores for different metrics
            success: Whether execution was successful
            error_message: Error message if failed
            
        Returns:
            Execution ID for reference
        """
        
        execution_id = f"exec_{hashlib.md5(f'{template_id}_{provider.value}_{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        execution = PromptExecution(
            execution_id=execution_id,
            template_id=template_id,
            provider=provider,
            prompt_text=prompt_text,
            variables=variables,
            response=response,
            execution_time=execution_time,
            token_cost=token_cost,
            performance_scores=performance_scores or {},
            success=success,
            error_message=error_message
        )
        
        self.executions.append(execution)
        
        # Update template usage statistics
        if template_id in self.templates:
            template = self.templates[template_id]
            template.usage_count += 1
            if success:
                # Update success rate (simple moving average)
                template.success_rate = (template.success_rate * (template.usage_count - 1) + 1.0) / template.usage_count
            else:
                template.success_rate = (template.success_rate * (template.usage_count - 1) + 0.0) / template.usage_count
        
        logger.debug(f"Tracked execution {execution_id} for template {template_id}")
        
        return execution_id
    
    def _calculate_cost_efficiency(self, executions: List[PromptExecution]) -> float:
        """Calculate cost efficiency metric from executions"""
        if not executions:
            return 0.0
        
        # Cost efficiency = (average success rate) / (average cost per execution)
        success_rate = sum(1 for e in executions if e.success) / len(executions)
        avg_cost = statistics.mean([e.token_cost for e in executions if e.token_cost > 0])
        
        if avg_cost > 0:
            return success_rate / avg_cost
        else:
            return success_rate
    
    def _estimate_improvements(
        self,
        strategy: OptimizationStrategy, 
        current_performance: Dict[PerformanceMetric, float],
        target_metrics: Optional[Dict[PerformanceMetric, float]]
    ) -> Dict[PerformanceMetric, float]:
        """Estimate performance improvements from optimization strategy"""
        
        improvements = {}
        
        # Strategy-specific improvement estimates
        if strategy == OptimizationStrategy.VERBOSE_REASONING:
            improvements[PerformanceMetric.ACCURACY] = 0.15
            improvements[PerformanceMetric.COMPLETENESS] = 0.20
            improvements[PerformanceMetric.STRATEGIC_VALUE] = 0.10
        elif strategy == OptimizationStrategy.STRUCTURED_OUTPUT:
            improvements[PerformanceMetric.RELEVANCE] = 0.18
            improvements[PerformanceMetric.ACTIONABILITY] = 0.15
        elif strategy == OptimizationStrategy.COST_EFFICIENT:
            improvements[PerformanceMetric.COST_EFFICIENCY] = 0.30
            improvements[PerformanceMetric.RESPONSE_TIME] = 0.10
        elif strategy == OptimizationStrategy.SPEED_OPTIMIZED:
            improvements[PerformanceMetric.RESPONSE_TIME] = 0.40
            improvements[PerformanceMetric.COST_EFFICIENCY] = 0.20
        
        # Apply diminishing returns based on current performance
        adjusted_improvements = {}
        for metric, improvement in improvements.items():
            current = current_performance.get(metric, 0.0)
            # Diminishing returns: harder to improve when already high
            diminishing_factor = max(0.1, 1.0 - current)
            adjusted_improvements[metric] = improvement * diminishing_factor
        
        return adjusted_improvements
    
    def _calculate_optimization_confidence(
        self,
        performance_history: List[PromptExecution],
        strategy: OptimizationStrategy
    ) -> float:
        """Calculate confidence in optimization based on historical data and strategy"""
        
        base_confidence = 0.7  # Default confidence
        
        # Increase confidence based on data quality
        if len(performance_history) > 50:
            base_confidence += 0.2
        elif len(performance_history) > 20:
            base_confidence += 0.1
        
        # Strategy-specific confidence adjustments
        strategy_confidence = {
            OptimizationStrategy.VERBOSE_REASONING: 0.85,
            OptimizationStrategy.STRUCTURED_OUTPUT: 0.80,
            OptimizationStrategy.COST_EFFICIENT: 0.75,
            OptimizationStrategy.SPEED_OPTIMIZED: 0.70
        }
        
        return min(1.0, base_confidence * strategy_confidence.get(strategy, 0.7))
    
    def _estimate_cost_impact(self, strategy: OptimizationStrategy) -> float:
        """Estimate cost impact of optimization strategy"""
        
        cost_impacts = {
            OptimizationStrategy.VERBOSE_REASONING: 0.25,  # Increase due to longer prompts
            OptimizationStrategy.STRUCTURED_OUTPUT: 0.10,  # Slight increase for structure
            OptimizationStrategy.COST_EFFICIENT: -0.30,    # Decrease through efficiency
            OptimizationStrategy.SPEED_OPTIMIZED: -0.15    # Decrease through speed
        }
        
        return cost_impacts.get(strategy, 0.0)
    
    def _generate_optimization_reasoning(
        self,
        template: PromptTemplate,
        provider: LLMProvider,
        strategy: OptimizationStrategy,
        current_performance: Dict[PerformanceMetric, float],
        expected_improvements: Dict[PerformanceMetric, float]
    ) -> str:
        """Generate detailed reasoning for optimization recommendations"""
        
        reasoning_parts = []
        
        # Context
        reasoning_parts.append(f"Optimizing {template.name} for {provider.value} using {strategy.value} strategy.")
        
        # Current performance analysis
        performance_summary = []
        thresholds = self.config["optimization_thresholds"]
        
        for metric, score in current_performance.items():
            threshold = thresholds.get(metric.value, 0.8)
            if score < threshold:
                gap = threshold - score
                performance_summary.append(f"{metric.value}: {score:.2f} (gap: {gap:.2f})")
        
        if performance_summary:
            reasoning_parts.append(f"Performance gaps identified: {'; '.join(performance_summary)}")
        
        # Strategy justification
        strategy_justification = {
            OptimizationStrategy.VERBOSE_REASONING: "Adding systematic reasoning steps to improve analysis depth and accuracy",
            OptimizationStrategy.STRUCTURED_OUTPUT: "Implementing strict output formatting to improve consistency and actionability", 
            OptimizationStrategy.COST_EFFICIENT: "Streamlining prompt for cost efficiency while maintaining quality",
            OptimizationStrategy.SPEED_OPTIMIZED: "Optimizing for rapid response while preserving strategic value"
        }
        
        reasoning_parts.append(strategy_justification.get(strategy, "Applying general optimization techniques"))
        
        # Expected improvements
        improvement_summary = [f"{metric.value}: +{improvement:.1%}" for metric, improvement in expected_improvements.items()]
        reasoning_parts.append(f"Expected improvements: {'; '.join(improvement_summary)}")
        
        return " ".join(reasoning_parts)
    
    def _calculate_business_impact(
        self,
        performance_comparison: Dict[PerformanceMetric, Dict[str, float]],
        sample_size: int
    ) -> Dict[str, float]:
        """Calculate business impact of A/B test results"""
        
        # Simplified business impact calculation
        impact = {}
        
        # Calculate overall performance improvement
        total_improvement = sum(
            comparison["improvement_pct"] 
            for comparison in performance_comparison.values()
        ) / len(performance_comparison)
        
        impact["performance_improvement_pct"] = total_improvement
        
        # Estimate cost impact
        cost_comparison = performance_comparison.get(PerformanceMetric.COST_EFFICIENCY, {})
        impact["cost_impact_pct"] = cost_comparison.get("improvement_pct", 0.0)
        
        # Estimate quality impact  
        quality_metrics = [PerformanceMetric.ACCURACY, PerformanceMetric.RELEVANCE, PerformanceMetric.ACTIONABILITY]
        quality_improvements = [
            performance_comparison.get(metric, {}).get("improvement_pct", 0.0)
            for metric in quality_metrics
            if metric in performance_comparison
        ]
        
        if quality_improvements:
            impact["quality_improvement_pct"] = statistics.mean(quality_improvements)
        else:
            impact["quality_improvement_pct"] = 0.0
        
        # Statistical confidence based on sample size
        min_sample = self.config["ab_test_settings"]["min_sample_size"]
        impact["statistical_confidence"] = min(1.0, sample_size / min_sample)
        
        return impact
    
    def _generate_ab_test_recommendation(
        self,
        winner: str,
        performance_comparison: Dict[PerformanceMetric, Dict[str, float]],
        statistical_significance: float,
        business_impact: Dict[str, float]
    ) -> str:
        """Generate A/B test recommendation based on results"""
        
        recommendation_parts = []
        
        # Winner declaration
        recommendation_parts.append(f"Recommended winner: {winner}")
        
        # Statistical confidence
        if statistical_significance >= 0.95:
            recommendation_parts.append("High statistical confidence in results.")
        elif statistical_significance >= 0.80:
            recommendation_parts.append("Moderate statistical confidence - consider extended testing.")
        else:
            recommendation_parts.append("Low statistical confidence - extend test duration or increase sample size.")
        
        # Performance highlights
        significant_improvements = []
        for metric, comparison in performance_comparison.items():
            if abs(comparison["improvement_pct"]) > 5.0:  # 5% threshold
                direction = "improved" if comparison["improvement_pct"] > 0 else "declined"
                significant_improvements.append(f"{metric.value} {direction} by {abs(comparison['improvement_pct']):.1f}%")
        
        if significant_improvements:
            recommendation_parts.append(f"Key changes: {'; '.join(significant_improvements)}")
        
        # Business impact summary
        overall_improvement = business_impact.get("performance_improvement_pct", 0.0)
        if overall_improvement > 10.0:
            recommendation_parts.append(f"Strong business case with {overall_improvement:.1f}% overall improvement.")
        elif overall_improvement > 5.0:
            recommendation_parts.append(f"Positive business impact with {overall_improvement:.1f}% improvement.")
        else:
            recommendation_parts.append("Limited business impact - consider alternative optimizations.")
        
        return " ".join(recommendation_parts)
    
    def get_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_executions = [e for e in self.executions if e.timestamp >= cutoff_date]
        
        report = {
            "period_days": days,
            "total_executions": len(recent_executions),
            "success_rate": sum(1 for e in recent_executions if e.success) / len(recent_executions) if recent_executions else 0,
            "average_response_time": statistics.mean([e.execution_time for e in recent_executions]) if recent_executions else 0,
            "total_cost": sum(e.token_cost for e in recent_executions),
            "provider_breakdown": {},
            "template_performance": {},
            "optimization_opportunities": []
        }
        
        # Provider breakdown
        for provider in LLMProvider:
            provider_executions = [e for e in recent_executions if e.provider == provider]
            if provider_executions:
                report["provider_breakdown"][provider.value] = {
                    "executions": len(provider_executions),
                    "success_rate": sum(1 for e in provider_executions if e.success) / len(provider_executions),
                    "avg_response_time": statistics.mean([e.execution_time for e in provider_executions]),
                    "total_cost": sum(e.token_cost for e in provider_executions),
                    "avg_performance": self._analyze_performance(provider_executions)
                }
        
        # Template performance
        for template_id, template in self.templates.items():
            template_executions = [e for e in recent_executions if e.template_id == template_id]
            if template_executions:
                performance = self._analyze_performance(template_executions)
                report["template_performance"][template_id] = {
                    "name": template.name,
                    "executions": len(template_executions),
                    "success_rate": sum(1 for e in template_executions if e.success) / len(template_executions),
                    "performance": performance,
                    "needs_optimization": any(score < 0.8 for score in performance.values())
                }
        
        # Optimization opportunities
        thresholds = self.config["optimization_thresholds"]
        for template_id, perf_data in report["template_performance"].items():
            performance = perf_data["performance"]
            opportunities = []
            
            for metric_str, threshold in thresholds.items():
                try:
                    metric = PerformanceMetric(metric_str)
                    if performance.get(metric, 0.0) < threshold:
                        gap = threshold - performance.get(metric, 0.0)
                        opportunities.append({
                            "template": template_id,
                            "metric": metric_str,
                            "current": performance.get(metric, 0.0),
                            "target": threshold,
                            "gap": gap
                        })
                except ValueError:
                    continue  # Skip invalid metric strings
            
            if opportunities:
                report["optimization_opportunities"].extend(opportunities)
        
        return report

    def export_templates(self, file_path: str):
        """Export templates to JSON file"""
        export_data = {}
        for template_id, template in self.templates.items():
            export_data[template_id] = {
                "id": template.id,
                "category": template.category.value,
                "name": template.name,
                "base_template": template.base_template,
                "provider_variants": {
                    provider.value: variant 
                    for provider, variant in template.provider_variants.items()
                },
                "required_variables": template.required_variables,
                "optional_variables": template.optional_variables,
                "expected_output_format": template.expected_output_format,
                "performance_requirements": {
                    metric.value: value 
                    for metric, value in template.performance_requirements.items()
                }
            }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(self.templates)} templates to {file_path}")

def main():
    """Example usage of PM33 Prompt Engineering Suite"""
    
    suite = PromptEngineeringSuite()
    
    # Example: Optimize RICE analysis template for Claude
    optimization_result = suite.optimize_prompt(
        template_id="pm33_rice_analysis",
        provider=LLMProvider.ANTHROPIC_CLAUDE,
        target_metrics={
            PerformanceMetric.ACCURACY: 0.90,
            PerformanceMetric.STRATEGIC_VALUE: 0.85
        }
    )
    
    print(f"Optimization Result:")
    print(f"Strategy: {optimization_result.optimization_strategy.value}")
    print(f"Confidence: {optimization_result.confidence_score:.2f}")
    print(f"Expected Improvements: {optimization_result.expected_improvements}")
    
    # Example: Get optimal template for competitive analysis
    template_id, confidence = suite.get_optimal_template(
        category=PromptCategory.COMPETITIVE_INTELLIGENCE,
        provider=LLMProvider.OPENAI_GPT,
        performance_requirements={
            PerformanceMetric.RELEVANCE: 0.85,
            PerformanceMetric.ACTIONABILITY: 0.80
        }
    )
    
    print(f"\nOptimal template for competitive intelligence: {template_id} (confidence: {confidence:.2f})")
    
    # Example: Performance report
    report = suite.get_performance_report(days=30)
    print(f"\nPerformance Report:")
    print(f"Total executions: {report['total_executions']}")
    print(f"Success rate: {report['success_rate']:.2%}")
    print(f"Optimization opportunities: {len(report['optimization_opportunities'])}")

if __name__ == "__main__":
    main()