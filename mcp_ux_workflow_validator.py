#!/usr/bin/env python3
"""
PM33 UX Workflow Validator
Enforces user experience workflows and interaction patterns
Usage: python mcp_ux_workflow_validator.py [component_path] [--workflow-type]
"""

import os
import re
import json
import glob
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UXViolation:
    """Represents a UX workflow violation"""
    file_path: str
    line_number: int
    rule_id: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: str
    pattern: str = ""
    ux_impact: str = ""

@dataclass
class UXValidationReport:
    """Complete UX validation report"""
    component_path: str
    timestamp: str
    total_violations: int
    workflow_type: str = ""
    errors: List[UXViolation] = field(default_factory=list)
    warnings: List[UXViolation] = field(default_factory=list)
    info: List[UXViolation] = field(default_factory=list)
    ux_score: float = 0.0
    passed: bool = False

class PM33UXWorkflowValidator:
    """
    PM33 UX Workflow Validator
    Enforces UX best practices and workflow patterns with zero tolerance
    """
    
    # UX Workflow Patterns (Enhanced with PM-specific patterns)
    WORKFLOW_PATTERNS = {
        'form_submission': [
            'show_loading_state',
            'disable_submit_button', 
            'show_success_or_error',
            'provide_next_action'
        ],
        'data_loading': [
            'show_skeleton',
            'handle_error_state',
            'show_empty_state',
            'provide_retry_mechanism'
        ],
        'user_action': [
            'immediate_feedback',
            'optimistic_update',
            'rollback_on_error',
            'confirm_destructive_actions'
        ],
        # PM-SPECIFIC WORKFLOW PATTERNS
        'strategic_analysis': [
            'show_framework_selection',
            'display_confidence_score',
            'show_reasoning_chain',
            'provide_alternative_frameworks',
            'show_success_probability',
            'display_risk_factors',
            'provide_next_actions',
            'show_progress_indicator'
        ],
        'framework_application': [
            'show_framework_explanation',
            'display_input_requirements',
            'validate_input_ranges',
            'show_calculation_transparency',
            'provide_context_help',
            'show_score_interpretation'
        ],
        'decision_validation': [
            'show_multiple_perspectives',
            'display_confidence_metrics',
            'provide_sensitivity_analysis',
            'show_implementation_timeline',
            'display_resource_requirements',
            'provide_rollback_plan'
        ],
        'pmo_transformation': [
            'show_capability_progress',
            'display_transformation_metrics',
            'provide_milestone_tracking',
            'show_skill_development',
            'display_time_savings',
            'provide_next_level_guidance'
        ],
        'competitive_intelligence': [
            'show_threat_assessment',
            'display_opportunity_matrix',
            'provide_response_options',
            'show_market_positioning',
            'display_differentiation_score',
            'provide_strategic_recommendations'
        ],
        'resource_optimization': [
            'show_cost_breakdown',
            'display_roi_projections',
            'provide_scenario_comparison',
            'show_risk_mitigation',
            'display_timeline_impact',
            'provide_optimization_suggestions'
        ]
    }
    
    # Cognitive Load Limits (Enhanced for PM workflows)
    COGNITIVE_LIMITS = {
        'choices_per_screen': 7,        # Miller's Law
        'form_fields_per_page': 5,      # Reduce overwhelm
        'menu_items': 7,                # Navigation clarity
        'onboarding_steps': 3,          # Completion rate
        'error_messages_shown': 3,      # Avoid error blindness
        # PM-SPECIFIC COGNITIVE LIMITS
        'frameworks_shown_simultaneously': 4,  # Max frameworks to display at once
        'strategic_options_per_decision': 5,   # Max strategic options to present
        'risk_factors_displayed': 6,           # Max risk factors before grouping
        'kpis_on_dashboard': 8,               # Max KPIs on single dashboard view
        'competitive_threats_shown': 4,        # Max threats before overwhelming
        'resource_scenarios': 3,              # Max scenarios for comparison
        'pmo_capabilities_tracked': 6,         # Max capabilities to track simultaneously
        'confidence_indicators': 1,            # Single confidence score per analysis
        'framework_steps': 5,                 # Max steps in framework application
        'transformation_milestones': 4,       # Max milestones visible at once
    }
    
    # Performance UX Requirements (Enhanced for PM workflows)
    PERFORMANCE_UX = {
        'search': {
            'max_response_time': 200,
            'loading_indicator_delay': 100,
            'debounce_delay': 300,
            'optimistic_update': False
        },
        'form_submit': {
            'max_response_time': 3000,
            'loading_indicator_delay': 0,
            'debounce_delay': 0,
            'optimistic_update': True
        },
        'navigation': {
            'max_response_time': 100,
            'loading_indicator_delay': 0,
            'debounce_delay': 0,
            'optimistic_update': True
        },
        # PM-SPECIFIC PERFORMANCE REQUIREMENTS
        'strategic_analysis': {
            'max_response_time': 10000,    # 10s for complex strategic analysis
            'loading_indicator_delay': 500, # Show thinking indicator after 0.5s
            'progress_updates': True,       # Show analysis progress
            'partial_results': True,        # Stream results as available
            'timeout_handling': True        # Graceful timeout with partial results
        },
        'framework_calculation': {
            'max_response_time': 2000,     # 2s for framework calculations (RICE, ICE)
            'loading_indicator_delay': 200, # Quick feedback for calculations
            'real_time_updates': True,      # Update scores as inputs change
            'validation_delay': 500,        # Validate inputs after 0.5s pause
            'optimistic_update': True
        },
        'competitive_intelligence': {
            'max_response_time': 15000,    # 15s for market analysis
            'loading_indicator_delay': 1000, # Allow time for data gathering
            'progress_stages': ['Gathering data', 'Analyzing competitors', 'Generating insights'],
            'partial_results': True,
            'cache_duration': 3600         # Cache results for 1 hour
        },
        'pmo_metrics': {
            'max_response_time': 5000,     # 5s for transformation metrics
            'loading_indicator_delay': 200,
            'real_time_updates': False,     # Batch update metrics
            'refresh_interval': 300,        # Auto-refresh every 5 minutes
            'optimistic_update': False
        },
        'resource_optimization': {
            'max_response_time': 8000,     # 8s for complex resource calculations
            'loading_indicator_delay': 500,
            'scenario_streaming': True,     # Stream scenario results
            'comparison_delay': 1000,       # Allow time to review scenarios
            'auto_save': True              # Auto-save optimization results
        }
    }
    
    # Critical User Journeys (Enhanced with PM-specific journeys)
    CRITICAL_JOURNEYS = {
        'onboarding': {
            'steps': ['welcome', 'setup', 'tutorial', 'first_action'],
            'max_steps': 3,
            'requirements': [
                'progress_indicator',
                'skip_option',
                'save_progress',
                'clear_value_proposition'
            ]
        },
        'checkout': {
            'steps': ['cart', 'shipping', 'payment', 'confirmation'],
            'max_steps': 4,
            'requirements': [
                'progress_bar',
                'back_navigation',
                'save_cart',
                'security_badges',
                'total_visible'
            ]
        },
        'error_recovery': {
            'steps': ['error_display', 'explanation', 'action'],
            'max_steps': 1,
            'requirements': [
                'clear_error_message',
                'why_it_happened',
                'how_to_fix',
                'retry_option',
                'contact_support'
            ]
        },
        # PM-SPECIFIC CRITICAL JOURNEYS
        'strategic_decision_making': {
            'steps': ['context_input', 'framework_selection', 'analysis_review', 'decision_confirmation'],
            'max_steps': 4,
            'requirements': [
                'clear_decision_question',
                'framework_explanation',
                'confidence_display',
                'reasoning_transparency',
                'next_actions_provided',
                'save_decision_rationale'
            ]
        },
        'pmo_capability_assessment': {
            'steps': ['current_state', 'capability_gaps', 'development_plan', 'progress_tracking'],
            'max_steps': 4,
            'requirements': [
                'skill_matrix_display',
                'gap_identification',
                'actionable_recommendations',
                'progress_visualization',
                'milestone_tracking'
            ]
        },
        'framework_application': {
            'steps': ['framework_selection', 'data_input', 'calculation_review', 'result_interpretation'],
            'max_steps': 4,
            'requirements': [
                'framework_education',
                'input_validation',
                'calculation_transparency',
                'score_interpretation',
                'comparison_options',
                'save_analysis'
            ]
        },
        'competitive_analysis': {
            'steps': ['competitor_selection', 'data_gathering', 'analysis_review', 'strategic_response'],
            'max_steps': 4,
            'requirements': [
                'competitor_context',
                'data_source_transparency',
                'threat_prioritization',
                'response_options',
                'implementation_guidance'
            ]
        },
        'resource_optimization': {
            'steps': ['current_allocation', 'scenario_modeling', 'optimization_review', 'implementation_plan'],
            'max_steps': 4,
            'requirements': [
                'resource_visualization',
                'scenario_comparison',
                'roi_projections',
                'risk_assessment',
                'implementation_timeline'
            ]
        }
    }
    
    # Accessibility Requirements
    A11Y_REQUIREMENTS = {
        'keyboard_navigation': ['tabIndex', 'onKeyDown', 'aria-label'],
        'screen_reader': ['aria-label', 'aria-describedby', 'role', 'aria-live'],
        'focus_management': ['autoFocus', 'focus()', 'useRef', 'FocusTrap']
    }
    
    def __init__(self):
        self.violations = []
        
    def validate_component(self, component_path: str, workflow_type: str = None) -> UXValidationReport:
        """Main validation method"""
        self.violations = []
        
        # Check if file exists and is valid
        if not os.path.exists(component_path):
            return self._create_error_report(component_path, "File not found")
        
        if not self._is_ui_component_file(component_path):
            return self._create_success_report(component_path, "Not a UI component file")
        
        # Read file content
        try:
            with open(component_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
        except Exception as e:
            return self._create_error_report(component_path, f"Failed to read file: {str(e)}")
        
        # Run all UX validation checks
        self._check_loading_states(content)
        self._check_error_handling(content)
        self._check_form_workflows(content)
        self._check_accessibility_patterns(content)
        self._check_cognitive_load(content)
        self._check_user_feedback(content)
        self._check_navigation_patterns(content)
        self._check_performance_patterns(content, workflow_type)
        
        if workflow_type:
            self._check_specific_workflow(content, workflow_type)
        
        # Generate final report
        return self._generate_report(component_path, workflow_type or 'general')
    
    def _check_loading_states(self, content: str) -> None:
        """Ensure proper loading states for async operations"""
        lines = content.split('\n')
        
        # Check for async operations without loading states
        async_patterns = [
            r'await\s+\w+', r'\.then\(', r'fetch\(', r'axios\.',
            r'useQuery', r'useMutation', r'async\s+\w+'
        ]
        
        has_async = any(re.search(pattern, content, re.IGNORECASE) for pattern in async_patterns)
        
        if has_async:
            loading_patterns = [
                r'isLoading', r'isPending', r'loading', r'useState.*loading',
                r'Spinner', r'LoadingSpinner', r'CircularProgress', r'skeleton'
            ]
            
            has_loading_state = any(re.search(pattern, content, re.IGNORECASE) for pattern in loading_patterns)
            
            if not has_loading_state:
                self._add_violation(
                    rule_id="missing_loading_state",
                    severity="error",
                    message="Async operation missing loading state",
                    suggestion="Add loading state: const [isLoading, setIsLoading] = useState(false)",
                    ux_impact="Users don't know if action was received",
                    line_number=self._find_line_with_async(lines)
                )
            
            # Check if buttons are disabled during loading
            if 'button' in content.lower() and 'disabled' not in content.lower():
                self._add_violation(
                    rule_id="button_not_disabled_loading",
                    severity="error",
                    message="Buttons not disabled during loading state",
                    suggestion="Add disabled={isLoading} to prevent double submission",
                    ux_impact="Users can submit multiple times causing errors",
                    line_number=self._find_line_with_text(lines, "button")
                )
    
    def _check_error_handling(self, content: str) -> None:
        """Validate comprehensive error handling"""
        lines = content.split('\n')
        
        # Check for async operations
        has_async = any(pattern in content.lower() for pattern in ['await', 'fetch', 'axios', '.then('])
        
        if has_async:
            error_handling_checks = {
                'try_catch': r'try\s*\{.*catch',
                'error_state': r'error|Error',
                'user_feedback': r'toast|alert|notification|message',
                'retry_mechanism': r'retry|try.*again',
                'network_error': r'network|NetworkError|fetch.*error'
            }
            
            for check_name, pattern in error_handling_checks.items():
                if not re.search(pattern, content, re.IGNORECASE):
                    severity = "error" if check_name in ['try_catch', 'error_state'] else "warning"
                    self._add_violation(
                        rule_id=f"missing_{check_name}",
                        severity=severity,
                        message=f"Missing {check_name.replace('_', ' ')} in async operation",
                        suggestion=self._get_error_handling_suggestion(check_name),
                        ux_impact=self._get_error_impact(check_name),
                        line_number=self._find_line_with_async(lines)
                    )
    
    def _check_form_workflows(self, content: str) -> None:
        """Validate form submission workflows"""
        lines = content.split('\n')
        
        if 'form' in content.lower() or 'submit' in content.lower():
            form_requirements = {
                'validation': r'validate|error|invalid',
                'loading_state': r'isSubmitting|submitting|loading',
                'success_feedback': r'success|complete|submitted',
                'field_errors': r'error.*field|field.*error',
                'disabled_submit': r'disabled.*submit|submit.*disabled'
            }
            
            for req_name, pattern in form_requirements.items():
                if not re.search(pattern, content, re.IGNORECASE):
                    self._add_violation(
                        rule_id=f"form_missing_{req_name}",
                        severity="error",
                        message=f"Form missing {req_name.replace('_', ' ')}",
                        suggestion=self._get_form_suggestion(req_name),
                        ux_impact=f"Poor form experience - {req_name} needed",
                        line_number=self._find_line_with_text(lines, "form")
                    )
    
    def _check_accessibility_patterns(self, content: str) -> None:
        """Validate accessibility requirements"""
        lines = content.split('\n')
        
        # Check for interactive elements
        interactive_elements = ['button', 'input', 'select', 'textarea', 'a href']
        has_interactive = any(element in content.lower() for element in interactive_elements)
        
        if has_interactive:
            # Check keyboard navigation
            keyboard_patterns = ['tabIndex', 'onKeyDown', 'onKeyPress', 'aria-']
            has_keyboard_support = any(pattern in content for pattern in keyboard_patterns)
            
            if not has_keyboard_support:
                self._add_violation(
                    rule_id="missing_keyboard_navigation",
                    severity="error",
                    message="Interactive elements missing keyboard navigation",
                    suggestion="Add tabIndex and onKeyDown handlers, or aria-label attributes",
                    ux_impact="Keyboard users cannot navigate interface",
                    line_number=self._find_line_with_text(lines, "button")
                )
            
            # Check ARIA labels
            aria_patterns = ['aria-label', 'aria-describedby', 'aria-live', 'role=']
            has_aria = any(pattern in content for pattern in aria_patterns)
            
            if not has_aria:
                self._add_violation(
                    rule_id="missing_aria_labels",
                    severity="warning",
                    message="Interactive elements missing ARIA labels",
                    suggestion="Add aria-label or aria-describedby for screen readers",
                    ux_impact="Screen reader users cannot understand interface",
                    line_number=self._find_line_with_text(lines, "button")
                )
    
    def _check_cognitive_load(self, content: str) -> None:
        """Validate cognitive load limits"""
        lines = content.split('\n')
        
        # Count form fields
        input_pattern = r'<input|<select|<textarea'
        input_count = len(re.findall(input_pattern, content, re.IGNORECASE))
        
        if input_count > self.COGNITIVE_LIMITS['form_fields_per_page']:
            self._add_violation(
                rule_id="too_many_form_fields",
                severity="warning",
                message=f"Too many form fields: {input_count} (max: {self.COGNITIVE_LIMITS['form_fields_per_page']})",
                suggestion="Break form into multiple steps or use progressive disclosure",
                ux_impact="Users feel overwhelmed and abandon form",
                line_number=self._find_line_with_text(lines, "input")
            )
        
        # Count choices (buttons, links)
        choice_pattern = r'<button|<a\s+href'
        choice_count = len(re.findall(choice_pattern, content, re.IGNORECASE))
        
        if choice_count > self.COGNITIVE_LIMITS['choices_per_screen']:
            self._add_violation(
                rule_id="too_many_choices",
                severity="warning", 
                message=f"Too many choices: {choice_count} (max: {self.COGNITIVE_LIMITS['choices_per_screen']})",
                suggestion="Group related actions or use progressive disclosure",
                ux_impact="Decision paralysis - users cannot choose",
                line_number=self._find_line_with_text(lines, "button")
            )
        
        # Check information hierarchy
        heading_pattern = r'<h[1-6]'
        headings = re.findall(heading_pattern, content, re.IGNORECASE)
        
        if not headings and len(lines) > 50:  # Complex component without headings
            self._add_violation(
                rule_id="missing_information_hierarchy",
                severity="info",
                message="Complex component missing information hierarchy",
                suggestion="Add headings (h1-h6) to structure content",
                ux_impact="Users cannot scan and understand content structure",
                line_number=1
            )
    
    def _check_user_feedback(self, content: str) -> None:
        """Ensure immediate user feedback for all actions"""
        lines = content.split('\n')
        
        # Check for click handlers without immediate feedback
        click_pattern = r'onClick|handleClick|onSubmit'
        has_click_handlers = re.search(click_pattern, content, re.IGNORECASE)
        
        if has_click_handlers:
            feedback_patterns = [
                r'setState|setLoading|setSuccess|setError',
                r'toast|alert|notification',
                r'disabled|loading|pending'
            ]
            
            has_immediate_feedback = any(re.search(pattern, content, re.IGNORECASE) for pattern in feedback_patterns)
            
            if not has_immediate_feedback:
                self._add_violation(
                    rule_id="missing_immediate_feedback",
                    severity="error",
                    message="User actions missing immediate feedback",
                    suggestion="Add state change or visual feedback on click: setIsLoading(true)",
                    ux_impact="Users don't know if their action was registered",
                    line_number=self._find_line_with_text(lines, "onClick")
                )
    
    def _check_navigation_patterns(self, content: str) -> None:
        """Validate navigation UX patterns"""
        lines = content.split('\n')
        
        # Check for navigation components
        nav_patterns = ['nav', 'navigation', 'breadcrumb', 'menu']
        has_navigation = any(pattern in content.lower() for pattern in nav_patterns)
        
        if has_navigation:
            # Check for active states
            if 'active' not in content.lower() and 'current' not in content.lower():
                self._add_violation(
                    rule_id="missing_active_states",
                    severity="warning",
                    message="Navigation missing active state indicators",
                    suggestion="Add active/current state styling to show user location",
                    ux_impact="Users don't know where they are in the app",
                    line_number=self._find_line_with_text(lines, "nav")
                )
            
            # Check for back navigation in deep flows
            if 'back' not in content.lower() and 'breadcrumb' not in content.lower():
                self._add_violation(
                    rule_id="missing_back_navigation",
                    severity="info",
                    message="Consider adding back navigation for deep flows",
                    suggestion="Add back button or breadcrumbs for complex navigation",
                    ux_impact="Users may feel trapped in deep navigation flows",
                    line_number=self._find_line_with_text(lines, "nav")
                )
    
    def _check_performance_patterns(self, content: str, workflow_type: str) -> None:
        """Validate performance-related UX patterns"""
        lines = content.split('\n')
        
        if workflow_type == 'search':
            # Check for debouncing
            if 'input' in content.lower() and 'debounce' not in content.lower():
                self._add_violation(
                    rule_id="missing_search_debounce",
                    severity="error",
                    message="Search input missing debounce (300ms recommended)",
                    suggestion="Add useDebounce hook or setTimeout to reduce API calls",
                    ux_impact="Poor performance - too many API requests",
                    line_number=self._find_line_with_text(lines, "input")
                )
        
        # Check for skeleton screens vs spinners
        if 'loading' in content.lower() and 'skeleton' not in content.lower():
            if 'spinner' in content.lower() or 'circular' in content.lower():
                self._add_violation(
                    rule_id="prefer_skeleton_over_spinner",
                    severity="info",
                    message="Consider skeleton screens instead of spinners",
                    suggestion="Use skeleton screens to maintain layout and reduce perceived loading time",
                    ux_impact="Skeleton screens feel faster than spinners",
                    line_number=self._find_line_with_text(lines, "spinner")
                )
    
    def _check_specific_workflow(self, content: str, workflow_type: str) -> None:
        """Validate specific workflow patterns"""
        if workflow_type not in self.WORKFLOW_PATTERNS:
            return
            
        required_patterns = self.WORKFLOW_PATTERNS[workflow_type]
        lines = content.split('\n')
        
        pattern_checks = {
            # Original patterns
            'show_loading_state': r'loading|pending|isLoading',
            'disable_submit_button': r'disabled.*submit|submit.*disabled',
            'show_success_or_error': r'success|error|complete',
            'provide_next_action': r'next|continue|redirect|navigate',
            'show_skeleton': r'skeleton|placeholder',
            'handle_error_state': r'error|catch|fail',
            'show_empty_state': r'empty|no.*data|not.*found',
            'provide_retry_mechanism': r'retry|try.*again',
            'immediate_feedback': r'setState|setLoading|feedback',
            'optimistic_update': r'optimistic|immediate.*update',
            'rollback_on_error': r'rollback|revert|undo',
            'confirm_destructive_actions': r'confirm|are.*you.*sure|delete.*confirm',
            
            # PM-SPECIFIC PATTERN CHECKS
            # Strategic Analysis patterns
            'show_framework_selection': r'framework.*select|select.*framework|rice|ice|jtbd|okr',
            'display_confidence_score': r'confidence.*score|confidence.*\d+|probability.*\d+',
            'show_reasoning_chain': r'reasoning|rationale|because|analysis.*steps',
            'provide_alternative_frameworks': r'alternative|other.*framework|try.*different',
            'show_success_probability': r'success.*rate|probability|likely.*success',
            'display_risk_factors': r'risk|risks|potential.*issue|concern',
            'provide_next_actions': r'next.*step|action.*item|recommendation',
            'show_progress_indicator': r'progress|step.*\d+|analysis.*progress',
            
            # Framework Application patterns
            'show_framework_explanation': r'what.*is.*rice|framework.*help|explanation',
            'display_input_requirements': r'required|mandatory|must.*provide',
            'validate_input_ranges': r'between|range|min.*max|validation',
            'show_calculation_transparency': r'calculated|formula|score.*based',
            'provide_context_help': r'help|tooltip|what.*means|info',
            'show_score_interpretation': r'score.*means|interpret|high.*medium.*low',
            
            # Decision Validation patterns
            'show_multiple_perspectives': r'perspective|viewpoint|different.*angle',
            'display_confidence_metrics': r'confidence.*level|certainty|reliability',
            'provide_sensitivity_analysis': r'sensitivity|what.*if|scenario',
            'show_implementation_timeline': r'timeline|schedule|when.*complete',
            'display_resource_requirements': r'resource|effort|team.*size',
            'provide_rollback_plan': r'rollback|backup.*plan|if.*fails',
            
            # PMO Transformation patterns
            'show_capability_progress': r'capability|skill.*progress|improvement',
            'display_transformation_metrics': r'transformation|pmo.*metric|capability.*score',
            'provide_milestone_tracking': r'milestone|goal.*progress|achievement',
            'show_skill_development': r'skill.*develop|learn|training',
            'display_time_savings': r'time.*sav|efficiency|faster',
            'provide_next_level_guidance': r'next.*level|advance|improve.*further',
            
            # Competitive Intelligence patterns
            'show_threat_assessment': r'threat|competitor.*risk|market.*challenge',
            'display_opportunity_matrix': r'opportunity|market.*gap|advantage',
            'provide_response_options': r'response|strategy|counter|action',
            'show_market_positioning': r'position|market.*place|competitive',
            'display_differentiation_score': r'differentiat|unique|advantage.*score',
            'provide_strategic_recommendations': r'recommend|suggest|strategy',
            
            # Resource Optimization patterns
            'show_cost_breakdown': r'cost|budget|expense|price',
            'display_roi_projections': r'roi|return.*investment|profit',
            'provide_scenario_comparison': r'scenario|compare|alternative',
            'show_risk_mitigation': r'mitigat|reduce.*risk|prevent',
            'display_timeline_impact': r'timeline|schedule.*impact|delay',
            'provide_optimization_suggestions': r'optimiz|improve|efficiency'
        }
        
        for pattern_name in required_patterns:
            if pattern_name in pattern_checks:
                pattern_regex = pattern_checks[pattern_name]
                if not re.search(pattern_regex, content, re.IGNORECASE):
                    self._add_violation(
                        rule_id=f"workflow_missing_{pattern_name}",
                        severity="error",
                        message=f"{workflow_type} workflow missing: {pattern_name.replace('_', ' ')}",
                        suggestion=self._get_workflow_suggestion(pattern_name),
                        ux_impact=f"Incomplete {workflow_type} user experience",
                        line_number=1
                    )
    
    def _add_violation(self, rule_id: str, severity: str, message: str, 
                      suggestion: str, ux_impact: str, line_number: int, pattern: str = "") -> None:
        """Add a UX violation to the list"""
        violation = UXViolation(
            file_path="",  # Will be set in generate_report
            line_number=line_number,
            rule_id=rule_id,
            severity=severity,
            message=message,
            suggestion=suggestion,
            pattern=pattern,
            ux_impact=ux_impact
        )
        self.violations.append(violation)
    
    def _generate_report(self, component_path: str, workflow_type: str) -> UXValidationReport:
        """Generate comprehensive UX validation report"""
        errors = []
        warnings = []
        info = []
        
        for violation in self.violations:
            violation.file_path = component_path
            
            if violation.severity == "error":
                errors.append(violation)
            elif violation.severity == "warning":
                warnings.append(violation)
            else:
                info.append(violation)
        
        total_violations = len(errors) + len(warnings)
        
        # Calculate UX score (0-100)
        max_possible_violations = 15  # Reasonable estimate
        ux_score = max(0, (max_possible_violations - total_violations) / max_possible_violations * 100)
        
        return UXValidationReport(
            component_path=component_path,
            timestamp=datetime.now().isoformat(),
            total_violations=total_violations,
            workflow_type=workflow_type,
            errors=errors,
            warnings=warnings,
            info=info,
            ux_score=ux_score,
            passed=len(errors) == 0
        )
    
    def _create_error_report(self, component_path: str, error_message: str) -> UXValidationReport:
        """Create error report for file issues"""
        return UXValidationReport(
            component_path=component_path,
            timestamp=datetime.now().isoformat(),
            total_violations=1,
            workflow_type="file_error",
            errors=[UXViolation(
                file_path=component_path,
                line_number=1,
                rule_id="file_error",
                severity="error",
                message=error_message,
                suggestion="Fix file access issues",
                ux_impact="Cannot validate UX patterns"
            )],
            ux_score=0.0,
            passed=False
        )
    
    def _create_success_report(self, component_path: str, message: str) -> UXValidationReport:
        """Create success report for non-UI files"""
        return UXValidationReport(
            component_path=component_path,
            timestamp=datetime.now().isoformat(),
            total_violations=0,
            workflow_type="skipped",
            ux_score=100.0,
            passed=True
        )
    
    def _is_ui_component_file(self, file_path: str) -> bool:
        """Check if file is a UI component that should be validated"""
        return any(file_path.endswith(ext) for ext in ['.tsx', '.jsx', '.vue', '.svelte'])
    
    def _find_line_with_text(self, lines: List[str], text: str) -> int:
        """Find line number containing specific text"""
        for i, line in enumerate(lines, 1):
            if text.lower() in line.lower():
                return i
        return 1
    
    def _find_line_with_async(self, lines: List[str]) -> int:
        """Find line with async operation"""
        async_patterns = ['await', 'async', '.then(', 'fetch(']
        for i, line in enumerate(lines, 1):
            if any(pattern in line.lower() for pattern in async_patterns):
                return i
        return 1
    
    def _get_error_handling_suggestion(self, check_name: str) -> str:
        """Get specific suggestion for error handling"""
        suggestions = {
            'try_catch': 'Wrap async operations in try-catch blocks',
            'error_state': 'Add error state: const [error, setError] = useState(null)',
            'user_feedback': 'Show error to user: toast.error(error.message)',
            'retry_mechanism': 'Add retry button: <button onClick={retry}>Try Again</button>',
            'network_error': 'Handle network errors specifically'
        }
        return suggestions.get(check_name, 'Add proper error handling')
    
    def _get_error_impact(self, check_name: str) -> str:
        """Get UX impact of missing error handling"""
        impacts = {
            'try_catch': 'App crashes on errors',
            'error_state': 'Users don\'t know what went wrong',
            'user_feedback': 'Silent failures confuse users',
            'retry_mechanism': 'Users cannot recover from errors',
            'network_error': 'Network issues cause poor experience'
        }
        return impacts.get(check_name, 'Poor error experience')
    
    def _get_form_suggestion(self, req_name: str) -> str:
        """Get specific form workflow suggestions"""
        suggestions = {
            'validation': 'Add field validation with error messages',
            'loading_state': 'Add isSubmitting state during form submission',
            'success_feedback': 'Show success message and next action',
            'field_errors': 'Display specific errors per field',
            'disabled_submit': 'Disable submit button while submitting'
        }
        return suggestions.get(req_name, 'Add proper form handling')
    
    def _get_workflow_suggestion(self, pattern_name: str) -> str:
        """Get specific workflow pattern suggestions (Enhanced with PM-specific patterns)"""
        suggestions = {
            # Original patterns
            'show_loading_state': 'Add const [isLoading, setIsLoading] = useState(false)',
            'disable_submit_button': 'Add disabled={isLoading} to prevent double submission',
            'show_success_or_error': 'Add success/error states with user feedback',
            'provide_next_action': 'Guide user to next step after completion',
            'show_skeleton': 'Use skeleton screens instead of spinners',
            'handle_error_state': 'Add comprehensive error handling with user messages',
            'show_empty_state': 'Show helpful empty state with action',
            'provide_retry_mechanism': 'Add retry option for failed operations',
            'immediate_feedback': 'Provide immediate visual feedback on user actions',
            'optimistic_update': 'Update UI immediately, rollback on error',
            'rollback_on_error': 'Revert optimistic updates if operation fails',
            'confirm_destructive_actions': 'Ask for confirmation before destructive actions',
            
            # PM-SPECIFIC PATTERN SUGGESTIONS
            # Strategic Analysis suggestions
            'show_framework_selection': 'Add framework selection dropdown with RICE, ICE, JTBD, OKRs options',
            'display_confidence_score': 'Show confidence percentage (85%) with visual indicator (progress bar/gauge)',
            'show_reasoning_chain': 'Display step-by-step analysis reasoning with expandable sections',
            'provide_alternative_frameworks': 'Suggest 2-3 alternative frameworks with brief explanations',
            'show_success_probability': 'Display success probability (75%) with risk-adjusted timeline',
            'display_risk_factors': 'List top 3-5 risk factors with mitigation suggestions',
            'provide_next_actions': 'Show specific, actionable next steps with assignees and timelines',
            'show_progress_indicator': 'Add multi-step progress bar for complex strategic analysis',
            
            # Framework Application suggestions
            'show_framework_explanation': 'Include framework tooltip: "RICE = Reach × Impact × Confidence ÷ Effort"',
            'display_input_requirements': 'Show required vs optional fields with clear validation messages',
            'validate_input_ranges': 'Add input validation with helpful range indicators (1-10 scale)',
            'show_calculation_transparency': 'Display formula and calculation breakdown in real-time',
            'provide_context_help': 'Add contextual help tooltips for each framework parameter',
            'show_score_interpretation': 'Include score interpretation guide (High: >15, Medium: 5-15, Low: <5)',
            
            # Decision Validation suggestions
            'show_multiple_perspectives': 'Present decision from multiple stakeholder viewpoints',
            'display_confidence_metrics': 'Show confidence intervals and reliability indicators',
            'provide_sensitivity_analysis': 'Add "What if..." scenario modeling with parameter sliders',
            'show_implementation_timeline': 'Display timeline with milestones, dependencies, and risk buffers',
            'display_resource_requirements': 'Show resource breakdown (team size, skills, budget)',
            'provide_rollback_plan': 'Include rollback strategy with decision checkpoints',
            
            # PMO Transformation suggestions
            'show_capability_progress': 'Display capability radar chart with before/after comparison',
            'display_transformation_metrics': 'Show PMO readiness score and capability multiplier (300%)',
            'provide_milestone_tracking': 'Add milestone progress with celebration animations',
            'show_skill_development': 'Include skill assessment with development recommendations',
            'display_time_savings': 'Show time savings metrics (8 hrs → 10 min) with efficiency gains',
            'provide_next_level_guidance': 'Suggest next PMO capabilities to develop with learning paths',
            
            # Competitive Intelligence suggestions
            'show_threat_assessment': 'Display competitive threat matrix with urgency levels',
            'display_opportunity_matrix': 'Show 2x2 opportunity matrix (impact vs effort)',
            'provide_response_options': 'Present strategic response options with pros/cons',
            'show_market_positioning': 'Include competitive positioning map with differentiation',
            'display_differentiation_score': 'Show competitive advantage score with improvement areas',
            'provide_strategic_recommendations': 'Offer prioritized strategic recommendations with timelines',
            
            # Resource Optimization suggestions
            'show_cost_breakdown': 'Display cost breakdown chart with category breakdowns',
            'display_roi_projections': 'Show ROI projections with confidence intervals over time',
            'provide_scenario_comparison': 'Add scenario comparison table with key metrics',
            'show_risk_mitigation': 'Include risk mitigation strategies with probability reductions',
            'display_timeline_impact': 'Show timeline impact visualization with critical path',
            'provide_optimization_suggestions': 'Suggest resource optimizations with expected improvements'
        }
        return suggestions.get(pattern_name, 'Implement proper PM workflow UX pattern')

    def print_summary(self, reports: List[UXValidationReport]) -> None:
        """Print UX validation summary to console"""
        if not reports:
            print("No components validated.")
            return
            
        passed = len([r for r in reports if r.passed])
        failed = len([r for r in reports if not r.passed])
        avg_score = sum(r.ux_score for r in reports) / len(reports)
        total_errors = sum(len(r.errors) for r in reports)
        total_warnings = sum(len(r.warnings) for r in reports)
        
        print("\n" + "="*60)
        print("🎯 PM33 UX WORKFLOW VALIDATION SUMMARY")
        print("="*60)
        print(f"📊 Components: {len(reports)} total, {passed} passed, {failed} failed")
        print(f"📈 Average UX Score: {avg_score:.1f}%")
        print(f"❌ Errors: {total_errors}")
        print(f"⚠️  Warnings: {total_warnings}")
        
        if failed > 0:
            print(f"\n🚨 UX ENFORCEMENT: {failed} components BLOCKED from deployment")
            print("   Fix all UX workflow violations before proceeding")
        else:
            print(f"\n✅ ALL COMPONENTS MEET UX STANDARDS - Ready for deployment")
        
        print("\n🎯 Common UX Issues Found:")
        issue_counts = {}
        for report in reports:
            for error in report.errors + report.warnings:
                rule = error.rule_id
                issue_counts[rule] = issue_counts.get(rule, 0) + 1
        
        for rule, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {rule.replace('_', ' ')}: {count} occurrences")
        
        print("="*60)

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='PM33 UX Workflow Validator')
    parser.add_argument('path', nargs='?', default='.', 
                       help='Component file or directory path')
    parser.add_argument('--workflow-type', choices=[
                           'form_submission', 'data_loading', 'user_action',
                           'strategic_analysis', 'framework_application', 'decision_validation',
                           'pmo_transformation', 'competitive_intelligence', 'resource_optimization'
                       ], help='Specific workflow type to validate')
    parser.add_argument('--strict', action='store_true',
                       help='Enable strict mode (warnings treated as errors)')
    parser.add_argument('--export', type=str, default='pm33_ux_validation_report.json',
                       help='Export report to JSON file')
    parser.add_argument('--consultation', action='store_true',
                       help='Provide UX workflow consultation')
    
    args = parser.parse_args()
    
    if args.consultation:
        print_ux_consultation(args.workflow_type)
        return
    
    validator = PM33UXWorkflowValidator()
    reports = []
    
    if os.path.isfile(args.path):
        # Single file validation
        report = validator.validate_component(args.path, args.workflow_type)
        reports.append(report)
        print_report(report, args.strict)
    elif os.path.isdir(args.path):
        # Directory validation
        pattern = os.path.join(args.path, '**/*.{tsx,jsx,vue,svelte}')
        files = glob.glob(pattern, recursive=True)
        
        if not files:
            print(f"No UI component files found in {args.path}")
            return
            
        print(f"🎯 Validating {len(files)} UX workflow components...")
        
        for file_path in files:
            report = validator.validate_component(file_path, args.workflow_type)
            reports.append(report)
        
        validator.print_summary(reports)
    
    # Export results if requested
    if args.export and reports:
        export_data = {
            'validation_timestamp': datetime.now().isoformat(),
            'validator_version': '1.0.0',
            'total_components': len(reports),
            'passed_components': len([r for r in reports if r.passed]),
            'failed_components': len([r for r in reports if not r.passed]),
            'average_ux_score': sum(r.ux_score for r in reports) / len(reports) if reports else 0,
            'reports': [
                {
                    'component_path': r.component_path,
                    'workflow_type': r.workflow_type,
                    'ux_score': r.ux_score,
                    'passed': r.passed,
                    'total_violations': r.total_violations,
                    'errors': [
                        {
                            'line': v.line_number,
                            'rule': v.rule_id,
                            'message': v.message,
                            'suggestion': v.suggestion,
                            'ux_impact': v.ux_impact
                        } for v in r.errors
                    ]
                } for r in reports
            ]
        }
        
        with open(args.export, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📊 UX validation report exported to: {args.export}")
    
    # Exit with error code if validation failed
    failed_reports = [r for r in reports if not r.passed]
    if failed_reports and not args.consultation:
        exit_code = len(failed_reports)
        print(f"\n🚨 {exit_code} components failed UX validation")
        exit(min(exit_code, 127))  # Max exit code is 127

def print_report(report: UXValidationReport, strict_mode: bool = False) -> None:
    """Print individual component report"""
    status = "✅ PASSED" if report.passed else "❌ FAILED"
    print(f"\n{status}: {report.component_path}")
    print(f"UX Score: {report.ux_score:.1f}%")
    
    if report.errors:
        print("\n❌ UX ERRORS:")
        for error in report.errors:
            print(f"   Line {error.line_number}: {error.message}")
            print(f"   💡 {error.suggestion}")
            print(f"   Impact: {error.ux_impact}")
    
    if report.warnings and strict_mode:
        print("\n⚠️  UX WARNINGS (treated as errors in strict mode):")
        for warning in report.warnings:
            print(f"   Line {warning.line_number}: {warning.message}")
            print(f"   💡 {warning.suggestion}")

def print_ux_consultation(workflow_type: str = None) -> None:
    """Provide UX workflow consultation"""
    print("🎯 PM33 UX WORKFLOW CONSULTATION")
    print("=" * 60)
    
    if workflow_type:
        patterns = PM33UXWorkflowValidator.WORKFLOW_PATTERNS.get(workflow_type, [])
        print(f"\n📋 {workflow_type.upper()} WORKFLOW REQUIREMENTS:")
        for pattern in patterns:
            print(f"   • {pattern.replace('_', ' ').title()}")
    else:
        print("\n📋 CORE UX WORKFLOW PRINCIPLES:")
        print("   • Every user action needs immediate feedback")
        print("   • Loading states for operations > 100ms")
        print("   • Comprehensive error handling with recovery")
        print("   • Accessibility: keyboard navigation + screen readers")
        print("   • Cognitive load: max 7 choices per screen")
        print("   • Performance: debounce search, skeleton screens")
    
    print("\n💡 COMMON UX PATTERNS:")
    print("   Form Submission: loading → success/error → next action")
    print("   Data Loading: skeleton → content/empty/error → retry")
    print("   User Actions: immediate feedback → optimistic update → rollback")
    
    # PM-SPECIFIC PATTERNS
    if not workflow_type:
        print("\n🎯 PM-SPECIFIC UX PATTERNS:")
        print("   Strategic Analysis: framework selection → analysis progress → confidence score → recommendations")
        print("   Framework Application: input validation → real-time calculation → score interpretation → save")
        print("   Decision Validation: multiple perspectives → confidence metrics → sensitivity analysis → implementation plan")
        print("   PMO Transformation: current assessment → capability gaps → development plan → progress tracking")
        print("   Competitive Intelligence: threat assessment → opportunity matrix → strategic responses → implementation")
        print("   Resource Optimization: current allocation → scenario modeling → ROI projections → optimization plan")
    
    elif workflow_type in ['strategic_analysis', 'framework_application', 'decision_validation', 
                          'pmo_transformation', 'competitive_intelligence', 'resource_optimization']:
        print(f"\n🎯 {workflow_type.upper()} SPECIFIC GUIDANCE:")
        
        pm_guidance = {
            'strategic_analysis': [
                "Always show framework selection with explanations",
                "Display confidence scores with visual indicators", 
                "Provide transparent reasoning chains",
                "Include success probability with risk factors",
                "Offer alternative framework suggestions"
            ],
            'framework_application': [
                "Include framework education and tooltips",
                "Validate input ranges with helpful messages",
                "Show calculation transparency in real-time",
                "Provide score interpretation guides",
                "Enable comparison between frameworks"
            ],
            'decision_validation': [
                "Present multiple stakeholder perspectives",
                "Show confidence intervals and reliability",
                "Provide 'what-if' scenario modeling",
                "Display implementation timeline with risks",
                "Include rollback plans and checkpoints"
            ],
            'pmo_transformation': [
                "Show capability progress with radar charts",
                "Display transformation metrics and multipliers",
                "Track milestones with celebration feedback",
                "Include skill development recommendations",
                "Highlight time savings and efficiency gains"
            ],
            'competitive_intelligence': [
                "Display threat assessment matrices",
                "Show opportunity vs impact visualizations",
                "Provide strategic response options with pros/cons",
                "Include competitive positioning maps",
                "Offer prioritized recommendations with timelines"
            ],
            'resource_optimization': [
                "Show detailed cost breakdowns with charts",
                "Display ROI projections over time",
                "Enable scenario comparison tables",
                "Include risk mitigation strategies",
                "Provide optimization suggestions with impact"
            ]
        }
        
        for guideline in pm_guidance.get(workflow_type, []):
            print(f"   • {guideline}")
    
    print("\n🎯 PM-SPECIFIC COGNITIVE LOAD LIMITS:")
    print("   • Max 4 frameworks displayed simultaneously")
    print("   • Max 5 strategic options per decision")
    print("   • Max 6 risk factors before grouping")
    print("   • Max 8 KPIs on single dashboard")
    print("   • Max 3 resource scenarios for comparison")
    print("   • Single confidence score per analysis")
    
    print("\n🚫 AUTOMATIC REJECTION TRIGGERS:")
    print("   • Missing loading states")
    print("   • No error handling")
    print("   • More than 7 choices per screen")
    print("   • No keyboard navigation")
    print("   • Missing user feedback")

if __name__ == "__main__":
    main()