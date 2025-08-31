#!/usr/bin/env python3
"""
PM33 Component Audit System
Analyzes component usage, duplication, and consistency
"""

import os
import glob
import re
from collections import defaultdict, Counter
from pathlib import Path
import json

def analyze_component_usage():
    """Analyze component usage patterns and identify issues"""
    print("🔍 PM33 Component Audit Starting...")
    
    # Find all component files
    component_files = []
    for pattern in ['**/*.tsx', '**/*.jsx']:
        component_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out node_modules
    component_files = [f for f in component_files if 'node_modules' not in f]
    
    print(f"📊 Found {len(component_files)} component files")
    
    # Analyze components
    components = {}
    imports = defaultdict(list)
    exports = defaultdict(list)
    violations = []
    
    for file_path in component_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component name
            component_name = Path(file_path).stem
            
            # Analyze component
            analysis = analyze_single_component(file_path, content)
            components[file_path] = analysis
            
            # Check for violations
            violations.extend(check_component_violations(file_path, content, analysis))
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    # Generate audit report
    generate_audit_report(components, violations)
    
    # Return status
    error_count = len([v for v in violations if v['severity'] == 'error'])
    return error_count == 0

def analyze_single_component(file_path, content):
    """Analyze individual component for PM33 compliance"""
    analysis = {
        'name': Path(file_path).stem,
        'path': file_path,
        'size_lines': len(content.split('\n')),
        'has_pm33_prefix': Path(file_path).stem.startswith('PM33'),
        'has_glass_morphism': bool(re.search(r'glass|backdrop-blur|backdrop-filter', content, re.IGNORECASE)),
        'has_gradients': bool(re.search(r'gradient|linear-gradient', content, re.IGNORECASE)),
        'has_hover_states': bool(re.search(r'hover:|:hover', content, re.IGNORECASE)),
        'imports': extract_imports(content),
        'exports': extract_exports(content),
        'brand_colors_used': extract_brand_colors(content),
        'spacing_compliance': check_spacing_compliance(content)
    }
    
    return analysis

def extract_imports(content):
    """Extract import statements"""
    imports = []
    import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
    matches = re.findall(import_pattern, content)
    return matches

def extract_exports(content):
    """Extract export statements"""
    exports = []
    export_patterns = [
        r'export\s+(?:default\s+)?(?:function|const|class)\s+(\w+)',
        r'export\s+{\s*([^}]+)\s*}',
        r'export\s+default\s+(\w+)'
    ]
    
    for pattern in export_patterns:
        matches = re.findall(pattern, content)
        exports.extend(matches)
    
    return exports

def extract_brand_colors(content):
    """Check for PM33 brand color usage"""
    brand_colors = {
        '#667eea': 'primary',
        '#764ba2': 'secondary', 
        '#10b981': 'success',
        '#ffffff': 'light_bg',
        '#0a0e27': 'dark_bg'
    }
    
    found_colors = {}
    for color, name in brand_colors.items():
        if color.lower() in content.lower():
            found_colors[color] = name
    
    return found_colors

def check_spacing_compliance(content):
    """Check 8px grid spacing compliance"""
    spacing_violations = []
    
    # Check for non-grid spacing values
    spacing_patterns = [
        r'p-(\d+)', r'px-(\d+)', r'py-(\d+)',
        r'm-(\d+)', r'mx-(\d+)', r'my-(\d+)',
        r'gap-(\d+)', r'space-[xy]-(\d+)'
    ]
    
    grid_values = {1: 4, 2: 8, 3: 12, 4: 16, 6: 24, 8: 32, 12: 48, 16: 64}  # Tailwind to px
    
    for pattern in spacing_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            value = int(match.group(1))
            px_value = grid_values.get(value, value * 4)  # Fallback calculation
            
            if px_value not in [4, 8, 16, 24, 32, 48, 64]:
                spacing_violations.append({
                    'pattern': match.group(),
                    'value': px_value,
                    'line': content[:match.start()].count('\n') + 1
                })
    
    return spacing_violations

def check_component_violations(file_path, content, analysis):
    """Check for PM33 design contract violations"""
    violations = []
    
    component_name = analysis['name']
    
    # Check for PM33 prefix on core components
    if (not analysis['has_pm33_prefix'] and 
        component_name not in ['index', 'page', 'layout', 'App'] and
        '/ui/' in file_path):
        violations.append({
            'file': file_path,
            'rule': 'pm33_prefix',
            'severity': 'warning',
            'message': f'Component {component_name} should use PM33 prefix for brand consistency',
            'suggestion': f'Rename to PM33{component_name}'
        })
    
    # Check for glass morphism on card components
    if ('card' in component_name.lower() and not analysis['has_glass_morphism']):
        violations.append({
            'file': file_path,
            'rule': 'glass_morphism',
            'severity': 'error',
            'message': f'Card component {component_name} missing glass morphism',
            'suggestion': 'Add backdrop-blur and glass styling'
        })
    
    # Check for gradient usage on headline components
    if (any(keyword in component_name.lower() for keyword in ['heading', 'title', 'hero']) and 
        not analysis['has_gradients']):
        violations.append({
            'file': file_path,
            'rule': 'gradient_text',
            'severity': 'error',
            'message': f'Headline component {component_name} missing gradient styling',
            'suggestion': 'Add gradient text or background'
        })
    
    # Check component size
    if analysis['size_lines'] > 200:
        violations.append({
            'file': file_path,
            'rule': 'component_size',
            'severity': 'warning',
            'message': f'Component {component_name} is {analysis["size_lines"]} lines - consider splitting',
            'suggestion': 'Break into smaller, focused components'
        })
    
    # Check for spacing violations
    if analysis['spacing_compliance']:
        violations.append({
            'file': file_path,
            'rule': 'spacing_grid',
            'severity': 'warning',
            'message': f'Component {component_name} has non-grid spacing',
            'suggestion': 'Use 8px grid system values only',
            'details': analysis['spacing_compliance']
        })
    
    return violations

def generate_audit_report(components, violations):
    """Generate comprehensive audit report"""
    print("\n" + "="*60)
    print("🎯 PM33 COMPONENT AUDIT REPORT")
    print("="*60)
    
    # Summary statistics
    total_components = len(components)
    pm33_prefixed = len([c for c in components.values() if c['has_pm33_prefix']])
    glass_morphism_count = len([c for c in components.values() if c['has_glass_morphism']])
    gradient_count = len([c for c in components.values() if c['has_gradients']])
    
    print(f"📊 Total Components: {total_components}")
    print(f"🏷️  PM33 Prefixed: {pm33_prefixed} ({pm33_prefixed/total_components*100:.1f}%)")
    print(f"✨ Glass Morphism: {glass_morphism_count} ({glass_morphism_count/total_components*100:.1f}%)")
    print(f"🌈 Gradients: {gradient_count} ({gradient_count/total_components*100:.1f}%)")
    
    # Violations summary
    errors = [v for v in violations if v['severity'] == 'error']
    warnings = [v for v in violations if v['severity'] == 'warning']
    
    print(f"\n❌ Errors: {len(errors)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    
    # Component size analysis
    large_components = [c for c in components.values() if c['size_lines'] > 200]
    if large_components:
        print(f"\n📏 Large Components ({len(large_components)}):")
        for comp in sorted(large_components, key=lambda x: x['size_lines'], reverse=True)[:5]:
            print(f"   {comp['name']}: {comp['size_lines']} lines")
    
    # Most common violations
    if violations:
        violation_types = Counter(v['rule'] for v in violations)
        print(f"\n🔍 Common Issues:")
        for rule, count in violation_types.most_common(5):
            print(f"   {rule}: {count} occurrences")
    
    # Brand color usage
    all_brand_colors = {}
    for comp in components.values():
        for color, name in comp['brand_colors_used'].items():
            all_brand_colors[name] = all_brand_colors.get(name, 0) + 1
    
    if all_brand_colors:
        print(f"\n🎨 Brand Color Usage:")
        for color, count in all_brand_colors.items():
            print(f"   {color}: {count} components")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if pm33_prefixed < total_components * 0.8:
        print("   • Add PM33 prefix to core components for brand consistency")
    if glass_morphism_count < total_components * 0.5:
        print("   • Implement glass morphism on more card/container components")
    if gradient_count < total_components * 0.3:
        print("   • Add gradient styling to headlines and key elements")
    
    # Export detailed report
    report_data = {
        'timestamp': str(os.popen('date').read().strip()),
        'summary': {
            'total_components': total_components,
            'pm33_prefixed': pm33_prefixed,
            'glass_morphism_count': glass_morphism_count,
            'gradient_count': gradient_count,
            'error_count': len(errors),
            'warning_count': len(warnings)
        },
        'components': components,
        'violations': violations
    }
    
    with open('component_audit_report.json', 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report exported to: component_audit_report.json")
    print("="*60)
    
    return len(errors) == 0

def run():
    """Main entry point"""
    success = analyze_component_usage()
    return 0 if success else 1

if __name__ == "__main__":
    exit(run())