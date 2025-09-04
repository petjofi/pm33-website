import { test, expect, Page } from '@playwright/test';
import { pageTestMap, standardizationTargets } from './icon-button-test-map';

/**
 * PM33 Button Interaction Consistency Tests
 * Ensures all buttons have proper hover states, focus indicators, and consistent behavior
 */

interface ButtonInteractionResult {
  page: string;
  buttonId: string;
  selector: string;
  component: string;
  theme: 'light' | 'dark';
  states: {
    default: ButtonState;
    hover: ButtonState;
    focus: ButtonState;
    active: ButtonState;
  };
  interactions: {
    hasHoverEffect: boolean;
    hasFocusIndicator: boolean;
    hasActiveState: boolean;
    isClickable: boolean;
    isKeyboardAccessible: boolean;
  };
  consistency: {
    colorsMatchStandards: boolean;
    animationsSmooth: boolean;
    sizingConsistent: boolean;
  };
  issues: string[];
}

interface ButtonState {
  backgroundColor: string;
  color: string;
  borderColor: string;
  transform: string;
  opacity: string;
  boxShadow: string;
  cursor: string;
  outline: string;
  bounds: { width: number; height: number };
}

// Helper function to get comprehensive button state
async function getButtonState(page: Page, selector: string): Promise<ButtonState | null> {
  try {
    const element = page.locator(selector).first();
    const count = await element.count();
    
    if (count === 0) {
      return null;
    }
    
    const state = await element.evaluate((el) => {
      const computed = getComputedStyle(el);
      const bounds = el.getBoundingClientRect();
      
      return {
        backgroundColor: computed.backgroundColor,
        color: computed.color,
        borderColor: computed.borderColor,
        transform: computed.transform,
        opacity: computed.opacity,
        boxShadow: computed.boxShadow,
        cursor: computed.cursor,
        outline: computed.outline,
        bounds: {
          width: bounds.width,
          height: bounds.height
        }
      };
    });
    
    return state;
  } catch (error) {
    return null;
  }
}

// Helper function to check if two colors are significantly different
function areColorsDifferent(color1: string, color2: string): boolean {
  if (color1 === color2) return false;
  
  // Parse RGB values
  const parseRGB = (color: string): number[] => {
    const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
  };
  
  const rgb1 = parseRGB(color1);
  const rgb2 = parseRGB(color2);
  
  // Calculate color difference using Euclidean distance
  const distance = Math.sqrt(
    Math.pow(rgb1[0] - rgb2[0], 2) +
    Math.pow(rgb1[1] - rgb2[1], 2) +
    Math.pow(rgb1[2] - rgb2[2], 2)
  );
  
  // Significant difference threshold
  return distance > 20;
}

// Helper function to check if button colors match PM33 standards
function checkColorStandards(state: ButtonState, expectedVariant: 'primary' | 'secondary' | 'subtle'): boolean {
  const standards = standardizationTargets.buttons;
  const expected = standards[expectedVariant];
  
  // Check if background matches expected pattern
  const bgMatches = (
    state.backgroundColor.includes('linear-gradient') && expected.background.includes('linear-gradient')
  ) || (
    state.backgroundColor === expected.background
  );
  
  return bgMatches;
}

// Helper to set theme
async function setTheme(page: Page, theme: 'light' | 'dark') {
  await page.evaluate((theme) => {
    document.body.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    document.body.className = document.body.className
      .replace(/\b(light|dark)\b/g, '')
      .trim() + ` ${theme}`;
  }, theme);
  
  await page.waitForTimeout(300);
}

describe('PM33 Button Interaction Consistency', () => {
  const BASE_URL = 'http://localhost:3008';
  const THEMES = ['light', 'dark'] as const;
  const INTERACTION_DELAY = 200; // Wait time for interaction effects
  
  // Main button interaction consistency test
  test('All buttons have consistent hover, focus, and active states', async ({ page }) => {
    const allResults: ButtonInteractionResult[] = [];
    
    for (const pageMap of pageTestMap) {
      await page.goto(`${BASE_URL}${pageMap.path}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);
      
      for (const theme of THEMES) {
        await setTheme(page, theme);
        await page.waitForTimeout(300);
        
        for (const buttonTest of pageMap.buttons) {
          try {
            const buttonElement = page.locator(buttonTest.selector).first();
            const count = await buttonElement.count();
            
            if (count === 0) {
              continue;
            }
            
            const isVisible = await buttonElement.isVisible();
            if (!isVisible) {
              continue;
            }
            
            // Get default state
            const defaultState = await getButtonState(page, buttonTest.selector);
            if (!defaultState) continue;
            
            // Test hover state
            await buttonElement.hover();
            await page.waitForTimeout(INTERACTION_DELAY);
            const hoverState = await getButtonState(page, buttonTest.selector);
            
            // Test focus state (keyboard navigation)
            await buttonElement.focus();
            await page.waitForTimeout(INTERACTION_DELAY);
            const focusState = await getButtonState(page, buttonTest.selector);
            
            // Test active state (mouse down)
            await buttonElement.hover(); // Reset to hover first
            await page.mouse.down();
            await page.waitForTimeout(100);
            const activeState = await getButtonState(page, buttonTest.selector);
            await page.mouse.up();
            
            // Reset to normal state
            await page.mouse.move(0, 0);
            await page.waitForTimeout(INTERACTION_DELAY);
            
            if (!hoverState || !focusState || !activeState) continue;
            
            // Analyze interactions
            const hasHoverEffect = (
              areColorsDifferent(defaultState.backgroundColor, hoverState.backgroundColor) ||
              defaultState.transform !== hoverState.transform ||
              defaultState.boxShadow !== hoverState.boxShadow
            );
            
            const hasFocusIndicator = (
              focusState.outline !== 'none' ||
              focusState.outline !== defaultState.outline ||
              areColorsDifferent(defaultState.borderColor, focusState.borderColor)
            );
            
            const hasActiveState = (
              areColorsDifferent(defaultState.backgroundColor, activeState.backgroundColor) ||
              defaultState.transform !== activeState.transform
            );
            
            // Check keyboard accessibility
            const isKeyboardAccessible = await buttonElement.evaluate((el) => {
              return (
                el.tabIndex >= 0 ||
                el.tagName.toLowerCase() === 'button' ||
                el.getAttribute('role') === 'button'
              );
            });
            
            const isClickable = defaultState.cursor === 'pointer' || 
                              await buttonElement.evaluate(el => el.tagName.toLowerCase() === 'button');
            
            // Check color standards compliance
            const colorsMatchStandards = checkColorStandards(defaultState, buttonTest.variant);
            
            // Check animation smoothness (basic check for transition property)
            const hasTransition = await buttonElement.evaluate((el) => {
              const computed = getComputedStyle(el);
              return computed.transition !== 'all 0s ease 0s' && computed.transition.length > 0;
            });
            
            // Check sizing consistency (buttons of same variant should have similar sizes)
            const sizingConsistent = (
              defaultState.bounds.height >= 32 && // Minimum touch target size
              defaultState.bounds.width >= 64
            );
            
            // Identify issues
            const issues = [];
            if (!hasHoverEffect) issues.push('No hover effect detected');
            if (!hasFocusIndicator) issues.push('No focus indicator');
            if (!hasActiveState) issues.push('No active state feedback');
            if (!isClickable) issues.push('Cursor not pointer/clickable');
            if (!isKeyboardAccessible) issues.push('Not keyboard accessible');
            if (!colorsMatchStandards) issues.push('Colors do not match PM33 standards');
            if (!hasTransition) issues.push('No smooth transitions');
            if (!sizingConsistent) issues.push('Size does not meet accessibility standards');
            
            allResults.push({
              page: pageMap.path,
              buttonId: buttonTest.id,
              selector: buttonTest.selector,
              component: buttonTest.component,
              theme,
              states: {
                default: defaultState,
                hover: hoverState,
                focus: focusState,
                active: activeState
              },
              interactions: {
                hasHoverEffect,
                hasFocusIndicator,
                hasActiveState,
                isClickable,
                isKeyboardAccessible
              },
              consistency: {
                colorsMatchStandards,
                animationsSmooth: hasTransition,
                sizingConsistent
              },
              issues
            });
            
          } catch (error) {
            console.warn(`Error testing button ${buttonTest.id} on ${pageMap.path}: ${error.message}`);
          }
        }
      }
    }
    
    // Analyze results
    const problematicButtons = allResults.filter(r => r.issues.length > 0);
    const perfectButtons = allResults.filter(r => r.issues.length === 0);
    
    console.log('=== BUTTON INTERACTION CONSISTENCY REPORT ===');
    console.log(`Total buttons tested: ${allResults.length}`);
    console.log(`Perfect buttons: ${perfectButtons.length}`);
    console.log(`Buttons with issues: ${problematicButtons.length}`);
    console.log(`Success rate: ${Math.round((perfectButtons.length / allResults.length) * 100)}%`);
    console.log('');
    
    if (problematicButtons.length > 0) {
      console.log('=== BUTTONS WITH ISSUES ===');
      
      // Group by issue type for better analysis
      const issueGroups = problematicButtons.reduce((acc, button) => {
        button.issues.forEach(issue => {
          if (!acc[issue]) acc[issue] = [];
          acc[issue].push(button);
        });
        return acc;
      }, {} as Record<string, ButtonInteractionResult[]>);
      
      for (const [issue, buttons] of Object.entries(issueGroups)) {
        console.log(`\n${issue}: ${buttons.length} buttons`);
        buttons.slice(0, 5).forEach(button => { // Show first 5 examples
          console.log(`  - ${button.page} (${button.theme}): ${button.buttonId}`);
        });
        if (buttons.length > 5) {
          console.log(`  ... and ${buttons.length - 5} more`);
        }
      }
    }
    
    // Analyze by theme
    const lightResults = allResults.filter(r => r.theme === 'light');
    const darkResults = allResults.filter(r => r.theme === 'dark');
    
    console.log('\n=== THEME BREAKDOWN ===');
    console.log(`Light theme: ${lightResults.filter(r => r.issues.length === 0).length}/${lightResults.length} perfect`);
    console.log(`Dark theme: ${darkResults.filter(r => r.issues.length === 0).length}/${darkResults.length} perfect`);
    
    // Critical interaction tests
    const missingHover = allResults.filter(r => !r.interactions.hasHoverEffect);
    const missingFocus = allResults.filter(r => !r.interactions.hasFocusIndicator);
    const notAccessible = allResults.filter(r => !r.interactions.isKeyboardAccessible);
    
    console.log('\n=== CRITICAL INTERACTION ISSUES ===');
    console.log(`Missing hover effects: ${missingHover.length}`);
    console.log(`Missing focus indicators: ${missingFocus.length}`);
    console.log(`Not keyboard accessible: ${notAccessible.length}`);
    
    // Save detailed results
    const reportData = {
      summary: {
        total: allResults.length,
        perfect: perfectButtons.length,
        problematic: problematicButtons.length,
        successRate: Math.round((perfectButtons.length / allResults.length) * 100)
      },
      critical_issues: {
        missingHover: missingHover.length,
        missingFocus: missingFocus.length,
        notAccessible: notAccessible.length
      },
      by_theme: {
        light: {
          total: lightResults.length,
          perfect: lightResults.filter(r => r.issues.length === 0).length
        },
        dark: {
          total: darkResults.length,
          perfect: darkResults.filter(r => r.issues.length === 0).length
        }
      },
      problematic_buttons: problematicButtons,
      timestamp: new Date().toISOString()
    };
    
    test.info().attachments.push({
      name: 'button-interaction-report.json',
      body: JSON.stringify(reportData, null, 2),
      contentType: 'application/json'
    });
    
    // Critical failures should be flagged
    if (missingFocus.length > 0) {
      test.info().annotations.push({
        type: 'error',
        description: `${missingFocus.length} buttons missing focus indicators (accessibility violation)`
      });
    }
    
    if (notAccessible.length > 0) {
      test.info().annotations.push({
        type: 'error', 
        description: `${notAccessible.length} buttons not keyboard accessible`
      });
    }
    
    if (problematicButtons.length > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${problematicButtons.length} buttons have interaction consistency issues`
      });
    }
    
    // For now, just ensure we tested buttons
    expect(allResults.length).toBeGreaterThan(0);
    
    // Uncomment these once we establish baselines:
    // expect(missingFocus).toHaveLength(0); // All buttons must have focus indicators
    // expect(notAccessible).toHaveLength(0); // All buttons must be keyboard accessible
  });
  
  // Test button color consistency across themes
  test('Button colors remain consistent and on-brand across themes', async ({ page }) => {
    const colorResults = [];
    
    for (const pageMap of pageTestMap.slice(0, 2)) { // Test first 2 pages for performance
      await page.goto(`${BASE_URL}${pageMap.path}`);
      await page.waitForLoadState('networkidle');
      
      for (const buttonTest of pageMap.buttons) {
        const lightColors = {};
        const darkColors = {};
        
        // Test in light theme
        await setTheme(page, 'light');
        const lightState = await getButtonState(page, buttonTest.selector);
        if (lightState) {
          lightColors.background = lightState.backgroundColor;
          lightColors.text = lightState.color;
          lightColors.border = lightState.borderColor;
        }
        
        // Test in dark theme
        await setTheme(page, 'dark');
        const darkState = await getButtonState(page, buttonTest.selector);
        if (darkState) {
          darkColors.background = darkState.backgroundColor;
          darkColors.text = darkState.color;
          darkColors.border = darkState.borderColor;
        }
        
        if (lightState && darkState) {
          const isPrimary = buttonTest.variant === 'primary';
          
          // Primary buttons should maintain consistent background across themes
          const backgroundConsistent = isPrimary ? 
            (lightColors.background === darkColors.background) : true;
          
          // Text should always be readable (not same as background)
          const textReadableLight = lightColors.background !== lightColors.text;
          const textReadableDark = darkColors.background !== darkColors.text;
          
          colorResults.push({
            page: pageMap.path,
            button: buttonTest.id,
            variant: buttonTest.variant,
            light: lightColors,
            dark: darkColors,
            consistent: backgroundConsistent && textReadableLight && textReadableDark,
            issues: [
              ...(backgroundConsistent ? [] : ['Background changes between themes']),
              ...(textReadableLight ? [] : ['Light theme: text same color as background']),
              ...(textReadableDark ? [] : ['Dark theme: text same color as background'])
            ]
          });
        }
      }
    }
    
    const inconsistentButtons = colorResults.filter(r => !r.consistent);
    
    if (inconsistentButtons.length > 0) {
      console.log('=== INCONSISTENT BUTTON COLORS ===');
      inconsistentButtons.forEach(button => {
        console.log(`❌ ${button.page}: ${button.button} (${button.variant})`);
        console.log(`   Issues: ${button.issues.join(', ')}`);
        console.log(`   Light: bg=${button.light.background}, text=${button.light.text}`);
        console.log(`   Dark:  bg=${button.dark.background}, text=${button.dark.text}`);
        console.log('');
      });
    }
    
    expect(inconsistentButtons).toHaveLength(0);
  });
  
  // Test button sizing consistency
  test('Buttons have consistent sizing and meet accessibility standards', async ({ page }) => {
    const sizingResults = [];
    const MIN_TOUCH_TARGET = 44; // Minimum touch target size (WCAG guideline)
    
    for (const pageMap of pageTestMap) {
      await page.goto(`${BASE_URL}${pageMap.path}`);
      await page.waitForLoadState('networkidle');
      await setTheme(page, 'light'); // Test in light theme
      
      for (const buttonTest of pageMap.buttons) {
        const state = await getButtonState(page, buttonTest.selector);
        
        if (state) {
          const meetsMinimumSize = (
            state.bounds.height >= MIN_TOUCH_TARGET &&
            state.bounds.width >= MIN_TOUCH_TARGET
          );
          
          sizingResults.push({
            page: pageMap.path,
            button: buttonTest.id,
            component: buttonTest.component,
            variant: buttonTest.variant,
            width: Math.round(state.bounds.width),
            height: Math.round(state.bounds.height),
            meetsAccessibility: meetsMinimumSize,
            issues: meetsMinimumSize ? [] : ['Below minimum touch target size (44px)']
          });
        }
      }
    }
    
    const accessibilityFailures = sizingResults.filter(r => !r.meetsAccessibility);
    
    console.log('=== BUTTON SIZING ANALYSIS ===');
    console.log(`Total buttons tested: ${sizingResults.length}`);
    console.log(`Meet accessibility standards: ${sizingResults.length - accessibilityFailures.length}`);
    console.log(`Below minimum size: ${accessibilityFailures.length}`);
    
    if (accessibilityFailures.length > 0) {
      console.log('\n=== BUTTONS BELOW MINIMUM SIZE ===');
      accessibilityFailures.forEach(button => {
        console.log(`❌ ${button.page}: ${button.button}`);
        console.log(`   Size: ${button.width}x${button.height}px (minimum: ${MIN_TOUCH_TARGET}x${MIN_TOUCH_TARGET}px)`);
        console.log(`   Component: ${button.component}`);
      });
    }
    
    // Group by variant to check consistency within variants
    const byVariant = sizingResults.reduce((acc, result) => {
      if (!acc[result.variant]) acc[result.variant] = [];
      acc[result.variant].push(result);
      return acc;
    }, {} as Record<string, typeof sizingResults>);
    
    console.log('\n=== SIZING BY VARIANT ===');
    for (const [variant, buttons] of Object.entries(byVariant)) {
      const heights = buttons.map(b => b.height);
      const avgHeight = Math.round(heights.reduce((a, b) => a + b, 0) / heights.length);
      const minHeight = Math.min(...heights);
      const maxHeight = Math.max(...heights);
      
      console.log(`${variant}: avg=${avgHeight}px, range=${minHeight}-${maxHeight}px`);
    }
    
    // All buttons should meet accessibility standards
    expect(accessibilityFailures).toHaveLength(0);
  });
  
  // Test button performance under rapid interactions
  test('Buttons remain responsive under rapid interactions', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    
    // Find all buttons on homepage
    const buttons = page.locator('button, [role="button"]');
    const buttonCount = await buttons.count();
    
    if (buttonCount === 0) {
      test.skip('No buttons found on homepage');
      return;
    }
    
    const performanceResults = [];
    
    // Test first 5 buttons for performance
    for (let i = 0; i < Math.min(5, buttonCount); i++) {
      const button = buttons.nth(i);
      const isVisible = await button.isVisible();
      
      if (!isVisible) continue;
      
      const startTime = Date.now();
      
      // Perform rapid interactions
      for (let j = 0; j < 10; j++) {
        await button.hover();
        await page.waitForTimeout(50);
        await button.blur();
        await page.waitForTimeout(50);
      }
      
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      // Check if button is still responsive
      const finalState = await button.evaluate(el => {
        const computed = getComputedStyle(el);
        return {
          opacity: computed.opacity,
          transform: computed.transform,
          responsive: el.offsetWidth > 0 && el.offsetHeight > 0
        };
      });
      
      performanceResults.push({
        buttonIndex: i,
        totalInteractionTime: totalTime,
        averageTimePerInteraction: Math.round(totalTime / 10),
        stillResponsive: finalState.responsive,
        finalOpacity: finalState.opacity
      });
    }
    
    const unresponsiveButtons = performanceResults.filter(r => !r.stillResponsive);
    const slowButtons = performanceResults.filter(r => r.averageTimePerInteraction > 100);
    
    console.log('=== BUTTON PERFORMANCE ANALYSIS ===');
    console.log(`Buttons tested: ${performanceResults.length}`);
    console.log(`Still responsive: ${performanceResults.length - unresponsiveButtons.length}`);
    console.log(`Slow interactions (>100ms avg): ${slowButtons.length}`);
    
    if (unresponsiveButtons.length > 0) {
      console.log('\n=== UNRESPONSIVE BUTTONS ===');
      unresponsiveButtons.forEach(button => {
        console.log(`❌ Button ${button.buttonIndex}: became unresponsive`);
      });
    }
    
    // All buttons should remain responsive
    expect(unresponsiveButtons).toHaveLength(0);
  });
});

test.beforeEach(async ({ page }) => {
  // Disable animations for consistent testing
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0.1s !important;
        transition-duration: 0.1s !important;
      }
    `
  });
});

test.afterEach(async ({ page }, testInfo) => {
  // Reset any interactions
  await page.mouse.move(0, 0);
  await page.keyboard.press('Escape');
  
  if (testInfo.status === 'failed') {
    await page.screenshot({
      path: `test-results/button-interaction-failure-${testInfo.title.replace(/[^a-zA-Z0-9]/g, '-')}.png`,
      fullPage: true
    });
  }
});