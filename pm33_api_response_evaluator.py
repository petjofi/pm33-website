#!/usr/bin/env python3
"""
PM33 API Response Evaluator
Analyzes and optimizes API responses for backend performance and PM33 compliance
Usage: python pm33_api_response_evaluator.py [--endpoint] [--analyze-file] [--optimize]
"""

import os
import re
import json
import time
import hashlib
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import argparse
from pathlib import Path

class ResponseCategory(Enum):
    """API Response Categories"""
    STRATEGIC_ANALYSIS = "strategic_analysis"
    FRAMEWORK_CALCULATION = "framework_calculation"
    PMO_METRICS = "pmo_metrics"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    USER_INTERACTION = "user_interaction"
    SYSTEM_STATUS = "system_status"

class PerformanceGrade(Enum):
    """Performance grades for API responses"""
    EXCELLENT = "A+"  # >95% score
    GOOD = "A"        # 85-95% score
    ACCEPTABLE = "B"  # 75-85% score
    NEEDS_IMPROVEMENT = "C"  # 65-75% score
    POOR = "D"        # 50-65% score
    FAILING = "F"     # <50% score

@dataclass
class ResponseViolation:
    """Represents a response quality violation"""
    rule_id: str
    severity: str  # 'critical', 'major', 'minor', 'info'
    category: str
    message: str
    suggestion: str
    performance_impact: str
    cost_impact: str
    line_location: Optional[str] = None

@dataclass
class ResponseMetrics:
    """Response performance and quality metrics"""
    response_size_bytes: int
    response_time_ms: float
    json_parse_time_ms: float
    compression_ratio: float
    cache_hit_possible: bool
    contains_sensitive_data: bool
    nested_depth: int
    array_sizes: List[int] = field(default_factory=list)
    redundant_fields: List[str] = field(default_factory=list)

@dataclass
class APIResponseEvaluation:
    """Comprehensive API response evaluation"""
    endpoint: str
    timestamp: str
    response_category: str
    overall_score: float
    performance_grade: str
    structure_score: float
    content_score: float
    pm33_compliance_score: float
    performance_score: float
    security_score: float
    violations: List[ResponseViolation] = field(default_factory=list)
    metrics: Optional[ResponseMetrics] = None
    optimization_suggestions: List[str] = field(default_factory=list)
    cost_optimization: Dict[str, Any] = field(default_factory=dict)
    benchmark_comparison: Dict[str, float] = field(default_factory=dict)

@dataclass
class HistoricalPerformance:
    """Historical performance tracking"""
    endpoint: str
    evaluations: List[APIResponseEvaluation] = field(default_factory=list)
    average_score: float = 0.0
    improvement_trend: str = "stable"  # improving, stable, degrading
    last_updated: str = ""

class PM33APIResponseEvaluator:
    """
    PM33 API Response Evaluator
    Comprehensive analysis and optimization of API responses for PM33 platform
    """
    
    # PM33 Response Standards
    PM33_RESPONSE_STANDARDS = {
        "required_fields": {
            "strategic_analysis": ["analysis", "confidence", "recommendation", "reasoning_chain"],
            "framework_calculation": ["framework", "score", "components", "interpretation"],
            "pmo_metrics": ["capabilities", "transformation_score", "progress", "next_actions"],
            "competitive_intelligence": ["threats", "opportunities", "recommendations", "positioning"],
            "resource_optimization": ["scenarios", "roi_projections", "recommendations", "timeline"]
        },
        "response_structure": {
            "status": "required",
            "data": "required", 
            "timestamp": "required",
            "confidence": "recommended",
            "metadata": "optional",
            "debug_info": "development_only"
        },
        "performance_targets": {
            "strategic_analysis": {"max_size_kb": 50, "max_time_ms": 10000},
            "framework_calculation": {"max_size_kb": 10, "max_time_ms": 2000},
            "pmo_metrics": {"max_size_kb": 25, "max_time_ms": 5000},
            "competitive_intelligence": {"max_size_kb": 100, "max_time_ms": 15000},
            "resource_optimization": {"max_size_kb": 75, "max_time_ms": 8000},
            "user_interaction": {"max_size_kb": 5, "max_time_ms": 1000},
            "system_status": {"max_size_kb": 2, "max_time_ms": 500}
        }
    }
    
    # Industry Benchmarks (based on Linear.app, Stripe.com, etc.)
    INDUSTRY_BENCHMARKS = {
        "response_time": {
            "excellent": 500,    # <0.5s
            "good": 1000,       # <1s  
            "acceptable": 2000,  # <2s
            "poor": 5000        # <5s
        },
        "response_size": {
            "excellent": 10,     # <10KB
            "good": 25,         # <25KB
            "acceptable": 50,    # <50KB
            "poor": 100         # <100KB
        },
        "json_depth": {
            "excellent": 3,      # max 3 levels
            "good": 5,          # max 5 levels
            "acceptable": 7,     # max 7 levels
            "poor": 10          # max 10 levels
        }
    }
    
    # Cost Optimization Patterns
    COST_OPTIMIZATION_PATTERNS = {
        "caching_opportunities": [
            r'"cache":\s*false',
            r'"ttl":\s*0',
            r'"static.*":\s*true'
        ],
        "compression_candidates": [
            r'"large_array":\s*\[.*\]',
            r'"text":\s*".{1000,}"',  # Large text fields
            r'"description":\s*".{500,}"'
        ],
        "pagination_needed": [
            r'"results":\s*\[.*\]',
            r'"items":\s*\[.*\]',
            r'"data":\s*\[.*\]'
        ],
        "redundant_data": [
            r'"id":\s*\d+.*"id":\s*\d+',  # Duplicate IDs
            r'"timestamp".*"timestamp"',   # Multiple timestamps
            r'"metadata".*"meta"'          # Redundant metadata
        ]
    }
    
    def __init__(self):
        """Initialize the API Response Evaluator"""
        self.historical_data: Dict[str, HistoricalPerformance] = {}
        self.evaluation_cache: Dict[str, APIResponseEvaluation] = {}
        self.load_historical_data()
        
        print("🔍 PM33 API Response Evaluator initialized")
        print(f"📊 Response categories: {len(ResponseCategory)}")
        print(f"🎯 Performance benchmarks loaded")
        
    def evaluate_response(self, 
                         endpoint: str,
                         response_data: Dict[str, Any],
                         response_time_ms: float = None,
                         response_category: str = None) -> APIResponseEvaluation:
        """
        Comprehensive evaluation of API response
        """
        print(f"🔍 Evaluating API response from {endpoint}")
        
        # Auto-detect response category if not provided
        if not response_category:
            response_category = self._detect_response_category(endpoint, response_data)
        
        # Calculate metrics
        metrics = self._calculate_response_metrics(response_data, response_time_ms)
        
        # Run all evaluation checks
        violations = []
        
        # Structure evaluation
        structure_score, structure_violations = self._evaluate_structure(response_data, response_category)
        violations.extend(structure_violations)
        
        # Content quality evaluation
        content_score, content_violations = self._evaluate_content(response_data, response_category)
        violations.extend(content_violations)
        
        # PM33 compliance evaluation
        compliance_score, compliance_violations = self._evaluate_pm33_compliance(response_data, response_category)
        violations.extend(compliance_violations)
        
        # Performance evaluation
        performance_score, performance_violations = self._evaluate_performance(metrics, response_category)
        violations.extend(performance_violations)
        
        # Security evaluation
        security_score, security_violations = self._evaluate_security(response_data)
        violations.extend(security_violations)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            structure_score, content_score, compliance_score, performance_score, security_score
        )
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(violations, metrics, response_category)
        
        # Cost optimization analysis
        cost_optimization = self._analyze_cost_optimization(response_data, metrics)
        
        # Benchmark comparison
        benchmark_comparison = self._compare_against_benchmarks(metrics, response_category)
        
        evaluation = APIResponseEvaluation(
            endpoint=endpoint,
            timestamp=datetime.now().isoformat(),
            response_category=response_category,
            overall_score=overall_score,
            performance_grade=self._calculate_performance_grade(overall_score),
            structure_score=structure_score,
            content_score=content_score,
            pm33_compliance_score=compliance_score,
            performance_score=performance_score,
            security_score=security_score,
            violations=violations,
            metrics=metrics,
            optimization_suggestions=optimization_suggestions,
            cost_optimization=cost_optimization,
            benchmark_comparison=benchmark_comparison
        )
        
        # Store for historical tracking
        self._store_evaluation(evaluation)
        
        return evaluation
    
    def batch_evaluate_responses(self, responses: List[Tuple[str, Dict[str, Any], float]]) -> List[APIResponseEvaluation]:
        """
        Evaluate multiple API responses in batch
        """
        print(f"📊 Batch evaluating {len(responses)} API responses")
        
        evaluations = []
        for endpoint, response_data, response_time in responses:
            evaluation = self.evaluate_response(endpoint, response_data, response_time)
            evaluations.append(evaluation)
            
            # Progress indicator
            if len(evaluations) % 10 == 0:
                print(f"   Completed {len(evaluations)}/{len(responses)} evaluations")
        
        return evaluations
    
    def generate_optimization_report(self, evaluations: List[APIResponseEvaluation]) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report
        """
        print("📈 Generating optimization report")
        
        # Calculate aggregate metrics
        avg_score = sum(e.overall_score for e in evaluations) / len(evaluations) if evaluations else 0
        grade_distribution = self._calculate_grade_distribution(evaluations)
        
        # Identify common issues
        common_issues = self._identify_common_issues(evaluations)
        
        # Cost optimization opportunities
        cost_savings = self._calculate_cost_savings_opportunities(evaluations)
        
        # Performance improvements
        performance_improvements = self._identify_performance_improvements(evaluations)
        
        # Priority recommendations
        priority_recommendations = self._generate_priority_recommendations(evaluations)
        
        return {
            "summary": {
                "total_endpoints": len(evaluations),
                "average_score": avg_score,
                "grade_distribution": grade_distribution,
                "total_violations": sum(len(e.violations) for e in evaluations)
            },
            "common_issues": common_issues,
            "cost_optimization": cost_savings,
            "performance_improvements": performance_improvements,
            "priority_recommendations": priority_recommendations,
            "endpoint_details": [
                {
                    "endpoint": e.endpoint,
                    "score": e.overall_score,
                    "grade": e.performance_grade,
                    "top_issues": [v.message for v in e.violations[:3]]
                } for e in evaluations
            ]
        }
    
    def monitor_endpoint_performance(self, endpoint: str, days: int = 7) -> Dict[str, Any]:
        """
        Monitor endpoint performance over time
        """
        print(f"📊 Monitoring {endpoint} performance over {days} days")
        
        if endpoint not in self.historical_data:
            return {"error": "No historical data available for endpoint"}
        
        historical = self.historical_data[endpoint]
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent evaluations
        recent_evaluations = [
            e for e in historical.evaluations
            if datetime.fromisoformat(e.timestamp) > cutoff_date
        ]
        
        if not recent_evaluations:
            return {"error": "No recent evaluations found"}
        
        # Calculate trends
        scores = [e.overall_score for e in recent_evaluations]
        response_times = [e.metrics.response_time_ms for e in recent_evaluations if e.metrics]
        
        return {
            "endpoint": endpoint,
            "period_days": days,
            "total_evaluations": len(recent_evaluations),
            "performance_trend": {
                "average_score": statistics.mean(scores),
                "score_trend": self._calculate_trend(scores),
                "best_score": max(scores),
                "worst_score": min(scores)
            },
            "response_time_trend": {
                "average_ms": statistics.mean(response_times) if response_times else 0,
                "time_trend": self._calculate_trend(response_times) if response_times else "no_data"
            },
            "recent_issues": self._get_recent_issues(recent_evaluations),
            "improvement_suggestions": self._get_improvement_suggestions(recent_evaluations)
        }
    
    # ============ INTERNAL EVALUATION METHODS ============
    
    def _detect_response_category(self, endpoint: str, response_data: Dict[str, Any]) -> str:
        """Auto-detect response category from endpoint and content"""
        endpoint_lower = endpoint.lower()
        content_str = str(response_data).lower()
        
        # Endpoint-based detection
        if 'strategic' in endpoint_lower or 'analyze' in endpoint_lower:
            return ResponseCategory.STRATEGIC_ANALYSIS.value
        elif 'framework' in endpoint_lower or 'rice' in endpoint_lower or 'ice' in endpoint_lower:
            return ResponseCategory.FRAMEWORK_CALCULATION.value
        elif 'pmo' in endpoint_lower or 'transformation' in endpoint_lower:
            return ResponseCategory.PMO_METRICS.value
        elif 'competitive' in endpoint_lower or 'market' in endpoint_lower:
            return ResponseCategory.COMPETITIVE_INTELLIGENCE.value
        elif 'resource' in endpoint_lower or 'optimization' in endpoint_lower:
            return ResponseCategory.RESOURCE_OPTIMIZATION.value
        elif 'status' in endpoint_lower or 'health' in endpoint_lower:
            return ResponseCategory.SYSTEM_STATUS.value
        
        # Content-based detection
        if any(term in content_str for term in ['confidence', 'analysis', 'recommendation']):
            return ResponseCategory.STRATEGIC_ANALYSIS.value
        elif any(term in content_str for term in ['score', 'framework', 'calculation']):
            return ResponseCategory.FRAMEWORK_CALCULATION.value
        elif any(term in content_str for term in ['capability', 'transformation', 'pmo']):
            return ResponseCategory.PMO_METRICS.value
        
        return ResponseCategory.USER_INTERACTION.value  # Default
    
    def _calculate_response_metrics(self, response_data: Dict[str, Any], response_time_ms: float = None) -> ResponseMetrics:
        """Calculate comprehensive response metrics"""
        response_json = json.dumps(response_data)
        response_size = len(response_json.encode('utf-8'))
        
        # JSON parsing performance test
        start_time = time.time()
        json.loads(response_json)
        json_parse_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Calculate nested depth
        nested_depth = self._calculate_nested_depth(response_data)
        
        # Calculate array sizes
        array_sizes = self._find_array_sizes(response_data)
        
        # Check for redundant fields
        redundant_fields = self._find_redundant_fields(response_data)
        
        # Estimate compression ratio
        try:
            import gzip
            compressed = gzip.compress(response_json.encode('utf-8'))
            compression_ratio = len(compressed) / response_size if response_size > 0 else 1.0
        except:
            compression_ratio = 0.7  # Estimate
        
        # Check cache potential
        cache_hit_possible = self._assess_cache_potential(response_data)
        
        # Check for sensitive data
        contains_sensitive_data = self._check_for_sensitive_data(response_data)
        
        return ResponseMetrics(
            response_size_bytes=response_size,
            response_time_ms=response_time_ms or 0.0,
            json_parse_time_ms=json_parse_time,
            compression_ratio=compression_ratio,
            cache_hit_possible=cache_hit_possible,
            contains_sensitive_data=contains_sensitive_data,
            nested_depth=nested_depth,
            array_sizes=array_sizes,
            redundant_fields=redundant_fields
        )
    
    def _evaluate_structure(self, response_data: Dict[str, Any], response_category: str) -> Tuple[float, List[ResponseViolation]]:
        """Evaluate response structure quality"""
        violations = []
        score = 100.0
        
        # Check required fields
        required_fields = self.PM33_RESPONSE_STANDARDS["response_structure"]
        for field, requirement in required_fields.items():
            if requirement == "required" and field not in response_data:
                violations.append(ResponseViolation(
                    rule_id="missing_required_field",
                    severity="critical",
                    category="structure",
                    message=f"Missing required field: {field}",
                    suggestion=f"Add {field} field to response structure",
                    performance_impact="High - breaks client expectations",
                    cost_impact="Medium - causes client-side error handling"
                ))
                score -= 20
        
        # Check data field structure
        if "data" in response_data:
            data = response_data["data"]
            if not isinstance(data, (dict, list)):
                violations.append(ResponseViolation(
                    rule_id="invalid_data_structure",
                    severity="major",
                    category="structure",
                    message="Data field should be object or array",
                    suggestion="Structure data as JSON object or array",
                    performance_impact="Medium - parsing complexity",
                    cost_impact="Low - slight processing overhead"
                ))
                score -= 15
        
        # Check category-specific required fields
        category_fields = self.PM33_RESPONSE_STANDARDS["required_fields"].get(response_category, [])
        data_content = str(response_data.get("data", "")).lower()
        
        for required_field in category_fields:
            if required_field.lower() not in data_content:
                violations.append(ResponseViolation(
                    rule_id="missing_category_field",
                    severity="major",
                    category="structure",
                    message=f"Missing {response_category} field: {required_field}",
                    suggestion=f"Add {required_field} to {response_category} response",
                    performance_impact="Medium - incomplete data",
                    cost_impact="High - may require additional API calls"
                ))
                score -= 10
        
        return max(0, score), violations
    
    def _evaluate_content(self, response_data: Dict[str, Any], response_category: str) -> Tuple[float, List[ResponseViolation]]:
        """Evaluate response content quality"""
        violations = []
        score = 100.0
        
        data = response_data.get("data", {})
        data_str = str(data)
        
        # Check for empty responses
        if not data or (isinstance(data, (list, dict)) and len(data) == 0):
            violations.append(ResponseViolation(
                rule_id="empty_response",
                severity="critical",
                category="content",
                message="Response contains no data",
                suggestion="Ensure response includes relevant data or proper empty state handling",
                performance_impact="High - user confusion",
                cost_impact="Medium - wasted API call"
            ))
            score -= 30
            return max(0, score), violations
        
        # Content quality checks based on category
        if response_category == ResponseCategory.STRATEGIC_ANALYSIS.value:
            if len(data_str) < 100:
                violations.append(ResponseViolation(
                    rule_id="insufficient_analysis",
                    severity="major",
                    category="content",
                    message="Strategic analysis too brief (< 100 chars)",
                    suggestion="Provide comprehensive analysis with reasoning",
                    performance_impact="High - poor user experience",
                    cost_impact="High - users may retry or seek alternatives"
                ))
                score -= 25
            
            # Check for confidence indicators
            if not any(term in data_str.lower() for term in ['confidence', 'probability', 'certainty']):
                violations.append(ResponseViolation(
                    rule_id="missing_confidence",
                    severity="major",
                    category="content",
                    message="Missing confidence indicators in strategic analysis",
                    suggestion="Add confidence scores or probability indicators",
                    performance_impact="Medium - reduces decision quality",
                    cost_impact="Medium - users may seek additional validation"
                ))
                score -= 15
        
        elif response_category == ResponseCategory.FRAMEWORK_CALCULATION.value:
            # Check for score and interpretation
            if not any(term in data_str.lower() for term in ['score', 'result', 'calculation']):
                violations.append(ResponseViolation(
                    rule_id="missing_calculation_result",
                    severity="critical",
                    category="content", 
                    message="Framework calculation missing score or result",
                    suggestion="Include calculated score and interpretation",
                    performance_impact="High - incomplete calculation",
                    cost_impact="High - users cannot make decisions"
                ))
                score -= 30
        
        # Check for actionable insights
        if not any(term in data_str.lower() for term in ['action', 'next', 'recommend', 'suggest']):
            violations.append(ResponseViolation(
                rule_id="missing_actionable_insights",
                severity="minor",
                category="content",
                message="Response lacks actionable insights or next steps",
                suggestion="Include specific recommendations or next actions",
                performance_impact="Medium - users unsure of next steps",
                cost_impact="Low - slight user friction"
            ))
            score -= 10
        
        return max(0, score), violations
    
    def _evaluate_pm33_compliance(self, response_data: Dict[str, Any], response_category: str) -> Tuple[float, List[ResponseViolation]]:
        """Evaluate PM33 platform compliance"""
        violations = []
        score = 100.0
        
        content = str(response_data).lower()
        
        # PM33 branding and context
        pm33_indicators = ['pm33', 'pmo', 'transformation', 'strategic', 'framework']
        if not any(indicator in content for indicator in pm33_indicators):
            violations.append(ResponseViolation(
                rule_id="missing_pm33_context",
                severity="minor",
                category="compliance",
                message="Response lacks PM33 context or branding",
                suggestion="Include PM33-specific context or terminology",
                performance_impact="Low - minor branding issue",
                cost_impact="Low - slight brand inconsistency"
            ))
            score -= 5
        
        # Timestamp compliance
        if "timestamp" not in response_data:
            violations.append(ResponseViolation(
                rule_id="missing_timestamp",
                severity="major",
                category="compliance",
                message="Response missing timestamp",
                suggestion="Add ISO timestamp for tracking and debugging",
                performance_impact="Medium - debugging difficulty",
                cost_impact="Medium - support overhead"
            ))
            score -= 15
        
        # PMO transformation alignment
        if response_category in [ResponseCategory.STRATEGIC_ANALYSIS.value, ResponseCategory.PMO_METRICS.value]:
            transformation_terms = ['capability', 'improvement', 'efficiency', 'transformation']
            if not any(term in content for term in transformation_terms):
                violations.append(ResponseViolation(
                    rule_id="missing_transformation_alignment",
                    severity="major",
                    category="compliance",
                    message="Response not aligned with PMO transformation goals",
                    suggestion="Include PMO transformation context and capability improvement metrics",
                    performance_impact="High - misaligned with product vision",
                    cost_impact="High - reduces product value proposition"
                ))
                score -= 20
        
        return max(0, score), violations
    
    def _evaluate_performance(self, metrics: ResponseMetrics, response_category: str) -> Tuple[float, List[ResponseViolation]]:
        """Evaluate performance characteristics"""
        violations = []
        score = 100.0
        
        # Get performance targets for category
        targets = self.PM33_RESPONSE_STANDARDS["performance_targets"].get(
            response_category, 
            {"max_size_kb": 25, "max_time_ms": 5000}
        )
        
        # Response size evaluation
        size_kb = metrics.response_size_bytes / 1024
        if size_kb > targets["max_size_kb"]:
            severity = "critical" if size_kb > targets["max_size_kb"] * 2 else "major"
            violations.append(ResponseViolation(
                rule_id="response_too_large",
                severity=severity,
                category="performance",
                message=f"Response size {size_kb:.1f}KB exceeds {targets['max_size_kb']}KB limit",
                suggestion="Implement pagination, compression, or field filtering",
                performance_impact="High - slow network transfer",
                cost_impact="High - increased bandwidth costs"
            ))
            score -= 25 if severity == "critical" else 15
        
        # Response time evaluation
        if metrics.response_time_ms > targets["max_time_ms"]:
            severity = "critical" if metrics.response_time_ms > targets["max_time_ms"] * 2 else "major"
            violations.append(ResponseViolation(
                rule_id="response_too_slow",
                severity=severity,
                category="performance",
                message=f"Response time {metrics.response_time_ms:.0f}ms exceeds {targets['max_time_ms']}ms limit",
                suggestion="Optimize database queries, add caching, or improve algorithm efficiency",
                performance_impact="High - poor user experience",
                cost_impact="Medium - higher server costs"
            ))
            score -= 30 if severity == "critical" else 20
        
        # JSON complexity evaluation
        if metrics.nested_depth > 7:
            violations.append(ResponseViolation(
                rule_id="json_too_complex",
                severity="minor",
                category="performance",
                message=f"JSON nesting depth {metrics.nested_depth} may impact parsing performance",
                suggestion="Flatten JSON structure or break into multiple endpoints",
                performance_impact="Medium - parsing overhead",
                cost_impact="Low - slight client CPU impact"
            ))
            score -= 10
        
        # Large arrays check
        large_arrays = [size for size in metrics.array_sizes if size > 100]
        if large_arrays:
            violations.append(ResponseViolation(
                rule_id="large_arrays",
                severity="major",
                category="performance",
                message=f"Large arrays found (max: {max(large_arrays)} items)",
                suggestion="Implement pagination for arrays > 100 items",
                performance_impact="High - memory usage and parsing time",
                cost_impact="Medium - increased processing costs"
            ))
            score -= 15
        
        return max(0, score), violations
    
    def _evaluate_security(self, response_data: Dict[str, Any]) -> Tuple[float, List[ResponseViolation]]:
        """Evaluate security aspects of response"""
        violations = []
        score = 100.0
        
        content = str(response_data).lower()
        
        # Check for potential sensitive data patterns
        sensitive_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email addresses'),
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN patterns'),
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', 'credit card patterns'),
            (r'password.*[:=]\s*["\'][^"\']+["\']', 'password fields'),
            (r'api[_-]?key.*[:=]\s*["\'][^"\']+["\']', 'API keys'),
            (r'secret.*[:=]\s*["\'][^"\']+["\']', 'secret fields')
        ]
        
        for pattern, description in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(ResponseViolation(
                    rule_id="potential_sensitive_data",
                    severity="critical",
                    category="security",
                    message=f"Response may contain {description}",
                    suggestion=f"Remove or mask {description} from API responses",
                    performance_impact="Low - no performance impact",
                    cost_impact="Critical - potential security breach"
                ))
                score -= 40
        
        # Check for debug information in production
        debug_indicators = ['debug', 'trace', 'stack', 'error_details', 'sql', 'query']
        if any(indicator in content for indicator in debug_indicators):
            violations.append(ResponseViolation(
                rule_id="debug_information_leak",
                severity="major",
                category="security",
                message="Response contains debug information",
                suggestion="Remove debug information from production responses",
                performance_impact="Low - no performance impact", 
                cost_impact="High - potential information disclosure"
            ))
            score -= 20
        
        return max(0, score), violations
    
    def _calculate_overall_score(self, structure: float, content: float, compliance: float, 
                               performance: float, security: float) -> float:
        """Calculate weighted overall score"""
        weights = {
            'structure': 0.25,
            'content': 0.30,
            'compliance': 0.15,
            'performance': 0.20,
            'security': 0.10
        }
        
        overall = (
            structure * weights['structure'] +
            content * weights['content'] +
            compliance * weights['compliance'] +
            performance * weights['performance'] +
            security * weights['security']
        )
        
        return round(overall, 1)
    
    def _calculate_performance_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 95:
            return PerformanceGrade.EXCELLENT.value
        elif score >= 85:
            return PerformanceGrade.GOOD.value
        elif score >= 75:
            return PerformanceGrade.ACCEPTABLE.value
        elif score >= 65:
            return PerformanceGrade.NEEDS_IMPROVEMENT.value
        elif score >= 50:
            return PerformanceGrade.POOR.value
        else:
            return PerformanceGrade.FAILING.value
    
    def _generate_optimization_suggestions(self, violations: List[ResponseViolation], 
                                         metrics: ResponseMetrics, response_category: str) -> List[str]:
        """Generate specific optimization suggestions"""
        suggestions = []
        
        # Suggestions based on violations
        critical_violations = [v for v in violations if v.severity == "critical"]
        if critical_violations:
            suggestions.append(f"CRITICAL: Fix {len(critical_violations)} critical issues immediately")
        
        # Performance optimizations
        if metrics.response_size_bytes > 50000:  # >50KB
            suggestions.append("Consider implementing response compression (gzip)")
            suggestions.append("Implement field selection to reduce response size")
        
        if metrics.nested_depth > 5:
            suggestions.append("Flatten JSON structure to reduce parsing complexity")
        
        if max(metrics.array_sizes) > 100 if metrics.array_sizes else 0:
            suggestions.append("Implement pagination for large data arrays")
        
        # Caching opportunities
        if metrics.cache_hit_possible:
            suggestions.append("Implement response caching with appropriate TTL")
        
        # Category-specific suggestions
        if response_category == ResponseCategory.STRATEGIC_ANALYSIS.value:
            suggestions.append("Stream long strategic analyses to improve perceived performance")
            suggestions.append("Provide confidence intervals for all recommendations")
        
        elif response_category == ResponseCategory.FRAMEWORK_CALCULATION.value:
            suggestions.append("Cache framework calculations for common input combinations")
            suggestions.append("Provide real-time calculation updates for interactive inputs")
        
        return suggestions
    
    def _analyze_cost_optimization(self, response_data: Dict[str, Any], metrics: ResponseMetrics) -> Dict[str, Any]:
        """Analyze cost optimization opportunities"""
        optimizations = {
            "potential_savings": 0.0,
            "optimization_opportunities": []
        }
        
        # Caching savings
        if metrics.cache_hit_possible:
            cache_savings = 0.15  # Assume 15% cost reduction with caching
            optimizations["potential_savings"] += cache_savings
            optimizations["optimization_opportunities"].append({
                "type": "caching",
                "savings_percent": cache_savings * 100,
                "description": "Implement response caching for repeated queries"
            })
        
        # Compression savings
        if metrics.response_size_bytes > 10000 and metrics.compression_ratio < 0.7:
            compression_savings = 0.25  # 25% bandwidth cost reduction
            optimizations["potential_savings"] += compression_savings
            optimizations["optimization_opportunities"].append({
                "type": "compression",
                "savings_percent": compression_savings * 100,
                "description": "Enable gzip compression for responses > 10KB"
            })
        
        # Pagination savings
        if max(metrics.array_sizes) > 50 if metrics.array_sizes else 0:
            pagination_savings = 0.40  # 40% cost reduction through pagination
            optimizations["potential_savings"] += pagination_savings
            optimizations["optimization_opportunities"].append({
                "type": "pagination", 
                "savings_percent": pagination_savings * 100,
                "description": "Implement pagination to reduce response sizes"
            })
        
        return optimizations
    
    def _compare_against_benchmarks(self, metrics: ResponseMetrics, response_category: str) -> Dict[str, float]:
        """Compare against industry benchmarks"""
        comparison = {}
        
        # Response time comparison
        time_ms = metrics.response_time_ms
        if time_ms <= self.INDUSTRY_BENCHMARKS["response_time"]["excellent"]:
            comparison["response_time_percentile"] = 95.0
        elif time_ms <= self.INDUSTRY_BENCHMARKS["response_time"]["good"]:
            comparison["response_time_percentile"] = 80.0
        elif time_ms <= self.INDUSTRY_BENCHMARKS["response_time"]["acceptable"]:
            comparison["response_time_percentile"] = 60.0
        else:
            comparison["response_time_percentile"] = 30.0
        
        # Response size comparison
        size_kb = metrics.response_size_bytes / 1024
        if size_kb <= self.INDUSTRY_BENCHMARKS["response_size"]["excellent"]:
            comparison["response_size_percentile"] = 95.0
        elif size_kb <= self.INDUSTRY_BENCHMARKS["response_size"]["good"]:
            comparison["response_size_percentile"] = 80.0
        elif size_kb <= self.INDUSTRY_BENCHMARKS["response_size"]["acceptable"]:
            comparison["response_size_percentile"] = 60.0
        else:
            comparison["response_size_percentile"] = 30.0
        
        # JSON complexity comparison
        if metrics.nested_depth <= self.INDUSTRY_BENCHMARKS["json_depth"]["excellent"]:
            comparison["complexity_percentile"] = 95.0
        elif metrics.nested_depth <= self.INDUSTRY_BENCHMARKS["json_depth"]["good"]:
            comparison["complexity_percentile"] = 80.0
        elif metrics.nested_depth <= self.INDUSTRY_BENCHMARKS["json_depth"]["acceptable"]:
            comparison["complexity_percentile"] = 60.0
        else:
            comparison["complexity_percentile"] = 30.0
        
        return comparison
    
    # ============ HELPER METHODS ============
    
    def _calculate_nested_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of JSON structure"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._calculate_nested_depth(value, current_depth + 1) 
                      for value in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._calculate_nested_depth(item, current_depth + 1) 
                      for item in data)
        else:
            return current_depth
    
    def _find_array_sizes(self, data: Any) -> List[int]:
        """Find sizes of all arrays in the data structure"""
        sizes = []
        
        if isinstance(data, dict):
            for value in data.values():
                sizes.extend(self._find_array_sizes(value))
        elif isinstance(data, list):
            sizes.append(len(data))
            for item in data:
                sizes.extend(self._find_array_sizes(item))
        
        return sizes
    
    def _find_redundant_fields(self, data: Any, seen_keys: set = None) -> List[str]:
        """Find potentially redundant field names"""
        if seen_keys is None:
            seen_keys = set()
        
        redundant = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key in seen_keys:
                    redundant.append(key)
                else:
                    seen_keys.add(key)
                redundant.extend(self._find_redundant_fields(value, seen_keys.copy()))
        elif isinstance(data, list):
            for item in data:
                redundant.extend(self._find_redundant_fields(item, seen_keys.copy()))
        
        return redundant
    
    def _assess_cache_potential(self, response_data: Dict[str, Any]) -> bool:
        """Assess if response could benefit from caching"""
        # Look for indicators that data is relatively static
        content = str(response_data).lower()
        
        # Static content indicators
        static_indicators = ['configuration', 'settings', 'metadata', 'constants']
        has_static_content = any(indicator in content for indicator in static_indicators)
        
        # Dynamic content indicators
        dynamic_indicators = ['timestamp', 'current_time', 'now', 'random', 'session']
        has_dynamic_content = any(indicator in content for indicator in dynamic_indicators)
        
        # Framework calculations are cacheable if inputs are provided
        framework_indicators = ['rice', 'ice', 'score', 'calculation']
        has_framework_calc = any(indicator in content for indicator in framework_indicators)
        
        return (has_static_content or has_framework_calc) and not has_dynamic_content
    
    def _check_for_sensitive_data(self, response_data: Dict[str, Any]) -> bool:
        """Check if response contains sensitive data patterns"""
        content = str(response_data)
        
        sensitive_patterns = [
            r'password', r'secret', r'key.*[A-Za-z0-9]{20,}', 
            r'token.*[A-Za-z0-9]{20,}', r'api.*key',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in sensitive_patterns)
    
    def _store_evaluation(self, evaluation: APIResponseEvaluation) -> None:
        """Store evaluation for historical tracking"""
        endpoint = evaluation.endpoint
        
        if endpoint not in self.historical_data:
            self.historical_data[endpoint] = HistoricalPerformance(endpoint=endpoint)
        
        historical = self.historical_data[endpoint]
        historical.evaluations.append(evaluation)
        historical.last_updated = evaluation.timestamp
        
        # Calculate average score
        if historical.evaluations:
            historical.average_score = sum(e.overall_score for e in historical.evaluations) / len(historical.evaluations)
        
        # Keep only last 100 evaluations per endpoint
        if len(historical.evaluations) > 100:
            historical.evaluations = historical.evaluations[-100:]
    
    def _calculate_grade_distribution(self, evaluations: List[APIResponseEvaluation]) -> Dict[str, int]:
        """Calculate distribution of performance grades"""
        distribution = {}
        for evaluation in evaluations:
            grade = evaluation.performance_grade
            distribution[grade] = distribution.get(grade, 0) + 1
        return distribution
    
    def _identify_common_issues(self, evaluations: List[APIResponseEvaluation]) -> List[Dict[str, Any]]:
        """Identify most common issues across evaluations"""
        issue_counts = {}
        
        for evaluation in evaluations:
            for violation in evaluation.violations:
                rule = violation.rule_id
                issue_counts[rule] = issue_counts.get(rule, 0) + 1
        
        # Sort by frequency and return top 5
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [
            {"issue": issue, "count": count, "percentage": (count / len(evaluations)) * 100}
            for issue, count in common_issues
        ]
    
    def _calculate_cost_savings_opportunities(self, evaluations: List[APIResponseEvaluation]) -> Dict[str, Any]:
        """Calculate aggregated cost savings opportunities"""
        total_savings = 0.0
        opportunities = {}
        
        for evaluation in evaluations:
            for opportunity in evaluation.cost_optimization.get("optimization_opportunities", []):
                opt_type = opportunity["type"]
                if opt_type not in opportunities:
                    opportunities[opt_type] = {"count": 0, "total_savings_percent": 0.0}
                
                opportunities[opt_type]["count"] += 1
                opportunities[opt_type]["total_savings_percent"] += opportunity["savings_percent"]
        
        # Calculate averages
        for opt_type, data in opportunities.items():
            data["average_savings_percent"] = data["total_savings_percent"] / data["count"]
        
        return opportunities
    
    def _identify_performance_improvements(self, evaluations: List[APIResponseEvaluation]) -> List[str]:
        """Identify top performance improvement opportunities"""
        improvements = []
        
        # Count performance-related violations
        perf_violations = {}
        for evaluation in evaluations:
            for violation in evaluation.violations:
                if violation.category == "performance":
                    perf_violations[violation.rule_id] = perf_violations.get(violation.rule_id, 0) + 1
        
        # Sort by frequency
        top_violations = sorted(perf_violations.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for rule_id, count in top_violations:
            if rule_id == "response_too_large":
                improvements.append(f"Reduce response sizes - affects {count} endpoints")
            elif rule_id == "response_too_slow":
                improvements.append(f"Improve response times - affects {count} endpoints")
            elif rule_id == "large_arrays":
                improvements.append(f"Implement pagination - affects {count} endpoints")
        
        return improvements
    
    def _generate_priority_recommendations(self, evaluations: List[APIResponseEvaluation]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_count = sum(len([v for v in e.violations if v.severity == "critical"]) for e in evaluations)
        if critical_count > 0:
            recommendations.append(f"URGENT: Fix {critical_count} critical security/functionality issues")
        
        # Performance improvements
        slow_responses = len([e for e in evaluations if e.performance_score < 70])
        if slow_responses > len(evaluations) * 0.3:  # >30% of endpoints
            recommendations.append(f"Performance priority: {slow_responses} endpoints need optimization")
        
        # Compliance improvements
        low_compliance = len([e for e in evaluations if e.pm33_compliance_score < 80])
        if low_compliance > 0:
            recommendations.append(f"Brand alignment: {low_compliance} endpoints need PM33 compliance review")
        
        return recommendations
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from list of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = list(range(len(values)))
        avg_x = sum(x) / len(x)
        avg_y = sum(values) / len(values)
        
        slope = sum((x[i] - avg_x) * (values[i] - avg_y) for i in range(len(values))) / sum((x[i] - avg_x) ** 2 for i in range(len(values)))
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "degrading"
        else:
            return "stable"
    
    def _get_recent_issues(self, evaluations: List[APIResponseEvaluation]) -> List[str]:
        """Get recent issues from evaluations"""
        recent_issues = []
        
        # Get issues from most recent evaluation
        if evaluations:
            latest = evaluations[-1]
            for violation in latest.violations:
                if violation.severity in ["critical", "major"]:
                    recent_issues.append(f"{violation.severity.upper()}: {violation.message}")
        
        return recent_issues[:5]  # Return top 5
    
    def _get_improvement_suggestions(self, evaluations: List[APIResponseEvaluation]) -> List[str]:
        """Get improvement suggestions based on recent evaluations"""
        suggestions = []
        
        # Analyze patterns in recent evaluations
        avg_score = sum(e.overall_score for e in evaluations) / len(evaluations)
        
        if avg_score < 80:
            suggestions.append("Focus on structural improvements and PM33 compliance")
        
        # Performance suggestions
        avg_perf = sum(e.performance_score for e in evaluations) / len(evaluations) if evaluations else 0
        if avg_perf < 70:
            suggestions.append("Implement caching and response optimization")
        
        return suggestions
    
    def load_historical_data(self) -> None:
        """Load historical performance data"""
        # In production, this would load from database
        # For now, initialize empty
        pass
    
    def save_historical_data(self) -> None:
        """Save historical performance data"""
        # In production, this would save to database
        pass

def main():
    """Command line interface for API Response Evaluator"""
    parser = argparse.ArgumentParser(description='PM33 API Response Evaluator')
    parser.add_argument('--endpoint', type=str,
                       help='API endpoint to evaluate')
    parser.add_argument('--analyze-file', type=str,
                       help='JSON file containing API response to analyze')
    parser.add_argument('--response-time', type=float, default=None,
                       help='Response time in milliseconds')
    parser.add_argument('--category', type=str,
                       choices=[c.value for c in ResponseCategory],
                       help='Response category for evaluation')
    parser.add_argument('--monitor', type=str,
                       help='Monitor endpoint performance over time')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days for monitoring analysis')
    parser.add_argument('--export', type=str, default='pm33_api_evaluation_report.json',
                       help='Export evaluation report to JSON file')
    
    args = parser.parse_args()
    
    evaluator = PM33APIResponseEvaluator()
    
    if args.monitor:
        # Monitor endpoint performance
        print("📊 PM33 API RESPONSE PERFORMANCE MONITORING")
        print("=" * 60)
        
        performance_report = evaluator.monitor_endpoint_performance(args.monitor, args.days)
        
        if "error" in performance_report:
            print(f"❌ {performance_report['error']}")
            return
        
        print(f"\n🎯 Endpoint: {performance_report['endpoint']}")
        print(f"📅 Period: {performance_report['period_days']} days")
        print(f"📊 Total Evaluations: {performance_report['total_evaluations']}")
        
        perf_trend = performance_report['performance_trend']
        print(f"\n📈 Performance Trend:")
        print(f"   Average Score: {perf_trend['average_score']:.1f}%")
        print(f"   Trend: {perf_trend['score_trend']}")
        print(f"   Best Score: {perf_trend['best_score']:.1f}%")
        print(f"   Worst Score: {perf_trend['worst_score']:.1f}%")
        
        if performance_report['recent_issues']:
            print(f"\n⚠️ Recent Issues:")
            for issue in performance_report['recent_issues']:
                print(f"   • {issue}")
        
        if performance_report['improvement_suggestions']:
            print(f"\n💡 Improvement Suggestions:")
            for suggestion in performance_report['improvement_suggestions']:
                print(f"   • {suggestion}")
    
    elif args.analyze_file:
        # Analyze response from file
        print("🔍 PM33 API RESPONSE EVALUATION")
        print("=" * 60)
        
        try:
            with open(args.analyze_file, 'r') as f:
                response_data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
        
        endpoint = args.endpoint or args.analyze_file
        evaluation = evaluator.evaluate_response(
            endpoint, response_data, args.response_time, args.category
        )
        
        print(f"\n🎯 Endpoint: {evaluation.endpoint}")
        print(f"📊 Overall Score: {evaluation.overall_score:.1f}% ({evaluation.performance_grade})")
        print(f"🏗️ Structure: {evaluation.structure_score:.1f}%")
        print(f"📝 Content: {evaluation.content_score:.1f}%")  
        print(f"🎯 PM33 Compliance: {evaluation.pm33_compliance_score:.1f}%")
        print(f"⚡ Performance: {evaluation.performance_score:.1f}%")
        print(f"🔒 Security: {evaluation.security_score:.1f}%")
        
        if evaluation.violations:
            print(f"\n❌ Issues Found ({len(evaluation.violations)}):")
            for violation in evaluation.violations[:5]:  # Show top 5
                print(f"   [{violation.severity.upper()}] {violation.message}")
                print(f"   💡 {violation.suggestion}")
        
        if evaluation.optimization_suggestions:
            print(f"\n💡 Optimization Suggestions:")
            for suggestion in evaluation.optimization_suggestions:
                print(f"   • {suggestion}")
        
        if evaluation.cost_optimization.get("optimization_opportunities"):
            print(f"\n💰 Cost Optimization Opportunities:")
            for opt in evaluation.cost_optimization["optimization_opportunities"]:
                print(f"   • {opt['description']} ({opt['savings_percent']:.1f}% savings)")
        
        # Benchmark comparison
        if evaluation.benchmark_comparison:
            print(f"\n🏆 Industry Benchmark Comparison:")
            for metric, percentile in evaluation.benchmark_comparison.items():
                print(f"   {metric.replace('_', ' ').title()}: {percentile:.0f}th percentile")
        
        # Export report
        if args.export:
            export_data = {
                "evaluation": {
                    "endpoint": evaluation.endpoint,
                    "timestamp": evaluation.timestamp,
                    "overall_score": evaluation.overall_score,
                    "performance_grade": evaluation.performance_grade,
                    "violations": [
                        {
                            "rule_id": v.rule_id,
                            "severity": v.severity,
                            "message": v.message,
                            "suggestion": v.suggestion
                        } for v in evaluation.violations
                    ],
                    "optimization_suggestions": evaluation.optimization_suggestions,
                    "cost_optimization": evaluation.cost_optimization,
                    "benchmark_comparison": evaluation.benchmark_comparison
                }
            }
            
            with open(args.export, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"\n📊 Evaluation report exported to: {args.export}")
    
    else:
        print("🔍 PM33 API RESPONSE EVALUATOR")
        print("=" * 60)
        print("Available commands:")
        print("  --analyze-file FILE     Analyze API response from JSON file")
        print("  --monitor ENDPOINT      Monitor endpoint performance over time")
        print("  --endpoint NAME         Specify endpoint name for analysis")
        print("  --category TYPE         Specify response category")
        print("  --response-time MS      Specify response time in milliseconds")
        print("  --days N               Number of days for monitoring (default: 7)")
        print("\nExample:")
        print("  python pm33_api_response_evaluator.py --analyze-file response.json --endpoint /api/strategic/analyze")

if __name__ == "__main__":
    main()