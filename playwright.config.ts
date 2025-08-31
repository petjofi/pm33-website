import { defineConfig, devices } from '@playwright/test';

/**
 * PM33 Visual Testing Configuration
 * Enforces 95% visual similarity to approved designs
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['line'],
    ['json', { outputFile: 'test-results/visual-results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },

  projects: [
    {
      name: 'Visual Consistency',
      testMatch: /.*\.visual\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        // 95% similarity required for PM33 design compliance
        threshold: 0.05, // 5% difference allowed
        maxDiffPixels: 100,
        animations: 'disabled', // Consistent screenshots
      },
    },
    
    {
      name: 'PM33 Component Library',
      testMatch: /.*\.component\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        // Strict component validation
        threshold: 0.02, // 2% difference allowed
        maxDiffPixels: 50,
      },
    },

    {
      name: 'Responsive Design',
      testMatch: /.*\.responsive\.spec\.ts/,
      use: {
        ...devices['iPhone 12'],
        threshold: 0.05,
      },
    },

    {
      name: 'Glass Morphism Validation',
      testMatch: /.*\.glass\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        // Very strict for glass effects
        threshold: 0.01,
        maxDiffPixels: 25,
      },
    },

    {
      name: 'marketing-contrast-validation',
      testDir: './tests/contrast',
      testMatch: /.*\.contrast\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        // Ensure we can test both themes
        colorScheme: 'no-preference',
        // WCAG 2.1 AA compliance testing
        threshold: 0.0, // No visual threshold for contrast testing
      },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});