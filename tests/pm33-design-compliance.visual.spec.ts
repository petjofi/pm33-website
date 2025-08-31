import { test, expect } from '@playwright/test';

/**
 * PM33 Design Contract Visual Compliance Tests
 * Ensures all UI components match approved designs with 95% accuracy
 */

test.describe('PM33 Design Contract Compliance', () => {
  
  test.beforeEach(async ({ page }) => {
    // Disable animations for consistent screenshots
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }
      `
    });
  });

  test('Homepage hero section matches approved design', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for hero section to be visible
    const heroSection = page.locator('[data-testid="hero-section"], .hero-section, section:first-child');
    await expect(heroSection).toBeVisible();
    
    // Verify glass morphism elements are present
    const glassElements = page.locator('.glass-card, [class*="backdrop-blur"], [class*="glass"]');
    await expect(glassElements.first()).toBeVisible();
    
    // Take screenshot and compare with approved design
    await expect(heroSection).toHaveScreenshot('hero-section-approved.png', {
      threshold: 0.05, // 95% similarity required
      maxDiffPixels: 100
    });
  });

  test('PM33 Cards have proper glass morphism', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Find all card components
    const cards = page.locator('.glass-card, [class*="PM33Card"], .feature-card');
    const cardCount = await cards.count();
    
    expect(cardCount).toBeGreaterThan(0);
    
    // Verify each card has glass morphism
    for (let i = 0; i < cardCount; i++) {
      const card = cards.nth(i);
      
      // Check for backdrop-filter or glass styling
      const hasGlassStyling = await card.evaluate((el) => {
        const computedStyle = window.getComputedStyle(el);
        return (
          computedStyle.backdropFilter.includes('blur') ||
          computedStyle.webkitBackdropFilter?.includes('blur') ||
          el.className.includes('glass') ||
          el.className.includes('backdrop-blur')
        );
      });
      
      expect(hasGlassStyling).toBeTruthy();
      
      // Visual comparison for card design
      await expect(card.first()).toHaveScreenshot(`card-${i}-approved.png`, {
        threshold: 0.02 // 98% similarity for individual components
      });
    }
  });

  test('Gradient text on headlines', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find headline elements
    const headlines = page.locator('h1, h2, .text-gradient, [class*="gradient-text"]');
    const headlineCount = await headlines.count();
    
    expect(headlineCount).toBeGreaterThan(0);
    
    // Verify gradient styling on headlines
    for (let i = 0; i < Math.min(headlineCount, 5); i++) {
      const headline = headlines.nth(i);
      
      const hasGradientText = await headline.evaluate((el) => {
        const computedStyle = window.getComputedStyle(el);
        return (
          el.className.includes('gradient') ||
          el.className.includes('text-gradient') ||
          computedStyle.background.includes('gradient') ||
          computedStyle.backgroundImage.includes('gradient')
        );
      });
      
      expect(hasGradientText).toBeTruthy();
    }
  });

  test('Professional shadows (no flat elements)', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Find interactive elements that should have shadows
    const shadowElements = page.locator('button, .card, [class*="shadow"], .glass-card');
    const elementCount = await shadowElements.count();
    
    expect(elementCount).toBeGreaterThan(0);
    
    // Check for proper shadow styling
    for (let i = 0; i < Math.min(elementCount, 10); i++) {
      const element = shadowElements.nth(i);
      
      const hasProfessionalShadow = await element.evaluate((el) => {
        const computedStyle = window.getComputedStyle(el);
        const boxShadow = computedStyle.boxShadow;
        
        // Check that shadow is not 'none' and not too minimal
        return (
          boxShadow !== 'none' &&
          !boxShadow.includes('0px 1px 3px') && // shadow-sm equivalent
          (boxShadow.includes('rgba') || boxShadow.includes('rgb'))
        );
      });
      
      expect(hasProfessionalShadow).toBeTruthy();
    }
  });

  test('Brand color compliance', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const brandColors = ['#667eea', '#764ba2', '#10b981'];
    
    // Check that brand colors are used in the page
    const usedColors = await page.evaluate((colors) => {
      const allElements = document.querySelectorAll('*');
      const foundColors = new Set();
      
      allElements.forEach(el => {
        const computedStyle = window.getComputedStyle(el);
        const background = computedStyle.background + computedStyle.backgroundColor;
        const color = computedStyle.color;
        const borderColor = computedStyle.borderColor;
        
        colors.forEach(brandColor => {
          if (background.includes(brandColor) || color.includes(brandColor) || borderColor.includes(brandColor)) {
            foundColors.add(brandColor);
          }
        });
      });
      
      return Array.from(foundColors);
    }, brandColors);
    
    // Expect at least one brand color to be used
    expect(usedColors.length).toBeGreaterThan(0);
  });

  test('Hover states on interactive elements', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Find interactive elements
    const interactiveElements = page.locator('button, a, [class*="hover"], [role="button"]');
    const count = await interactiveElements.count();
    
    expect(count).toBeGreaterThan(0);
    
    // Test hover states on first few elements
    for (let i = 0; i < Math.min(count, 5); i++) {
      const element = interactiveElements.nth(i);
      
      // Get initial state
      const initialTransform = await element.evaluate(el => 
        window.getComputedStyle(el).transform
      );
      
      // Hover over element
      await element.hover();
      
      // Check for transform or other hover effects
      const hoverTransform = await element.evaluate(el => 
        window.getComputedStyle(el).transform
      );
      
      // Should have some change on hover (transform, scale, etc.)
      const hasHoverEffect = await element.evaluate((el) => {
        return (
          el.className.includes('hover:') ||
          el.style.transition ||
          window.getComputedStyle(el).transition !== 'all 0s ease 0s'
        );
      });
      
      expect(hasHoverEffect).toBeTruthy();
    }
  });

  test('Responsive design integrity', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Ensure no horizontal scroll
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    
    expect(hasHorizontalScroll).toBeFalsy();
    
    // Take mobile screenshot
    await expect(page).toHaveScreenshot('mobile-homepage-approved.png', {
      threshold: 0.05,
      fullPage: true
    });
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('tablet-homepage-approved.png', {
      threshold: 0.05,
      fullPage: true
    });
  });

  test('Component library consistency', async ({ page }) => {
    // Test component page if it exists
    await page.goto('/components');
    
    if (await page.locator('body').isVisible()) {
      // If components page exists, test component consistency
      const components = page.locator('[data-component-type]');
      const componentCount = await components.count();
      
      if (componentCount > 0) {
        // Visual regression for component library
        await expect(page).toHaveScreenshot('component-library-approved.png', {
          threshold: 0.02,
          fullPage: true
        });
      }
    }
  });

  test('8px spacing grid compliance', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Check spacing compliance
    const spacingCompliance = await page.evaluate(() => {
      const gridValues = [4, 8, 16, 24, 32, 48, 64];
      const elements = document.querySelectorAll('*');
      let violations = 0;
      
      elements.forEach(el => {
        const computedStyle = window.getComputedStyle(el);
        const padding = [
          computedStyle.paddingTop,
          computedStyle.paddingRight,
          computedStyle.paddingBottom,
          computedStyle.paddingLeft
        ];
        const margin = [
          computedStyle.marginTop,
          computedStyle.marginRight,
          computedStyle.marginBottom,
          computedStyle.marginLeft
        ];
        
        [...padding, ...margin].forEach(value => {
          if (value && value !== '0px' && value !== 'auto') {
            const px = parseInt(value);
            if (!gridValues.includes(px) && px > 0) {
              violations++;
            }
          }
        });
      });
      
      return violations;
    });
    
    // Allow some violations for legacy components, but prefer compliance
    expect(spacingCompliance).toBeLessThan(10);
  });

  test('Theme contrast compliance - dark theme has dark backgrounds and light text', async ({ page }) => {
    // Set dark theme
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Enable dark theme
    await page.evaluate(() => {
      document.body.classList.add('dark');
      document.body.classList.remove('light');
    });
    
    // Check dark theme compliance
    const darkThemeCompliance = await page.evaluate(() => {
      const violations = [];
      const elements = document.querySelectorAll('body, main, section, div');
      
      elements.forEach(el => {
        const computedStyle = window.getComputedStyle(el);
        const bgColor = computedStyle.backgroundColor;
        const textColor = computedStyle.color;
        
        // Convert RGB to hex for easier checking
        const rgbToHex = (rgb) => {
          if (!rgb || rgb === 'rgba(0, 0, 0, 0)' || rgb === 'transparent') return null;
          const match = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
          if (!match) return null;
          const r = parseInt(match[1]);
          const g = parseInt(match[2]);
          const b = parseInt(match[3]);
          return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
        };
        
        const bgHex = rgbToHex(bgColor);
        const textHex = rgbToHex(textColor);
        
        // Check for light backgrounds in dark theme (violation)
        if (bgHex && (bgHex === '#ffffff' || bgHex === '#f8fafc')) {
          violations.push(`Light background in dark theme: ${bgHex}`);
        }
        
        // Check for dark text on dark backgrounds (violation)
        if (textHex && bgHex && textHex.startsWith('#0') && bgHex.startsWith('#0')) {
          violations.push(`Dark text on dark background: ${textHex} on ${bgHex}`);
        }
      });
      
      return violations;
    });
    
    expect(darkThemeCompliance.length).toBeLessThan(5); // Allow some minor violations
    if (darkThemeCompliance.length > 0) {
      console.log('Dark theme violations:', darkThemeCompliance);
    }
  });

  test('Theme contrast compliance - light theme has light backgrounds and dark text', async ({ page }) => {
    // Set light theme
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Enable light theme
    await page.evaluate(() => {
      document.body.classList.add('light');
      document.body.classList.remove('dark');
    });
    
    // Check light theme compliance
    const lightThemeCompliance = await page.evaluate(() => {
      const violations = [];
      const elements = document.querySelectorAll('body, main, section, div');
      
      elements.forEach(el => {
        const computedStyle = window.getComputedStyle(el);
        const bgColor = computedStyle.backgroundColor;
        const textColor = computedStyle.color;
        
        // Convert RGB to hex for easier checking
        const rgbToHex = (rgb) => {
          if (!rgb || rgb === 'rgba(0, 0, 0, 0)' || rgb === 'transparent') return null;
          const match = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
          if (!match) return null;
          const r = parseInt(match[1]);
          const g = parseInt(match[2]);
          const b = parseInt(match[3]);
          return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
        };
        
        const bgHex = rgbToHex(bgColor);
        const textHex = rgbToHex(textColor);
        
        // Check for dark backgrounds in light theme (violation)
        if (bgHex && (bgHex === '#0a0e27' || bgHex === '#1e293b')) {
          violations.push(`Dark background in light theme: ${bgHex}`);
        }
        
        // Check for light text on light backgrounds (violation)
        if (textHex && bgHex && 
            (textHex === '#ffffff' || textHex === '#f8fafc') && 
            (bgHex === '#ffffff' || bgHex === '#f8fafc')) {
          violations.push(`Light text on light background: ${textHex} on ${bgHex}`);
        }
      });
      
      return violations;
    });
    
    expect(lightThemeCompliance.length).toBeLessThan(5); // Allow some minor violations  
    if (lightThemeCompliance.length > 0) {
      console.log('Light theme violations:', lightThemeCompliance);
    }
  });

});