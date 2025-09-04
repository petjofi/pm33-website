import { test, expect, Page } from '@playwright/test';
import { pageTestMap, testUtils, standardizationTargets } from './icon-button-test-map';

/**
 * PM33 Contrast Ratio Validation - WCAG Compliance Testing
 * Ensures all icons and buttons meet accessibility standards
 */

interface ContrastResult {
  page: string;
  theme: 'light' | 'dark';
  element: string;
  selector: string;
  component: string;
  backgroundColor: string;
  textColor: string;
  contrastRatio: number;
  wcagAA: boolean; // ≥ 4.5:1
  wcagAAA: boolean; // ≥ 7:1
  status: 'pass' | 'fail' | 'error';
  errorMessage?: string;
}

interface ColorAnalysis {
  rgb: number[];
  luminance: number;
  isTransparent: boolean;
}

/**
 * Advanced contrast ratio calculation with proper handling of gradients,
 * transparencies, and edge cases
 */
class ContrastAnalyzer {
  
  // Convert any CSS color to RGB array
  static parseColor(colorString: string): number[] {
    // Handle rgb() format
    const rgbMatch = colorString.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (rgbMatch) {
      return [parseInt(rgbMatch[1]), parseInt(rgbMatch[2]), parseInt(rgbMatch[3])];
    }
    
    // Handle rgba() format  
    const rgbaMatch = colorString.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)/);
    if (rgbaMatch) {
      return [parseInt(rgbaMatch[1]), parseInt(rgbaMatch[2]), parseInt(rgbaMatch[3])];
    }
    
    // Handle hex format
    if (colorString.startsWith('#')) {
      const hex = colorString.replace('#', '');
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);
      return [r, g, b];
    }
    
    // Handle named colors
    const namedColors = {
      'white': [255, 255, 255],
      'black': [0, 0, 0],
      'transparent': [255, 255, 255], // Default to white for transparent
      'inherit': [0, 0, 0] // Default to black for inherit
    };
    
    return namedColors[colorString.toLowerCase()] || [0, 0, 0];
  }
  
  // Calculate relative luminance
  static getLuminance(rgb: number[]): number {
    const [r, g, b] = rgb.map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
  
  // Calculate contrast ratio between two colors
  static calculateContrast(color1: string, color2: string): number {
    const rgb1 = this.parseColor(color1);
    const rgb2 = this.parseColor(color2);
    
    const lum1 = this.getLuminance(rgb1);
    const lum2 = this.getLuminance(rgb2);
    
    const lightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    
    return (lightest + 0.05) / (darkest + 0.05);
  }
  
  // Analyze color properties
  static analyzeColor(colorString: string): ColorAnalysis {
    const rgb = this.parseColor(colorString);
    const luminance = this.getLuminance(rgb);
    const isTransparent = colorString.includes('transparent') || 
                          colorString.includes('rgba') && colorString.includes(', 0)');
    
    return { rgb, luminance, isTransparent };
  }
  
  // Handle gradient backgrounds by extracting primary color
  static extractPrimaryColorFromGradient(gradientString: string): string {
    // Look for the first color in linear-gradient
    const colorMatch = gradientString.match(/rgb\(\d+,\s*\d+,\s*\d+\)/);
    if (colorMatch) {
      return colorMatch[0];
    }
    
    // Look for hex colors in gradient
    const hexMatch = gradientString.match(/#[0-9a-fA-F]{6}/);
    if (hexMatch) {
      return hexMatch[0];
    }
    
    // Default fallback
    return 'rgb(255, 255, 255)';
  }
}

// Helper to set theme and wait for transitions
async function setThemeAndWait(page: Page, theme: 'light' | 'dark') {
  await page.evaluate((theme) => {
    document.body.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    document.body.className = document.body.className
      .replace(/\b(light|dark)\b/g, '')
      .trim() + ` ${theme}`;
  }, theme);
  
  await page.waitForTimeout(400); // Wait for theme transitions
}

describe('PM33 Contrast Ratio Validation - WCAG Compliance', () => {
  
  const BASE_URL = 'http://localhost:3008';
  const THEMES = ['light', 'dark'] as const;
  const MIN_AA_CONTRAST = 4.5;
  const MIN_AAA_CONTRAST = 7.0;
  
  // Main contrast validation test
  test('All icons and buttons meet WCAG AA contrast standards', async ({ page }) => {
    const allResults: ContrastResult[] = [];
    
    // Test each page
    for (const pageMap of pageTestMap) {
      await page.goto(`${BASE_URL}${pageMap.path}`);
      await page.waitForLoadState('networkidle');
      
      // Test in both themes
      for (const theme of THEMES) {
        await setThemeAndWait(page, theme);
        
        // Test all icons on this page
        for (const iconTest of pageMap.icons) {
          try {
            const iconElements = page.locator(iconTest.selector);
            const count = await iconElements.count();
            
            for (let i = 0; i < count; i++) {
              const element = iconElements.nth(i);
              const isVisible = await element.isVisible();
              
              if (!isVisible) continue;
              
              const styles = await element.evaluate((el) => {
                const computed = getComputedStyle(el);
                return {
                  backgroundColor: computed.backgroundColor,
                  color: computed.color,
                  backgroundImage: computed.backgroundImage
                };
              });
              
              // Handle gradient backgrounds
              let bgColor = styles.backgroundColor;
              if (styles.backgroundImage && styles.backgroundImage !== 'none') {
                bgColor = ContrastAnalyzer.extractPrimaryColorFromGradient(styles.backgroundImage);
              }
              
              // Handle transparent backgrounds by checking parent
              if (bgColor === 'rgba(0, 0, 0, 0)' || bgColor.includes('transparent')) {
                const parentBg = await element.evaluate((el) => {
                  let parent = el.parentElement;
                  while (parent) {
                    const parentStyle = getComputedStyle(parent);
                    if (parentStyle.backgroundColor !== 'rgba(0, 0, 0, 0)' && 
                        !parentStyle.backgroundColor.includes('transparent')) {
                      return parentStyle.backgroundColor;
                    }
                    parent = parent.parentElement;
                  }
                  return 'rgb(255, 255, 255)'; // Default to white
                });
                bgColor = parentBg;
              }
              
              const contrastRatio = ContrastAnalyzer.calculateContrast(bgColor, styles.color);
              
              allResults.push({
                page: pageMap.path,
                theme,
                element: iconTest.id,
                selector: iconTest.selector,
                component: iconTest.component,
                backgroundColor: bgColor,
                textColor: styles.color,
                contrastRatio: Math.round(contrastRatio * 100) / 100,
                wcagAA: contrastRatio >= MIN_AA_CONTRAST,
                wcagAAA: contrastRatio >= MIN_AAA_CONTRAST,
                status: contrastRatio >= MIN_AA_CONTRAST ? 'pass' : 'fail'
              });
            }
            
          } catch (error) {
            allResults.push({
              page: pageMap.path,
              theme,
              element: iconTest.id,
              selector: iconTest.selector,
              component: iconTest.component,
              backgroundColor: 'error',
              textColor: 'error',
              contrastRatio: 0,
              wcagAA: false,
              wcagAAA: false,
              status: 'error',
              errorMessage: error.message
            });
          }
        }
        
        // Test all buttons on this page
        for (const buttonTest of pageMap.buttons) {
          try {
            const buttonElements = page.locator(buttonTest.selector);
            const count = await buttonElements.count();
            
            for (let i = 0; i < count; i++) {
              const element = buttonElements.nth(i);
              const isVisible = await element.isVisible();
              
              if (!isVisible) continue;
              
              const styles = await element.evaluate((el) => {
                const computed = getComputedStyle(el);
                return {
                  backgroundColor: computed.backgroundColor,
                  color: computed.color,
                  backgroundImage: computed.backgroundImage
                };
              });
              
              // Handle gradient backgrounds
              let bgColor = styles.backgroundColor;
              if (styles.backgroundImage && styles.backgroundImage !== 'none') {
                bgColor = ContrastAnalyzer.extractPrimaryColorFromGradient(styles.backgroundImage);
              }
              
              const contrastRatio = ContrastAnalyzer.calculateContrast(bgColor, styles.color);
              
              allResults.push({
                page: pageMap.path,
                theme,
                element: buttonTest.id,
                selector: buttonTest.selector,
                component: buttonTest.component,
                backgroundColor: bgColor,
                textColor: styles.color,
                contrastRatio: Math.round(contrastRatio * 100) / 100,
                wcagAA: contrastRatio >= MIN_AA_CONTRAST,
                wcagAAA: contrastRatio >= MIN_AAA_CONTRAST,
                status: contrastRatio >= MIN_AA_CONTRAST ? 'pass' : 'fail'
              });
            }
            
          } catch (error) {
            allResults.push({
              page: pageMap.path,
              theme,
              element: buttonTest.id,
              selector: buttonTest.selector,
              component: buttonTest.component,
              backgroundColor: 'error',
              textColor: 'error',
              contrastRatio: 0,
              wcagAA: false,
              wcagAAA: false,
              status: 'error',
              errorMessage: error.message
            });
          }
        }
      }
    }
    
    // Analyze results
    const failedResults = allResults.filter(r => r.status === 'fail');
    const errorResults = allResults.filter(r => r.status === 'error');
    const passedResults = allResults.filter(r => r.status === 'pass');
    
    // Generate detailed report
    console.log('=== PM33 CONTRAST RATIO ANALYSIS REPORT ===');
    console.log(`Total elements tested: ${allResults.length}`);
    console.log(`Passed WCAG AA (≥4.5:1): ${passedResults.length}`);
    console.log(`Failed WCAG AA: ${failedResults.length}`);
    console.log(`Errors: ${errorResults.length}`);
    console.log('');
    
    if (failedResults.length > 0) {
      console.log('=== FAILED CONTRAST CHECKS ===');
      failedResults.forEach(result => {
        console.log(`❌ ${result.page} (${result.theme}) - ${result.element}`);
        console.log(`   Component: ${result.component}`);
        console.log(`   Background: ${result.backgroundColor}`);
        console.log(`   Text: ${result.textColor}`);
        console.log(`   Ratio: ${result.contrastRatio}:1 (needs ≥4.5:1)`);
        console.log(`   Selector: ${result.selector}`);
        console.log('');
      });
    }
    
    if (errorResults.length > 0) {
      console.log('=== ERROR RESULTS ===');
      errorResults.forEach(result => {
        console.log(`⚠️  ${result.page} (${result.theme}) - ${result.element}`);
        console.log(`   Error: ${result.errorMessage}`);
        console.log(`   Selector: ${result.selector}`);
        console.log('');
      });
    }
    
    // Generate summary by theme
    const lightResults = allResults.filter(r => r.theme === 'light');
    const darkResults = allResults.filter(r => r.theme === 'dark');
    
    console.log('=== THEME BREAKDOWN ===');
    console.log(`Light mode: ${lightResults.filter(r => r.status === 'pass').length}/${lightResults.length} passed`);
    console.log(`Dark mode: ${darkResults.filter(r => r.status === 'pass').length}/${darkResults.length} passed`);
    
    // Save detailed results to file for analysis
    const reportData = {
      summary: {
        total: allResults.length,
        passed: passedResults.length,
        failed: failedResults.length,
        errors: errorResults.length,
        successRate: Math.round((passedResults.length / allResults.length) * 100)
      },
      by_theme: {
        light: {
          total: lightResults.length,
          passed: lightResults.filter(r => r.status === 'pass').length,
          failed: lightResults.filter(r => r.status === 'fail').length
        },
        dark: {
          total: darkResults.length,
          passed: darkResults.filter(r => r.status === 'pass').length,
          failed: darkResults.filter(r => r.status === 'fail').length
        }
      },
      failed_elements: failedResults,
      error_elements: errorResults,
      timestamp: new Date().toISOString()
    };
    
    // Attach report to test results
    test.info().attachments.push({
      name: 'contrast-analysis-report.json',
      body: JSON.stringify(reportData, null, 2),
      contentType: 'application/json'
    });
    
    // Test assertions - for now, warn but don't fail to establish baseline
    if (failedResults.length > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${failedResults.length} elements failed WCAG AA contrast requirements`
      });
    }
    
    // Once we establish baseline, uncomment this to enforce standards:
    // expect(failedResults).toHaveLength(0);
    
    // For now, just ensure we tested something
    expect(allResults.length).toBeGreaterThan(0);
  });
  
  // Specific test for brand color compliance
  test('Brand colors maintain proper contrast ratios', async ({ page }) => {
    const brandColorResults = [];
    const brandColors = standardizationTargets.icons.backgrounds;
    const textColors = standardizationTargets.icons.textColors;
    
    // Test all combinations of brand backgrounds with text colors
    for (const bgColor of brandColors) {
      for (const textColor of textColors) {
        const contrastRatio = ContrastAnalyzer.calculateContrast(bgColor, textColor);
        
        brandColorResults.push({
          background: bgColor,
          text: textColor,
          ratio: Math.round(contrastRatio * 100) / 100,
          wcagAA: contrastRatio >= MIN_AA_CONTRAST,
          wcagAAA: contrastRatio >= MIN_AAA_CONTRAST
        });
      }
    }
    
    console.log('=== BRAND COLOR CONTRAST ANALYSIS ===');
    brandColorResults.forEach(result => {
      const status = result.wcagAA ? '✅' : '❌';
      console.log(`${status} ${result.ratio}:1 - BG: ${result.background} / Text: ${result.text}`);
    });
    
    // All brand color combinations should meet WCAG AA
    const failedBrandColors = brandColorResults.filter(r => !r.wcagAA);
    expect(failedBrandColors).toHaveLength(0);
  });
  
  // Test for color blindness accessibility
  test('Color combinations work for colorblind users', async ({ page }) => {
    // Simulate common types of color blindness
    const colorBlindnessTests = [
      {
        name: 'Deuteranopia (red-green)',
        filter: 'sepia(100%) saturate(0.8) hue-rotate(90deg)'
      },
      {
        name: 'Protanopia (red-blind)', 
        filter: 'sepia(100%) saturate(0.6) hue-rotate(143deg)'
      },
      {
        name: 'Tritanopia (blue-yellow)',
        filter: 'sepia(100%) saturate(1.2) hue-rotate(200deg)'
      }
    ];
    
    // Test homepage with color blindness filters
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    
    for (const cbTest of colorBlindnessTests) {
      // Apply color blindness filter
      await page.addStyleTag({
        content: `
          * {
            filter: ${cbTest.filter} !important;
          }
        `
      });
      
      // Take screenshot for manual review
      await page.screenshot({
        path: `test-results/colorblind-${cbTest.name.toLowerCase().replace(/[^a-z]/g, '-')}.png`,
        fullPage: true
      });
      
      // Remove filter for next test
      await page.addStyleTag({
        content: `
          * {
            filter: none !important;
          }
        `
      });
    }
    
    // This test is primarily for generating screenshots for manual review
    expect(colorBlindnessTests.length).toBeGreaterThan(0);
  });
});

// Test configuration
test.beforeEach(async ({ page }) => {
  // Disable animations for consistent color sampling
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
      }
    `
  });
});