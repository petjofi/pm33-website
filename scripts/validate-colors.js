#!/usr/bin/env node

/**
 * PM33 Brand Color Validation
 * Enforces PM33 brand color palette across all UI components
 */

const fs = require('fs');
const path = require('path');

// PM33 Brand Color Rules
const COLOR_RULES = {
  brandColors: {
    '#667eea': 'PM33 Primary (Purple-blue)',
    '#764ba2': 'PM33 Secondary (Deep purple)',
    '#10b981': 'PM33 Success (Teal)',
    '#ffffff': 'Light background',
    '#0a0e27': 'Dark background',
    '#f8fafc': 'Light secondary',
    '#1e293b': 'Dark secondary',
    '#334155': 'Dark tertiary'
  },
  
  // Additional approved colors (system colors)
  systemColors: {
    '#000000': 'True black',
    '#ef4444': 'Error red', 
    '#f59e0b': 'Warning amber',
    '#3b82f6': 'Info blue',
    '#6b7280': 'Neutral gray',
    '#9ca3af': 'Light gray',
    '#d1d5db': 'Border gray',
    '#e5e7eb': 'Background gray',
    '#f3f4f6': 'Light background',
    '#1f2937': 'Dark text',
    '#374151': 'Medium gray',
    '#4b5563': 'Dark gray'
  },
  
  // Forbidden colors (common mistakes)
  forbiddenColors: {
    '#ff0000': 'Pure red (use #ef4444)',
    '#00ff00': 'Pure green (use #10b981)', 
    '#0000ff': 'Pure blue (use #3b82f6)',
    '#ffc0cb': 'Pink',
    '#800080': 'Purple (use #764ba2)',
    '#ffa500': 'Orange (use #f59e0b)',
    '#a52a2a': 'Brown',
    '#008080': 'Teal (use #10b981)'
  },
  
  getAllowedColors() {
    return {
      ...this.brandColors,
      ...this.systemColors
    };
  },
  
  isColorAllowed(color) {
    const normalizedColor = color.toLowerCase();
    const allowedColors = Object.keys(this.getAllowedColors()).map(c => c.toLowerCase());
    return allowedColors.includes(normalizedColor);
  },
  
  isForbidden(color) {
    const normalizedColor = color.toLowerCase();
    const forbiddenColors = Object.keys(this.forbiddenColors).map(c => c.toLowerCase());
    return forbiddenColors.includes(normalizedColor);
  },
  
  findClosestBrandColor(color) {
    const brandKeys = Object.keys(this.brandColors);
    // Simple closest color logic (in real implementation, would use color distance)
    if (color.includes('blue') || color.includes('indigo')) return '#667eea';
    if (color.includes('purple') || color.includes('violet')) return '#764ba2';
    if (color.includes('green') || color.includes('teal')) return '#10b981';
    return brandKeys[0]; // Default to primary
  }
};

class ColorValidator {
  constructor() {
    this.violations = [];
    this.files = 0;
    this.colorUsage = new Map();
  }

  validateFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      this.checkHexColors(lines, filePath);
      this.checkRgbColors(lines, filePath);
      this.checkNamedColors(lines, filePath);
      this.checkTailwindColors(lines, filePath);
      this.checkCSSVariables(lines, filePath);
      
      this.files++;
    } catch (error) {
      console.error(`❌ Error reading ${filePath}: ${error.message}`);
      process.exit(1);
    }
  }

  checkHexColors(lines, filePath) {
    const hexColorPattern = /#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = hexColorPattern.exec(line)) !== null) {
        const fullColor = match[0].toLowerCase();
        const shortColor = fullColor.length === 4 ? 
          `#${fullColor[1]}${fullColor[1]}${fullColor[2]}${fullColor[2]}${fullColor[3]}${fullColor[3]}` : 
          fullColor;
        
        this.trackColorUsage(shortColor, filePath);
        
        if (COLOR_RULES.isForbidden(shortColor)) {
          const suggestion = this.getSuggestedColor(shortColor);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'forbidden_color',
            severity: 'error',
            message: `Forbidden color: ${fullColor}`,
            suggestion: `Use approved color: ${suggestion}`,
            current: fullColor,
            recommended: suggestion
          });
        } else if (!COLOR_RULES.isColorAllowed(shortColor)) {
          const suggestion = COLOR_RULES.findClosestBrandColor(shortColor);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'unauthorized_color',
            severity: 'warning',
            message: `Unauthorized color: ${fullColor}`,
            suggestion: `Use brand color: ${suggestion}`,
            current: fullColor,
            recommended: suggestion
          });
        }
      }
    });
  }

  checkRgbColors(lines, filePath) {
    const rgbColorPattern = /rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = rgbColorPattern.exec(line)) !== null) {
        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);
        const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
        
        this.trackColorUsage(hexColor, filePath);
        
        if (!COLOR_RULES.isColorAllowed(hexColor)) {
          const suggestion = COLOR_RULES.findClosestBrandColor(hexColor);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'unauthorized_rgb_color',
            severity: 'warning',
            message: `Unauthorized RGB color: ${match[0]}`,
            suggestion: `Use brand color: ${suggestion}`,
            current: match[0],
            recommended: suggestion
          });
        }
      }
    });
  }

  checkNamedColors(lines, filePath) {
    const namedColors = [
      'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 
      'brown', 'gray', 'grey', 'black', 'white'
    ];
    
    lines.forEach((line, index) => {
      namedColors.forEach(color => {
        const colorPattern = new RegExp(`\\b${color}\\b`, 'gi');
        if (colorPattern.test(line)) {
          // Skip if it's part of a comment or in quotes (might be content)
          if (line.includes('//') || line.includes('/*') || 
              line.includes('"') || line.includes("'")) {
            return;
          }
          
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'named_color',
            severity: 'info',
            message: `Named color detected: ${color}`,
            suggestion: 'Use specific hex values for consistency',
            current: color,
            recommended: 'Specific hex value'
          });
        }
      });
    });
  }

  checkTailwindColors(lines, filePath) {
    // Check for non-brand Tailwind color classes
    const tailwindColorPattern = /(bg|text|border)-(red|green|blue|yellow|purple|pink|indigo|orange)-(\d+)/g;
    
    lines.forEach((line, index) => {
      let match;
      while ((match = tailwindColorPattern.exec(line)) !== null) {
        const colorClass = match[0];
        const colorName = match[2];
        
        // Allow certain system colors
        const allowedTailwindColors = ['red', 'green', 'blue', 'gray', 'slate'];
        
        if (!allowedTailwindColors.includes(colorName)) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'non_brand_tailwind',
            severity: 'warning',
            message: `Non-brand Tailwind color: ${colorClass}`,
            suggestion: 'Use CSS custom properties with brand colors',
            current: colorClass,
            recommended: 'Custom CSS variable'
          });
        }
      }
    });
  }

  checkCSSVariables(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for undefined CSS variables
      const cssVarPattern = /var\((--[a-zA-Z0-9-]+)\)/g;
      let match;
      
      while ((match = cssVarPattern.exec(line)) !== null) {
        const varName = match[1];
        
        // Check if it's a PM33 variable
        if (!varName.startsWith('--pm33-') && !varName.startsWith('--color-')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'non_pm33_variable',
            severity: 'info',
            message: `Non-PM33 CSS variable: ${varName}`,
            suggestion: 'Use --pm33- prefixed variables for brand consistency',
            current: varName,
            recommended: '--pm33-[property]'
          });
        }
      }
    });
  }

  trackColorUsage(color, filePath) {
    if (!this.colorUsage.has(color)) {
      this.colorUsage.set(color, []);
    }
    this.colorUsage.get(color).push(filePath);
  }

  getSuggestedColor(forbiddenColor) {
    const suggestions = {
      '#ff0000': '#ef4444', // red -> error red
      '#00ff00': '#10b981', // green -> PM33 success
      '#0000ff': '#667eea', // blue -> PM33 primary
      '#800080': '#764ba2', // purple -> PM33 secondary
      '#ffa500': '#f59e0b', // orange -> warning
      '#008080': '#10b981'  // teal -> PM33 success
    };
    
    return suggestions[forbiddenColor.toLowerCase()] || COLOR_RULES.findClosestBrandColor(forbiddenColor);
  }

  generateReport() {
    const errors = this.violations.filter(v => v.severity === 'error');
    const warnings = this.violations.filter(v => v.severity === 'warning');
    const info = this.violations.filter(v => v.severity === 'info');

    console.log('\n' + '='.repeat(60));
    console.log('🎨 PM33 BRAND COLOR VALIDATION REPORT');
    console.log('='.repeat(60));
    console.log(`📊 Files Scanned: ${this.files}`);
    console.log(`❌ Errors: ${errors.length}`);
    console.log(`⚠️  Warnings: ${warnings.length}`);
    console.log(`💡 Info: ${info.length}`);

    if (errors.length > 0) {
      console.log('\n❌ COLOR ERRORS (BLOCKING):');
      errors.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  COLOR WARNINGS:');
      warnings.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    // Show color usage statistics
    if (this.colorUsage.size > 0) {
      console.log('\n📊 COLOR USAGE ANALYSIS:');
      const sortedColors = Array.from(this.colorUsage.entries())
        .sort(([,a], [,b]) => b.length - a.length);
      
      sortedColors.slice(0, 10).forEach(([color, files]) => {
        const colorName = COLOR_RULES.brandColors[color] || COLOR_RULES.systemColors[color] || 'Unknown';
        console.log(`  ${color} (${colorName}): ${files.length} usage(s)`);
      });
      
      if (sortedColors.length > 10) {
        console.log(`  ... and ${sortedColors.length - 10} more colors`);
      }
    }

    if (errors.length === 0 && warnings.length === 0) {
      console.log('\n✅ All colors follow PM33 brand standards!');
      console.log('🎨 Brand color consistency maintained');
    }

    // Show brand color reference
    console.log('\n🌈 PM33 Brand Color Palette:');
    Object.entries(COLOR_RULES.brandColors).forEach(([hex, name]) => {
      console.log(`   ${hex} - ${name}`);
    });

    if (info.length > 0 && !process.argv.includes('--verbose')) {
      console.log('\n💡 Run with --verbose to see color suggestions');
    }

    console.log('='.repeat(60));
    
    return errors.length === 0;
  }
}

// Main execution
function main() {
  console.log('🎨 Validating PM33 Brand Colors...');

  const validator = new ColorValidator();
  
  // Find files to validate
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
      // Directory doesn't exist, skip
    }
    return files;
  }

  // Find all UI files
  const extensions = ['.tsx', '.jsx', '.css', '.scss'];
  const searchDirs = ['app', 'components', 'src', 'styles'];
  
  let allFiles = [];
  searchDirs.forEach(dir => {
    allFiles = allFiles.concat(findFiles(dir, extensions));
  });

  // Remove duplicates
  allFiles = [...new Set(allFiles)];

  if (allFiles.length === 0) {
    console.log('⚠️  No color files found to validate');
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