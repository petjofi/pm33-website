#!/usr/bin/env python3
"""
PM33 LLM Cost Optimizer
Intelligent routing and cost optimization for multi-LLM usage across PM33 platform
Usage: python pm33_llm_cost_optimizer.py [--analyze-usage] [--optimize-request] [--budget-report]
"""

import os
import re
import json
import time
import hashlib
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import argparse
from pathlib import Path

class LLMProvider(Enum):
    """Available LLM providers with cost optimization focus"""
    CLAUDE = "claude"           # Best for strategic reasoning, highest cost
    OPENAI = "openai"          # Best for structured outputs, medium cost  
    TOGETHER_AI = "together"   # Best for bulk processing, lowest cost
    GROQ = "groq"             # Best for speed, very low cost

class TaskComplexity(Enum):
    """Task complexity levels for optimal LLM selection"""
    SIMPLE = "simple"       # Basic queries, classifications
    MEDIUM = "medium"       # Analysis, summaries, calculations
    COMPLEX = "complex"     # Strategic reasoning, creative tasks
    CRITICAL = "critical"   # High-stakes decisions, detailed analysis

class CostOptimizationStrategy(Enum):
    """Cost optimization strategies"""
    MINIMIZE_COST = "minimize_cost"           # Always use cheapest option
    OPTIMIZE_QUALITY_COST = "optimize_qc"    # Balance quality and cost
    MAXIMIZE_QUALITY = "maximize_quality"    # Best quality regardless of cost
    MAXIMIZE_SPEED = "maximize_speed"        # Fastest response time

@dataclass
class LLMProviderProfile:
    """Comprehensive LLM provider profile with cost characteristics"""
    provider: LLMProvider
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    avg_response_time_ms: float
    quality_score: float  # 0-10 scale
    reliability_score: float  # 0-10 scale
    max_tokens_per_request: int
    supports_streaming: bool
    supports_function_calling: bool
    context_window: int
    best_use_cases: List[str]
    limitations: List[str]

@dataclass
class UsageRecord:
    """Individual LLM usage record for tracking"""
    request_id: str
    timestamp: str
    provider: LLMProvider
    task_type: str
    task_complexity: TaskComplexity
    input_tokens: int
    output_tokens: int
    total_cost: float
    response_time_ms: float
    quality_rating: Optional[float] = None  # User/system provided rating
    cost_efficiency_score: Optional[float] = None  # Calculated efficiency
    optimization_applied: Optional[str] = None  # Which optimization was used

@dataclass
class CostBudget:
    """Cost budget tracking and management"""
    daily_limit: float
    weekly_limit: float
    monthly_limit: float
    current_day_spend: float = 0.0
    current_week_spend: float = 0.0
    current_month_spend: float = 0.0
    alert_threshold: float = 0.8  # Alert at 80% of budget

@dataclass
class OptimizationRecommendation:
    """LLM optimization recommendation"""
    current_provider: LLMProvider
    recommended_provider: LLMProvider
    estimated_cost_savings: float
    estimated_quality_impact: float
    confidence: float  # 0-1
    reasoning: str
    alternative_options: List[Tuple[LLMProvider, float, str]] = field(default_factory=list)

@dataclass
class BatchOptimizationResult:
    """Result of batch optimization analysis"""
    total_requests: int
    original_cost: float
    optimized_cost: float
    cost_savings: float
    cost_savings_percent: float
    quality_impact: float
    optimization_details: List[OptimizationRecommendation]

class PM33LLMCostOptimizer:
    """
    PM33 LLM Cost Optimizer
    Intelligent routing and cost optimization for multi-LLM usage
    """
    
    # LLM Provider Profiles (Updated with real-world data)
    PROVIDER_PROFILES = {
        LLMProvider.CLAUDE: LLMProviderProfile(
            provider=LLMProvider.CLAUDE,
            cost_per_1k_input_tokens=0.015,
            cost_per_1k_output_tokens=0.075,
            avg_response_time_ms=3200,
            quality_score=9.5,
            reliability_score=9.8,
            max_tokens_per_request=200000,
            supports_streaming=True,
            supports_function_calling=True,
            context_window=200000,
            best_use_cases=["strategic_reasoning", "complex_analysis", "creative_solutions", "pm_frameworks"],
            limitations=["higher_cost", "slower_responses", "rate_limits"]
        ),
        LLMProvider.OPENAI: LLMProviderProfile(
            provider=LLMProvider.OPENAI,
            cost_per_1k_input_tokens=0.010,
            cost_per_1k_output_tokens=0.030,
            avg_response_time_ms=2100,
            quality_score=9.0,
            reliability_score=9.5,
            max_tokens_per_request=128000,
            supports_streaming=True,
            supports_function_calling=True,
            context_window=128000,
            best_use_cases=["structured_outputs", "technical_analysis", "code_generation", "json_parsing"],
            limitations=["moderate_cost", "context_limitations", "consistency_issues"]
        ),
        LLMProvider.TOGETHER_AI: LLMProviderProfile(
            provider=LLMProvider.TOGETHER_AI,
            cost_per_1k_input_tokens=0.0008,
            cost_per_1k_output_tokens=0.0008,
            avg_response_time_ms=1800,
            quality_score=7.5,
            reliability_score=8.0,
            max_tokens_per_request=32000,
            supports_streaming=True,
            supports_function_calling=False,
            context_window=32000,
            best_use_cases=["bulk_processing", "data_analysis", "classification", "simple_summaries"],
            limitations=["lower_quality", "limited_reasoning", "smaller_context"]
        ),
        LLMProvider.GROQ: LLMProviderProfile(
            provider=LLMProvider.GROQ,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0005,
            avg_response_time_ms=800,
            quality_score=7.0,
            reliability_score=8.5,
            max_tokens_per_request=8000,
            supports_streaming=True,
            supports_function_calling=False,
            context_window=8000,
            best_use_cases=["speed_critical", "simple_analysis", "quick_responses", "real_time"],
            limitations=["basic_reasoning", "very_limited_context", "quality_inconsistency"]
        )
    }
    
    # Task type to complexity mapping
    TASK_COMPLEXITY_MAP = {
        # Simple tasks
        "classification": TaskComplexity.SIMPLE,
        "keyword_extraction": TaskComplexity.SIMPLE,
        "simple_summary": TaskComplexity.SIMPLE,
        "data_formatting": TaskComplexity.SIMPLE,
        "basic_qa": TaskComplexity.SIMPLE,
        
        # Medium tasks  
        "analysis": TaskComplexity.MEDIUM,
        "framework_calculation": TaskComplexity.MEDIUM,
        "content_generation": TaskComplexity.MEDIUM,
        "translation": TaskComplexity.MEDIUM,
        "detailed_summary": TaskComplexity.MEDIUM,
        
        # Complex tasks
        "strategic_analysis": TaskComplexity.COMPLEX,
        "competitive_intelligence": TaskComplexity.COMPLEX,
        "creative_writing": TaskComplexity.COMPLEX,
        "complex_reasoning": TaskComplexity.COMPLEX,
        "pmo_transformation": TaskComplexity.COMPLEX,
        
        # Critical tasks
        "strategic_decision": TaskComplexity.CRITICAL,
        "risk_assessment": TaskComplexity.CRITICAL,
        "high_stakes_analysis": TaskComplexity.CRITICAL,
        "executive_summary": TaskComplexity.CRITICAL
    }
    
    # Quality requirements by PM33 use case
    PM33_QUALITY_REQUIREMENTS = {
        "strategic_analysis": {"min_quality": 9.0, "min_confidence": 0.85},
        "framework_application": {"min_quality": 8.5, "min_confidence": 0.80},
        "competitive_intelligence": {"min_quality": 8.0, "min_confidence": 0.75},
        "pmo_metrics": {"min_quality": 7.5, "min_confidence": 0.70},
        "resource_optimization": {"min_quality": 8.0, "min_confidence": 0.75},
        "user_interaction": {"min_quality": 7.0, "min_confidence": 0.65},
        "data_processing": {"min_quality": 6.5, "min_confidence": 0.60}
    }
    
    def __init__(self, budget_config: Dict[str, float] = None):
        """Initialize the LLM Cost Optimizer"""
        self.usage_history: List[UsageRecord] = []
        self.optimization_cache: Dict[str, Tuple[LLMProvider, float]] = {}
        
        # Set up budget management
        if budget_config:
            self.budget = CostBudget(**budget_config)
        else:
            self.budget = CostBudget(
                daily_limit=50.0,
                weekly_limit=300.0,
                monthly_limit=1000.0
            )
        
        # Load historical data
        self.load_usage_history()
        
        print("💰 PM33 LLM Cost Optimizer initialized")
        print(f"🎯 Providers configured: {len(self.PROVIDER_PROFILES)}")
        print(f"📊 Budget limits: ${self.budget.daily_limit}/day, ${self.budget.monthly_limit}/month")
        print(f"📈 Historical records: {len(self.usage_history)}")
        
    def optimize_request(self, 
                        task_type: str,
                        content: str,
                        quality_requirements: Dict[str, Any] = None,
                        strategy: CostOptimizationStrategy = CostOptimizationStrategy.OPTIMIZE_QUALITY_COST,
                        max_cost: float = None) -> OptimizationRecommendation:
        """
        Optimize LLM selection for a specific request
        """
        print(f"🔍 Optimizing LLM selection for task: {task_type}")
        
        # Analyze request characteristics
        request_analysis = self._analyze_request(task_type, content, quality_requirements)
        
        # Generate cache key for similar requests
        cache_key = self._generate_cache_key(task_type, request_analysis)
        
        # Check cache first
        if cache_key in self.optimization_cache:
            cached_provider, cached_confidence = self.optimization_cache[cache_key]
            print(f"📋 Using cached optimization: {cached_provider.value}")
            return self._create_cached_recommendation(cached_provider, cached_confidence, request_analysis)
        
        # Score all providers for this request
        provider_scores = self._score_providers(request_analysis, strategy, max_cost)
        
        # Select optimal provider
        optimal_provider = self._select_optimal_provider(provider_scores, strategy)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            optimal_provider, provider_scores, request_analysis, strategy
        )
        
        # Cache result
        self.optimization_cache[cache_key] = (optimal_provider, recommendation.confidence)
        
        print(f"✅ Recommended provider: {optimal_provider.value} (confidence: {recommendation.confidence:.2f})")
        
        return recommendation
    
    def batch_optimize_requests(self, 
                              requests: List[Tuple[str, str, Dict[str, Any]]],
                              strategy: CostOptimizationStrategy = CostOptimizationStrategy.OPTIMIZE_QUALITY_COST
                              ) -> BatchOptimizationResult:
        """
        Optimize a batch of requests for maximum cost efficiency
        """
        print(f"📊 Batch optimizing {len(requests)} requests")
        
        optimization_details = []
        original_total_cost = 0.0
        optimized_total_cost = 0.0
        
        for task_type, content, quality_reqs in requests:
            # Calculate original cost (assume Claude as default)
            original_provider = LLMProvider.CLAUDE
            original_cost = self._estimate_request_cost(original_provider, content)
            original_total_cost += original_cost
            
            # Get optimization recommendation
            recommendation = self.optimize_request(task_type, content, quality_reqs, strategy)
            optimized_cost = self._estimate_request_cost(recommendation.recommended_provider, content)
            optimized_total_cost += optimized_cost
            
            recommendation.current_provider = original_provider
            recommendation.estimated_cost_savings = original_cost - optimized_cost
            optimization_details.append(recommendation)
        
        cost_savings = original_total_cost - optimized_total_cost
        cost_savings_percent = (cost_savings / original_total_cost * 100) if original_total_cost > 0 else 0
        
        # Calculate average quality impact
        avg_quality_impact = sum(r.estimated_quality_impact for r in optimization_details) / len(optimization_details)
        
        result = BatchOptimizationResult(
            total_requests=len(requests),
            original_cost=original_total_cost,
            optimized_cost=optimized_total_cost,
            cost_savings=cost_savings,
            cost_savings_percent=cost_savings_percent,
            quality_impact=avg_quality_impact,
            optimization_details=optimization_details
        )
        
        print(f"💰 Batch optimization complete:")
        print(f"   Original cost: ${original_total_cost:.2f}")
        print(f"   Optimized cost: ${optimized_total_cost:.2f}")
        print(f"   Savings: ${cost_savings:.2f} ({cost_savings_percent:.1f}%)")
        
        return result
    
    def track_usage(self, 
                   request_id: str,
                   provider: LLMProvider,
                   task_type: str,
                   input_tokens: int,
                   output_tokens: int,
                   response_time_ms: float,
                   quality_rating: float = None) -> UsageRecord:
        """
        Track actual LLM usage for cost monitoring and optimization learning
        """
        # Calculate cost
        profile = self.PROVIDER_PROFILES[provider]
        cost = (
            (input_tokens / 1000) * profile.cost_per_1k_input_tokens +
            (output_tokens / 1000) * profile.cost_per_1k_output_tokens
        )
        
        # Determine complexity
        complexity = self.TASK_COMPLEXITY_MAP.get(task_type, TaskComplexity.MEDIUM)
        
        # Calculate cost efficiency score
        cost_efficiency = self._calculate_cost_efficiency(provider, cost, quality_rating, complexity)
        
        # Create usage record
        record = UsageRecord(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            provider=provider,
            task_type=task_type,
            task_complexity=complexity,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=cost,
            response_time_ms=response_time_ms,
            quality_rating=quality_rating,
            cost_efficiency_score=cost_efficiency
        )
        
        # Store record
        self.usage_history.append(record)
        
        # Update budget tracking
        self._update_budget_tracking(cost)
        
        # Check budget alerts
        self._check_budget_alerts()
        
        # Keep only last 10,000 records to prevent memory issues
        if len(self.usage_history) > 10000:
            self.usage_history = self.usage_history[-10000:]
        
        print(f"📊 Usage tracked: ${cost:.4f} for {provider.value} ({input_tokens + output_tokens} tokens)")
        
        return record
    
    def analyze_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze usage patterns and identify optimization opportunities
        """
        print(f"📈 Analyzing usage patterns over {days} days")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [
            r for r in self.usage_history
            if datetime.fromisoformat(r.timestamp) > cutoff_date
        ]
        
        if not recent_records:
            return {"error": "No usage data found for specified period"}
        
        # Calculate key metrics
        total_cost = sum(r.total_cost for r in recent_records)
        total_requests = len(recent_records)
        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
        
        # Provider usage breakdown
        provider_stats = {}
        for provider in LLMProvider:
            provider_records = [r for r in recent_records if r.provider == provider]
            if provider_records:
                provider_cost = sum(r.total_cost for r in provider_records)
                provider_stats[provider.value] = {
                    "requests": len(provider_records),
                    "total_cost": provider_cost,
                    "avg_cost_per_request": provider_cost / len(provider_records),
                    "cost_percentage": (provider_cost / total_cost) * 100,
                    "avg_quality": statistics.mean([r.quality_rating for r in provider_records if r.quality_rating]),
                    "avg_response_time": statistics.mean([r.response_time_ms for r in provider_records])
                }
        
        # Task type analysis
        task_stats = {}
        for record in recent_records:
            task = record.task_type
            if task not in task_stats:
                task_stats[task] = {"requests": 0, "total_cost": 0.0, "quality_ratings": []}
            
            task_stats[task]["requests"] += 1
            task_stats[task]["total_cost"] += record.total_cost
            if record.quality_rating:
                task_stats[task]["quality_ratings"].append(record.quality_rating)
        
        # Calculate cost efficiency trends
        efficiency_trend = self._calculate_efficiency_trend(recent_records)
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(recent_records, provider_stats)
        
        return {
            "period_days": days,
            "summary": {
                "total_requests": total_requests,
                "total_cost": total_cost,
                "avg_cost_per_request": avg_cost_per_request,
                "cost_efficiency_trend": efficiency_trend
            },
            "provider_breakdown": provider_stats,
            "task_breakdown": task_stats,
            "optimization_opportunities": optimization_opportunities,
            "budget_status": {
                "daily_usage": self.budget.current_day_spend,
                "weekly_usage": self.budget.current_week_spend,
                "monthly_usage": self.budget.current_month_spend,
                "daily_remaining": self.budget.daily_limit - self.budget.current_day_spend,
                "monthly_remaining": self.budget.monthly_limit - self.budget.current_month_spend
            }
        }
    
    def generate_cost_report(self, period: str = "monthly") -> Dict[str, Any]:
        """
        Generate comprehensive cost report with recommendations
        """
        print(f"📊 Generating {period} cost report")
        
        # Determine time period
        if period == "daily":
            days = 1
        elif period == "weekly":
            days = 7
        elif period == "monthly":
            days = 30
        else:
            days = 30
        
        # Get usage analysis
        usage_analysis = self.analyze_usage_patterns(days)
        
        if "error" in usage_analysis:
            return usage_analysis
        
        # Generate cost forecasts
        current_cost = usage_analysis["summary"]["total_cost"]
        if period == "daily":
            forecast = {
                "weekly_forecast": current_cost * 7,
                "monthly_forecast": current_cost * 30,
                "yearly_forecast": current_cost * 365
            }
        elif period == "weekly":
            forecast = {
                "monthly_forecast": current_cost * 4.33,  # avg weeks per month
                "yearly_forecast": current_cost * 52
            }
        else:  # monthly
            forecast = {
                "yearly_forecast": current_cost * 12
            }
        
        # Budget comparison
        budget_comparison = self._compare_against_budget(current_cost, period)
        
        # ROI analysis
        roi_analysis = self._calculate_llm_roi(usage_analysis)
        
        # Cost optimization recommendations
        optimization_recommendations = self._generate_cost_recommendations(usage_analysis)
        
        return {
            "report_period": period,
            "timestamp": datetime.now().isoformat(),
            "cost_summary": usage_analysis["summary"],
            "provider_breakdown": usage_analysis["provider_breakdown"],
            "cost_forecast": forecast,
            "budget_analysis": budget_comparison,
            "roi_analysis": roi_analysis,
            "optimization_recommendations": optimization_recommendations,
            "action_items": self._generate_cost_action_items(usage_analysis, budget_comparison)
        }
    
    # ============ INTERNAL OPTIMIZATION METHODS ============
    
    def _analyze_request(self, task_type: str, content: str, quality_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze request characteristics for optimization"""
        
        # Estimate token count (rough approximation: 4 chars per token)
        estimated_tokens = len(content) // 4
        
        # Determine complexity
        complexity = self.TASK_COMPLEXITY_MAP.get(task_type, TaskComplexity.MEDIUM)
        
        # Get quality requirements
        pm33_requirements = self.PM33_QUALITY_REQUIREMENTS.get(task_type, {"min_quality": 7.0, "min_confidence": 0.65})
        if quality_requirements:
            pm33_requirements.update(quality_requirements)
        
        # Analyze content characteristics
        content_analysis = {
            "requires_reasoning": any(word in content.lower() for word in ['analyze', 'compare', 'evaluate', 'decide']),
            "requires_creativity": any(word in content.lower() for word in ['create', 'generate', 'design', 'brainstorm']),
            "requires_accuracy": any(word in content.lower() for word in ['calculate', 'precise', 'exact', 'critical']),
            "is_time_sensitive": any(word in content.lower() for word in ['urgent', 'asap', 'quickly', 'immediate']),
            "has_structured_output": 'json' in content.lower() or 'format' in content.lower()
        }
        
        return {
            "task_type": task_type,
            "estimated_tokens": estimated_tokens,
            "complexity": complexity,
            "quality_requirements": pm33_requirements,
            "content_analysis": content_analysis,
            "content_length": len(content)
        }
    
    def _score_providers(self, request_analysis: Dict[str, Any], 
                        strategy: CostOptimizationStrategy, max_cost: float = None) -> Dict[LLMProvider, float]:
        """Score all providers for the given request"""
        
        scores = {}
        
        for provider, profile in self.PROVIDER_PROFILES.items():
            score = self._calculate_provider_score(provider, profile, request_analysis, strategy, max_cost)
            scores[provider] = score
        
        return scores
    
    def _calculate_provider_score(self, provider: LLMProvider, profile: LLMProviderProfile,
                                request_analysis: Dict[str, Any], strategy: CostOptimizationStrategy,
                                max_cost: float = None) -> float:
        """Calculate score for a specific provider"""
        
        # Base score
        score = 0.0
        
        # Quality scoring (0-40 points)
        quality_requirement = request_analysis["quality_requirements"]["min_quality"]
        if profile.quality_score >= quality_requirement:
            quality_score = min(40, (profile.quality_score / 10) * 40)
        else:
            # Penalty for not meeting quality requirements
            quality_score = max(0, ((profile.quality_score - quality_requirement) / 10) * 40)
        score += quality_score
        
        # Cost scoring (0-30 points) - lower cost = higher score
        estimated_cost = self._estimate_request_cost(provider, "x" * request_analysis["content_length"])
        if max_cost and estimated_cost > max_cost:
            return 0.0  # Disqualify if over budget
        
        # Normalize cost score (assuming max reasonable cost of $5)
        max_reasonable_cost = 5.0
        cost_score = max(0, 30 * (1 - (estimated_cost / max_reasonable_cost)))
        score += cost_score
        
        # Performance scoring (0-20 points)
        perf_score = min(20, (10 - (profile.avg_response_time_ms / 1000)) * 2)  # Favor faster responses
        score += max(0, perf_score)
        
        # Use case fit scoring (0-10 points)
        usecase_score = 0
        content_analysis = request_analysis["content_analysis"]
        
        if content_analysis["requires_reasoning"] and "strategic_reasoning" in profile.best_use_cases:
            usecase_score += 3
        if content_analysis["requires_creativity"] and "creative_solutions" in profile.best_use_cases:
            usecase_score += 3
        if content_analysis["has_structured_output"] and "structured_outputs" in profile.best_use_cases:
            usecase_score += 2
        if content_analysis["is_time_sensitive"] and "speed" in profile.best_use_cases:
            usecase_score += 2
        
        score += min(10, usecase_score)
        
        # Strategy-specific adjustments
        if strategy == CostOptimizationStrategy.MINIMIZE_COST:
            score = cost_score * 3  # Only care about cost
        elif strategy == CostOptimizationStrategy.MAXIMIZE_QUALITY:
            score = quality_score * 2 + perf_score  # Prioritize quality and speed
        elif strategy == CostOptimizationStrategy.MAXIMIZE_SPEED:
            score = perf_score * 3 + usecase_score  # Prioritize speed
        # OPTIMIZE_QUALITY_COST uses the balanced scoring above
        
        # Reliability bonus
        score += (profile.reliability_score / 10) * 5
        
        return score
    
    def _select_optimal_provider(self, provider_scores: Dict[LLMProvider, float], 
                               strategy: CostOptimizationStrategy) -> LLMProvider:
        """Select the optimal provider based on scores"""
        
        if not provider_scores:
            return LLMProvider.OPENAI  # Default fallback
        
        # Sort by score
        sorted_providers = sorted(provider_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return highest scoring provider
        return sorted_providers[0][0]
    
    def _generate_recommendation(self, optimal_provider: LLMProvider, 
                               provider_scores: Dict[LLMProvider, float],
                               request_analysis: Dict[str, Any],
                               strategy: CostOptimizationStrategy) -> OptimizationRecommendation:
        """Generate detailed optimization recommendation"""
        
        # Calculate cost savings vs Claude (assumed default)
        claude_cost = self._estimate_request_cost(LLMProvider.CLAUDE, "x" * request_analysis["content_length"])
        optimal_cost = self._estimate_request_cost(optimal_provider, "x" * request_analysis["content_length"])
        cost_savings = claude_cost - optimal_cost
        
        # Calculate quality impact
        claude_quality = self.PROVIDER_PROFILES[LLMProvider.CLAUDE].quality_score
        optimal_quality = self.PROVIDER_PROFILES[optimal_provider].quality_score
        quality_impact = optimal_quality - claude_quality
        
        # Confidence based on score difference
        sorted_scores = sorted(provider_scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence = min(1.0, (sorted_scores[0] - sorted_scores[1]) / 20)
        else:
            confidence = 0.8
        
        # Reasoning
        profile = self.PROVIDER_PROFILES[optimal_provider]
        reasoning = f"Selected {optimal_provider.value} for {request_analysis['task_type']} task. "
        
        if cost_savings > 0:
            reasoning += f"Cost savings: ${cost_savings:.3f} ({(cost_savings/claude_cost)*100:.1f}%). "
        
        if quality_impact >= 0:
            reasoning += f"Quality maintained (score: {optimal_quality:.1f}). "
        else:
            reasoning += f"Quality trade-off (score: {optimal_quality:.1f} vs {claude_quality:.1f}). "
        
        reasoning += f"Best for: {', '.join(profile.best_use_cases[:2])}."
        
        # Alternative options
        sorted_providers = sorted(provider_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = []
        for provider, score in sorted_providers[1:3]:  # Top 2 alternatives
            alt_cost = self._estimate_request_cost(provider, "x" * request_analysis["content_length"])
            alt_savings = claude_cost - alt_cost
            alt_reason = f"Alternative with ${alt_savings:.3f} savings, quality {self.PROVIDER_PROFILES[provider].quality_score:.1f}"
            alternatives.append((provider, alt_savings, alt_reason))
        
        return OptimizationRecommendation(
            current_provider=LLMProvider.CLAUDE,  # Assumed default
            recommended_provider=optimal_provider,
            estimated_cost_savings=cost_savings,
            estimated_quality_impact=quality_impact,
            confidence=confidence,
            reasoning=reasoning,
            alternative_options=alternatives
        )
    
    def _estimate_request_cost(self, provider: LLMProvider, content: str) -> float:
        """Estimate cost for a request with given provider"""
        profile = self.PROVIDER_PROFILES[provider]
        
        # Rough token estimation (4 chars per token average)
        estimated_input_tokens = len(content) // 4
        estimated_output_tokens = estimated_input_tokens // 3  # Assume 1:3 input:output ratio
        
        cost = (
            (estimated_input_tokens / 1000) * profile.cost_per_1k_input_tokens +
            (estimated_output_tokens / 1000) * profile.cost_per_1k_output_tokens
        )
        
        return cost
    
    def _calculate_cost_efficiency(self, provider: LLMProvider, cost: float, 
                                 quality_rating: float = None, complexity: TaskComplexity = None) -> float:
        """Calculate cost efficiency score for a request"""
        if not quality_rating:
            quality_rating = self.PROVIDER_PROFILES[provider].quality_score
        
        # Cost efficiency = Quality per dollar
        if cost > 0:
            base_efficiency = quality_rating / cost
        else:
            base_efficiency = quality_rating * 100  # Free requests get high efficiency
        
        # Adjust for task complexity
        complexity_multiplier = {
            TaskComplexity.SIMPLE: 0.8,    # Simple tasks don't need high quality
            TaskComplexity.MEDIUM: 1.0,    # Medium tasks are baseline
            TaskComplexity.COMPLEX: 1.2,   # Complex tasks benefit more from quality
            TaskComplexity.CRITICAL: 1.5   # Critical tasks justify higher costs for quality
        }
        
        if complexity:
            base_efficiency *= complexity_multiplier.get(complexity, 1.0)
        
        return base_efficiency
    
    def _update_budget_tracking(self, cost: float) -> None:
        """Update budget tracking with new usage"""
        now = datetime.now()
        
        # For simplicity, reset daily/weekly/monthly at fixed intervals
        # In production, this would be more sophisticated
        self.budget.current_day_spend += cost
        self.budget.current_week_spend += cost
        self.budget.current_month_spend += cost
    
    def _check_budget_alerts(self) -> None:
        """Check for budget alerts and warnings"""
        alerts = []
        
        # Daily budget check
        if self.budget.current_day_spend >= self.budget.daily_limit * self.budget.alert_threshold:
            alerts.append(f"⚠️ Daily budget alert: ${self.budget.current_day_spend:.2f} of ${self.budget.daily_limit:.2f}")
        
        # Monthly budget check
        if self.budget.current_month_spend >= self.budget.monthly_limit * self.budget.alert_threshold:
            alerts.append(f"⚠️ Monthly budget alert: ${self.budget.current_month_spend:.2f} of ${self.budget.monthly_limit:.2f}")
        
        for alert in alerts:
            print(alert)
    
    def _generate_cache_key(self, task_type: str, request_analysis: Dict[str, Any]) -> str:
        """Generate cache key for similar requests"""
        # Create key from task characteristics
        key_components = [
            task_type,
            request_analysis["complexity"].value,
            str(request_analysis["quality_requirements"]["min_quality"]),
            str(request_analysis["estimated_tokens"] // 100)  # Bucket token counts
        ]
        
        cache_key = "|".join(key_components)
        return hashlib.md5(cache_key.encode()).hexdigest()[:12]
    
    def _create_cached_recommendation(self, provider: LLMProvider, confidence: float, 
                                    request_analysis: Dict[str, Any]) -> OptimizationRecommendation:
        """Create recommendation from cached result"""
        
        # Estimate savings
        claude_cost = self._estimate_request_cost(LLMProvider.CLAUDE, "x" * request_analysis["content_length"])
        cached_cost = self._estimate_request_cost(provider, "x" * request_analysis["content_length"])
        cost_savings = claude_cost - cached_cost
        
        # Quality impact
        claude_quality = self.PROVIDER_PROFILES[LLMProvider.CLAUDE].quality_score
        cached_quality = self.PROVIDER_PROFILES[provider].quality_score
        quality_impact = cached_quality - claude_quality
        
        return OptimizationRecommendation(
            current_provider=LLMProvider.CLAUDE,
            recommended_provider=provider,
            estimated_cost_savings=cost_savings,
            estimated_quality_impact=quality_impact,
            confidence=confidence,
            reasoning=f"Cached optimization for {request_analysis['task_type']} task"
        )
    
    def _calculate_efficiency_trend(self, records: List[UsageRecord]) -> str:
        """Calculate efficiency trend from recent records"""
        if len(records) < 10:
            return "insufficient_data"
        
        # Sort by timestamp
        sorted_records = sorted(records, key=lambda r: r.timestamp)
        
        # Calculate efficiency scores for first and last quarters
        quarter_size = len(sorted_records) // 4
        first_quarter = sorted_records[:quarter_size]
        last_quarter = sorted_records[-quarter_size:]
        
        first_avg_efficiency = statistics.mean([r.cost_efficiency_score for r in first_quarter if r.cost_efficiency_score])
        last_avg_efficiency = statistics.mean([r.cost_efficiency_score for r in last_quarter if r.cost_efficiency_score])
        
        if last_avg_efficiency > first_avg_efficiency * 1.1:
            return "improving"
        elif last_avg_efficiency < first_avg_efficiency * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _identify_optimization_opportunities(self, records: List[UsageRecord], 
                                           provider_stats: Dict[str, Dict]) -> List[str]:
        """Identify specific optimization opportunities"""
        opportunities = []
        
        # Check for expensive provider overuse
        if "claude" in provider_stats and provider_stats["claude"]["cost_percentage"] > 60:
            opportunities.append("Consider reducing Claude usage for simple tasks - potential 40%+ cost savings")
        
        # Check for low-efficiency tasks
        low_efficiency_tasks = {}
        for record in records:
            if record.cost_efficiency_score and record.cost_efficiency_score < 50:
                task = record.task_type
                if task not in low_efficiency_tasks:
                    low_efficiency_tasks[task] = 0
                low_efficiency_tasks[task] += 1
        
        for task, count in low_efficiency_tasks.items():
            if count > 5:  # Multiple low-efficiency instances
                opportunities.append(f"Optimize {task} tasks - {count} instances with low cost efficiency")
        
        # Check for speed optimization opportunities
        slow_tasks = [r for r in records if r.response_time_ms > 5000]  # >5 seconds
        if len(slow_tasks) > len(records) * 0.2:  # >20% of requests are slow
            opportunities.append("Consider Groq for speed-critical tasks - potential 75% response time reduction")
        
        return opportunities
    
    def _compare_against_budget(self, current_cost: float, period: str) -> Dict[str, Any]:
        """Compare current usage against budget"""
        
        if period == "daily":
            budget_limit = self.budget.daily_limit
            current_usage = self.budget.current_day_spend
        elif period == "weekly":
            budget_limit = self.budget.weekly_limit
            current_usage = self.budget.current_week_spend
        else:  # monthly
            budget_limit = self.budget.monthly_limit
            current_usage = self.budget.current_month_spend
        
        usage_percent = (current_usage / budget_limit) * 100 if budget_limit > 0 else 0
        remaining_budget = budget_limit - current_usage
        
        status = "green"
        if usage_percent >= 100:
            status = "red"
        elif usage_percent >= self.budget.alert_threshold * 100:
            status = "yellow"
        
        return {
            "budget_limit": budget_limit,
            "current_usage": current_usage,
            "usage_percent": usage_percent,
            "remaining_budget": remaining_budget,
            "status": status,
            "days_remaining": self._get_days_remaining(period)
        }
    
    def _calculate_llm_roi(self, usage_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ROI of LLM usage"""
        
        # Estimate time savings (assumed 8 hours manual vs 10 minutes with LLM)
        total_requests = usage_analysis["summary"]["total_requests"]
        estimated_time_saved_hours = total_requests * 7.83  # 8 hours - 10 minutes
        
        # Estimate cost of manual work (assumed $50/hour PM rate)
        manual_cost_estimate = estimated_time_saved_hours * 50
        llm_cost = usage_analysis["summary"]["total_cost"]
        
        roi = ((manual_cost_estimate - llm_cost) / llm_cost) * 100 if llm_cost > 0 else 0
        
        return {
            "total_llm_cost": llm_cost,
            "estimated_manual_cost": manual_cost_estimate,
            "estimated_time_saved_hours": estimated_time_saved_hours,
            "roi_percent": roi,
            "cost_savings": manual_cost_estimate - llm_cost,
            "efficiency_multiplier": manual_cost_estimate / llm_cost if llm_cost > 0 else 0
        }
    
    def _generate_cost_recommendations(self, usage_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific cost optimization recommendations"""
        recommendations = []
        
        provider_stats = usage_analysis["provider_breakdown"]
        
        # Provider optimization recommendations
        if "claude" in provider_stats and provider_stats["claude"]["cost_percentage"] > 50:
            recommendations.append("HIGH IMPACT: Reduce Claude usage for simple tasks - switch to Together AI for 95% cost savings")
        
        if "openai" in provider_stats and provider_stats["openai"]["cost_percentage"] > 30:
            recommendations.append("MEDIUM IMPACT: Review OpenAI usage - consider Together AI for non-creative tasks")
        
        if provider_stats.get("together", {}).get("cost_percentage", 0) < 20:
            recommendations.append("OPPORTUNITY: Increase Together AI usage for bulk processing - potential 80% cost reduction")
        
        # Usage pattern recommendations
        total_cost = usage_analysis["summary"]["total_cost"]
        if total_cost > 100:  # High usage
            recommendations.append("Consider implementing request batching to reduce API overhead")
            recommendations.append("Implement response caching for repeated queries")
        
        # Budget recommendations
        budget_status = usage_analysis["budget_status"]
        if budget_status["monthly_remaining"] < 100:  # Low budget remaining
            recommendations.append("URGENT: Approaching monthly budget limit - implement cost controls")
        
        return recommendations
    
    def _generate_cost_action_items(self, usage_analysis: Dict[str, Any], 
                                   budget_comparison: Dict[str, Any]) -> List[str]:
        """Generate specific action items for cost optimization"""
        action_items = []
        
        # Budget-based actions
        if budget_comparison["status"] == "red":
            action_items.append("IMMEDIATE: Implement spending freeze until next period")
            action_items.append("IMMEDIATE: Review all non-critical LLM usage")
        elif budget_comparison["status"] == "yellow":
            action_items.append("Within 24h: Switch high-cost tasks to cheaper providers")
            action_items.append("Within 48h: Implement usage monitoring alerts")
        
        # Optimization actions
        provider_stats = usage_analysis["provider_breakdown"]
        if "claude" in provider_stats and provider_stats["claude"]["requests"] > 100:
            action_items.append("Within 1 week: Audit Claude usage and migrate 50% to cheaper alternatives")
        
        # Efficiency actions
        if usage_analysis["summary"]["avg_cost_per_request"] > 0.10:
            action_items.append("Within 2 weeks: Implement request optimization to reduce average cost per request")
        
        return action_items
    
    def _get_days_remaining(self, period: str) -> int:
        """Get days remaining in current period"""
        now = datetime.now()
        
        if period == "daily":
            return 1
        elif period == "weekly":
            return 7 - now.weekday()
        else:  # monthly
            import calendar
            return calendar.monthrange(now.year, now.month)[1] - now.day
    
    def load_usage_history(self) -> None:
        """Load historical usage data"""
        # In production, this would load from database
        # For now, initialize with empty history
        pass
    
    def save_usage_history(self) -> None:
        """Save usage history to persistent storage"""
        # In production, this would save to database
        pass

def main():
    """Command line interface for LLM Cost Optimizer"""
    parser = argparse.ArgumentParser(description='PM33 LLM Cost Optimizer')
    parser.add_argument('--optimize-request', action='store_true',
                       help='Optimize LLM selection for a request')
    parser.add_argument('--task-type', type=str, default='analysis',
                       help='Type of task to optimize')
    parser.add_argument('--content', type=str, default='Sample content for analysis',
                       help='Content to analyze for optimization')
    parser.add_argument('--strategy', type=str, default='optimize_quality_cost',
                       choices=['minimize_cost', 'optimize_quality_cost', 'maximize_quality', 'maximize_speed'],
                       help='Optimization strategy to use')
    parser.add_argument('--analyze-usage', type=int, metavar='DAYS',
                       help='Analyze usage patterns over N days')
    parser.add_argument('--cost-report', type=str, 
                       choices=['daily', 'weekly', 'monthly'],
                       help='Generate cost report for specified period')
    parser.add_argument('--budget-daily', type=float, default=50.0,
                       help='Daily budget limit in dollars')
    parser.add_argument('--budget-monthly', type=float, default=1000.0,
                       help='Monthly budget limit in dollars')
    
    args = parser.parse_args()
    
    # Initialize optimizer with budget
    budget_config = {
        "daily_limit": args.budget_daily,
        "weekly_limit": args.budget_daily * 7,
        "monthly_limit": args.budget_monthly
    }
    optimizer = PM33LLMCostOptimizer(budget_config)
    
    if args.optimize_request:
        print("🎯 PM33 LLM REQUEST OPTIMIZATION")
        print("=" * 60)
        
        strategy_map = {
            'minimize_cost': CostOptimizationStrategy.MINIMIZE_COST,
            'optimize_quality_cost': CostOptimizationStrategy.OPTIMIZE_QUALITY_COST,
            'maximize_quality': CostOptimizationStrategy.MAXIMIZE_QUALITY,
            'maximize_speed': CostOptimizationStrategy.MAXIMIZE_SPEED
        }
        
        recommendation = optimizer.optimize_request(
            args.task_type,
            args.content,
            strategy=strategy_map[args.strategy]
        )
        
        print(f"\n🎯 Task: {args.task_type}")
        print(f"📝 Content length: {len(args.content)} characters")
        print(f"🔄 Strategy: {args.strategy}")
        
        print(f"\n✅ RECOMMENDATION:")
        print(f"   Provider: {recommendation.recommended_provider.value}")
        print(f"   Cost savings: ${recommendation.estimated_cost_savings:.4f}")
        print(f"   Quality impact: {recommendation.estimated_quality_impact:+.1f}")
        print(f"   Confidence: {recommendation.confidence:.1%}")
        
        print(f"\n💡 Reasoning:")
        print(f"   {recommendation.reasoning}")
        
        if recommendation.alternative_options:
            print(f"\n🔄 Alternatives:")
            for provider, savings, reason in recommendation.alternative_options:
                print(f"   {provider.value}: ${savings:.4f} savings - {reason}")
    
    elif args.analyze_usage:
        print("📈 PM33 LLM USAGE ANALYSIS")
        print("=" * 60)
        
        analysis = optimizer.analyze_usage_patterns(args.analyze_usage)
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        summary = analysis["summary"]
        print(f"\n📊 Summary ({args.analyze_usage} days):")
        print(f"   Total requests: {summary['total_requests']}")
        print(f"   Total cost: ${summary['total_cost']:.2f}")
        print(f"   Avg cost per request: ${summary['avg_cost_per_request']:.4f}")
        print(f"   Cost efficiency trend: {summary['cost_efficiency_trend']}")
        
        print(f"\n💰 Provider Breakdown:")
        for provider, stats in analysis["provider_breakdown"].items():
            print(f"   {provider.title()}:")
            print(f"     Requests: {stats['requests']} ({stats['cost_percentage']:.1f}% of cost)")
            print(f"     Avg cost: ${stats['avg_cost_per_request']:.4f}")
            print(f"     Avg quality: {stats['avg_quality']:.1f}")
            print(f"     Avg response time: {stats['avg_response_time']:.0f}ms")
        
        print(f"\n💡 Optimization Opportunities:")
        for opportunity in analysis["optimization_opportunities"]:
            print(f"   • {opportunity}")
        
        print(f"\n💳 Budget Status:")
        budget = analysis["budget_status"]
        print(f"   Daily: ${budget['daily_usage']:.2f} (${budget['daily_remaining']:.2f} remaining)")
        print(f"   Monthly: ${budget['monthly_usage']:.2f} (${budget['monthly_remaining']:.2f} remaining)")
    
    elif args.cost_report:
        print("📊 PM33 LLM COST REPORT")
        print("=" * 60)
        
        report = optimizer.generate_cost_report(args.cost_report)
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print(f"\n📈 {args.cost_report.title()} Cost Summary:")
        summary = report["cost_summary"]
        print(f"   Total cost: ${summary['total_cost']:.2f}")
        print(f"   Total requests: {summary['total_requests']}")
        print(f"   Avg cost per request: ${summary['avg_cost_per_request']:.4f}")
        
        print(f"\n🔮 Cost Forecast:")
        for period, cost in report["cost_forecast"].items():
            print(f"   {period.replace('_', ' ').title()}: ${cost:.2f}")
        
        print(f"\n📊 ROI Analysis:")
        roi = report["roi_analysis"]
        print(f"   LLM cost: ${roi['total_llm_cost']:.2f}")
        print(f"   Manual cost equivalent: ${roi['estimated_manual_cost']:.2f}")
        print(f"   ROI: {roi['roi_percent']:.0f}%")
        print(f"   Time saved: {roi['estimated_time_saved_hours']:.1f} hours")
        
        print(f"\n🎯 Optimization Recommendations:")
        for rec in report["optimization_recommendations"]:
            print(f"   • {rec}")
        
        print(f"\n📋 Action Items:")
        for item in report["action_items"]:
            print(f"   • {item}")
    
    else:
        print("💰 PM33 LLM COST OPTIMIZER")
        print("=" * 60)
        print("Available commands:")
        print("  --optimize-request      Optimize LLM selection for a request")
        print("  --task-type TYPE        Specify task type for optimization")
        print("  --content TEXT          Content to analyze")
        print("  --strategy STRATEGY     Optimization strategy to use")
        print("  --analyze-usage DAYS    Analyze usage patterns over N days")
        print("  --cost-report PERIOD    Generate cost report (daily/weekly/monthly)")
        print("  --budget-daily AMOUNT   Set daily budget limit")
        print("  --budget-monthly AMOUNT Set monthly budget limit")
        print("\nExample:")
        print("  python pm33_llm_cost_optimizer.py --optimize-request --task-type strategic_analysis --strategy minimize_cost")

if __name__ == "__main__":
    main()