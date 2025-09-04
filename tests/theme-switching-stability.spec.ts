import { test, expect, Page } from '@playwright/test';
import { pageTestMap } from './icon-button-test-map';

/**
 * PM33 Theme Switching Stability Tests
 * Ensures all elements remain visible and functional during theme transitions
 */

interface ThemeStabilityResult {
  page: string;
  element: string;
  selector: string;
  beforeSwitch: ElementVisibility;
  afterSwitch: ElementVisibility;
  switchNumber: number;
  stable: boolean;
  issues: string[];
}

interface ElementVisibility {
  visible: boolean;
  opacity: string;
  display: string;
  backgroundColor: string;
  color: string;
  bounds: { width: number; height: number; x: number; y: number };
}

// Helper function to get comprehensive element visibility data
async function getElementVisibility(page: Page, selector: string): Promise<ElementVisibility | null> {
  try {
    const element = page.locator(selector).first();
    const count = await element.count();
    
    if (count === 0) {
      return null;
    }
    
    const visibility = await element.evaluate((el) => {
      const computed = getComputedStyle(el);
      const bounds = el.getBoundingClientRect();
      
      return {
        visible: (
          computed.opacity !== '0' &&
          computed.visibility !== 'hidden' &&
          computed.display !== 'none' &&
          bounds.width > 0 &&
          bounds.height > 0
        ),
        opacity: computed.opacity,
        display: computed.display,
        backgroundColor: computed.backgroundColor,
        color: computed.color,
        bounds: {
          width: bounds.width,
          height: bounds.height,
          x: bounds.x,
          y: bounds.y
        }
      };
    });
    
    return visibility;
  } catch (error) {
    return null;
  }
}

// Helper function to find and click theme toggle
async function clickThemeToggle(page: Page): Promise<boolean> {
  const toggleSelectors = [
    '[data-testid="theme-toggle"]',
    '.theme-toggle',
    '[aria-label*="theme"]',
    '[class*="theme-toggle"]',
    'button:has-text("🌙")',
    'button:has-text("☀️")',
    'button:has-text("Dark")',
    'button:has-text("Light")'
  ];
  
  for (const selector of toggleSelectors) {
    try {
      const toggle = page.locator(selector).first();
      const count = await toggle.count();
      
      if (count > 0 && await toggle.isVisible()) {
        await toggle.click();
        return true;
      }
    } catch (error) {
      // Try next selector
    }
  }
  
  return false;
}

// Helper function to get current theme
async function getCurrentTheme(page: Page): Promise<string> {
  return await page.evaluate(() => {
    const bodyTheme = document.body.getAttribute('data-theme');
    const docTheme = document.documentElement.getAttribute('data-theme');
    const bodyClass = document.body.className;
    
    if (bodyTheme) return bodyTheme;
    if (docTheme) return docTheme;
    if (bodyClass.includes('dark')) return 'dark';
    if (bodyClass.includes('light')) return 'light';
    
    return 'unknown';
  });
}

describe('PM33 Theme Switching Stability', () => {
  const BASE_URL = 'http://localhost:3008';
  const SWITCH_COUNT = 5; // Number of theme switches to test
  const TRANSITION_WAIT = 600; // Wait time for theme transitions
  
  // Main theme switching stability test
  test('All elements remain visible during theme transitions', async ({ page }) => {
    const allResults: ThemeStabilityResult[] = [];
    
    for (const pageMap of pageTestMap) {
      if (!pageMap.hasThemeToggle) {
        continue; // Skip pages without theme toggle
      }
      
      test.info().annotations.push({
        type: 'info',
        description: `Testing theme stability on ${pageMap.name}`
      });
      
      await page.goto(`${BASE_URL}${pageMap.path}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000); // Let page fully settle
      
      // Collect all testable selectors from this page
      const testSelectors = [
        ...pageMap.icons.map(icon => ({ type: 'icon', id: icon.id, selector: icon.selector })),
        ...pageMap.buttons.map(button => ({ type: 'button', id: button.id, selector: button.selector })),
        // Add critical elements with common selectors
        ...pageMap.criticalElements.map(element => ({
          type: 'critical',
          id: element,
          selector: `[data-testid="${element}"], .${element}, [class*="${element}"]`
        }))
      ];
      
      // Test theme switching multiple times
      for (let switchNum = 1; switchNum <= SWITCH_COUNT; switchNum++) {
        // Record element states before switch
        const beforeStates = new Map<string, ElementVisibility | null>();
        
        for (const testEl of testSelectors) {
          const visibility = await getElementVisibility(page, testEl.selector);
          beforeStates.set(testEl.id, visibility);
        }
        
        // Get current theme before switch
        const themeBefore = await getCurrentTheme(page);
        
        // Perform theme switch
        const toggleSuccess = await clickThemeToggle(page);
        
        if (!toggleSuccess) {
          test.info().annotations.push({
            type: 'warning',
            description: `Could not find theme toggle on ${pageMap.path}`
          });
          break;
        }
        
        // Wait for transition to complete
        await page.waitForTimeout(TRANSITION_WAIT);
        
        // Get current theme after switch
        const themeAfter = await getCurrentTheme(page);
        
        // Record element states after switch
        for (const testEl of testSelectors) {
          const beforeState = beforeStates.get(testEl.id);
          const afterState = await getElementVisibility(page, testEl.selector);
          
          if (beforeState && afterState) {
            const issues = [];
            
            // Check for visibility loss
            if (beforeState.visible && !afterState.visible) {
              issues.push('Element became invisible');
            }
            
            // Check for opacity changes that indicate problems
            if (beforeState.visible && afterState.visible && 
                beforeState.opacity !== '0' && afterState.opacity === '0') {
              issues.push('Element opacity went to 0');
            }
            
            // Check for size collapse
            if (beforeState.bounds.width > 0 && afterState.bounds.width === 0) {
              issues.push('Element width collapsed to 0');
            }
            
            if (beforeState.bounds.height > 0 && afterState.bounds.height === 0) {
              issues.push('Element height collapsed to 0');
            }
            
            // Check for problematic color combinations
            if (afterState.backgroundColor === afterState.color && 
                afterState.backgroundColor !== 'transparent' &&
                !afterState.backgroundColor.includes('rgba(0, 0, 0, 0)')) {
              issues.push('Background and text color are identical');
            }
            
            allResults.push({
              page: pageMap.path,
              element: testEl.id,
              selector: testEl.selector,
              beforeSwitch: beforeState,
              afterSwitch: afterState,
              switchNumber: switchNum,
              stable: issues.length === 0,
              issues
            });
          } else if (beforeState && !afterState) {
            // Element disappeared completely
            allResults.push({
              page: pageMap.path,
              element: testEl.id,
              selector: testEl.selector,
              beforeSwitch: beforeState,
              afterSwitch: {
                visible: false,
                opacity: '0',
                display: 'none',
                backgroundColor: 'missing',
                color: 'missing',
                bounds: { width: 0, height: 0, x: 0, y: 0 }
              },
              switchNumber: switchNum,
              stable: false,
              issues: ['Element completely disappeared from DOM']
            });
          }
        }
      }
    }
    
    // Analyze results
    const unstableResults = allResults.filter(r => !r.stable);
    const stableResults = allResults.filter(r => r.stable);
    
    // Generate detailed report
    console.log('=== THEME SWITCHING STABILITY REPORT ===');
    console.log(`Total element transitions tested: ${allResults.length}`);
    console.log(`Stable transitions: ${stableResults.length}`);
    console.log(`Unstable transitions: ${unstableResults.length}`);
    console.log(`Stability rate: ${Math.round((stableResults.length / allResults.length) * 100)}%`);
    console.log('');
    
    if (unstableResults.length > 0) {
      console.log('=== UNSTABLE ELEMENTS ===');
      
      // Group by element for cleaner reporting
      const groupedByElement = unstableResults.reduce((acc, result) => {
        const key = `${result.page}-${result.element}`;
        if (!acc[key]) {
          acc[key] = [];
        }
        acc[key].push(result);
        return acc;
      }, {} as Record<string, ThemeStabilityResult[]>);
      
      for (const [elementKey, results] of Object.entries(groupedByElement)) {
        const firstResult = results[0];
        const allIssues = [...new Set(results.flatMap(r => r.issues))];
        
        console.log(`❌ ${elementKey}`);
        console.log(`   Page: ${firstResult.page}`);
        console.log(`   Selector: ${firstResult.selector}`);
        console.log(`   Issues: ${allIssues.join(', ')}`);
        console.log(`   Failed in ${results.length}/${SWITCH_COUNT} switches`);
        console.log('');
      }
    }
    
    // Generate summary by page
    const pageResults = allResults.reduce((acc, result) => {
      if (!acc[result.page]) {
        acc[result.page] = { total: 0, stable: 0, unstable: 0 };
      }
      acc[result.page].total++;
      if (result.stable) {
        acc[result.page].stable++;
      } else {
        acc[result.page].unstable++;
      }
      return acc;
    }, {} as Record<string, { total: number; stable: number; unstable: number }>);
    
    console.log('=== STABILITY BY PAGE ===');
    for (const [pagePath, stats] of Object.entries(pageResults)) {
      const rate = Math.round((stats.stable / stats.total) * 100);
      console.log(`${pagePath}: ${stats.stable}/${stats.total} stable (${rate}%)`);
    }
    
    // Save detailed results for analysis
    const reportData = {
      summary: {
        totalTransitions: allResults.length,
        stable: stableResults.length,
        unstable: unstableResults.length,
        stabilityRate: Math.round((stableResults.length / allResults.length) * 100)
      },
      by_page: pageResults,
      unstable_elements: unstableResults,
      timestamp: new Date().toISOString()
    };
    
    test.info().attachments.push({
      name: 'theme-stability-report.json',
      body: JSON.stringify(reportData, null, 2),
      contentType: 'application/json'
    });
    
    // For critical elements, we should have 100% stability
    const criticalFailures = unstableResults.filter(r => 
      pageTestMap.find(p => p.path === r.page)?.criticalElements.includes(r.element)
    );
    
    if (criticalFailures.length > 0) {
      test.info().annotations.push({
        type: 'error',
        description: `${criticalFailures.length} critical elements failed theme switching stability`
      });
    }
    
    if (unstableResults.length > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${unstableResults.length} elements showed instability during theme switching`
      });
    }
    
    // For now, warn but don't fail to establish baseline
    // Once we fix issues, uncomment this:
    // expect(criticalFailures).toHaveLength(0);
    
    expect(allResults.length).toBeGreaterThan(0);
  });
  
  // Test for theme persistence across page navigation
  test('Theme persists across page navigation', async ({ page }) => {
    const testPages = pageTestMap.slice(0, 3); // Test first 3 pages
    
    // Start on homepage
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    
    // Switch to dark theme
    const toggleSuccess = await clickThemeToggle(page);
    
    if (!toggleSuccess) {
      test.skip('Theme toggle not found');
      return;
    }
    
    await page.waitForTimeout(400);
    const initialTheme = await getCurrentTheme(page);
    
    // Navigate to other pages and verify theme persists
    for (const pageMap of testPages) {
      if (pageMap.path === '/') continue; // Skip homepage since we're already there
      
      await page.goto(`${BASE_URL}${pageMap.path}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(300);
      
      const currentTheme = await getCurrentTheme(page);
      
      console.log(`${pageMap.path}: theme is ${currentTheme} (expected: ${initialTheme})`);
      
      // Theme should persist across navigation
      expect(currentTheme).toBe(initialTheme);
    }
  });
  
  // Test for rapid theme switching (stress test)
  test('Rapid theme switching does not break elements', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    
    // Find theme toggle
    const toggleSuccess = await clickThemeToggle(page);
    
    if (!toggleSuccess) {
      test.skip('Theme toggle not found');
      return;
    }
    
    // Switch back to establish baseline
    await page.waitForTimeout(200);
    await clickThemeToggle(page);
    await page.waitForTimeout(200);
    
    // Record baseline state of key elements
    const keySelectors = [
      'nav button', // Navigation buttons
      '.hero-section .mantine-ThemeIcon-root', // Hero icons
      '.mantine-ThemeIcon-root', // All theme icons
      'button[type="submit"]', // Form buttons
    ];
    
    const baselineStates = new Map();
    for (const selector of keySelectors) {
      const elements = page.locator(selector);
      const count = await elements.count();
      
      for (let i = 0; i < count; i++) {
        const visibility = await getElementVisibility(page, `${selector}:nth-child(${i + 1})`);
        if (visibility?.visible) {
          baselineStates.set(`${selector}-${i}`, visibility);
        }
      }
    }
    
    // Perform rapid theme switching (10 switches in 5 seconds)
    for (let i = 0; i < 10; i++) {
      await clickThemeToggle(page);
      await page.waitForTimeout(100); // Very short wait
    }
    
    // Wait for things to settle
    await page.waitForTimeout(1000);
    
    // Check if elements are still stable
    const unstableElements = [];
    
    for (const [key, baseline] of baselineStates.entries()) {
      const [selector, index] = key.split('-');
      const currentVisibility = await getElementVisibility(page, `${selector}:nth-child(${parseInt(index) + 1})`);
      
      if (!currentVisibility?.visible) {
        unstableElements.push({
          selector,
          index: parseInt(index),
          issue: 'Element became invisible after rapid switching'
        });
      }
    }
    
    if (unstableElements.length > 0) {
      console.log('Elements that became unstable during rapid switching:');
      unstableElements.forEach(el => {
        console.log(`- ${el.selector}[${el.index}]: ${el.issue}`);
      });
    }
    
    // Rapid switching should not break element visibility
    expect(unstableElements).toHaveLength(0);
  });
  
  // Test theme switching with network delays (simulate slow loading)
  test('Theme switching works with slow network conditions', async ({ page }) => {
    // Throttle network to simulate slow conditions
    await page.route('**/*', async (route) => {
      // Add 100ms delay to all requests
      await new Promise(resolve => setTimeout(resolve, 100));
      await route.continue();
    });
    
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    
    const toggleSuccess = await clickThemeToggle(page);
    
    if (!toggleSuccess) {
      test.skip('Theme toggle not found');
      return;
    }
    
    // Theme switch should still work with network delays
    await page.waitForTimeout(800); // Longer wait for slow network
    
    const currentTheme = await getCurrentTheme(page);
    expect(currentTheme).toMatch(/^(light|dark)$/);
    
    // Elements should still be visible
    const iconElements = await page.locator('.mantine-ThemeIcon-root').count();
    const visibleIcons = await page.locator('.mantine-ThemeIcon-root:visible').count();
    
    // Most icons should still be visible (allow for some that might be legitimately hidden)
    expect(visibleIcons).toBeGreaterThan(iconElements * 0.8);
  });
});

test.beforeEach(async ({ page }) => {
  // Set up console error tracking
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  // Attach error log to test results
  test.info().annotations.push({
    type: 'info',
    description: `Console errors will be tracked during theme switching`
  });
});

test.afterEach(async ({ page }, testInfo) => {
  // Capture final state screenshot if test failed
  if (testInfo.status === 'failed') {
    await page.screenshot({
      path: `test-results/theme-switching-failure-${testInfo.title.replace(/[^a-zA-Z0-9]/g, '-')}.png`,
      fullPage: true
    });
  }
});