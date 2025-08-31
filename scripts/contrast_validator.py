#!/usr/bin/env python3
"""
PM33 Marketing Website Pre-Commit Contrast Validator
Automated contrast validation for git pre-commit hooks
"""

import sys
import asyncio
import os
from pathlib import Path

# Add parent directory to path to import mcp_design_validator
sys.path.append(str(Path(__file__).parent.parent))

from mcp_design_validator import PM33DesignValidator, PLAYWRIGHT_AVAILABLE

async def main():
    """Run automated contrast validation for pre-commit hook"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️ Playwright not available - skipping contrast validation")
        print("Install with: pip install playwright && playwright install")
        return 0
    
    # Check if development server is running (marketing website typically runs on port 3000 or 3001)
    import requests
    
    # Try common marketing website ports
    test_urls = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002"
    ]
    
    working_url = None
    for url in test_urls:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                working_url = url
                break
        except requests.exceptions.RequestException:
            continue
    
    if not working_url:
        print("⚠️ Marketing website server not running - skipping contrast validation")
        print("Start server with: npm run dev (typically on port 3000)")
        return 0
    
    print(f"🎨 Running PM33 marketing website automated contrast validation on {working_url}...")
    
    # Initialize validator
    validator = PM33DesignValidator()
    
    try:
        # Run contrast validation
        results = await validator.validate_contrast_automated(working_url)
        
        if 'error' in results:
            print(f"❌ Contrast validation failed: {results['error']}")
            return 1
        
        summary = results['summary']
        
        # Print results
        print(f"✅ Themes tested: {', '.join(summary['themes_tested'])}")
        print(f"📊 Total violations: {summary['total_violations']}")
        print(f"🚨 Critical violations: {summary['critical_violations']}")
        print(f"✔️ WCAG 2.1 AA Compliant: {'YES' if summary['wcag_compliance'] else 'NO'}")
        
        if summary['total_violations'] > 0:
            print("\n❌ CONTRAST VIOLATIONS DETECTED!")
            print("📋 Violations by theme:")
            
            for theme, violations in results['results'].items():
                if violations:
                    print(f"\n{theme.upper()} THEME ({len(violations)} issues):")
                    for v in violations[:3]:  # Show first 3
                        print(f"  • {v['type']} - {v['element']} (contrast: {v['contrast']:.2f})")
                        print(f"    Text: '{v['text_sample'][:30]}...'")
                        print(f"    Colors: {v['textColor']} on {v['bgColor']}")
                        print(f"    Required: {v['required_ratio']:.1f}")
            
            # Save fixes
            print(f"\n🔧 CSS Fixes generated:")
            with open('marketing-contrast-fixes.css', 'w') as f:
                f.write(results['fixes'])
            print("   → marketing-contrast-fixes.css")
            
            print(f"\n📸 Screenshots saved:")
            for screenshot in summary['screenshots_saved']:
                print(f"   → {screenshot}")
            
            print("\n💡 TO FIX MARKETING WEBSITE:")
            print("1. Apply fixes from marketing-contrast-fixes.css")
            print("2. Review screenshots for visual verification")
            print("3. Test both light and dark themes manually")
            print("4. Update globals.css or component styles")
            print("5. Re-run: python scripts/contrast_validator.py")
            
            return 1
        
        else:
            print("✅ All marketing website contrast checks passed!")
            print("🎯 WCAG 2.1 AA compliance verified for marketing website")
            return 0
            
    except Exception as e:
        print(f"❌ Marketing website contrast validation error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)