/**
 * PM33 Marketing Design System
 * Provides CSS custom properties for theme-aware styling
 */

export const PM33_DESIGN = {
  colors: {
    marketing: {
      primary: '#667eea',
      secondary: '#764ba2', 
      text: {
        primary: '#1a202c',
        secondary: '#4a5568',
        inverse: '#ffffff'
      },
      bg: {
        primary: '#ffffff',
        secondary: '#f7fafc'
      }
    },
    app: {
      primary: '#667eea',
      secondary: '#764ba2'
    }
  }
};

export function generateCSSCustomProperties(): string {
  return `
    :root {
      /* PM33 Design Tokens */
      --pm33-brand-primary: ${PM33_DESIGN.colors.marketing.primary};
      --pm33-brand-secondary: ${PM33_DESIGN.colors.marketing.secondary};
      --pm33-brand-success: #10b981;
      --pm33-brand-dark: #0a0e27;
      --pm33-brand-white: #ffffff;
      
      /* PM33 Spacing */
      --pm33-spacing-xs: 4px;
      --pm33-spacing-sm: 8px;
      --pm33-spacing-md: 16px;
      --pm33-spacing-lg: 24px;
      --pm33-spacing-xl: 32px;
      --pm33-spacing-2xl: 40px;
      --pm33-spacing-3xl: 80px;
      
      /* PM33 Typography */
      --pm33-text-xs: 0.75rem;
      --pm33-text-sm: 0.875rem;
      --pm33-text-md: 1rem;
      --pm33-text-lg: 1.125rem;
      --pm33-text-xl: 1.25rem;
      --pm33-text-2xl: 1.5rem;
      --pm33-text-3xl: 2rem;
      --pm33-text-4xl: 3.5rem;
      
      /* PM33 Radius */
      --pm33-radius-sm: 8px;
      --pm33-radius-md: 12px;
      --pm33-radius-lg: 16px;
      --pm33-radius-xl: 24px;
      
      /* PM33 Shadows */
      --pm33-shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
      --pm33-shadow-premium: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
      --pm33-shadow-hover: 0 20px 60px 0 rgba(31, 38, 135, 0.6);
      
      /* Marketing Colors */
      --marketing-primary: var(--pm33-brand-primary);
      --marketing-secondary: var(--pm33-brand-secondary);
      --marketing-text-primary: ${PM33_DESIGN.colors.marketing.text.primary};
      --marketing-text-secondary: ${PM33_DESIGN.colors.marketing.text.secondary};
      --marketing-text-inverse: ${PM33_DESIGN.colors.marketing.text.inverse};
      --marketing-bg-primary: ${PM33_DESIGN.colors.marketing.bg.primary};
      --marketing-bg-secondary: ${PM33_DESIGN.colors.marketing.bg.secondary};
      
      /* Glass Morphism */
      --marketing-glass-bg: rgba(255, 255, 255, 0.05);
      --marketing-glass-border: rgba(255, 255, 255, 0.2);
      --marketing-glass-shadow: var(--pm33-shadow-glass);
      
      /* Gradients */
      --marketing-gradient-primary: linear-gradient(135deg, var(--pm33-brand-primary) 0%, var(--pm33-brand-secondary) 100%);
      --marketing-gradient-text: linear-gradient(135deg, var(--pm33-brand-primary) 0%, var(--pm33-brand-secondary) 100%);
      --marketing-text-on-gradient: var(--pm33-brand-white);
    }
    
    [data-theme="dark"] {
      --marketing-text-primary: #ffffff;
      --marketing-text-secondary: #cbd5e0;
      --marketing-text-inverse: #1a202c;
      --marketing-bg-primary: #1a202c;
      --marketing-bg-secondary: #2d3748;
      --marketing-glass-bg: rgba(0, 0, 0, 0.1);
    }
    
    /* PM33 Design Classes */
    .pm33-text-gradient {
      background: var(--marketing-gradient-text);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .pm33-glass-card {
      background: var(--marketing-glass-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--marketing-glass-border);
      border-radius: var(--pm33-radius-lg);
      box-shadow: var(--pm33-shadow-glass);
      transition: all 0.3s ease;
    }
    
    .pm33-glass-card:hover {
      transform: translateY(-4px);
      box-shadow: var(--pm33-shadow-hover);
    }
    
    .pm33-btn-primary {
      background: var(--marketing-gradient-primary);
      color: var(--pm33-brand-white);
      border: none;
      border-radius: var(--pm33-radius-md);
      padding: var(--pm33-spacing-md) var(--pm33-spacing-xl);
      font-size: var(--pm33-text-lg);
      transition: all 0.3s ease;
    }
    
    .pm33-btn-primary:hover {
      transform: translateY(-2px) scale(1.05);
      box-shadow: var(--pm33-shadow-premium);
    }
    
    .pm33-btn-outline {
      background: transparent;
      color: var(--marketing-text-inverse);
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: var(--pm33-radius-md);
      padding: var(--pm33-spacing-md) var(--pm33-spacing-xl);
      font-size: var(--pm33-text-lg);
      transition: all 0.3s ease;
    }
    
    .pm33-btn-outline:hover {
      transform: translateY(-2px) scale(1.05);
      background: rgba(255,255,255,0.1);
      border-color: rgba(255,255,255,0.5);
    }
    
    .pm33-nav-glass {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--marketing-glass-border);
    }
    
    /* Theme-aware text classes */
    .marketing-text-primary { color: var(--marketing-text-primary); }
    .marketing-text-secondary { color: var(--marketing-text-secondary); }
    .marketing-text-inverse { color: var(--marketing-text-inverse); }
    .marketing-gradient-text { 
      background: var(--marketing-gradient-text);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    /* Legacy glass morphism card for compatibility */
    .marketing-glass-card {
      background: var(--marketing-glass-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--marketing-glass-border);
      border-radius: var(--pm33-radius-lg);
      box-shadow: var(--pm33-shadow-glass);
      transition: all 0.3s ease;
    }
    
    .marketing-glass-card:hover {
      transform: translateY(-4px);
      box-shadow: var(--pm33-shadow-hover);
    }
  `;
}