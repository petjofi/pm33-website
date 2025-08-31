#!/usr/bin/env node

/**
 * PM33 Typography Validation
 * Enforces typography standards across all UI components
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// PM33 Typography Rules
const TYPOGRAPHY_RULES = {
  fonts: {
    allowed: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto'],
    forbidden: ['Times', 'Times New Roman', 'Arial', 'Comic Sans', 'serif', 'Helvetica']
  },
  sizes: {
    h1: [48, 56, 64],     // Large headlines
    h2: [32, 36, 40],     // Section headers  
    h3: [24, 28, 32],     // Subsection headers
    h4: [20, 24],         // Small headers
    h5: [18, 20],         // Captions
    h6: [16, 18],         // Smallest headers
    body: [14, 16, 18],   // Body text
    small: [12, 14]       // Small text
  },
  lineHeights: [1.2, 1.4, 1.5, 1.6, 1.75],
  fontWeights: [400, 500, 600, 700]  // normal, medium, semibold, bold
};

class TypographyValidator {
  constructor() {
    this.violations = [];
    this.files = 0;
  }

  validateFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      this.checkFontFamilies(lines, filePath);
      this.checkFontSizes(lines, filePath);
      this.checkFontWeights(lines, filePath);
      this.checkLineHeights(lines, filePath);
      
      this.files++;
    } catch (error) {
      console.error(`❌ Error reading ${filePath}: ${error.message}`);
      process.exit(1);
    }
  }

  checkFontFamilies(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for forbidden fonts
      TYPOGRAPHY_RULES.fonts.forbidden.forEach(font => {
        if (line.toLowerCase().includes(font.toLowerCase())) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'forbidden_font',
            severity: 'error',
            message: `Forbidden font family: ${font}`,
            suggestion: `Use approved fonts: ${TYPOGRAPHY_RULES.fonts.allowed.join(', ')}`
          });
        }
      });
      
      // Check for missing font fallbacks
      if (line.includes('font-family:') && !line.includes('system-ui')) {
        this.violations.push({
          file: filePath,
          line: index + 1,
          rule: 'missing_fallbacks',
          severity: 'warning',
          message: 'Missing system font fallbacks',
          suggestion: 'Include system-ui, -apple-system fallbacks'
        });
      }
    });
  }

  checkFontSizes(lines, filePath) {
    const fontSizePattern = /font-size:\s*(\d+)px|text-(\w+)/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = fontSizePattern.exec(line)) !== null) {
        if (match[1]) {  // Direct px value
          const size = parseInt(match[1]);
          const allAllowedSizes = Object.values(TYPOGRAPHY_RULES.sizes).flat();
          
          if (!allAllowedSizes.includes(size)) {
            const closestSize = this.findClosestValue(size, allAllowedSizes);
            this.violations.push({
              file: filePath,
              line: index + 1,
              rule: 'invalid_font_size',
              severity: 'error',
              message: `Non-standard font size: ${size}px`,
              suggestion: `Use approved size: ${closestSize}px`
            });
          }
        }
      }
    });
  }

  checkFontWeights(lines, filePath) {
    const fontWeightPattern = /font-weight:\s*(\d+)|font-(thin|light|normal|medium|semibold|bold|extrabold|black)/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = fontWeightPattern.exec(line)) !== null) {
        if (match[1]) {  // Numeric weight
          const weight = parseInt(match[1]);
          if (!TYPOGRAPHY_RULES.fontWeights.includes(weight)) {
            const closestWeight = this.findClosestValue(weight, TYPOGRAPHY_RULES.fontWeights);
            this.violations.push({
              file: filePath,
              line: index + 1,
              rule: 'invalid_font_weight',
              severity: 'warning',
              message: `Non-standard font weight: ${weight}`,
              suggestion: `Use approved weight: ${closestWeight}`
            });
          }
        }
      }
    });
  }

  checkLineHeights(lines, filePath) {
    const lineHeightPattern = /line-height:\s*([\d.]+)/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = lineHeightPattern.exec(line)) !== null) {
        const lineHeight = parseFloat(match[1]);
        if (!TYPOGRAPHY_RULES.lineHeights.includes(lineHeight)) {
          const closestHeight = this.findClosestValue(lineHeight, TYPOGRAPHY_RULES.lineHeights);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'invalid_line_height',
            severity: 'warning',
            message: `Non-standard line height: ${lineHeight}`,
            suggestion: `Use approved line height: ${closestHeight}`
          });
        }
      }
    });
  }

  findClosestValue(target, allowedValues) {
    return allowedValues.reduce((prev, curr) => 
      Math.abs(curr - target) < Math.abs(prev - target) ? curr : prev
    );
  }

  generateReport() {
    const errors = this.violations.filter(v => v.severity === 'error');
    const warnings = this.violations.filter(v => v.severity === 'warning');

    console.log('\n' + '='.repeat(60));
    console.log('📝 PM33 TYPOGRAPHY VALIDATION REPORT');
    console.log('='.repeat(60));
    console.log(`📊 Files Scanned: ${this.files}`);
    console.log(`❌ Errors: ${errors.length}`);
    console.log(`⚠️  Warnings: ${warnings.length}`);

    if (errors.length > 0) {
      console.log('\n❌ TYPOGRAPHY ERRORS (BLOCKING):');
      errors.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  TYPOGRAPHY WARNINGS:');
      warnings.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (errors.length === 0 && warnings.length === 0) {
      console.log('\n✅ All typography rules validated successfully!');
      console.log('🎨 PM33 typography standards maintained');
    }

    console.log('='.repeat(60));
    
    return errors.length === 0;
  }
}

// Main execution
function main() {
  console.log('📝 Validating PM33 Typography Standards...');

  const validator = new TypographyValidator();
  
  // Find all UI files
  const patterns = [
    'app/**/*.{tsx,jsx,css,scss}',
    'components/**/*.{tsx,jsx,css,scss}',
    'src/**/*.{tsx,jsx,css,scss}',
    'styles/**/*.{css,scss}'
  ];

  let allFiles = [];
  patterns.forEach(pattern => {
    try {
      const files = glob.sync(pattern, { 
        ignore: ['**/node_modules/**', '**/dist/**', '**/build/**', '**/.next/**']
      });
      allFiles = allFiles.concat(files);
    } catch (err) {
      // Pattern might not match, continue
    }
  });

  // Remove duplicates
  allFiles = [...new Set(allFiles)];

  if (allFiles.length === 0) {
    console.log('⚠️  No UI files found to validate');
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

// Handle missing glob dependency
try {
  require('glob');
  main();
} catch (error) {
  console.log('📝 Typography validation (basic mode - install glob for full validation)');
  
  // Basic validation without glob
  const validator = new TypographyValidator();
  
  // Check common files if they exist
  const commonFiles = [
    'app/globals.css',
    'src/index.css', 
    'styles/globals.css'
  ];

  let validatedAny = false;
  commonFiles.forEach(file => {
    if (fs.existsSync(file)) {
      validator.validateFile(file);
      validatedAny = true;
    }
  });

  if (validatedAny) {
    const passed = validator.generateReport();
    process.exit(passed ? 0 : 1);
  } else {
    console.log('✅ No common typography files found to validate');
    process.exit(0);
  }
}