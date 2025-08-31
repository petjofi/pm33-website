#!/usr/bin/env node

/**
 * PM33 Theme Toggle Validation
 * Validates all toggle elements, buttons, and navigation in both dark and light themes
 */

const fs = require('fs');
const path = require('path');

class ThemeToggleValidator {
  constructor() {
    this.violations = [];
    this.files = 0;
    this.components = [];
  }

  validateFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      this.checkToggleElements(lines, filePath);
      this.checkButtonElements(lines, filePath);
      this.checkNavigationElements(lines, filePath);
      this.checkThemeClasses(lines, filePath);
      this.checkGlassMorphism(lines, filePath);
      
      this.files++;
    } catch (error) {
      console.error(`❌ Error reading ${filePath}: ${error.message}`);
    }
  }

  checkToggleElements(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for toggle components
      if (line.includes('Toggle') || line.includes('Switch') || line.includes('toggle')) {
        this.components.push({ type: 'toggle', file: filePath, line: index + 1 });
        
        // Check for theme awareness
        if (!this.hasThemeSupport(line)) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'toggle_theme_support',
            severity: 'error',
            message: 'Toggle element missing dark/light theme support',
            suggestion: 'Add dark: classes and theme-conditional styling',
            current: line.trim(),
            recommended: 'Add dark:bg-gray-800 dark:text-white classes'
          });
        }
        
        // Check for proper toggle states
        if (!line.includes('checked') && !line.includes('value') && !line.includes('state')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'toggle_state_management',
            severity: 'warning',
            message: 'Toggle missing state management',
            suggestion: 'Add proper checked/value state handling',
            current: line.trim(),
            recommended: 'Add checked={isToggled} or similar state'
          });
        }
        
        // Check for accessibility
        if (!line.includes('aria-') && !line.includes('role=')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'toggle_accessibility',
            severity: 'warning',
            message: 'Toggle missing accessibility attributes',
            suggestion: 'Add aria-checked, role="switch", or aria-label',
            current: line.trim(),
            recommended: 'Add aria-checked={isToggled} aria-label="Toggle theme"'
          });
        }
      }
    });
  }

  checkButtonElements(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for button elements
      if (line.includes('<button') || line.includes('Button') || line.includes('btn')) {
        this.components.push({ type: 'button', file: filePath, line: index + 1 });
        
        // Check PM33 brand colors
        const hasBrandColors = this.hasPM33Colors(line);
        if (!hasBrandColors) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'button_brand_colors',
            severity: 'error',
            message: 'Button not using PM33 brand colors',
            suggestion: 'Use gradient from #667eea to #764ba2 or #10b981',
            current: line.trim(),
            recommended: 'bg-gradient-to-r from-[#667eea] to-[#764ba2]'
          });
        }
        
        // Check for hover states
        if (!line.includes('hover:') && !line.includes(':hover')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'button_hover_states',
            severity: 'error',
            message: 'Button missing hover states',
            suggestion: 'Add hover:scale-105 or hover:opacity-90',
            current: line.trim(),
            recommended: 'Add hover:scale-105 transition-transform'
          });
        }
        
        // Check for theme support in buttons
        if (!this.hasThemeSupport(line) && (line.includes('bg-') || line.includes('text-'))) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'button_theme_support',
            severity: 'error',
            message: 'Button colors not theme-aware',
            suggestion: 'Add dark: variants for all colors',
            current: line.trim(),
            recommended: 'Add dark:bg-gray-800 dark:text-white variants'
          });
        }
        
        // Check for professional shadows
        if (line.includes('shadow-sm') || (!line.includes('shadow-') && line.includes('shadow'))) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'button_professional_shadows',
            severity: 'error',
            message: 'Button using flat or minimal shadow',
            suggestion: 'Use shadow-lg, shadow-xl, or shadow-2xl for professional depth',
            current: line.trim(),
            recommended: 'Replace with shadow-xl'
          });
        }
      }
    });
  }

  checkNavigationElements(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for navigation components
      if (line.includes('nav') || line.includes('Nav') || line.includes('header') || 
          line.includes('Header') || line.includes('menu') || line.includes('Menu')) {
        this.components.push({ type: 'navigation', file: filePath, line: index + 1 });
        
        // Check for glass morphism
        if (!this.hasGlassMorphism(line)) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'nav_glass_morphism',
            severity: 'error',
            message: 'Navigation missing glass morphism effect',
            suggestion: 'Add backdrop-blur-lg and rgba background',
            current: line.trim(),
            recommended: 'Add bg-white/95 backdrop-blur-lg dark:bg-gray-900/95'
          });
        }
        
        // Check for consistent positioning
        if (line.includes('fixed') || line.includes('sticky')) {
          if (!line.includes('top-') && !line.includes('z-')) {
            this.violations.push({
              file: filePath,
              line: index + 1,
              rule: 'nav_positioning',
              severity: 'warning',
              message: 'Fixed navigation missing proper positioning',
              suggestion: 'Add top-0 and z-50 for consistent positioning',
              current: line.trim(),
              recommended: 'Add top-0 z-50 left-0 right-0'
            });
          }
        }
        
        // Check for theme toggle in navigation
        const navContent = this.getNavContent(lines, index);
        if (!navContent.includes('theme') && !navContent.includes('Toggle') && 
            !navContent.includes('dark') && !navContent.includes('light')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'nav_theme_toggle',
            severity: 'info',
            message: 'Navigation missing theme toggle component',
            suggestion: 'Consider adding theme toggle for user control',
            current: 'Navigation component',
            recommended: 'Add ThemeToggle component'
          });
        }
      }
    });
  }

  checkThemeClasses(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for theme class inconsistencies
      if (line.includes('dark:')) {
        const darkClasses = line.match(/dark:[a-zA-Z-]+/g) || [];
        const lightClasses = line.match(/(?:^|\s)(bg-|text-|border-)[a-zA-Z-]+(?:\s|$)/g) || [];
        
        // Check for light backgrounds with dark text in dark mode
        darkClasses.forEach(darkClass => {
          if (darkClass.includes('dark:bg-white') || darkClass.includes('dark:bg-gray-50')) {
            this.violations.push({
              file: filePath,
              line: index + 1,
              rule: 'dark_theme_light_backgrounds',
              severity: 'error',
              message: 'Dark theme using light backgrounds',
              suggestion: 'Use dark backgrounds (gray-800, gray-900, black) in dark mode',
              current: darkClass,
              recommended: 'dark:bg-gray-800 or dark:bg-gray-900'
            });
          }
          
          if (darkClass.includes('dark:text-black') || darkClass.includes('dark:text-gray-900')) {
            this.violations.push({
              file: filePath,
              line: index + 1,
              rule: 'dark_theme_dark_text',
              severity: 'error',
              message: 'Dark theme using dark text',
              suggestion: 'Use light text (white, gray-100, gray-200) in dark mode',
              current: darkClass,
              recommended: 'dark:text-white or dark:text-gray-100'
            });
          }
        });
        
        // Check for missing dark variants
        if (lightClasses.length > darkClasses.length) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'missing_dark_variants',
            severity: 'warning',
            message: 'Missing dark: variants for some colors',
            suggestion: 'Add dark: variants for all bg-, text-, and border- classes',
            current: line.trim(),
            recommended: 'Add corresponding dark: classes'
          });
        }
      }
      
      // Check for light theme violations
      if (line.includes('bg-gray-900') || line.includes('bg-black')) {
        if (!line.includes('dark:')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'light_theme_dark_backgrounds',
            severity: 'error',
            message: 'Light theme using dark backgrounds without theme conditioning',
            suggestion: 'Use light backgrounds or add dark: prefix',
            current: line.trim(),
            recommended: 'bg-white dark:bg-gray-900'
          });
        }
      }
    });
  }

  checkGlassMorphism(lines, filePath) {
    lines.forEach((line, index) => {
      // Check glass morphism implementation
      if (line.includes('glass') || line.includes('backdrop-blur') || 
          line.includes('bg-white/') || line.includes('bg-black/')) {
        
        // Check for proper backdrop blur
        if (line.includes('backdrop-blur') && !line.includes('backdrop-blur-lg') && 
            !line.includes('backdrop-blur-xl') && !line.includes('backdrop-blur-2xl')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'glass_morphism_blur',
            severity: 'warning',
            message: 'Glass morphism using weak blur effect',
            suggestion: 'Use backdrop-blur-lg or stronger for better glass effect',
            current: line.trim(),
            recommended: 'backdrop-blur-lg or backdrop-blur-xl'
          });
        }
        
        // Check for proper transparency
        if (line.includes('bg-white/') || line.includes('bg-black/')) {
          const transparencyMatch = line.match(/bg-(?:white|black)\/(\d+)/);
          if (transparencyMatch) {
            const transparency = parseInt(transparencyMatch[1]);
            if (transparency > 95 || transparency < 5) {
              this.violations.push({
                file: filePath,
                line: index + 1,
                rule: 'glass_morphism_transparency',
                severity: 'warning',
                message: 'Glass morphism transparency too extreme',
                suggestion: 'Use transparency between 10-90 for proper glass effect',
                current: transparencyMatch[0],
                recommended: 'bg-white/90 or bg-white/20'
              });
            }
          }
        }
        
        // Check for Safari compatibility
        if (line.includes('backdrop-blur') && !line.includes('-webkit-backdrop-filter')) {
          // This is more of a CSS check, but we can suggest it
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'glass_morphism_safari',
            severity: 'info',
            message: 'Consider Safari compatibility for backdrop-blur',
            suggestion: 'Ensure -webkit-backdrop-filter is included in CSS',
            current: line.trim(),
            recommended: 'Add -webkit-backdrop-filter in CSS'
          });
        }
      }
    });
  }

  hasThemeSupport(line) {
    return line.includes('dark:') || line.includes('light:') || 
           line.includes('theme') || line.includes('data-theme');
  }

  hasPM33Colors(line) {
    const pm33Colors = ['#667eea', '#764ba2', '#10b981', '667eea', '764ba2', '10b981'];
    return pm33Colors.some(color => line.includes(color)) ||
           line.includes('from-[#667eea]') ||
           line.includes('to-[#764ba2]') ||
           line.includes('bg-gradient');
  }

  hasGlassMorphism(line) {
    return line.includes('backdrop-blur') || 
           line.includes('bg-white/') || 
           line.includes('bg-black/') ||
           (line.includes('bg-') && (line.includes('/90') || line.includes('/95')));
  }

  getNavContent(lines, startIndex) {
    // Get a few lines of context around navigation
    const start = Math.max(0, startIndex - 2);
    const end = Math.min(lines.length, startIndex + 10);
    return lines.slice(start, end).join('\n');
  }

  generateReport() {
    const errors = this.violations.filter(v => v.severity === 'error');
    const warnings = this.violations.filter(v => v.severity === 'warning');
    const info = this.violations.filter(v => v.severity === 'info');

    console.log('\n' + '='.repeat(70));
    console.log('🎨 PM33 THEME TOGGLE & NAVIGATION VALIDATION REPORT');
    console.log('='.repeat(70));
    console.log(`📊 Files Scanned: ${this.files}`);
    console.log(`🔧 Components Found: ${this.components.length}`);
    console.log(`❌ Errors: ${errors.length}`);
    console.log(`⚠️  Warnings: ${warnings.length}`);
    console.log(`💡 Info: ${info.length}`);

    // Component breakdown
    const componentTypes = this.components.reduce((acc, comp) => {
      acc[comp.type] = (acc[comp.type] || 0) + 1;
      return acc;
    }, {});

    console.log('\n🔍 COMPONENT BREAKDOWN:');
    Object.entries(componentTypes).forEach(([type, count]) => {
      console.log(`   ${type}: ${count} components`);
    });

    if (errors.length > 0) {
      console.log('\n❌ CRITICAL THEME ERRORS (BLOCKING):');
      errors.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log(`    Current: ${violation.current.substring(0, 80)}...`);
        console.log(`    Fix: ${violation.recommended}`);
        console.log('');
      });
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  THEME WARNINGS:');
      warnings.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    // Theme compliance summary
    const themeErrors = errors.filter(e => e.rule.includes('theme'));
    const toggleErrors = errors.filter(e => e.rule.includes('toggle'));
    const navErrors = errors.filter(e => e.rule.includes('nav'));
    const buttonErrors = errors.filter(e => e.rule.includes('button'));

    console.log('\n📊 THEME COMPLIANCE SUMMARY:');
    console.log(`   Theme Support: ${themeErrors.length} errors`);
    console.log(`   Toggle Elements: ${toggleErrors.length} errors`);
    console.log(`   Navigation: ${navErrors.length} errors`);
    console.log(`   Buttons: ${buttonErrors.length} errors`);

    if (errors.length === 0 && warnings.length === 0) {
      console.log('\n✅ All theme toggles and navigation meet PM33 standards!');
      console.log('🎨 Dark/light theme compliance achieved');
    } else {
      console.log('\n🚨 REQUIRED ACTIONS:');
      console.log('   1. Fix all theme toggle elements for both dark and light modes');
      console.log('   2. Ensure buttons have proper hover states and brand colors');
      console.log('   3. Implement glass morphism on all navigation components');
      console.log('   4. Add proper dark: variants for all color classes');
      console.log('   5. Test visual consistency in both themes');
    }

    console.log('\n🎯 PM33 Theme Standards:');
    console.log('   • Dark Mode: Dark backgrounds (#0a0e27, #1e293b) + Light text');
    console.log('   • Light Mode: Light backgrounds (#ffffff, #f8fafc) + Dark text');
    console.log('   • Glass Morphism: backdrop-blur-lg with 90-95% opacity');
    console.log('   • Brand Colors: #667eea, #764ba2, #10b981 only');
    console.log('   • Professional Shadows: shadow-xl or shadow-2xl (no shadow-sm)');

    console.log('='.repeat(70));
    
    return errors.length === 0;
  }
}

// Main execution
function main() {
  console.log('🎨 Validating PM33 Theme Toggles & Navigation...');

  const validator = new ThemeToggleValidator();
  
  // Find files to validate
  function findFiles(dir, extensions) {
    let files = [];
    try {
      if (!require('fs').existsSync(dir)) return files;
      
      const items = require('fs').readdirSync(dir);
      items.forEach(item => {
        const fullPath = require('path').join(dir, item);
        const stat = require('fs').statSync(fullPath);
        
        if (stat.isDirectory() && !['node_modules', 'dist', 'build', '.next'].includes(item)) {
          files = files.concat(findFiles(fullPath, extensions));
        } else if (stat.isFile() && extensions.some(ext => item.endsWith(ext))) {
          files.push(fullPath);
        }
      });
    } catch (error) {
      // Directory doesn't exist, skip
    }
    return files;
  }

  // Find all UI files
  const extensions = ['.tsx', '.jsx'];
  const searchDirs = ['app', 'components', 'src', 'pages'];
  
  let allFiles = [];
  searchDirs.forEach(dir => {
    allFiles = allFiles.concat(findFiles(dir, extensions));
  });

  // Remove duplicates
  allFiles = [...new Set(allFiles)];

  if (allFiles.length === 0) {
    console.log('⚠️  No theme files found to validate');
    process.exit(0);
  }

  console.log(`🔍 Found ${allFiles.length} files to validate`);

  // Validate each file
  allFiles.forEach(file => {
    validator.validateFile(file);
  });

  // Generate report and exit
  const passed = validator.generateReport();
  process.exit(passed ? 0 : 1);
}

main();