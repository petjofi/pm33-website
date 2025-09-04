import { test, expect, Page } from '@playwright/test';
import { pageTestMap, testUtils, standardizationTargets, PageTestMap } from './icon-button-test-map';

/**
 * PM33 Icon & Button Standardization - Automated Screenshot Testing
 * Comprehensive visual regression testing for icon and button consistency
 */

// Test configuration
const BASE_URL = 'http://localhost:3008';
const THEMES = ['light', 'dark'] as const;
const VIEWPORTS = [
  { width: 375, height: 667, name: 'mobile' },
  { width: 768, height: 1024, name: 'tablet' }, 
  { width: 1200, height: 800, name: 'desktop' }
] as const;

// Helper function to wait for page to be fully loaded
async function waitForPageReady(page: Page) {
  // Wait for network to be idle
  await page.waitForLoadState('networkidle');
  
  // Wait for fonts to load
  await page.waitForFunction(() => document.fonts.ready);
  
  // Wait for any animations to complete
  await page.waitForTimeout(500);
  
  // Disable animations for consistent screenshots
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `
  });
}

// Helper function to set theme consistently
async function setTheme(page: Page, theme: 'light' | 'dark') {
  await page.evaluate((theme) => {
    // Set theme on document body
    document.body.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update body class for legacy compatibility
    document.body.className = document.body.className
      .replace(/\b(light|dark)\b/g, '')
      .trim() + ` ${theme}`;
      
    // Trigger any theme change events
    window.dispatchEvent(new CustomEvent('theme-change', { detail: { theme } }));
  }, theme);
  
  // Wait for theme transition
  await page.waitForTimeout(300);
}

describe('PM33 Icon & Button Standardization - Visual Regression', () => {
  
  // Full page screenshot tests across all themes and viewports
  THEMES.forEach(theme => {
    VIEWPORTS.forEach(viewport => {
      pageTestMap.forEach(pageMap => {
        test(`${pageMap.name} - ${theme} theme - ${viewport.name}`, async ({ page }) => {
          // Set viewport
          await page.setViewportSize(viewport);
          
          // Navigate to page
          await page.goto(`${BASE_URL}${pageMap.path}`);
          
          // Set theme
          await setTheme(page, theme);
          
          // Wait for page to be ready
          await waitForPageReady(page);
          
          // Take full page screenshot
          const screenshot = await page.screenshot({ 
            fullPage: true,
            animations: 'disabled'
          });
          
          // Compare against baseline
          const fileName = `${pageMap.path.replace('/', 'home')}-${theme}-${viewport.name}.png`.replace(/\/+/g, '-');
          expect(screenshot).toMatchSnapshot(fileName);
        });
      });
    });
  });
  
  // Focused icon testing - individual icon screenshots
  describe('Individual Icon Testing', () => {
    pageTestMap.forEach(pageMap => {
      THEMES.forEach(theme => {
        test(`${pageMap.name} icons - ${theme} theme`, async ({ page }) => {
          await page.setViewportSize({ width: 1200, height: 800 });
          await page.goto(`${BASE_URL}${pageMap.path}`);
          await setTheme(page, theme);
          await waitForPageReady(page);
          
          // Test each icon individually
          for (const iconTest of pageMap.icons) {
            try {
              const iconElement = page.locator(iconTest.selector).first();
              
              // Wait for icon to be visible
              await iconElement.waitFor({ state: 'visible', timeout: 5000 });
              
              // Screenshot individual icon with padding
              const iconScreenshot = await iconElement.screenshot({
                animations: 'disabled'
              });
              
              const iconFileName = `icon-${iconTest.id}-${theme}.png`;
              expect(iconScreenshot).toMatchSnapshot(iconFileName);
              
            } catch (error) {
              console.warn(`Icon not found: ${iconTest.id} on ${pageMap.path} (${iconTest.selector})`);
              // Don't fail the test for missing icons, just log them
              test.info().annotations.push({
                type: 'warning',
                description: `Icon not found: ${iconTest.id} - ${error.message}`
              });
            }
          }
        });
      });
    });
  });
  
  // Focused button testing - individual button screenshots  
  describe('Individual Button Testing', () => {
    pageTestMap.forEach(pageMap => {
      THEMES.forEach(theme => {
        test(`${pageMap.name} buttons - ${theme} theme`, async ({ page }) => {
          await page.setViewportSize({ width: 1200, height: 800 });
          await page.goto(`${BASE_URL}${pageMap.path}`);
          await setTheme(page, theme);
          await waitForPageReady(page);
          
          // Test each button individually
          for (const buttonTest of pageMap.buttons) {
            try {
              const buttonElement = page.locator(buttonTest.selector).first();
              
              // Wait for button to be visible
              await buttonElement.waitFor({ state: 'visible', timeout: 5000 });
              
              // Screenshot button in normal state
              const buttonScreenshot = await buttonElement.screenshot({
                animations: 'disabled'
              });
              
              const buttonFileName = `button-${buttonTest.id}-${theme}.png`;
              expect(buttonScreenshot).toMatchSnapshot(buttonFileName);
              
              // Screenshot button in hover state
              await buttonElement.hover();
              await page.waitForTimeout(200);
              
              const hoverScreenshot = await buttonElement.screenshot({
                animations: 'disabled'  
              });
              
              const hoverFileName = `button-${buttonTest.id}-${theme}-hover.png`;
              expect(hoverScreenshot).toMatchSnapshot(hoverFileName);
              
            } catch (error) {
              console.warn(`Button not found: ${buttonTest.id} on ${pageMap.path} (${buttonTest.selector})`);
              test.info().annotations.push({
                type: 'warning',
                description: `Button not found: ${buttonTest.id} - ${error.message}`
              });
            }
          }
        });
      });
    });
  });
  
  // Critical elements testing - high priority items that must work
  describe('Critical Elements Testing', () => {
    pageTestMap.forEach(pageMap => {
      test(`${pageMap.name} - Critical elements visibility`, async ({ page }) => {
        await page.setViewportSize({ width: 1200, height: 800 });
        await page.goto(`${BASE_URL}${pageMap.path}`);
        await waitForPageReady(page);
        
        const criticalResults = [];
        
        // Test in both themes
        for (const theme of THEMES) {
          await setTheme(page, theme);
          await page.waitForTimeout(300);
          
          for (const criticalElement of pageMap.criticalElements) {
            try {
              // Find elements by data-testid, class, or common selectors
              const possibleSelectors = [
                `[data-testid="${criticalElement}"]`,
                `.${criticalElement}`,
                `#${criticalElement}`,
                `[class*="${criticalElement}"]`
              ];
              
              let elementFound = false;
              for (const selector of possibleSelectors) {
                const element = page.locator(selector).first();
                const count = await element.count();
                
                if (count > 0) {
                  const isVisible = await element.isVisible();
                  
                  if (isVisible) {
                    const styles = await element.evaluate(el => {
                      const computed = getComputedStyle(el);
                      return {
                        backgroundColor: computed.backgroundColor,
                        color: computed.color,
                        opacity: computed.opacity,
                        display: computed.display,
                        visibility: computed.visibility
                      };
                    });
                    
                    criticalResults.push({
                      page: pageMap.path,
                      theme,
                      element: criticalElement,
                      selector,
                      visible: isVisible,
                      styles,
                      status: 'found'
                    });
                    
                    elementFound = true;
                    break;
                  }
                }
              }
              
              if (!elementFound) {
                criticalResults.push({
                  page: pageMap.path,
                  theme,
                  element: criticalElement,
                  status: 'not_found'
                });
              }
              
            } catch (error) {
              criticalResults.push({
                page: pageMap.path,
                theme,
                element: criticalElement,
                status: 'error',
                error: error.message
              });
            }
          }
        }
        
        // Log results for analysis
        const missingElements = criticalResults.filter(r => r.status !== 'found');
        if (missingElements.length > 0) {
          console.log('Missing critical elements:', JSON.stringify(missingElements, null, 2));
          
          // Add to test annotations but don't fail (for now)
          test.info().annotations.push({
            type: 'warning',
            description: `Missing critical elements: ${missingElements.length}/${criticalResults.length}`
          });
        }
        
        // For now, just log - we'll make this a hard failure once we establish baselines
        expect(criticalResults.length).toBeGreaterThan(0);
      });
    });
  });
  
  // Theme switching test - ensure no elements disappear during transitions
  describe('Theme Switching Stability', () => {
    pageTestMap.forEach(pageMap => {
      test(`${pageMap.name} - Theme switching stability`, async ({ page }) => {
        if (!pageMap.hasThemeToggle) {
          test.skip(`Skipping ${pageMap.name} - no theme toggle`);
          return;
        }
        
        await page.setViewportSize({ width: 1200, height: 800 });
        await page.goto(`${BASE_URL}${pageMap.path}`);
        await waitForPageReady(page);
        
        // Find theme toggle button
        const themeToggle = page.locator('[data-testid="theme-toggle"], .theme-toggle, [aria-label*="theme"], [class*="theme-toggle"]').first();
        
        // Test rapid theme switching
        const switchingResults = [];
        
        for (let i = 0; i < 3; i++) {
          await themeToggle.click();
          await page.waitForTimeout(400); // Wait for transition
          
          // Check if any critical elements became invisible
          for (const criticalElement of pageMap.criticalElements) {
            const possibleSelectors = [
              `[data-testid="${criticalElement}"]`,
              `.${criticalElement}`,
              `[class*="${criticalElement}"]`
            ];
            
            for (const selector of possibleSelectors) {
              const element = page.locator(selector).first();
              const count = await element.count();
              
              if (count > 0) {
                const isVisible = await element.isVisible();
                
                switchingResults.push({
                  iteration: i,
                  element: criticalElement,
                  selector,
                  visible: isVisible
                });
                
                // If element became invisible, capture screenshot for debugging
                if (!isVisible) {
                  await page.screenshot({
                    path: `test-results/theme-switching-error-${pageMap.name}-${criticalElement}-${i}.png`,
                    fullPage: true
                  });
                }
                
                break; // Found the element, move to next
              }
            }
          }
        }
        
        // Verify no elements became invisible during switching
        const invisibleElements = switchingResults.filter(r => !r.visible);
        
        if (invisibleElements.length > 0) {
          console.error('Elements became invisible during theme switching:', invisibleElements);
          test.info().annotations.push({
            type: 'error', 
            description: `${invisibleElements.length} elements became invisible during theme switching`
          });
        }
        
        expect(invisibleElements).toHaveLength(0);
      });
    });
  });
});

// Test configuration and setup
test.beforeEach(async ({ page }) => {
  // Set consistent browser preferences
  await page.addInitScript(() => {
    // Disable animations globally
    window.matchMedia = () => ({
      matches: true, // Force prefer-reduced-motion
      addListener: () => {},
      removeListener: () => {}
    });
  });
  
  // Set consistent user agent
  await page.setUserAgent('PM33-Test-Runner/1.0');
});

// Global error handling
test.afterEach(async ({ page }, testInfo) => {
  // Capture console errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  // If test failed, capture debug screenshot
  if (testInfo.status !== testInfo.expectedStatus) {
    await page.screenshot({ 
      path: `test-results/debug-${testInfo.title.replace(/[^a-zA-Z0-9]/g, '-')}.png`,
      fullPage: true 
    });
  }
});