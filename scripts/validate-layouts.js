#!/usr/bin/env node

/**
 * PM33 Layout System Validation
 * Enforces layout standards - containers, grids, flexbox
 */

const fs = require('fs');
const path = require('path');

// PM33 Layout Rules
const LAYOUT_RULES = {
  containers: {
    maxWidths: [640, 768, 1024, 1280, 1536], // Standard breakpoints
    padding: {
      mobile: 16,
      tablet: 24,
      desktop: 32
    },
    tailwindClasses: {
      640: 'max-w-xl',
      768: 'max-w-3xl', 
      1024: 'max-w-5xl',
      1280: 'max-w-7xl',
      1536: 'max-w-screen-2xl'
    }
  },
  
  grid: {
    columns: [1, 2, 3, 4, 5, 6, 8, 10, 12], // Allowed column counts
    gaps: [4, 8, 12, 16, 24, 32, 48, 64],    // Allowed gap values (px)
    tailwindGaps: {
      4: 'gap-1', 8: 'gap-2', 12: 'gap-3', 16: 'gap-4',
      24: 'gap-6', 32: 'gap-8', 48: 'gap-12', 64: 'gap-16'
    }
  },
  
  flexbox: {
    alignments: ['start', 'center', 'end', 'stretch', 'baseline'],
    justifications: ['start', 'center', 'end', 'between', 'around', 'evenly'],
    directions: ['row', 'col', 'row-reverse', 'col-reverse'],
    wraps: ['nowrap', 'wrap', 'wrap-reverse']
  }
};

class LayoutValidator {
  constructor() {
    this.violations = [];
    this.files = 0;
  }

  validateFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      this.checkContainers(lines, filePath);
      this.checkGridLayouts(lines, filePath);
      this.checkFlexboxLayouts(lines, filePath);
      this.checkResponsivePatterns(lines, filePath);
      
      this.files++;
    } catch (error) {
      console.error(`❌ Error reading ${filePath}: ${error.message}`);
      process.exit(1);
    }
  }

  checkContainers(lines, filePath) {
    lines.forEach((line, index) => {
      // Check max-width values
      const maxWidthPattern = /max-w(?:idth)?-\[(\d+)(?:px)?\]|max-w-(\w+)/g;
      let match;
      
      while ((match = maxWidthPattern.exec(line)) !== null) {
        if (match[1]) { // Custom width [500px]
          const width = parseInt(match[1]);
          if (!LAYOUT_RULES.containers.maxWidths.includes(width)) {
            const closest = this.findClosestValue(width, LAYOUT_RULES.containers.maxWidths);
            const tailwindClass = LAYOUT_RULES.containers.tailwindClasses[closest];
            
            this.violations.push({
              file: filePath,
              line: index + 1,
              rule: 'non_standard_container',
              severity: 'warning',
              message: `Non-standard container width: ${width}px`,
              suggestion: `Use standard width: ${closest}px (${tailwindClass})`,
              current: match[0],
              recommended: tailwindClass
            });
          }
        }
      }
      
      // Check for missing container classes on layout components
      if (line.includes('className=') && (
          line.includes('section') || 
          line.includes('main') || 
          line.includes('container')
        )) {
        if (!line.includes('max-w-') && !line.includes('container')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'missing_container',
            severity: 'info',
            message: 'Layout component missing container width',
            suggestion: 'Add max-width constraint (max-w-5xl recommended)',
            current: 'No container',
            recommended: 'max-w-5xl mx-auto'
          });
        }
      }
    });
  }

  checkGridLayouts(lines, filePath) {
    lines.forEach((line, index) => {
      // Check grid columns
      const gridColPattern = /grid-cols-(\d+)/g;
      let match;
      
      while ((match = gridColPattern.exec(line)) !== null) {
        const cols = parseInt(match[1]);
        if (!LAYOUT_RULES.grid.columns.includes(cols)) {
          const closest = this.findClosestValue(cols, LAYOUT_RULES.grid.columns);
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'invalid_grid_columns',
            severity: 'warning',
            message: `Non-standard grid columns: ${cols}`,
            suggestion: `Use approved columns: ${closest} (grid-cols-${closest})`,
            current: match[0],
            recommended: `grid-cols-${closest}`
          });
        }
      }
      
      // Check grid gaps
      const gapPattern = /gap-(\d+|\[(\d+)(?:px)?\])/g;
      while ((match = gapPattern.exec(line)) !== null) {
        let gapValue;
        
        if (match[2]) { // gap-[20px]
          gapValue = parseInt(match[2]);
        } else { // gap-4
          const tailwindValue = parseInt(match[1]);
          gapValue = tailwindValue * 4; // Convert Tailwind to px
        }
        
        if (!LAYOUT_RULES.grid.gaps.includes(gapValue)) {
          const closest = this.findClosestValue(gapValue, LAYOUT_RULES.grid.gaps);
          const tailwindClass = LAYOUT_RULES.grid.tailwindGaps[closest];
          
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'invalid_gap',
            severity: 'warning',
            message: `Non-standard gap: ${gapValue}px`,
            suggestion: `Use approved gap: ${closest}px (${tailwindClass})`,
            current: match[0],
            recommended: tailwindClass
          });
        }
      }
      
      // Check for grid without gap
      if (line.includes('grid-cols-') && !line.includes('gap-')) {
        this.violations.push({
          file: filePath,
          line: index + 1,
          rule: 'missing_grid_gap',
          severity: 'info',
          message: 'Grid layout missing gap spacing',
          suggestion: 'Add gap for visual hierarchy (gap-4 or gap-6 recommended)',
          current: 'No gap',
          recommended: 'gap-4'
        });
      }
    });
  }

  checkFlexboxLayouts(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for flex without direction on complex layouts
      if (line.includes('flex ') && line.includes('items-') && line.includes('justify-')) {
        if (!line.includes('flex-row') && !line.includes('flex-col')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'implicit_flex_direction',
            severity: 'info',
            message: 'Complex flex layout without explicit direction',
            suggestion: 'Add flex-row or flex-col for clarity',
            current: 'flex',
            recommended: 'flex flex-row'
          });
        }
      }
      
      // Check for non-standard alignment combinations
      const alignPattern = /items-(\w+)/;
      const justifyPattern = /justify-(\w+)/;
      
      const alignMatch = line.match(alignPattern);
      const justifyMatch = line.match(justifyPattern);
      
      if (alignMatch && !LAYOUT_RULES.flexbox.alignments.includes(alignMatch[1])) {
        this.violations.push({
          file: filePath,
          line: index + 1,
          rule: 'invalid_alignment',
          severity: 'warning',
          message: `Non-standard alignment: items-${alignMatch[1]}`,
          suggestion: `Use approved alignment: ${LAYOUT_RULES.flexbox.alignments.join(', ')}`,
          current: alignMatch[0],
          recommended: 'items-center'
        });
      }
      
      if (justifyMatch && !LAYOUT_RULES.flexbox.justifications.includes(justifyMatch[1])) {
        this.violations.push({
          file: filePath,
          line: index + 1,
          rule: 'invalid_justification',
          severity: 'warning',
          message: `Non-standard justification: justify-${justifyMatch[1]}`,
          suggestion: `Use approved justification: ${LAYOUT_RULES.flexbox.justifications.join(', ')}`,
          current: justifyMatch[0],
          recommended: 'justify-center'
        });
      }
    });
  }

  checkResponsivePatterns(lines, filePath) {
    lines.forEach((line, index) => {
      // Check for responsive grid patterns
      const responsiveGridPattern = /grid-cols-\d+.*(?:md|lg|xl):grid-cols-\d+/;
      if (line.includes('grid-cols-') && !responsiveGridPattern.test(line)) {
        // Only flag if it's a complex grid (3+ columns)
        const colMatch = line.match(/grid-cols-(\d+)/);
        if (colMatch && parseInt(colMatch[1]) >= 3) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'missing_responsive_grid',
            severity: 'info',
            message: 'Complex grid missing responsive breakpoints',
            suggestion: 'Add mobile-first responsive grid: grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
            current: colMatch[0],
            recommended: `grid-cols-1 md:grid-cols-2 lg:${colMatch[0]}`
          });
        }
      }
      
      // Check for responsive padding/margin
      if ((line.includes('p-') || line.includes('m-')) && 
          (line.includes('section') || line.includes('container'))) {
        if (!line.includes('md:') && !line.includes('lg:')) {
          this.violations.push({
            file: filePath,
            line: index + 1,
            rule: 'missing_responsive_spacing',
            severity: 'info',
            message: 'Layout container missing responsive spacing',
            suggestion: 'Add responsive spacing: p-4 md:p-6 lg:p-8',
            current: 'Static spacing',
            recommended: 'p-4 md:p-6 lg:p-8'
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
    const info = this.violations.filter(v => v.severity === 'info');

    console.log('\n' + '='.repeat(60));
    console.log('📐 PM33 LAYOUT SYSTEM VALIDATION REPORT');
    console.log('='.repeat(60));
    console.log(`📊 Files Scanned: ${this.files}`);
    console.log(`❌ Errors: ${errors.length}`);
    console.log(`⚠️  Warnings: ${warnings.length}`);
    console.log(`💡 Info: ${info.length}`);

    if (errors.length > 0) {
      console.log('\n❌ LAYOUT ERRORS (BLOCKING):');
      errors.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  LAYOUT WARNINGS:');
      warnings.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (info.length > 0 && process.argv.includes('--verbose')) {
      console.log('\n💡 LAYOUT SUGGESTIONS:');
      info.forEach(violation => {
        console.log(`  ${violation.file}:${violation.line}`);
        console.log(`    ${violation.message}`);
        console.log(`    💡 ${violation.suggestion}`);
        console.log('');
      });
    }

    if (errors.length === 0 && warnings.length === 0) {
      console.log('\n✅ All layout patterns follow PM33 standards!');
      console.log('📐 Layout system maintained');
    }

    // Show layout reference
    console.log('\n🏗️  PM33 Layout Reference:');
    console.log('   Containers: max-w-xl(640), max-w-3xl(768), max-w-5xl(1024), max-w-7xl(1280)');
    console.log('   Grid: 1, 2, 3, 4, 6, 12 columns with gap-2, gap-4, gap-6');
    console.log('   Responsive: Mobile-first with md:, lg:, xl: breakpoints');

    if (info.length > 0 && !process.argv.includes('--verbose')) {
      console.log('\n💡 Run with --verbose to see layout suggestions');
    }

    console.log('='.repeat(60));
    
    return errors.length === 0;
  }
}

// Main execution
function main() {
  console.log('📐 Validating PM33 Layout System...');

  const validator = new LayoutValidator();
  
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
  const extensions = ['.tsx', '.jsx'];
  const searchDirs = ['app', 'components', 'src', 'pages'];
  
  let allFiles = [];
  searchDirs.forEach(dir => {
    allFiles = allFiles.concat(findFiles(dir, extensions));
  });

  // Remove duplicates
  allFiles = [...new Set(allFiles)];

  if (allFiles.length === 0) {
    console.log('⚠️  No layout files found to validate');
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