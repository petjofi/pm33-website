#!/usr/bin/env node

/**
 * PM33 Spacing Grid Validation
 * Enforces 8px grid system across all UI components
 */

const fs = require('fs');
const path = require('path');

// PM33 Spacing Grid Rules
const SPACING_GRID = {
  base: 8,
  allowed: [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 128, 160, 192, 224, 256],
  
  // Tailwind class to px mapping
  tailwindMap: {
    'p-0': 0, 'p-1': 4, 'p-2': 8, 'p-3': 12, 'p-4': 16, 'p-5': 20, 'p-6': 24,
    'p-8': 32, 'p-10': 40, 'p-12': 48, 'p-14': 56, 'p-16': 64, 'p-20': 80,
    'p-24': 96, 'p-32': 128, 'p-40': 160, 'p-48': 192, 'p-56': 224, 'p-64': 256,
    
    'm-0': 0, 'm-1': 4, 'm-2': 8, 'm-3': 12, 'm-4': 16, 'm-5': 20, 'm-6': 24,
    'm-8': 32, 'm-10': 40, 'm-12': 48, 'm-14': 56, 'm-16': 64, 'm-20': 80,
    'm-24': 96, 'm-32': 128, 'm-40': 160, 'm-48': 192, 'm-56': 224, 'm-64': 256,
    
    'gap-0': 0, 'gap-1': 4, 'gap-2': 8, 'gap-3': 12, 'gap-4': 16, 'gap-5': 20, 'gap-6': 24,
    'gap-8': 32, 'gap-10': 40, 'gap-12': 48, 'gap-14': 56, 'gap-16': 64, 'gap-20': 80,
    'gap-24': 96, 'gap-32': 128
  },
  
  validate(value) {
    return this.allowed.includes(value);
  },
  
  getClosest(value) {
    return this.allowed.reduce((prev, curr) => 
      Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev
    );
  },
  
  getTailwindClass(value, type = 'p') {
    const entries = Object.entries(this.tailwindMap);
    const match = entries.find(([key, val]) => key.startsWith(type) && val === value);
    return match ? match[0] : `${type}-[${value}px]`;
  }
};

class SpacingValidator {
  constructor() {
    this.violations = [];
    this.files = 0;
    this.autoFixMode = process.argv.includes('--fix');
  }

  validateFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      let modifiedContent = content;
      let hasChanges = false;
      
      this.checkCSSSpacing(lines, filePath);
      this.checkTailwindSpacing(lines, filePath);
      this.checkCustomSpacing(lines, filePath);
      
      // Auto-fix mode
      if (this.autoFixMode) {
        const { fixed, fixedContent } = this.autoFixSpacing(content);
        if (fixed) {
          fs.writeFileSync(filePath, fixedContent);
          console.log(`🔧 Auto-fixed spacing in: ${filePath}`);
          hasChanges = true;
        }
      }
      
      this.files++;
      return hasChanges;
    } catch (error) {
      console.error(`❌ Error reading ${filePath}: ${error.message}`);
      process.exit(1);
    }
  }

  checkCSSSpacing(lines, filePath) {
    const spacingPattern = /(?:padding|margin|gap|space)(?:-[trblxy])?:\s*(\d+)px/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = spacingPattern.exec(line)) !== null) {
        const value = parseInt(match[1]);
        if (!SPACING_GRID.validate(value)) {
          const closest = SPACING_GRID.getClosest(value);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'invalid_css_spacing',
            severity: 'error',
            message: `Invalid spacing: ${value}px (not on 8px grid)`,
            suggestion: `Use: ${closest}px (closest grid value)`,
            current: `${value}px`,
            recommended: `${closest}px`
          });
        }
      }
    });
  }

  checkTailwindSpacing(lines, filePath) {
    // Check for arbitrary Tailwind values that don't match grid
    const arbitrarySpacingPattern = /(?:p|m|gap)-\[(\d+)(?:px)?\]/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = arbitrarySpacingPattern.exec(line)) !== null) {
        const value = parseInt(match[1]);
        if (!SPACING_GRID.validate(value)) {
          const closest = SPACING_GRID.getClosest(value);
          const tailwindClass = SPACING_GRID.getTailwindClass(closest, match[0].charAt(0));
          
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'invalid_tailwind_spacing',
            severity: 'error',
            message: `Invalid Tailwind spacing: ${match[0]} (${value}px not on grid)`,
            suggestion: `Use: ${tailwindClass} (${closest}px)`,
            current: match[0],
            recommended: tailwindClass
          });
        }
      }
    });
  }

  checkCustomSpacing(lines, filePath) {
    // Check for hardcoded spacing in style attributes
    const styleSpacingPattern = /style=["'][^"']*(?:padding|margin|gap):\s*(\d+)px/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = styleSpacingPattern.exec(line)) !== null) {
        const value = parseInt(match[1]);
        if (!SPACING_GRID.validate(value)) {
          const closest = SPACING_GRID.getClosest(value);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'invalid_inline_spacing',
            severity: 'warning',
            message: `Inline spacing not on grid: ${value}px`,
            suggestion: `Use: ${closest}px or Tailwind classes`,
            current: `${value}px`,
            recommended: `${closest}px`
          });
        }
      }
    });
  }

  autoFixSpacing(content) {
    let fixedContent = content;
    let hasChanges = false;

    // Common spacing fixes
    const fixes = {
      // CSS fixes
      'padding: 5px': 'padding: 4px',
      'padding: 10px': 'padding: 8px',
      'padding: 15px': 'padding: 16px',
      'padding: 20px': 'padding: 24px',
      'padding: 25px': 'padding: 24px',
      'padding: 30px': 'padding: 32px',
      
      'margin: 5px': 'margin: 4px',
      'margin: 10px': 'margin: 8px',
      'margin: 15px': 'margin: 16px',
      'margin: 20px': 'margin: 24px',
      'margin: 25px': 'margin: 24px',
      'margin: 30px': 'margin: 32px',
      
      'gap: 5px': 'gap: 4px',
      'gap: 10px': 'gap: 8px',
      'gap: 15px': 'gap: 16px',
      'gap: 20px': 'gap: 24px',
      
      // Tailwind fixes
      'p-[5px]': 'p-1',
      'p-[10px]': 'p-2',
      'p-[15px]': 'p-4',
      'p-[20px]': 'p-5',
      'p-[25px]': 'p-6',
      'p-[30px]': 'p-8',
      
      'm-[5px]': 'm-1',
      'm-[10px]': 'm-2',
      'm-[15px]': 'm-4',
      'm-[20px]': 'm-5',
      'm-[25px]': 'm-6',
      'm-[30px]': 'm-8',
      
      'gap-[5px]': 'gap-1',
      'gap-[10px]': 'gap-2',
      'gap-[15px]': 'gap-4',
      'gap-[20px]': 'gap-5'
    };

    Object.entries(fixes).forEach(([wrong, correct]) => {
      const regex = new RegExp(wrong.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
      if (fixedContent.includes(wrong)) {
        fixedContent = fixedContent.replace(regex, correct);
        hasChanges = true;
      }
    });

    return { fixed: hasChanges, fixedContent };
  }

  generateReport() {
    const errors = this.violations.filter(v => v.severity === 'error');
    const warnings = this.violations.filter(v => v.severity === 'warning');

    console.log('\n' + '='.repeat(60));
    console.log('📏 PM33 SPACING GRID VALIDATION REPORT');
    console.log('='.repeat(60));
    console.log(`📊 Files Scanned: ${this.files}`);
    console.log(`❌ Errors: ${errors.length}`);
    console.log(`⚠️  Warnings: ${warnings.length}`);

    if (this.autoFixMode) {
      console.log(`🔧 Auto-fix Mode: ${this.autoFixMode ? 'ON' : 'OFF'}`);
    }

    if (errors.length > 0) {
      console.log('\n❌ SPACING GRID ERRORS (BLOCKING):');
      errors.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  SPACING WARNINGS:');
      warnings.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (errors.length === 0 && warnings.length === 0) {
      console.log('\n✅ All spacing follows 8px grid system!');
      console.log('📏 PM33 spacing standards maintained');
    }

    // Show 8px grid reference
    console.log('\n📐 PM33 8px Grid Reference:');
    console.log('   Allowed values: 0, 4, 8, 16, 24, 32, 48, 64, 96, 128px');
    console.log('   Tailwind: p-0, p-1, p-2, p-4, p-6, p-8, p-12, p-16, p-24, p-32');

    console.log('='.repeat(60));
    
    return errors.length === 0;
  }
}

// Main execution
function main() {
  console.log('📏 Validating PM33 Spacing Grid (8px System)...');

  const validator = new SpacingValidator();
  
  // Find files to validate
  const patterns = [
    'app/**/*.{tsx,jsx,css,scss}',
    'components/**/*.{tsx,jsx,css,scss}',
    'src/**/*.{tsx,jsx,css,scss}',
    'styles/**/*.{css,scss}'
  ];

  let allFiles = [];
  
  // Use simple directory traversal if glob is not available
  function findFiles(dir, extensions) {
    let files = [];
    try {
      if (!fs.existsSync(dir)) return files;
      
      const items = fs.readdirSync(dir);
      items.forEach(item => {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && !['node_modules', 'dist', 'build', '.next'].includes(item)) {
          files = files.concat(findFiles(fullPath, extensions));
        } else if (stat.isFile() && extensions.some(ext => item.endsWith(ext))) {
          files.push(fullPath);
        }
      });
    } catch (error) {
      // Directory doesn't exist or no permission, skip
    }
    return files;
  }

  // Find all UI files
  const extensions = ['.tsx', '.jsx', '.css', '.scss'];
  const searchDirs = ['app', 'components', 'src', 'styles'];
  
  searchDirs.forEach(dir => {
    allFiles = allFiles.concat(findFiles(dir, extensions));
  });

  // Remove duplicates
  allFiles = [...new Set(allFiles)];

  if (allFiles.length === 0) {
    console.log('⚠️  No UI files found to validate');
    
    // Check for common files
    const commonFiles = ['app/globals.css', 'src/index.css', 'styles/globals.css'];
    commonFiles.forEach(file => {
      if (fs.existsSync(file)) {
        allFiles.push(file);
      }
    });
    
    if (allFiles.length === 0) {
      console.log('✅ No spacing files found to validate');
      process.exit(0);
    }
  }

  console.log(`🔍 Found ${allFiles.length} files to validate`);

  // Validate each file
  allFiles.forEach(file => {
    validator.validateFile(file);
  });

  // Generate report and exit
  const passed = validator.generateReport();
  
  if (!passed) {
    console.log('\n💡 Run with --fix flag to auto-correct common spacing issues:');
    console.log('   node scripts/validate-spacing.js --fix');
  }
  
  process.exit(passed ? 0 : 1);
}

main();