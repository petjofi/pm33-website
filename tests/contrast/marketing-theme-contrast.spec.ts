import { test, expect } from '@playwright/test';

/**
 * PM33 Marketing Website Theme Contrast Validation
 * Ensures WCAG 2.1 AA compliance across all themes and marketing pages
 */

interface ContrastViolation {
  element: string;
  className: string;
  textColor: string;
  backgroundColor: string;
  contrast: number;
  required: number;
  textSample: string;
  selector: string;
}

// Helper function to calculate WCAG contrast ratio
function calculateContrast(color1: string, color2: string): number {
  const getRGB = (colorStr: string): [number, number, number] => {
    // Handle various color formats
    if (colorStr.startsWith('rgb(')) {
      const match = colorStr.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
    }
    if (colorStr.startsWith('rgba(')) {
      const match = colorStr.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)/);
      return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
    }
    if (colorStr.startsWith('#')) {
      const hex = colorStr.slice(1);
      return [
        parseInt(hex.slice(0, 2), 16),
        parseInt(hex.slice(2, 4), 16),
        parseInt(hex.slice(4, 6), 16)
      ];
    }
    return [0, 0, 0]; // Default fallback
  };

  const getLuminance = ([r, g, b]: [number, number, number]): number => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c /= 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const rgb1 = getRGB(color1);
  const rgb2 = getRGB(color2);
  
  const lum1 = getLuminance(rgb1);
  const lum2 = getLuminance(rgb2);
  
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
}

test.describe('PM33 Marketing Website Theme Contrast Validation', () => {
  // PM33 marketing website pages to test
  const pages = [
    { path: '/', name: 'homepage' },
    { path: '/pricing', name: 'pricing' },
    { path: '/features', name: 'features' },
    { path: '/about', name: 'about' },
    { path: '/contact', name: 'contact' },
    { path: '/blog', name: 'blog' },
  ];
  
  const themes = ['light', 'dark'];
  
  for (const pageInfo of pages) {
    for (const theme of themes) {
      test(`Marketing ${pageInfo.name} - ${theme} theme WCAG 2.1 AA contrast compliance`, async ({ page }) => {
        // Navigate to page
        await page.goto(pageInfo.path);
        
        // Set theme using PM33 marketing website's theme system
        await page.evaluate((themeValue) => {
          // Try multiple theme switching methods for PM33 marketing website
          document.documentElement.setAttribute('data-theme', themeValue);
          document.documentElement.className = document.documentElement.className.replace(/theme-\w+/, `theme-${themeValue}`);
          document.body.setAttribute('data-theme', themeValue);
          document.body.className = document.body.className.replace(/theme-\w+/, `theme-${themeValue}`);
          
          // Try PM33 marketing specific theme switching functions
          if ((window as any).setTheme) (window as any).setTheme(themeValue);
          if ((window as any).toggleTheme) (window as any).toggleTheme(themeValue);
          if ((window as any).updateTheme) (window as any).updateTheme(themeValue);
          
          // Dispatch theme change event for listeners
          window.dispatchEvent(new CustomEvent('themeChange', { detail: themeValue }));
          window.dispatchEvent(new CustomEvent('theme-changed', { detail: themeValue }));
        }, theme);
        
        // Wait for theme transition and CSS variables to update
        await page.waitForTimeout(500);
        
        // Check all text elements for contrast violations
        const violations = await page.evaluate(() => {
          function findBackgroundColor(element: Element): string {
            let current = element;
            while (current && current !== document.body) {
              const style = window.getComputedStyle(current);
              const bgColor = style.backgroundColor;
              if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                return bgColor;
              }
              current = current.parentElement!;
            }
            return window.getComputedStyle(document.body).backgroundColor || '#ffffff';
          }

          const issues: ContrastViolation[] = [];
          
          // Check all text elements
          const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, a, button, li, td, th, label');
          
          textElements.forEach((el, index) => {
            // Skip if element has no visible text content
            if (!el.textContent || el.textContent.trim().length === 0) return;
            
            // Skip if element is hidden
            const styles = window.getComputedStyle(el);
            if (styles.display === 'none' || styles.visibility === 'hidden' || styles.opacity === '0') return;
            
            const textColor = styles.color;
            const backgroundColor = findBackgroundColor(el);
            
            // Calculate contrast using the embedded function
            function getRGB(colorStr: string): [number, number, number] {
              if (colorStr.startsWith('rgb(')) {
                const match = colorStr.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
                return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
              }
              if (colorStr.startsWith('rgba(')) {
                const match = colorStr.match(/rgba\\((\\d+),\\s*(\\d+),\\s*(\\d+),\\s*[\\d.]+\\)/);
                return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
              }
              if (colorStr.startsWith('#')) {
                const hex = colorStr.slice(1);
                return [
                  parseInt(hex.slice(0, 2), 16),
                  parseInt(hex.slice(2, 4), 16),
                  parseInt(hex.slice(4, 6), 16)
                ];
              }
              return [0, 0, 0];
            }

            function getLuminance([r, g, b]: [number, number, number]): number {
              const [rs, gs, bs] = [r, g, b].map(c => {
                c /= 255;
                return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
              });
              return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
            }

            function getContrast(color1: string, color2: string): number {
              const rgb1 = getRGB(color1);
              const rgb2 = getRGB(color2);
              
              const lum1 = getLuminance(rgb1);
              const lum2 = getLuminance(rgb2);
              
              const brightest = Math.max(lum1, lum2);
              const darkest = Math.min(lum1, lum2);
              
              return (brightest + 0.05) / (darkest + 0.05);
            }
            
            const contrast = getContrast(textColor, backgroundColor);
            const fontSize = parseFloat(styles.fontSize);
            const fontWeight = parseInt(styles.fontWeight) || 400;
            
            // Determine if it's large text (18pt+ or 14pt+ bold)
            const isLargeText = fontSize >= 18 || (fontSize >= 14 && fontWeight >= 700);
            const requiredRatio = isLargeText ? 3.0 : 4.5;
            
            // Check for violations
            if (contrast < requiredRatio) {
              issues.push({
                element: el.tagName.toLowerCase(),
                className: el.className || '',
                textColor: textColor,
                backgroundColor: backgroundColor,
                contrast: Math.round(contrast * 100) / 100,
                required: requiredRatio,
                textSample: el.textContent.substring(0, 50),
                selector: el.className || el.id || `${el.tagName.toLowerCase()}[${index}]`
              });
            }
          });
          
          return issues;
        });
        
        // Take screenshot for visual reference
        await page.screenshot({ 
          path: `screenshots/contrast/marketing-${pageInfo.name}-${theme}.png`,
          fullPage: true 
        });
        
        // Log violations if any found
        if (violations.length > 0) {
          console.log(`\\n🚨 ${violations.length} contrast violations found on marketing ${pageInfo.name} (${theme} theme):`);
          violations.slice(0, 10).forEach((violation, index) => {
            console.log(`${index + 1}. ${violation.element} - "${violation.textSample}"`);
            console.log(`   Contrast: ${violation.contrast} (required: ${violation.required})`);
            console.log(`   Colors: ${violation.textColor} on ${violation.backgroundColor}\\n`);
          });
        }
        
        // Generate detailed failure message with actionable fixes
        const failureMessage = violations.length > 0 ? 
          `WCAG 2.1 AA Contrast Failure: ${violations.length} violations on marketing ${pageInfo.name} (${theme} theme)\\n` +
          violations.slice(0, 5).map(v => 
            `• ${v.element} "${v.textSample}" - contrast ${v.contrast} (need ${v.required})\\n` +
            `  Fix: Adjust colors for ${v.textColor} on ${v.backgroundColor}`
          ).join('\\n') +
          `\\n\\nScreenshot saved: screenshots/contrast/marketing-${pageInfo.name}-${theme}.png\\n` +
          `Total violations: ${violations.length} (showing first 5)`
          : '';
        
        // Assert WCAG 2.1 AA compliance
        expect(violations, failureMessage).toHaveLength(0);
      });
    }
  }
  
  // Test specific PM33 marketing components for contrast
  test('PM33 Marketing Hero Section - contrast validation', async ({ page }) => {
    await page.goto('/');
    
    for (const theme of themes) {
      // Set theme
      await page.evaluate((t) => {
        document.documentElement.setAttribute('data-theme', t);
      }, theme);
      
      await page.waitForTimeout(300);
      
      // Check hero section contrast
      const heroViolations = await page.evaluate(() => {
        const heros = document.querySelectorAll('.hero, .hero-section, [class*="hero"], .banner, [class*="banner"]');
        const issues: ContrastViolation[] = [];
        
        heros.forEach((hero, index) => {
          const textElements = hero.querySelectorAll('h1, h2, h3, p, span, a, button');
          
          textElements.forEach(el => {
            if (!el.textContent || el.textContent.trim() === '') return;
            
            const styles = window.getComputedStyle(el);
            const textColor = styles.color;
            
            // Find background considering gradient overlays
            let current = el;
            let backgroundColor = 'rgba(255, 255, 255, 1)';
            while (current && current !== document.body) {
              const style = window.getComputedStyle(current);
              const bg = style.backgroundColor;
              const bgImage = style.backgroundImage;
              
              if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                backgroundColor = bg;
                break;
              }
              
              // Check for gradient overlays common in hero sections
              if (bgImage && bgImage !== 'none') {
                backgroundColor = 'rgba(0, 0, 0, 0.3)'; // Assume dark overlay
                break;
              }
              
              current = current.parentElement;
            }
            
            // Use simplified contrast check for hero sections with complex backgrounds
            const isLightText = textColor.includes('255, 255, 255') || textColor.includes('rgb(255, 255, 255)');
            const isDarkBg = backgroundColor.includes('0, 0, 0') || backgroundColor.includes('rgba(0, 0, 0');
            const isLightBg = backgroundColor.includes('255, 255, 255') || backgroundColor.includes('rgba(255, 255, 255');
            
            // Flag potential issues
            if ((isLightText && !isDarkBg && isLightBg) || (!isLightText && isDarkBg)) {
              issues.push({
                element: el.tagName.toLowerCase(),
                className: (hero as HTMLElement).className,
                textColor: textColor,
                backgroundColor: backgroundColor,
                contrast: 1.0, // Placeholder
                required: 4.5,
                textSample: el.textContent!.substring(0, 30),
                selector: `hero[${index}] ${el.tagName.toLowerCase()}`
              });
            }
          });
        });
        
        return issues;
      });
      
      expect(heroViolations, `Marketing hero section contrast issues in ${theme} theme`).toHaveLength(0);
    }
  });

  // Test pricing cards for consistent contrast
  test('PM33 Marketing Pricing Cards - contrast validation', async ({ page }) => {
    await page.goto('/pricing');
    
    for (const theme of themes) {
      // Set theme
      await page.evaluate((t) => {
        document.documentElement.setAttribute('data-theme', t);
      }, theme);
      
      await page.waitForTimeout(300);
      
      // Check pricing cards contrast
      const pricingViolations = await page.evaluate(() => {
        const cards = document.querySelectorAll('.pricing-card, [class*="pricing"], .card, [class*="card"]');
        const issues: ContrastViolation[] = [];
        
        cards.forEach((card, index) => {
          const textElements = card.querySelectorAll('*');
          
          textElements.forEach(el => {
            if (!el.textContent || el.textContent.trim() === '') return;
            
            const styles = window.getComputedStyle(el);
            const textColor = styles.color;
            const cardBg = window.getComputedStyle(card).backgroundColor;
            
            // Simplified check for pricing cards
            const lightText = textColor.includes('255') || textColor.includes('white');
            const lightBg = cardBg.includes('255') || cardBg.includes('white');
            
            if (lightText === lightBg) { // Both light or both dark = potential issue
              issues.push({
                element: el.tagName.toLowerCase(),
                className: (card as HTMLElement).className,
                textColor: textColor,
                backgroundColor: cardBg,
                contrast: 1.0, // Placeholder
                required: 4.5,
                textSample: el.textContent!.substring(0, 30),
                selector: `pricing-card[${index}]`
              });
            }
          });
        });
        
        return issues;
      });
      
      expect(pricingViolations, `Marketing pricing cards contrast issues in ${theme} theme`).toHaveLength(0);
    }
  });
});