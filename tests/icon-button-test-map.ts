/**
 * PM33 Icon & Button Test Mapping
 * Comprehensive inventory of all icon and button variations across the website
 * Used for automated testing and standardization validation
 */

export interface IconTestCase {
  id: string;
  selector: string;
  component: string;
  expectedBackground: 'white' | 'gradient' | 'themed' | 'colored';
  expectedTextColor: 'dark' | 'white';
  size: 'small' | 'medium' | 'large';
  purpose: string;
}

export interface ButtonTestCase {
  id: string;
  selector: string;
  component: string;
  variant: 'primary' | 'secondary' | 'subtle';
  expectedColors: {
    background: string;
    text: string;
    border?: string;
  };
  purpose: string;
}

export interface PageTestMap {
  path: string;
  name: string;
  icons: IconTestCase[];
  buttons: ButtonTestCase[];
  hasThemeToggle: boolean;
  criticalElements: string[]; // High-priority elements that must work perfectly
}

/**
 * Complete test mapping for all PM33 pages
 */
export const pageTestMap: PageTestMap[] = [
  {
    path: '/',
    name: 'Homepage',
    hasThemeToggle: true,
    criticalElements: [
      'hero-banner-badge',
      'nav-cta-button',
      'hero-primary-cta',
      'benefits-icons',
      'trust-signals'
    ],
    icons: [
      {
        id: 'hero-ai-strategy-assistant',
        selector: '[data-testid="ai-strategy-icon"], .hero-section .mantine-ThemeIcon-root',
        component: 'SegmentMessaging (hero)',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'AI Strategy Assistant visual indicator'
      },
      {
        id: 'benefits-strategic-intelligence',
        selector: '[data-testid="strategic-intelligence-icon"]',
        component: 'SegmentMessaging (benefits)',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'large',
        purpose: 'Strategic Intelligence benefit icon'
      },
      {
        id: 'benefits-execution-speed',
        selector: '[data-testid="execution-speed-icon"]',
        component: 'SegmentMessaging (benefits)',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'large',
        purpose: 'Execution Speed benefit icon'
      },
      {
        id: 'benefits-business-impact',
        selector: '[data-testid="business-impact-icon"]',
        component: 'SegmentMessaging (benefits)',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'large',
        purpose: 'Business Impact benefit icon'
      },
      {
        id: 'trust-signals-check-icons',
        selector: '.trust-signals .mantine-ThemeIcon-root',
        component: 'SegmentMessaging (trust-signals)',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'small',
        purpose: 'Trust signal checkmarks'
      },
      {
        id: 'social-proof-metric-icons',
        selector: '.social-proof .mantine-ThemeIcon-root',
        component: 'SocialProofMetrics',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'large',
        purpose: 'Metric icons (users, trending, star, etc.)'
      },
      {
        id: 'enterprise-security-icons',
        selector: '.trust-badges .mantine-ThemeIcon-root',
        component: 'TrustBadges',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'Security and trust badge icons'
      }
    ],
    buttons: [
      {
        id: 'nav-start-free-trial',
        selector: 'nav [href="/trial"], nav button:has-text("Start Free Trial")',
        component: 'Navigation',
        variant: 'primary',
        expectedColors: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          text: 'white'
        },
        purpose: 'Primary navigation CTA'
      },
      {
        id: 'hero-primary-cta',
        selector: '.hero-section button:first-of-type, .hero-section [role="button"]:first-of-type',
        component: 'SegmentMessaging (hero)',
        variant: 'primary',
        expectedColors: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          text: 'white'
        },
        purpose: 'Hero section main action'
      },
      {
        id: 'hero-secondary-cta',
        selector: '.hero-section button:last-of-type, .hero-section [role="button"]:last-of-type',
        component: 'SegmentMessaging (hero)',
        variant: 'secondary',
        expectedColors: {
          background: 'white',
          text: '#667eea',
          border: '#667eea'
        },
        purpose: 'Hero section secondary action'
      }
    ]
  },
  {
    path: '/pricing',
    name: 'Pricing',
    hasThemeToggle: true,
    criticalElements: [
      'pricing-tier-icons',
      'feature-check-icons',
      'pricing-cta-buttons',
      'most-popular-badge'
    ],
    icons: [
      {
        id: 'pricing-tier-icons',
        selector: '.pricing-tier .mantine-ThemeIcon-root',
        component: 'Pricing page tiers',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'Pricing tier feature icons'
      },
      {
        id: 'feature-check-icons',
        selector: '.pricing-features .mantine-ThemeIcon-root',
        component: 'Pricing features',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'small',
        purpose: 'Feature inclusion checkmarks'
      }
    ],
    buttons: [
      {
        id: 'pricing-primary-cta',
        selector: '.pricing-card button[data-variant="primary"]',
        component: 'Pricing tiers',
        variant: 'primary',
        expectedColors: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          text: 'white'
        },
        purpose: 'Main pricing tier CTA'
      },
      {
        id: 'pricing-toggle-button',
        selector: '.pricing-toggle button',
        component: 'Pricing toggle',
        variant: 'secondary',
        expectedColors: {
          background: 'white',
          text: '#667eea',
          border: '#667eea'
        },
        purpose: 'Monthly/Annual toggle'
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    hasThemeToggle: true,
    criticalElements: [
      'about-feature-icons',
      'team-section-elements',
      'company-values-icons'
    ],
    icons: [
      {
        id: 'about-feature-icons',
        selector: '.about-features .mantine-ThemeIcon-root',
        component: 'About features section',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'Company feature/value icons'
      },
      {
        id: 'company-values-icons',
        selector: '.company-values .mantine-ThemeIcon-root',
        component: 'Company values',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'large',
        purpose: 'Company value representation icons'
      }
    ],
    buttons: [
      {
        id: 'about-contact-cta',
        selector: '.about-cta button, .about-cta [role="button"]',
        component: 'About page CTA',
        variant: 'primary',
        expectedColors: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          text: 'white'
        },
        purpose: 'About page contact/trial CTA'
      }
    ]
  },
  {
    path: '/contact',
    name: 'Contact',
    hasThemeToggle: true,
    criticalElements: [
      'contact-form-elements',
      'contact-info-icons'
    ],
    icons: [
      {
        id: 'contact-info-icons',
        selector: '.contact-info .mantine-ThemeIcon-root',
        component: 'Contact information',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'Contact method icons (email, phone, etc.)'
      }
    ],
    buttons: [
      {
        id: 'contact-form-submit',
        selector: '.contact-form button[type="submit"]',
        component: 'Contact form',
        variant: 'primary',
        expectedColors: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          text: 'white'
        },
        purpose: 'Contact form submission'
      }
    ]
  },
  {
    path: '/resources',
    name: 'Resources',
    hasThemeToggle: true,
    criticalElements: [
      'resource-category-icons',
      'resource-cta-buttons'
    ],
    icons: [
      {
        id: 'resource-category-icons',
        selector: '.resources-grid .mantine-ThemeIcon-root',
        component: 'Resource categories',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'Resource type/category icons'
      }
    ],
    buttons: [
      {
        id: 'resource-download-buttons',
        selector: '.resource-item button, .resource-item [role="button"]',
        component: 'Resource items',
        variant: 'secondary',
        expectedColors: {
          background: 'white',
          text: '#667eea',
          border: '#667eea'
        },
        purpose: 'Resource download/access buttons'
      }
    ]
  },
  {
    path: '/trial',
    name: 'Free Trial',
    hasThemeToggle: true,
    criticalElements: [
      'trial-signup-form',
      'trial-benefits-icons',
      'trial-cta-button'
    ],
    icons: [
      {
        id: 'trial-benefits-icons',
        selector: '.trial-benefits .mantine-ThemeIcon-root',
        component: 'Trial benefits',
        expectedBackground: 'white',
        expectedTextColor: 'dark',
        size: 'medium',
        purpose: 'Trial benefit/feature icons'
      }
    ],
    buttons: [
      {
        id: 'trial-signup-submit',
        selector: '.trial-form button[type="submit"], .trial-cta button',
        component: 'Trial signup',
        variant: 'primary',
        expectedColors: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          text: 'white'
        },
        purpose: 'Trial signup submission'
      }
    ]
  }
];

/**
 * Test utilities and helper functions
 */
export const testUtils = {
  // Theme switching utilities
  async setTheme(page: any, theme: 'light' | 'dark') {
    await page.evaluate((theme) => {
      document.body.setAttribute('data-theme', theme);
      document.body.className = theme === 'dark' ? 'dark' : 'light';
    }, theme);
    await page.waitForTimeout(300); // Wait for theme transition
  },

  async toggleTheme(page: any) {
    await page.click('[data-testid="theme-toggle"], .theme-toggle, [aria-label*="theme"]');
    await page.waitForTimeout(500); // Wait for theme transition
  },

  // Contrast ratio calculation
  calculateContrastRatio(bgColor: string, textColor: string): number {
    // Convert RGB strings to luminance values and calculate contrast ratio
    const getRGB = (color: string) => {
      const match = color.match(/\d+/g);
      return match ? match.map(Number) : [0, 0, 0];
    };
    
    const getLuminance = (rgb: number[]) => {
      const [r, g, b] = rgb.map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };

    const bgLum = getLuminance(getRGB(bgColor));
    const textLum = getLuminance(getRGB(textColor));
    
    const contrast = (Math.max(bgLum, textLum) + 0.05) / (Math.min(bgLum, textLum) + 0.05);
    return Math.round(contrast * 100) / 100;
  },

  // Element visibility checks
  async checkElementVisibility(page: any, selector: string) {
    return await page.locator(selector).evaluate(el => {
      const style = getComputedStyle(el);
      return {
        visible: style.opacity !== '0' && style.visibility !== 'hidden' && style.display !== 'none',
        backgroundColor: style.backgroundColor,
        color: style.color,
        bounds: el.getBoundingClientRect()
      };
    });
  }
};

/**
 * Expected outcomes for standardization
 */
export const standardizationTargets = {
  icons: {
    backgrounds: [
      'rgb(255, 255, 255)', // White background for maximum contrast
      'linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%)', // PM33 brand gradient
      'rgb(16, 185, 129)', // Success green
      'rgb(245, 158, 11)'  // Warning orange
    ],
    textColors: [
      'rgb(26, 32, 44)', // Dark text on light backgrounds
      'rgb(255, 255, 255)' // White text on dark/colored backgrounds
    ],
    sizes: {
      small: '20px',
      medium: '32px', 
      large: '48px'
    }
  },
  buttons: {
    primary: {
      background: 'linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%)',
      text: 'rgb(255, 255, 255)',
      border: 'none'
    },
    secondary: {
      background: 'rgb(255, 255, 255)',
      text: 'rgb(102, 126, 234)',
      border: '2px solid rgb(102, 126, 234)'
    },
    subtle: {
      background: 'transparent',
      text: 'rgb(102, 126, 234)',
      border: '1px solid rgba(102, 126, 234, 0.3)'
    }
  },
  wcagCompliance: {
    minimumContrastRatio: 4.5, // WCAG AA standard
    preferredContrastRatio: 7.0  // WCAG AAA standard
  }
};