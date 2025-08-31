#!/usr/bin/env python3
"""
PM33 Design Contract Validator
Enforces design standards across all UI components
Usage: python mcp_design_validator.py [component_path] [--strict]
"""

import os
import re
import json
import glob
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available - automated contrast testing will be skipped")

@dataclass
class Violation:
    """Represents a design contract violation"""
    file_path: str
    line_number: int
    rule_id: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: str
    pattern: str = ""

@dataclass
class ValidationReport:
    """Complete validation report"""
    component_path: str
    timestamp: str
    total_violations: int
    errors: List[Violation] = field(default_factory=list)
    warnings: List[Violation] = field(default_factory=list)
    info: List[Violation] = field(default_factory=list)
    compliance_score: float = 0.0
    passed: bool = False

class PM33DesignValidator:
    """
    PM33 Design Contract Validator
    Enforces PM33 design standards with zero tolerance for violations
    """
    
    # PM33 Design Contract Rules
    BRAND_COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2', 
        'success': '#10b981',
        'bg_light': '#ffffff',
        'bg_dark': '#0a0e27'
    }
    
    # Typography Rules (Comprehensive)
    TYPOGRAPHY_RULES = {
        'fonts': {
            'allowed': ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto'],
            'forbidden': ['Times', 'Times New Roman', 'Arial', 'Comic Sans', 'serif']
        },
        'sizes': {
            'h1': [48, 56, 64],  # px values allowed
            'h2': [32, 36, 40],
            'h3': [24, 28, 32],
            'h4': [20, 24],
            'h5': [18, 20],
            'h6': [16, 18],
            'body': [14, 16, 18],
            'small': [12, 14]
        },
        'line_heights': [1.2, 1.4, 1.5, 1.6, 1.75],
        'font_weights': [400, 500, 600, 700]  # normal, medium, semibold, bold
    }
    
    # Spacing Grid Rules (8px System)
    SPACING_GRID = {
        'base': 8,
        'allowed': [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 128, 160, 192, 224, 256],
        'tailwind_map': {
            'p-0': 0, 'p-1': 4, 'p-2': 8, 'p-3': 12, 'p-4': 16, 'p-5': 20, 'p-6': 24,
            'p-8': 32, 'p-10': 40, 'p-12': 48, 'p-14': 56, 'p-16': 64, 'p-20': 80,
            'p-24': 96, 'p-32': 128, 'p-40': 160, 'p-48': 192, 'p-56': 224, 'p-64': 256,
            'm-0': 0, 'm-1': 4, 'm-2': 8, 'm-3': 12, 'm-4': 16, 'm-5': 20, 'm-6': 24,
            'm-8': 32, 'm-10': 40, 'm-12': 48, 'm-14': 56, 'm-16': 64, 'm-20': 80,
            'm-24': 96, 'm-32': 128, 'm-40': 160, 'm-48': 192, 'm-56': 224, 'm-64': 256
        }
    }
    
    # Layout System Rules
    LAYOUT_RULES = {
        'containers': {
            'max_widths': [640, 768, 1024, 1280, 1536],  # Standard breakpoints
            'padding': {
                'mobile': 16,
                'tablet': 24, 
                'desktop': 32
            }
        },
        'grid': {
            'columns': [1, 2, 3, 4, 5, 6, 8, 10, 12],  # Allowed column counts
            'gaps': [4, 8, 12, 16, 24, 32, 48, 64]      # Allowed gap values
        },
        'flexbox': {
            'alignments': ['start', 'center', 'end', 'stretch', 'baseline'],
            'justifications': ['start', 'center', 'end', 'between', 'around', 'evenly']
        }
    }
    
    REQUIRED_PATTERNS = {
        # Design Token Usage Requirements (NEW)
        'design_token_usage': {
            'patterns': [
                r'var\(--pm33-',
                r'className.*pm33-',
                r'\.pm33-[a-zA-Z-]+'
            ],
            'severity': 'error',
            'message': 'Must use PM33 design tokens and CSS classes',
            'suggestion': 'Use className="pm33-*" classes and var(--pm33-*) CSS custom properties'
        },
        'glass_morphism': {
            'patterns': [
                r'backdrop-blur',
                r'-webkit-backdrop-filter',
                r'glass-card',
                r'glass-morphism',
                r'backdrop-filter:\s*blur\(\d+px\)',
                r'pm33-glass-card',
                r'pm33-modal-overlay',
                r'pm33-modal-content'
            ],
            'severity': 'error',
            'message': 'Missing glass morphism - ALL cards must have backdrop-blur',
            'suggestion': 'Add: backdrop-filter: blur(20px) and -webkit-backdrop-filter: blur(20px) or use className="pm33-glass-card"'
        },
        'gradient_text': {
            'patterns': [
                r'text-gradient',
                r'bg-gradient-to-',
                r'background-clip:\s*text',
                r'-webkit-background-clip:\s*text',
                r'linear-gradient.*text'
            ],
            'severity': 'error', 
            'message': 'Missing gradient text - ALL headlines must use gradient styling',
            'suggestion': 'Add: className="text-gradient" or background: linear-gradient(...)'
        },
        'professional_shadows': {
            'patterns': [
                r'shadow-(?!sm\b)',  # Any shadow except shadow-sm
                r'shadow-glass',
                r'shadow-premium',
                r'shadow-ai',
                r'box-shadow:\s*0\s+\d+px\s+\d+px'
            ],
            'severity': 'error',
            'message': 'Insufficient shadow depth - Use professional shadows, never flat',
            'suggestion': 'Replace shadow-sm with shadow-glass or shadow-premium'
        },
        'hover_states': {
            'patterns': [
                r'hover:',
                r'transition',
                r'transform',
                r':hover\s*{',
                r'hover-lift',
                r'hover-scale'
            ],
            'severity': 'warning',
            'message': 'Missing hover states - All interactive elements need hover feedback',
            'suggestion': 'Add: hover:transform hover:translateY(-4px) transition-transform'
        },
        'rounded_corners': {
            'patterns': [
                r'rounded',
                r'border-radius',
                r'rounded-\w+'
            ],
            'severity': 'warning',
            'message': 'Sharp corners detected - Use rounded corners for professional feel',
            'suggestion': 'Add: rounded-lg or border-radius: var(--radius-lg)'
        }
    }
    
    FORBIDDEN_PATTERNS = {
        # Design Token Enforcement Rules (NEW)
        'theme_conditional_inline': {
            'patterns': [
                r'theme\s*===\s*[\'"]dark[\'"].*\?.*:',
                r'theme\s*===\s*[\'"]light[\'"].*\?.*:',
                r'isDark\s*\?.*:',
                r'isLight\s*\?.*:'
            ],
            'severity': 'error',
            'message': 'Theme-conditional inline styles forbidden - Use CSS classes with design tokens',
            'suggestion': 'Replace with className using CSS custom properties (e.g., className="pm33-glass-card")'
        },
        'hardcoded_design_values': {
            'patterns': [
                r'padding:\s*[\'"]?\d+px[\'"]?',
                r'margin:\s*[\'"]?\d+px[\'"]?',
                r'fontSize:\s*[\'"]?\d+px[\'"]?',
                r'borderRadius:\s*[\'"]?\d+px[\'"]?',
                r'gap:\s*[\'"]?\d+px[\'"]?'
            ],
            'severity': 'error',
            'message': 'Hardcoded design values forbidden - Use design tokens',
            'suggestion': 'Use CSS custom properties: var(--pm33-spacing-md), var(--pm33-text-lg), var(--pm33-radius-md)'
        },
        'brand_color_hardcoding': {
            'patterns': [
                r'background:\s*[\'"]?#667eea[\'"]?',
                r'background:\s*[\'"]?#764ba2[\'"]?',
                r'background:\s*[\'"]?#10b981[\'"]?',
                r'color:\s*[\'"]?#667eea[\'"]?',
                r'color:\s*[\'"]?#764ba2[\'"]?'
            ],
            'severity': 'error',
            'message': 'Brand color hardcoding forbidden - Use design tokens',
            'suggestion': 'Use CSS custom properties: var(--pm33-brand), var(--pm33-success)'
        },
        'component_specific_css_blocks': {
            'patterns': [
                r'<style>\s*\{.*\.(?!pm33-)[a-zA-Z-]+.*\}',
                r'<style.*>\s*\{[^@].*\}'
            ],
            'severity': 'error',
            'message': 'Component-specific CSS blocks discouraged - Use globals.css or CSS modules',
            'suggestion': 'Move styles to globals.css with .pm33- prefix or use CSS modules'
        },
        'flat_white': {
            'patterns': [r'bg-white(?!/)', r'background:\s*#ffffff(?!\s*[,;])'],
            'severity': 'error',
            'message': 'Flat white backgrounds forbidden - Use glass morphism instead',
            'suggestion': 'Replace with: bg-white/95 or glass-bg variable'
        },
        'basic_grays': {
            'patterns': [r'bg-gray-\d+', r'text-gray-\d+'],
            'severity': 'warning', 
            'message': 'Basic gray colors - Use theme-aware variables instead',
            'suggestion': 'Use: text-primary, text-secondary, bg-primary, bg-secondary'
        },
        'harsh_borders': {
            'patterns': [r'border-black', r'border-solid.*#000'],
            'severity': 'error',
            'message': 'Harsh black borders forbidden - Use subtle glass borders',
            'suggestion': 'Use: border border-white/10 or border-glass'
        },
        'weak_shadows': {
            'patterns': [r'shadow-sm\b', r'shadow-xs\b'],
            'severity': 'error',
            'message': 'Weak shadows forbidden - Use professional depth',
            'suggestion': 'Replace with: shadow-glass, shadow-premium, or shadow-ai'
        },
        'non_brand_colors': {
            'patterns': [
                r'#(?!667eea|764ba2|10b981|ffffff|0a0e27)[0-9a-fA-F]{6}',
                r'rgb\(\s*(?!102,\s*126,\s*234|118,\s*75,\s*162|16,\s*185,\s*129)'
            ],
            'severity': 'warning',
            'message': 'Non-brand colors detected - Use approved PM33 palette only',
            'suggestion': f'Use approved colors: {", ".join(BRAND_COLORS.values())}'
        }
    }
    
    SPACING_GRID = [4, 8, 16, 24, 32, 48, 64]  # 8px grid system
    
    def __init__(self, strict_mode: bool = True):
        """Initialize validator with optional strict mode"""
        self.violations: List[Violation] = []
        self.warnings: List[Violation] = []
        self.strict_mode = strict_mode
        self.current_file = ""
        
    def validate_component(self, component_path: str) -> ValidationReport:
        """
        Validate a single component against PM33 design contract
        Returns: ValidationReport with all violations and compliance score
        """
        self.violations = []
        self.warnings = []
        self.current_file = component_path
        
        print(f"🔍 Validating: {component_path}")
        
        if not os.path.exists(component_path):
            return ValidationReport(
                component_path=component_path,
                timestamp=datetime.now().isoformat(),
                total_violations=1,
                errors=[Violation(
                    file_path=component_path,
                    line_number=0,
                    rule_id="file_not_found",
                    severity="error",
                    message="Component file not found",
                    suggestion="Verify file path exists"
                )],
                passed=False
            )
        
        # Read component content
        try:
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self._create_error_report(component_path, f"Failed to read file: {str(e)}")
        
        # Run all validation checks
        self._check_required_patterns(content)
        self._check_forbidden_patterns(content) 
        self._check_spacing_compliance(content)
        self._check_touch_targets(content)
        self._check_accessibility(content)
        self._check_typography_compliance(content)
        self._check_layout_compliance(content)
        self._check_theme_toggle_compliance(content)
        self._check_button_standards(content)
        self._check_navigation_consistency(content)
        
        # Generate final report
        return self._generate_report(component_path)
    
    def validate_directory(self, directory_path: str, pattern: str = "**/*.{tsx,jsx,css}") -> List[ValidationReport]:
        """Validate all components in a directory"""
        reports = []
        
        base_path = Path(directory_path)
        files = list(base_path.glob(pattern))
        
        print(f"🔍 Validating {len(files)} files in {directory_path}")
        
        for file_path in files:
            if self._should_validate_file(str(file_path)):
                report = self.validate_component(str(file_path))
                reports.append(report)
                
                # Print immediate feedback
                status = "✅ PASS" if report.passed else "❌ FAIL"
                print(f"  {status} {file_path.name} ({report.compliance_score:.1%})")
        
        return reports
    
    def _check_required_patterns(self, content: str) -> None:
        """Check for mandatory design patterns"""
        lines = content.split('\n')
        
        for rule_name, rule_config in self.REQUIRED_PATTERNS.items():
            pattern_found = False
            
            for pattern in rule_config['patterns']:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_found = True
                    break
            
            if not pattern_found:
                self._add_violation(
                    rule_id=rule_name,
                    severity=rule_config['severity'],
                    message=rule_config['message'],
                    suggestion=rule_config['suggestion'],
                    line_number=1  # Component-level violation
                )
    
    def _check_forbidden_patterns(self, content: str) -> None:
        """Check for forbidden design patterns"""
        lines = content.split('\n')
        
        for rule_name, rule_config in self.FORBIDDEN_PATTERNS.items():
            for pattern in rule_config['patterns']:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Check if this violation should be allowed (exceptions)
                        if self._is_allowed_inline_exception(line, rule_name, match.group()):
                            continue
                            
                        self._add_violation(
                            rule_id=rule_name,
                            severity=rule_config['severity'], 
                            message=rule_config['message'],
                            suggestion=rule_config['suggestion'],
                            line_number=line_num,
                            pattern=match.group()
                        )
    
    def _is_allowed_inline_exception(self, line: str, rule_name: str, pattern: str) -> bool:
        """Check if an inline pattern should be allowed as an exception"""
        
        # Allow mathematical/calculated values
        mathematical_patterns = [
            r'\$\{.*\*.*\}',  # ${(progress / total) * 100}
            r'\$\{.*\/.*\}',  # Division calculations
            r'\$\{.*\+.*\}',  # Addition calculations
            r'\$\{.*-.*\}',   # Subtraction calculations
            r'translateX?\(\$\{.*\}\)',  # Transform calculations
            r'scale\(\$\{.*\}\)',        # Scale calculations
        ]
        
        for math_pattern in mathematical_patterns:
            if re.search(math_pattern, line):
                return True
        
        # Allow CSS keyframes in <style> blocks
        if rule_name == 'component_specific_css_blocks':
            keyframe_indicators = ['@keyframes', 'animation:', 'transform:', 'from {', 'to {', '0% {', '100% {']
            if any(indicator in line.lower() for indicator in keyframe_indicators):
                return True
        
        # Allow performance-critical transforms
        performance_patterns = [
            r'transform.*translate3d',
            r'willChange.*transform',
            r'backface-visibility',
            r'transform-origin'
        ]
        
        for perf_pattern in performance_patterns:
            if re.search(perf_pattern, line, re.IGNORECASE):
                return True
        
        # Allow accessibility-required styles
        accessibility_patterns = [
            r'clipPath.*screenReader',
            r'position.*screenReader',
            r'visibility.*hidden.*screen',
            r'aria-hidden.*true'
        ]
        
        for a11y_pattern in accessibility_patterns:
            if re.search(a11y_pattern, line, re.IGNORECASE):
                return True
        
        # Allow SVG attributes
        if 'viewBox' in line or 'xmlns' in line or '<svg' in line or '<path' in line:
            return True
        
        return False

    def _check_spacing_compliance(self, content: str) -> None:
        """Validate 8px grid spacing system"""
        spacing_patterns = [
            r'p-(\d+)', r'px-(\d+)', r'py-(\d+)',
            r'm-(\d+)', r'mx-(\d+)', r'my-(\d+)',
            r'gap-(\d+)', r'space-[xy]-(\d+)',
            r'padding:\s*(\d+)px', r'margin:\s*(\d+)px'
        ]
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in spacing_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    value = int(match.group(1))
                    # Convert Tailwind spacing to pixels (multiply by 4)
                    px_value = value * 4 if 'px' not in match.group() else value
                    
                    if px_value not in self.SPACING_GRID:
                        closest_grid = min(self.SPACING_GRID, key=lambda x: abs(x - px_value))
                        self._add_violation(
                            rule_id="spacing_grid",
                            severity="warning",
                            message=f"Non-grid spacing: {px_value}px",
                            suggestion=f"Use 8px grid value: {closest_grid}px",
                            line_number=line_num,
                            pattern=match.group()
                        )
    
    def _check_touch_targets(self, content: str) -> None:
        """Validate 16px minimum touch targets"""
        small_size_patterns = [
            r'h-[1-3]\b',  # h-1, h-2, h-3 (4px, 8px, 12px)
            r'w-[1-3]\b',  # w-1, w-2, w-3
            r'size-[1-3]\b',  # size-1, size-2, size-3
            r'height:\s*([4-9]|1[0-5])px',  # Under 16px
            r'width:\s*([4-9]|1[0-5])px'
        ]
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Only check interactive elements
            if any(keyword in line.lower() for keyword in ['button', 'click', 'hover', 'interactive', 'cursor-pointer']):
                for pattern in small_size_patterns:
                    if re.search(pattern, line):
                        self._add_violation(
                            rule_id="touch_targets",
                            severity="error",
                            message="Interactive element under 16px minimum",
                            suggestion="Ensure minimum 16px × 16px touch targets",
                            line_number=line_num,
                            pattern=pattern
                        )
    
    def _check_accessibility(self, content: str) -> None:
        """Basic accessibility compliance checks"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for missing alt text on images
            if re.search(r'<img(?![^>]*alt=)', line, re.IGNORECASE):
                self._add_violation(
                    rule_id="accessibility",
                    severity="warning",
                    message="Image missing alt text",
                    suggestion="Add descriptive alt attribute",
                    line_number=line_num
                )
            
            # Check for low contrast combinations
            if re.search(r'text-gray-400.*bg-gray-100|text-white.*bg-yellow', line, re.IGNORECASE):
                self._add_violation(
                    rule_id="accessibility",
                    severity="warning", 
                    message="Potential contrast violation",
                    suggestion="Verify WCAG AA compliance (4.5:1 ratio)",
                    line_number=line_num
                )
    
    def _check_typography_compliance(self, content: str) -> None:
        """Validate typography rules - fonts, sizes, weights, line heights"""
        lines = content.split('\n')
        
        # Check for forbidden fonts
        for rule_name, fonts in self.TYPOGRAPHY_RULES['fonts'].items():
            if rule_name == 'forbidden':
                for font in fonts:
                    if font.lower() in content.lower():
                        self._add_violation(
                            rule_id="forbidden_font",
                            severity="error",
                            message=f"Forbidden font family: {font}",
                            suggestion=f"Use approved fonts: {', '.join(self.TYPOGRAPHY_RULES['fonts']['allowed'])}",
                            line_number=self._find_line_with_text(lines, font)
                        )
        
        # Check font sizes
        font_size_pattern = r'font-size:\s*(\d+)px|text-(\w+)'
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(font_size_pattern, line)
            for match in matches:
                if match.group(1):  # Direct px value
                    size = int(match.group(1))
                    all_allowed_sizes = sum(self.TYPOGRAPHY_RULES['sizes'].values(), [])
                    if size not in all_allowed_sizes:
                        closest_size = min(all_allowed_sizes, key=lambda x: abs(x - size))
                        self._add_violation(
                            rule_id="invalid_font_size",
                            severity="error",
                            message=f"Non-standard font size: {size}px",
                            suggestion=f"Use approved size: {closest_size}px",
                            line_number=line_num,
                            pattern=match.group()
                        )
        
        # Check font weights
        font_weight_pattern = r'font-weight:\s*(\d+)|font-(\w+)'
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(font_weight_pattern, line)
            for match in matches:
                if match.group(1):  # Direct weight value
                    weight = int(match.group(1))
                    if weight not in self.TYPOGRAPHY_RULES['font_weights']:
                        closest_weight = min(self.TYPOGRAPHY_RULES['font_weights'], key=lambda x: abs(x - weight))
                        self._add_violation(
                            rule_id="invalid_font_weight",
                            severity="warning",
                            message=f"Non-standard font weight: {weight}",
                            suggestion=f"Use approved weight: {closest_weight}",
                            line_number=line_num,
                            pattern=match.group()
                        )
    
    def _check_layout_compliance(self, content: str) -> None:
        """Validate layout system usage - containers, grid, flexbox"""
        lines = content.split('\n')
        
        # Check container max-widths
        max_width_pattern = r'max-w(?:idth)?-(\w+)|max-w-\[(\d+)(?:px)?\]'
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(max_width_pattern, line)
            for match in matches:
                if match.group(2):  # Custom width value
                    width = int(match.group(2))
                    if width not in self.LAYOUT_RULES['containers']['max_widths']:
                        closest_width = min(self.LAYOUT_RULES['containers']['max_widths'], 
                                          key=lambda x: abs(x - width))
                        self._add_violation(
                            rule_id="non_standard_container",
                            severity="warning",
                            message=f"Non-standard container width: {width}px",
                            suggestion=f"Use standard width: {closest_width}px (max-w-{self._px_to_tailwind_container(closest_width)})",
                            line_number=line_num,
                            pattern=match.group()
                        )
        
        # Check grid columns
        grid_pattern = r'grid-cols-(\d+)'
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(grid_pattern, line)
            for match in matches:
                cols = int(match.group(1))
                if cols not in self.LAYOUT_RULES['grid']['columns']:
                    closest_cols = min(self.LAYOUT_RULES['grid']['columns'], key=lambda x: abs(x - cols))
                    self._add_violation(
                        rule_id="invalid_grid_columns",
                        severity="warning",
                        message=f"Non-standard grid columns: {cols}",
                        suggestion=f"Use approved columns: {closest_cols} (grid-cols-{closest_cols})",
                        line_number=line_num,
                        pattern=match.group()
                    )
        
        # Check grid/flex gaps
        gap_pattern = r'gap-(\d+)'
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(gap_pattern, line)
            for match in matches:
                gap_value = int(match.group(1)) * 4  # Convert Tailwind to px
                if gap_value not in self.LAYOUT_RULES['grid']['gaps']:
                    closest_gap = min(self.LAYOUT_RULES['grid']['gaps'], key=lambda x: abs(x - gap_value))
                    tailwind_gap = closest_gap // 4
                    self._add_violation(
                        rule_id="invalid_gap",
                        severity="warning",
                        message=f"Non-standard gap: {gap_value}px",
                        suggestion=f"Use approved gap: {closest_gap}px (gap-{tailwind_gap})",
                        line_number=line_num,
                        pattern=match.group()
                    )
    
    def _find_line_with_text(self, lines, text: str) -> int:
        """Find line number containing specific text"""
        for i, line in enumerate(lines, 1):
            if text.lower() in line.lower():
                return i
        return 1
    
    def _px_to_tailwind_container(self, px_value: int) -> str:
        """Convert px value to Tailwind container class"""
        container_map = {
            640: 'xl', 768: '2xl', 1024: '4xl', 1280: '6xl', 1536: '7xl'
        }
        return container_map.get(px_value, 'xl')
    
    def _add_violation(self, rule_id: str, severity: str, message: str, suggestion: str, 
                      line_number: int, pattern: str = "") -> None:
        """Add violation to appropriate list"""
        violation = Violation(
            file_path=self.current_file,
            line_number=line_number,
            rule_id=rule_id,
            severity=severity,
            message=message,
            suggestion=suggestion,
            pattern=pattern
        )
        
        if severity == "error":
            self.violations.append(violation)
        else:
            self.warnings.append(violation)
    
    def _generate_report(self, component_path: str) -> ValidationReport:
        """Generate comprehensive validation report"""
        total_violations = len(self.violations) + len(self.warnings)
        
        # Calculate compliance score
        max_possible_score = 100
        error_penalty = len(self.violations) * 15  # Errors are 15 points each
        warning_penalty = len(self.warnings) * 5   # Warnings are 5 points each
        
        compliance_score = max(0, (max_possible_score - error_penalty - warning_penalty) / max_possible_score)
        
        # Pass/fail determination
        passed = len(self.violations) == 0 and compliance_score >= 0.8
        
        return ValidationReport(
            component_path=component_path,
            timestamp=datetime.now().isoformat(),
            total_violations=total_violations,
            errors=self.violations.copy(),
            warnings=self.warnings.copy(),
            compliance_score=compliance_score,
            passed=passed
        )
    
    def _create_error_report(self, component_path: str, error_message: str) -> ValidationReport:
        """Create error report for file system issues"""
        return ValidationReport(
            component_path=component_path,
            timestamp=datetime.now().isoformat(),
            total_violations=1,
            errors=[Violation(
                file_path=component_path,
                line_number=0,
                rule_id="system_error",
                severity="error",
                message=error_message,
                suggestion="Check file permissions and path"
            )],
            passed=False
        )
    
    def _should_validate_file(self, file_path: str) -> bool:
        """Determine if file should be validated"""
        # Skip node_modules, dist, build directories
        skip_dirs = ['node_modules', 'dist', 'build', '.git', '.next']
        
        for skip_dir in skip_dirs:
            if skip_dir in file_path:
                return False
        
        # Only validate UI component files
        return any(file_path.endswith(ext) for ext in ['.tsx', '.jsx', '.css', '.scss'])
    
    def validate_against_screenshot(self, new_component: str, reference_image: str) -> Dict[str, Any]:
        """
        Compare visual similarity to approved designs
        TODO: Implement visual regression testing
        """
        return {
            'visual_similarity': 0.0,
            'message': 'Visual regression testing not yet implemented',
            'suggestion': 'Use Playwright or similar tool for visual diffs'
        }
    
    def export_report(self, reports: List[ValidationReport], output_path: str = "pm33_validation_report.json") -> None:
        """Export validation reports to JSON"""
        report_data = {
            'validation_timestamp': datetime.now().isoformat(),
            'validator_version': '1.0.0',
            'total_components': len(reports),
            'passed_components': len([r for r in reports if r.passed]),
            'failed_components': len([r for r in reports if not r.passed]),
            'average_compliance': sum(r.compliance_score for r in reports) / len(reports) if reports else 0,
            'reports': [
                {
                    'component_path': r.component_path,
                    'timestamp': r.timestamp,
                    'compliance_score': r.compliance_score,
                    'passed': r.passed,
                    'total_violations': r.total_violations,
                    'errors': [
                        {
                            'line': v.line_number,
                            'rule': v.rule_id,
                            'message': v.message,
                            'suggestion': v.suggestion,
                            'pattern': v.pattern
                        } for v in r.errors
                    ],
                    'warnings': [
                        {
                            'line': v.line_number,
                            'rule': v.rule_id,
                            'message': v.message,
                            'suggestion': v.suggestion,
                            'pattern': v.pattern
                        } for v in r.warnings
                    ]
                } for r in reports
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Validation report exported to: {output_path}")
    
    def print_summary(self, reports: List[ValidationReport]) -> None:
        """Print validation summary to console"""
        if not reports:
            print("No components validated.")
            return
            
        passed = len([r for r in reports if r.passed])
        failed = len([r for r in reports if not r.passed])
        avg_score = sum(r.compliance_score for r in reports) / len(reports)
        total_errors = sum(len(r.errors) for r in reports)
        total_warnings = sum(len(r.warnings) for r in reports)
        
        print("\n" + "="*60)
        print("🎯 PM33 DESIGN CONTRACT VALIDATION SUMMARY")
        print("="*60)
        print(f"📊 Components: {len(reports)} total, {passed} passed, {failed} failed")
        print(f"📈 Average Compliance: {avg_score:.1%}")
        print(f"❌ Errors: {total_errors}")
        print(f"⚠️  Warnings: {total_warnings}")
        
        if failed > 0:
            print(f"\n🚨 ENFORCEMENT: {failed} components BLOCKED from deployment")
            print("   Fix all errors before proceeding with development")
        else:
            print(f"\n✅ ALL COMPONENTS COMPLIANT - Ready for deployment")
        
        print("="*60)

    def _check_theme_toggle_compliance(self, content: str) -> None:
        """Validate theme toggle elements for dark/light mode compliance"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for toggle components
            if any(keyword in line.lower() for keyword in ['toggle', 'switch', 'theme']):
                # Check for theme awareness
                if not self._has_theme_support(line):
                    self._add_violation(
                        rule_id="toggle_theme_support",
                        severity="error",
                        message="Toggle element missing dark/light theme support",
                        suggestion="Add dark: classes and theme-conditional styling (e.g., dark:bg-gray-800 dark:text-white)",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for accessibility
                if not any(attr in line for attr in ['aria-checked', 'role=', 'aria-label']):
                    self._add_violation(
                        rule_id="toggle_accessibility",
                        severity="warning",
                        message="Toggle missing accessibility attributes",
                        suggestion="Add aria-checked, role=\"switch\", or aria-label",
                        line_number=line_num,
                        pattern=line.strip()
                    )
            
            # Check for theme class inconsistencies
            if 'dark:' in line:
                # Check for light backgrounds in dark mode
                if any(bg in line for bg in ['dark:bg-white', 'dark:bg-gray-50', 'dark:bg-gray-100']):
                    self._add_violation(
                        rule_id="dark_theme_light_backgrounds",
                        severity="error", 
                        message="Dark theme using light backgrounds",
                        suggestion="Use dark backgrounds (dark:bg-gray-800, dark:bg-gray-900) in dark mode",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for dark text in dark mode
                if any(text in line for text in ['dark:text-black', 'dark:text-gray-900', 'dark:text-gray-800']):
                    self._add_violation(
                        rule_id="dark_theme_dark_text",
                        severity="error",
                        message="Dark theme using dark text",
                        suggestion="Use light text (dark:text-white, dark:text-gray-100) in dark mode", 
                        line_number=line_num,
                        pattern=line.strip()
                    )

    def _check_button_standards(self, content: str) -> None:
        """Validate button elements meet PM33 standards in both themes"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if any(keyword in line for keyword in ['<button', 'Button', 'btn']):
                # Check PM33 brand colors
                if not self._has_pm33_colors(line):
                    self._add_violation(
                        rule_id="button_brand_colors",
                        severity="error", 
                        message="Button not using PM33 brand colors",
                        suggestion="Use gradient: bg-gradient-to-r from-[#667eea] to-[#764ba2] or solid: bg-[#10b981]",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for hover states
                if not any(hover in line for hover in ['hover:', ':hover']):
                    self._add_violation(
                        rule_id="button_hover_states",
                        severity="error",
                        message="Button missing hover states",
                        suggestion="Add hover:scale-105 transition-transform or hover:opacity-90",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for theme support in buttons
                if any(style in line for style in ['bg-', 'text-']) and not self._has_theme_support(line):
                    self._add_violation(
                        rule_id="button_theme_support", 
                        severity="error",
                        message="Button colors not theme-aware",
                        suggestion="Add dark: variants for all colors (e.g., dark:bg-gray-800 dark:text-white)",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for professional shadows
                if 'shadow-sm' in line or ('shadow' in line and not any(s in line for s in ['shadow-lg', 'shadow-xl', 'shadow-2xl'])):
                    self._add_violation(
                        rule_id="button_professional_shadows",
                        severity="error",
                        message="Button using flat or minimal shadow",
                        suggestion="Use shadow-xl or shadow-2xl for professional depth",
                        line_number=line_num,
                        pattern=line.strip()
                    )

    def _check_navigation_consistency(self, content: str) -> None:
        """Validate navigation components have consistent glass morphism"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if any(keyword in line for keyword in ['nav', 'Nav', 'header', 'Header', 'menu', 'Menu']):
                # Check for glass morphism
                if not self._has_glass_morphism(line):
                    self._add_violation(
                        rule_id="nav_glass_morphism",
                        severity="error",
                        message="Navigation missing glass morphism effect",
                        suggestion="Add bg-white/95 backdrop-blur-lg dark:bg-gray-900/95 for glass effect",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for consistent positioning
                if any(pos in line for pos in ['fixed', 'sticky']) and not all(attr in line for attr in ['top-', 'z-']):
                    self._add_violation(
                        rule_id="nav_positioning",
                        severity="warning",
                        message="Fixed navigation missing proper positioning",
                        suggestion="Add top-0 z-50 for consistent positioning",
                        line_number=line_num,
                        pattern=line.strip()
                    )
                
                # Check for theme support
                if not self._has_theme_support(line):
                    self._add_violation(
                        rule_id="nav_theme_support",
                        severity="error",
                        message="Navigation missing theme support",
                        suggestion="Add dark: variants for all colors and backgrounds",
                        line_number=line_num,
                        pattern=line.strip()
                    )

    def _has_theme_support(self, line: str) -> bool:
        """Check if line has theme support"""
        return any(theme in line for theme in ['dark:', 'light:', 'theme', 'data-theme'])

    def _has_pm33_colors(self, line: str) -> bool:
        """Check if line uses PM33 brand colors"""
        pm33_colors = ['#667eea', '#764ba2', '#10b981', '667eea', '764ba2', '10b981']
        return any(color in line for color in pm33_colors) or 'bg-gradient' in line

    def _has_glass_morphism(self, line: str) -> bool:
        """Check if line has glass morphism effect"""
        return any(glass in line for glass in ['backdrop-blur', 'bg-white/', 'bg-black/', '/90', '/95'])

    async def validate_contrast_automated(self, url: str) -> Dict[str, Any]:
        """Run automated contrast validation using Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "error": "Playwright not available",
                "message": "Install with: pip install playwright && playwright install"
            }
        
        contrast_validator = AutomatedContrastValidator()
        return await contrast_validator.validate_all_themes(url)


class AutomatedContrastValidator:
    """
    Automated contrast validator using Playwright for live theme testing
    Validates WCAG 2.1 AA compliance across light and dark themes
    """
    
    def __init__(self):
        self.min_contrast_ratios = {
            'normal_text': 4.5,
            'large_text': 3.0,
            'ui_component': 3.0
        }
    
    async def validate_all_themes(self, url: str) -> Dict[str, Any]:
        """Check contrast in both light and dark themes"""
        if not PLAYWRIGHT_AVAILABLE:
            return {"error": "Playwright not available"}
            
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            
            results = {}
            
            for theme in ['light', 'dark']:
                # Switch theme
                await page.evaluate(f'''
                    // Try multiple theme switching methods
                    document.documentElement.setAttribute('data-theme', '{theme}');
                    document.documentElement.className = document.documentElement.className.replace(/theme-\w+/, 'theme-{theme}');
                    document.body.setAttribute('data-theme', '{theme}');
                    
                    // Try PM33 specific theme switching
                    if (window.setTheme) window.setTheme('{theme}');
                    if (window.themeToggle) window.themeToggle('{theme}');
                    
                    // Dispatch theme change event
                    window.dispatchEvent(new CustomEvent('themeChange', {{ detail: '{theme}' }}));
                ''')
                
                await page.wait_for_timeout(500)
                
                # Inject comprehensive contrast checking script
                violations = await page.evaluate('''
                    () => {
                        function getRGB(colorStr) {
                            // Handle various color formats
                            if (colorStr.startsWith('rgb(')) {
                                const match = colorStr.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
                                return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
                            }
                            if (colorStr.startsWith('rgba(')) {
                                const match = colorStr.match(/rgba\\((\\d+),\\s*(\\d+),\\s*(\\d+),\\s*[\\d.]+\\)/);
                                return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
                            }
                            if (colorStr.startsWith('#')) {
                                const hex = colorStr.slice(1);
                                return [
                                    parseInt(hex.slice(0, 2), 16),
                                    parseInt(hex.slice(2, 4), 16),
                                    parseInt(hex.slice(4, 6), 16)
                                ];
                            }
                            return [0, 0, 0]; // Default fallback
                        }
                        
                        function getLuminance([r, g, b]) {
                            const [rs, gs, bs] = [r, g, b].map(c => {
                                c /= 255;
                                return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                            });
                            return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
                        }
                        
                        function getContrast(color1, color2) {
                            const rgb1 = getRGB(color1);
                            const rgb2 = getRGB(color2);
                            
                            const lum1 = getLuminance(rgb1);
                            const lum2 = getLuminance(rgb2);
                            
                            const brightest = Math.max(lum1, lum2);
                            const darkest = Math.min(lum1, lum2);
                            
                            return (brightest + 0.05) / (darkest + 0.05);
                        }
                        
                        function findBackgroundColor(element) {
                            let current = element;
                            while (current && current !== document.body) {
                                const style = window.getComputedStyle(current);
                                const bgColor = style.backgroundColor;
                                if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                                    return bgColor;
                                }
                                current = current.parentElement;
                            }
                            return window.getComputedStyle(document.body).backgroundColor || '#ffffff';
                        }
                        
                        const violations = [];
                        
                        // Check all buttons and interactive elements
                        document.querySelectorAll('button, a.button, [role="button"], .btn, [class*="button"]').forEach((btn, index) => {
                            const styles = window.getComputedStyle(btn);
                            const textColor = styles.color;
                            const bgColor = styles.backgroundColor === 'rgba(0, 0, 0, 0)' ? 
                                findBackgroundColor(btn) : styles.backgroundColor;
                            
                            const contrast = getContrast(textColor, bgColor);
                            
                            if (contrast < 3.0) {
                                violations.push({
                                    type: 'interactive_element',
                                    element: 'button',
                                    selector: btn.className || btn.id || `button[${index}]`,
                                    contrast: Math.round(contrast * 100) / 100,
                                    textColor: textColor,
                                    bgColor: bgColor,
                                    required_ratio: 3.0,
                                    text_sample: btn.textContent ? btn.textContent.substring(0, 30) : 'No text'
                                });
                            }
                        });
                        
                        // Check all text elements
                        document.querySelectorAll('p, span, h1, h2, h3, h4, h5, h6, div, li, td, th').forEach((el, index) => {
                            // Skip if element has no visible text
                            if (!el.textContent || el.textContent.trim().length === 0) return;
                            
                            const styles = window.getComputedStyle(el);
                            const textColor = styles.color;
                            const bgColor = findBackgroundColor(el);
                            
                            const contrast = getContrast(textColor, bgColor);
                            const fontSize = parseFloat(styles.fontSize);
                            const isLargeText = fontSize >= 18 || (fontSize >= 14 && styles.fontWeight >= 700);
                            
                            const requiredRatio = isLargeText ? 3.0 : 4.5;
                            
                            if (contrast < requiredRatio) {
                                violations.push({
                                    type: 'text',
                                    element: el.tagName.toLowerCase(),
                                    selector: el.className || el.id || `${el.tagName.toLowerCase()}[${index}]`,
                                    contrast: Math.round(contrast * 100) / 100,
                                    textColor: textColor,
                                    bgColor: bgColor,
                                    required_ratio: requiredRatio,
                                    font_size: fontSize,
                                    is_large_text: isLargeText,
                                    text_sample: el.textContent.substring(0, 50)
                                });
                            }
                        });
                        
                        return violations;
                    }
                ''')
                
                results[theme] = violations
                
                # Take screenshot for visual verification
                await page.screenshot(path=f'contrast-check-{theme}.png')
            
            await browser.close()
            
            # Generate summary
            total_violations = sum(len(violations) for violations in results.values())
            critical_violations = sum(
                len([v for v in violations if v['contrast'] < 2.0]) 
                for violations in results.values()
            )
            
            return {
                'results': results,
                'summary': {
                    'total_violations': total_violations,
                    'critical_violations': critical_violations,
                    'themes_tested': list(results.keys()),
                    'wcag_compliance': total_violations == 0,
                    'screenshots_saved': [f'contrast-check-{theme}.png' for theme in results.keys()]
                },
                'fixes': self.generate_fix_css(results)
            }
    
    def generate_fix_css(self, violations: Dict[str, List[Dict]]) -> str:
        """Generate CSS fixes for contrast violations"""
        fixes = []
        fixes.append('/* PM33 Automated Contrast Fixes */')
        fixes.append('/* Apply these fixes to resolve WCAG 2.1 AA violations */\n')
        
        for theme, issues in violations.items():
            if not issues:
                continue
                
            fixes.append(f'/* Fixes for {theme} theme */')
            fixes.append(f'[data-theme="{theme}"] {{')
            
            # Group fixes by severity
            critical_fixes = [issue for issue in issues if issue['contrast'] < 2.0]
            moderate_fixes = [issue for issue in issues if 2.0 <= issue['contrast'] < issue['required_ratio']]
            
            if critical_fixes:
                fixes.append('  /* CRITICAL: Very low contrast - immediate fix required */')
                for issue in critical_fixes:
                    if theme == 'light':
                        color_fix = '#000000'  # Black text for light theme
                        bg_fix = '#ffffff'     # White background for light theme
                    else:
                        color_fix = '#ffffff'  # White text for dark theme  
                        bg_fix = '#1a202c'     # Dark background for dark theme
                    
                    if issue['type'] == 'text':
                        fixes.append(f'  .{issue["selector"]}, #{issue["selector"]} {{ color: {color_fix} !important; }}')
                    else:
                        fixes.append(f'  .{issue["selector"]}, #{issue["selector"]} {{')
                        fixes.append(f'    color: {color_fix} !important;')
                        fixes.append(f'    background-color: {bg_fix} !important;')
                        fixes.append('  }')
            
            if moderate_fixes:
                fixes.append('  /* MODERATE: Below WCAG standards - should be fixed */')
                for issue in moderate_fixes:
                    fixes.append(f'  /* {issue["element"]} - Current: {issue["contrast"]:.2f}, Required: {issue["required_ratio"]:.1f} */')
                    
            fixes.append('}\n')
        
        fixes.append('/* End PM33 Contrast Fixes */\n')
        
        return '\n'.join(fixes)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='PM33 Design Contract Validator')
    parser.add_argument('path', nargs='?', default='.', 
                       help='Component file or directory path')
    parser.add_argument('--strict', action='store_true',
                       help='Enable strict mode (warnings treated as errors)')
    parser.add_argument('--export', type=str, default='pm33_validation_report.json',
                       help='Export report to JSON file')
    parser.add_argument('--pattern', type=str, default='**/*.{tsx,jsx,css}',
                       help='File pattern for directory validation')
    parser.add_argument('--contrast-test', type=str, 
                       help='Run automated contrast validation on URL (requires Playwright)')
    parser.add_argument('--async-mode', action='store_true',
                       help='Enable async mode for Playwright contrast testing')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = PM33DesignValidator(strict_mode=args.strict)
    
    # Handle contrast testing
    if args.contrast_test:
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Error: Playwright required for contrast testing")
            print("Install with: pip install playwright && playwright install")
            return 1
        
        print(f"🎨 Running automated contrast validation on {args.contrast_test}")
        
        async def run_contrast_test():
            contrast_results = await validator.validate_contrast_automated(args.contrast_test)
            
            if 'error' in contrast_results:
                print(f"❌ Contrast test failed: {contrast_results['error']}")
                return 1
            
            # Print results
            summary = contrast_results['summary']
            print(f"✅ Themes tested: {', '.join(summary['themes_tested'])}")
            print(f"📊 Total violations: {summary['total_violations']}")
            print(f"🚨 Critical violations: {summary['critical_violations']}")
            print(f"✔️ WCAG 2.1 AA Compliant: {'YES' if summary['wcag_compliance'] else 'NO'}")
            
            if summary['total_violations'] > 0:
                print("\n📋 Violations by theme:")
                for theme, violations in contrast_results['results'].items():
                    if violations:
                        print(f"\n{theme.upper()} THEME ({len(violations)} issues):")
                        for v in violations[:5]:  # Show first 5
                            print(f"  • {v['type']} - {v['element']} (contrast: {v['contrast']:.2f}, required: {v['required_ratio']:.1f})")
                            print(f"    Text: '{v['text_sample']}' | Colors: {v['textColor']} on {v['bgColor']}")
                
                print(f"\n🔧 CSS Fixes saved to contrast-fixes.css")
                with open('contrast-fixes.css', 'w') as f:
                    f.write(contrast_results['fixes'])
            
            print(f"\n📷 Screenshots: {', '.join(summary['screenshots_saved'])}")
            return 0 if summary['wcag_compliance'] else 1
        
        if args.async_mode:
            import asyncio
            return asyncio.run(run_contrast_test())
        else:
            print("Use --async-mode flag to run contrast testing")
            return 1
    
    # Validate single file or directory
    if os.path.isfile(args.path):
        reports = [validator.validate_component(args.path)]
    elif os.path.isdir(args.path):
        reports = validator.validate_directory(args.path, args.pattern)
    else:
        print(f"❌ Error: Path not found: {args.path}")
        return 1
    
    # Print summary
    validator.print_summary(reports)
    
    # Export report if requested
    if args.export and reports:
        validator.export_report(reports, args.export)
    
    # Exit with error code if validation failed
    failed_count = len([r for r in reports if not r.passed])
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    exit(main())