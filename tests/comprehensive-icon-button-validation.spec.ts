import { test, expect, Page, Locator } from '@playwright/test';

/**
 * Comprehensive Icon & Button Validation
 * Tests visibility, hover states, and theme compatibility
 */

const BASE_URL = 'http://localhost:3008';
const THEMES = ['light', 'dark'] as const;

// PM33 Standardized Classes
const PM33_BUTTON_CLASSES = [
  'pm33-button-primary',
  'pm33-button-secondary', 
  'pm33-button-subtle'
] as const;

const PM33_ICON_CLASSES = [
  'pm33-icon-standard',
  'pm33-icon-branded', 
  'pm33-icon-success',
  'pm33-icon-warning'
] as const;

const PM33_BADGE_CLASSES = [
  'pm33-badge-branded',
  'pm33-badge-success'
] as const;

// Forbidden patterns that should NOT exist
const FORBIDDEN_BUTTON_PATTERNS = [
  'variant="gradient"',
  'gradient={{',
  'variant="outline"',
  'variant="white"',
  'variant="light"'
] as const;

const FORBIDDEN_ICON_PATTERNS = [
  'variant="gradient"',
  'gradient={{',
  'variant="light"'
] as const;

// Helper to wait for page to be ready
async function waitForPageReady(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForFunction(() => document.fonts.ready);
  await page.waitForTimeout(300);
}

// Helper to set theme
async function setTheme(page: Page, theme: 'light' | 'dark') {
  await page.evaluate((theme) => {
    document.body.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    document.body.className = `theme-${theme}`;
  }, theme);
  await page.waitForTimeout(200);
}

// Helper to get contrast ratio
async function getContrastRatio(page: Page, element: Locator): Promise<number> {
  return await element.evaluate((el) => {
    const style = window.getComputedStyle(el);
    const bgColor = style.backgroundColor;
    const textColor = style.color;
    
    // Simple contrast calculation (would be more complex in real implementation)
    // This is a simplified version for testing
    const getBrightness = (color: string) => {
      const rgb = color.match(/\d+/g);
      if (!rgb) return 0;
      return (parseInt(rgb[0]) * 0.299 + parseInt(rgb[1]) * 0.587 + parseInt(rgb[2]) * 0.114);
    };
    
    const bgBrightness = getBrightness(bgColor);
    const textBrightness = getBrightness(textColor);
    
    const lighter = Math.max(bgBrightness, textBrightness);
    const darker = Math.min(bgBrightness, textBrightness);
    
    return (lighter + 0.05) / (darker + 0.05);
  });
}

// Test pages to validate
const TEST_PAGES = [
  { path: '/', name: 'Homepage' },
  { path: '/pricing', name: 'Pricing' },
  { path: '/features', name: 'Features' }
];

// Test each page
for (const testPage of TEST_PAGES) {
  for (const theme of THEMES) {
    test(`${testPage.name} - ${theme} theme - Visibility and Hover Validation`, async ({ page }) => {
      // Navigate and set theme
      await page.goto(`${BASE_URL}${testPage.path}`);
      await setTheme(page, theme);
      await waitForPageReady(page);

      // Find all icons and buttons with potential visibility issues
      const problematicSelectors = [
        // Blue text that might be invisible
        '[class*="text-blue"]',
        '[class*="text-indigo"]', 
        'text[fill*="blue"]',
        'text[fill*="indigo"]',
        
        // Mantine color props that might cause issues
        '[data-mantine-color*="blue"]',
        '[data-mantine-color*="indigo"]',
        
        // Elements with c="blue" or similar
        '*[style*="color: blue"]',
        '*[style*="color: indigo"]',
        '*[style*="color: #667eea"]',
        '*[style*="color: #764ba2"]',
        
        // PM33 standardized classes
        '.pm33-icon-standard',
        '.pm33-icon-branded', 
        '.pm33-icon-success',
        '.pm33-button-primary',
        '.pm33-badge-branded'
      ];

      for (const selector of problematicSelectors) {
        const elements = await page.locator(selector).all();
        
        for (let i = 0; i < elements.length; i++) {
          const element = elements[i];
          
          // Check if element is visible
          const isVisible = await element.isVisible();
          if (!isVisible) continue;
          
          // Test visibility - element should have sufficient contrast
          const contrastRatio = await getContrastRatio(page, element);
          
          // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
          expect(contrastRatio, 
            `${selector}[${i}] has insufficient contrast (${contrastRatio}) in ${theme} theme`
          ).toBeGreaterThan(3.0);
          
          // Test hover state if it's an interactive element
          const isInteractive = await element.evaluate((el) => {
            const style = window.getComputedStyle(el);
            return style.cursor === 'pointer' || 
                   el.tagName.toLowerCase() === 'button' ||
                   el.tagName.toLowerCase() === 'a' ||
                   el.closest('button') !== null ||
                   el.closest('a') !== null;
          });
          
          if (isInteractive) {
            // Test hover state
            await element.hover();
            await page.waitForTimeout(100);
            
            // Check hover contrast
            const hoverContrastRatio = await getContrastRatio(page, element);
            expect(hoverContrastRatio,
              `${selector}[${i}] hover state has insufficient contrast in ${theme} theme`
            ).toBeGreaterThan(3.0);
            
            // Check that hover state actually changed something
            const hoverStyles = await element.evaluate((el) => {
              const style = window.getComputedStyle(el);
              return {
                transform: style.transform,
                boxShadow: style.boxShadow,
                backgroundColor: style.backgroundColor,
                borderColor: style.borderColor
              };
            });
            
            // At least one style property should change on hover for interactive elements
            const hasHoverEffect = hoverStyles.transform !== 'none' || 
                                 hoverStyles.boxShadow !== 'none' ||
                                 hoverStyles.backgroundColor !== 'rgba(0, 0, 0, 0)' ||
                                 hoverStyles.borderColor !== 'rgb(0, 0, 0)';
            
            expect(hasHoverEffect,
              `${selector}[${i}] should have visible hover effects in ${theme} theme`
            ).toBe(true);
          }
        }
      }
    });

    test(`${testPage.name} - ${theme} theme - Blue Text Detection`, async ({ page }) => {
      await page.goto(`${BASE_URL}${testPage.path}`);
      await setTheme(page, theme);
      await waitForPageReady(page);

      // Check for elements with blue/indigo text that might be invisible
      const blueTextElements = await page.evaluate(() => {
        const elements = document.querySelectorAll('*');
        const problematicElements: Array<{selector: string, color: string, background: string}> = [];
        
        elements.forEach((el, index) => {
          if (el instanceof HTMLElement) {
            const style = window.getComputedStyle(el);
            const color = style.color;
            const backgroundColor = style.backgroundColor;
            
            // Check for blue-ish colors
            const isBlueText = color.includes('rgb(102, 126, 234)') || // #667eea
                              color.includes('rgb(118, 75, 162)') ||   // #764ba2
                              color.includes('blue') ||
                              color.includes('indigo');
            
            const isBlueBackground = backgroundColor.includes('rgb(102, 126, 234)') ||
                                   backgroundColor.includes('rgb(118, 75, 162)') ||
                                   backgroundColor.includes('blue') ||
                                   backgroundColor.includes('indigo');
            
            if (isBlueText && isBlueBackground) {
              problematicElements.push({
                selector: `${el.tagName.toLowerCase()}[${index}]`,
                color: color,
                background: backgroundColor
              });
            }
          }
        });
        
        return problematicElements;
      });

      // Report any blue-on-blue combinations found
      expect(blueTextElements, 
        `Found ${blueTextElements.length} elements with blue text on blue background in ${theme} theme: ${JSON.stringify(blueTextElements)}`
      ).toHaveLength(0);
    });

    test(`${testPage.name} - ${theme} theme - PM33 Standardized Classes Validation`, async ({ page }) => {
      await page.goto(`${BASE_URL}${testPage.path}`);
      await setTheme(page, theme);
      await waitForPageReady(page);

      // Test PM33 standardized classes
      const pm33Classes = [
        '.pm33-icon-standard',
        '.pm33-icon-branded',
        '.pm33-icon-success',
        '.pm33-button-primary',
        '.pm33-card-glass',
        '.pm33-badge-branded'
      ];

      for (const className of pm33Classes) {
        const elements = await page.locator(className).all();
        
        for (let i = 0; i < elements.length; i++) {
          const element = elements[i];
          
          if (await element.isVisible()) {
            // Check theme-aware styling
            const styles = await element.evaluate((el) => {
              const style = window.getComputedStyle(el);
              return {
                background: style.backgroundColor,
                color: style.color,
                border: style.border,
                backdropFilter: style.backdropFilter,
                transition: style.transition
              };
            });

            // PM33 classes should have proper styling
            expect(styles.transition, 
              `${className}[${i}] should have transition effects`
            ).toContain('0.3s');

            // Glass morphism classes should have backdrop filter
            if (className.includes('glass') || className.includes('standard')) {
              expect(styles.backdropFilter,
                `${className}[${i}] should have backdrop filter for glass morphism`
              ).toContain('blur');
            }

            // Branded classes should have gradients
            if (className.includes('branded') || className.includes('primary')) {
              expect(styles.background,
                `${className}[${i}] should have gradient background`
              ).toMatch(/gradient|linear-gradient/);
            }
          }
        }
      }
    });
  }
}

// Theme switching test
test('Theme Switching Stability', async ({ page }) => {
  await page.goto(`${BASE_URL}/`);
  await waitForPageReady(page);

  // Test rapid theme switching
  for (let i = 0; i < 5; i++) {
    await setTheme(page, 'light');
    await page.waitForTimeout(100);
    
    await setTheme(page, 'dark');
    await page.waitForTimeout(100);
  }

  // Final check - ensure no elements are invisible after rapid switching
  const invisibleElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    let invisible = 0;
    
    elements.forEach((el) => {
      if (el instanceof HTMLElement) {
        const style = window.getComputedStyle(el);
        const color = style.color;
        const backgroundColor = style.backgroundColor;
        
        // Check if text and background are too similar (simplified check)
        if (color === backgroundColor || 
            (color.includes('255, 255, 255') && backgroundColor.includes('255, 255, 255')) ||
            (color.includes('0, 0, 0') && backgroundColor.includes('0, 0, 0'))) {
          invisible++;
        }
      }
    });
    
    return invisible;
  });

  expect(invisibleElements, 
    'Theme switching should not create invisible elements'
  ).toBeLessThan(5); // Allow for some edge cases
});

// Test PM33 Button Standardization
test.describe('PM33 Button Standardization', () => {
  test('should have no forbidden button patterns on homepage', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    // Get page content
    const pageContent = await page.content();
    
    // Check for forbidden patterns
    for (const pattern of FORBIDDEN_BUTTON_PATTERNS) {
      const matches = pageContent.match(new RegExp(pattern, 'g'));
      if (matches) {
        console.error(`Found forbidden button pattern "${pattern}" ${matches.length} times`);
        console.error('Matches:', matches.slice(0, 3)); // Show first 3 matches
      }
      expect(matches).toBeNull();
    }
    
    console.log('✅ No forbidden button patterns found');
  });
  
  test('should have standardized PM33 button classes', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    // Count buttons using PM33 classes vs total buttons
    const totalButtons = await page.locator('button, .mantine-Button-root').count();
    let pm33ButtonCount = 0;
    
    for (const className of PM33_BUTTON_CLASSES) {
      const count = await page.locator(`button.${className}, .${className}`).count();
      pm33ButtonCount += count;
      console.log(`Found ${count} buttons with class: ${className}`);
    }
    
    console.log(`PM33 buttons: ${pm33ButtonCount} / Total buttons: ${totalButtons}`);
    
    // At least 80% of buttons should use PM33 classes
    const standardizationRatio = pm33ButtonCount / totalButtons;
    expect(standardizationRatio).toBeGreaterThan(0.8);
    
    console.log(`✅ Button standardization: ${(standardizationRatio * 100).toFixed(1)}%`);
  });
  
  test('should have consistent button variants', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    // Check that buttons don't have mixed variant attributes
    const buttonsWithVariant = await page.locator('button[class*="variant"], .mantine-Button-root[class*="variant"]').count();
    const buttonsWithPM33 = await page.locator('button[class*="pm33-button"], .mantine-Button-root[class*="pm33-button"]').count();
    
    console.log(`Buttons with variant attributes: ${buttonsWithVariant}`);
    console.log(`Buttons with PM33 classes: ${buttonsWithPM33}`);
    
    // Should not have buttons with both old variant system and new PM33 system
    expect(buttonsWithVariant).toBeLessThanOrEqual(2); // Allow minimal legacy usage
  });
});

// Test PM33 Icon Standardization
test.describe('PM33 Icon Standardization', () => {
  test('should have no forbidden icon patterns on homepage', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    const pageContent = await page.content();
    
    for (const pattern of FORBIDDEN_ICON_PATTERNS) {
      const matches = pageContent.match(new RegExp(pattern, 'g'));
      if (matches) {
        console.error(`Found forbidden icon pattern "${pattern}" ${matches.length} times`);
      }
      expect(matches).toBeNull();
    }
    
    console.log('✅ No forbidden icon patterns found');
  });
  
  test('should have standardized ThemeIcon classes', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    const totalIcons = await page.locator('.mantine-ThemeIcon-root').count();
    let pm33IconCount = 0;
    
    for (const className of PM33_ICON_CLASSES) {
      const count = await page.locator(`.${className}`).count();
      pm33IconCount += count;
      console.log(`Found ${count} icons with class: ${className}`);
    }
    
    console.log(`PM33 icons: ${pm33IconCount} / Total ThemeIcons: ${totalIcons}`);
    
    if (totalIcons > 0) {
      const iconStandardizationRatio = pm33IconCount / totalIcons;
      expect(iconStandardizationRatio).toBeGreaterThan(0.8);
      console.log(`✅ Icon standardization: ${(iconStandardizationRatio * 100).toFixed(1)}%`);
    }
  });
});

// Test PM33 Badge Standardization
test.describe('PM33 Badge Standardization', () => {
  test('should have standardized Badge classes', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    const totalBadges = await page.locator('.mantine-Badge-root').count();
    let pm33BadgeCount = 0;
    
    for (const className of PM33_BADGE_CLASSES) {
      const count = await page.locator(`.${className}`).count();
      pm33BadgeCount += count;
      console.log(`Found ${count} badges with class: ${className}`);
    }
    
    console.log(`PM33 badges: ${pm33BadgeCount} / Total badges: ${totalBadges}`);
    
    if (totalBadges > 0) {
      const badgeStandardizationRatio = pm33BadgeCount / totalBadges;
      expect(badgeStandardizationRatio).toBeGreaterThan(0.6); // Lower threshold for badges
      console.log(`✅ Badge standardization: ${(badgeStandardizationRatio * 100).toFixed(1)}%`);
    }
  });
});

// Test Overall Component Consistency
test.describe('PM33 Component Consistency', () => {
  test('should catch different button types on homepage', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    // This test specifically addresses user feedback about "4 different kinds of buttons"
    const buttonAnalysis = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, .mantine-Button-root'));
      const buttonTypes = new Set<string>();
      
      buttons.forEach(button => {
        const classList = button.className;
        const buttonType = [
          classList.includes('pm33-button-primary') ? 'pm33-primary' : null,
          classList.includes('pm33-button-secondary') ? 'pm33-secondary' : null,
          classList.includes('pm33-button-subtle') ? 'pm33-subtle' : null,
          classList.includes('mantine-Button-gradient') ? 'mantine-gradient' : null,
          classList.includes('mantine-Button-outline') ? 'mantine-outline' : null,
          classList.includes('mantine-Button-light') ? 'mantine-light' : null,
          classList.includes('mantine-Button-white') ? 'mantine-white' : null,
        ].filter(Boolean).join(',') || 'unknown';
        
        buttonTypes.add(buttonType);
      });
      
      return {
        totalButtons: buttons.length,
        uniqueButtonTypes: Array.from(buttonTypes),
        buttonTypeCount: buttonTypes.size
      };
    });
    
    console.log('Button Analysis:', buttonAnalysis);
    
    // Should not have more than 3 different button types (PM33 primary, secondary, subtle)
    expect(buttonAnalysis.buttonTypeCount).toBeLessThanOrEqual(3);
    console.log(`✅ Button type consistency: ${buttonAnalysis.buttonTypeCount} different types found`);
  });
  
  test('should catch different icon types on homepage', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageReady(page);
    
    // This test specifically addresses user feedback about "3 different kinds of icons"
    const iconAnalysis = await page.evaluate(() => {
      const icons = Array.from(document.querySelectorAll('.mantine-ThemeIcon-root'));
      const iconTypes = new Set<string>();
      
      icons.forEach(icon => {
        const classList = icon.className;
        const iconType = [
          classList.includes('pm33-icon-standard') ? 'pm33-standard' : null,
          classList.includes('pm33-icon-branded') ? 'pm33-branded' : null,
          classList.includes('pm33-icon-success') ? 'pm33-success' : null,
          classList.includes('pm33-icon-warning') ? 'pm33-warning' : null,
          classList.includes('mantine-ThemeIcon-gradient') ? 'mantine-gradient' : null,
          classList.includes('mantine-ThemeIcon-light') ? 'mantine-light' : null,
        ].filter(Boolean).join(',') || 'unknown';
        
        iconTypes.add(iconType);
      });
      
      return {
        totalIcons: icons.length,
        uniqueIconTypes: Array.from(iconTypes),
        iconTypeCount: iconTypes.size
      };
    });
    
    console.log('Icon Analysis:', iconAnalysis);
    
    // Should not have more than 4 different icon types (PM33 standard, branded, success, warning)
    expect(iconAnalysis.iconTypeCount).toBeLessThanOrEqual(4);
    console.log(`✅ Icon type consistency: ${iconAnalysis.iconTypeCount} different types found`);
  });
});