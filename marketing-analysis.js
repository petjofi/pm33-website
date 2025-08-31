const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function analyzeMarketingWebsite() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  
  // Test different viewport sizes
  const viewports = [
    { name: 'desktop', width: 1920, height: 1080 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 }
  ];

  const results = {
    homepage: {},
    navigation: {},
    pages: {},
    technical: {},
    marketing: {},
    screenshots: []
  };

  for (const viewport of viewports) {
    console.log(`\n🔍 Testing ${viewport.name} viewport (${viewport.width}x${viewport.height})`);
    
    const page = await context.newPage();
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    
    try {
      // Navigate to homepage
      console.log('📱 Navigating to homepage...');
      await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
      
      // Take homepage screenshot
      const screenshotPath = `marketing-analysis-${viewport.name}-homepage.png`;
      await page.screenshot({ 
        path: screenshotPath, 
        fullPage: true 
      });
      results.screenshots.push(screenshotPath);
      console.log(`📸 Screenshot saved: ${screenshotPath}`);

      // Analyze homepage content
      const title = await page.title();
      const h1 = await page.locator('h1').first().textContent().catch(() => 'Not found');
      const description = await page.locator('meta[name="description"]').getAttribute('content').catch(() => 'Not found');
      
      results.homepage[viewport.name] = {
        title,
        h1,
        description,
        url: page.url()
      };

      // Check navigation links
      console.log('🔗 Checking navigation links...');
      const navLinks = await page.locator('nav a, header a').allTextContents().catch(() => []);
      const navHrefs = await page.locator('nav a, header a').evaluateAll(links => 
        links.map(link => ({ text: link.textContent, href: link.href }))
      ).catch(() => []);
      
      results.navigation[viewport.name] = { navLinks, navHrefs };

      // Test key pages
      const testPages = ['/pricing', '/about', '/features', '/dashboard', '/strategic-intelligence', '/command-center'];
      
      for (const testPage of testPages) {
        try {
          console.log(`🔍 Testing page: ${testPage}`);
          await page.goto(`http://localhost:3000${testPage}`, { waitUntil: 'networkidle' });
          
          const pageTitle = await page.title();
          const pageH1 = await page.locator('h1').first().textContent().catch(() => 'Not found');
          
          // Take screenshot of key pages
          if (['/', '/pricing', '/dashboard'].includes(testPage)) {
            const pageScreenshot = `marketing-analysis-${viewport.name}-${testPage.replace('/', '') || 'home'}.png`;
            await page.screenshot({ 
              path: pageScreenshot, 
              fullPage: true 
            });
            results.screenshots.push(pageScreenshot);
          }
          
          results.pages[`${testPage}-${viewport.name}`] = {
            title: pageTitle,
            h1: pageH1,
            status: 'accessible'
          };
          
        } catch (error) {
          results.pages[`${testPage}-${viewport.name}`] = {
            status: 'error',
            error: error.message
          };
        }
      }

      // Check for marketing elements
      console.log('📊 Analyzing marketing elements...');
      const ctaButtons = await page.locator('button, .btn, a[class*="button"], a[class*="cta"]').allTextContents().catch(() => []);
      const valueProps = await page.locator('h1, h2, h3, .hero, .value-prop, .tagline').allTextContents().catch(() => []);
      const pricing = await page.locator('[class*="price"], [class*="plan"], .pricing').allTextContents().catch(() => []);
      
      results.marketing[viewport.name] = {
        ctaButtons,
        valueProps: valueProps.slice(0, 5), // First 5 key messages
        pricingElements: pricing.slice(0, 3) // First 3 pricing elements
      };

      // Technical checks
      console.log('⚙️ Running technical checks...');
      const performanceMetrics = await page.evaluate(() => {
        return {
          domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
          loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart,
          firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
        };
      }).catch(() => ({}));

      // Check for errors in console
      const consoleLogs = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleLogs.push(msg.text());
        }
      });

      results.technical[viewport.name] = {
        performance: performanceMetrics,
        consoleErrors: consoleLogs
      };

    } catch (error) {
      console.error(`❌ Error testing ${viewport.name}:`, error.message);
      results.technical[viewport.name] = {
        error: error.message
      };
    }
    
    await page.close();
  }

  await browser.close();

  // Save results to file
  fs.writeFileSync('marketing-analysis-results.json', JSON.stringify(results, null, 2));
  console.log('\n✅ Analysis complete! Results saved to marketing-analysis-results.json');
  console.log(`📸 Screenshots saved: ${results.screenshots.join(', ')}`);
  
  return results;
}

// Run the analysis
analyzeMarketingWebsite().catch(console.error);