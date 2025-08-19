# PM33 Design System Implementation & Enforcement
*Making Sure Design Systems Get Used - Not Just Documented*

## The Problem: Design Systems That Don't Get Used

**Common Failures**:
- Design tokens documented but not enforced
- Components created but not consistently used
- Marketing vs App inconsistencies
- Developers bypass system for "quick fixes"

## PM33 Solution: Multi-Layer Enforcement

### Layer 1: CSS Architecture Enforcement

#### Global Design Tokens (ENFORCED)
```css
/* styles/design-tokens.css - MUST BE IMPORTED FIRST */

/* Block usage of hardcoded colors */
* {
  /* This will cause errors if hardcoded colors are used */
  color: revert;
  background-color: revert;
  border-color: revert;
}

/* Marketing Design Tokens */
.marketing-page {
  --primary: var(--marketing-primary);
  --primary-hover: var(--marketing-primary-hover);
  --cta: var(--marketing-cta);
  --cta-hover: var(--marketing-cta-hover);
  --text-primary: var(--marketing-text-primary);
  --text-secondary: var(--marketing-text-secondary);
  --bg-primary: var(--marketing-bg-primary);
  --bg-secondary: var(--marketing-bg-secondary);
}

/* App Design Tokens */
.app-page {
  --primary: var(--app-primary);
  --primary-hover: var(--app-primary-hover);
  --text-primary: var(--app-text-primary);
  --text-secondary: var(--app-text-secondary);
  --bg-primary: var(--app-bg-primary);
  --bg-secondary: var(--app-bg-secondary);
}
```

#### PostCSS Plugin for Token Enforcement
```javascript
// postcss-design-system-enforcer.js
module.exports = () => {
  return {
    postcssPlugin: 'design-system-enforcer',
    Declaration(decl) {
      const hardcodedColorRegex = /#[0-9a-fA-F]{3,6}|rgb|rgba|hsl|hsla/;
      
      if (['color', 'background-color', 'border-color'].includes(decl.prop)) {
        if (hardcodedColorRegex.test(decl.value)) {
          throw decl.error(`Hardcoded color '${decl.value}' not allowed. Use design tokens.`);
        }
      }
    }
  }
}
```

### Layer 2: Component Architecture Enforcement

#### Higher-Order Component Wrapper
```tsx
// components/design-system/DesignSystemProvider.tsx
interface DesignSystemProviderProps {
  type: 'marketing' | 'app';
  children: React.ReactNode;
}

export const DesignSystemProvider: React.FC<DesignSystemProviderProps> = ({
  type, children
}) => {
  useEffect(() => {
    // Add appropriate CSS class to body
    document.body.classList.add(`${type}-page`);
    
    return () => {
      document.body.classList.remove(`${type}-page`);
    };
  }, [type]);

  return (
    <div className={`design-system-${type}`}>
      {children}
    </div>
  );
};
```

#### Component Factory with Validation
```tsx
// components/design-system/ComponentFactory.tsx
type ComponentType = 'marketing' | 'app';

interface ComponentFactoryProps {
  type: ComponentType;
  variant: string;
  [key: string]: any;
}

export const createDesignSystemComponent = <T extends ComponentFactoryProps>(
  Component: React.ComponentType<T>
) => {
  return (props: T) => {
    // Validate component is being used in correct context
    const currentContext = useContext(DesignSystemContext);
    
    if (props.type !== currentContext.type) {
      throw new Error(
        `${Component.name} designed for '${props.type}' used in '${currentContext.type}' context`
      );
    }
    
    return <Component {...props} />;
  };
};

// Usage enforcement
export const MarketingButton = createDesignSystemComponent(
  (props: ButtonProps & { type: 'marketing' }) => (
    <button className={`marketing-cta-${props.variant}`} {...props} />
  )
);

export const AppButton = createDesignSystemComponent(
  (props: ButtonProps & { type: 'app' }) => (
    <button className={`app-button-${props.variant}`} {...props} />
  )
);
```

### Layer 3: Build-Time Validation

#### ESLint Rules for Design System Compliance
```javascript
// eslint-plugin-pm33-design-system.js
module.exports = {
  rules: {
    'require-design-system-components': {
      create(context) {
        return {
          JSXElement(node) {
            const elementName = node.openingElement.name.name;
            
            // Block usage of generic HTML elements in favor of design system
            if (['button', 'input', 'card'].includes(elementName.toLowerCase())) {
              context.report({
                node,
                message: `Use design system component instead of generic '${elementName}'`
              });
            }
          }
        };
      }
    },
    
    'enforce-context-appropriate-components': {
      create(context) {
        return {
          JSXElement(node) {
            const elementName = node.openingElement.name.name;
            const filename = context.getFilename();
            
            const isMarketingFile = filename.includes('/marketing/') || 
                                  filename.includes('/(marketing)');
            const isAppFile = filename.includes('/app/') || 
                            filename.includes('/(app)');
            
            if (isMarketingFile && elementName.startsWith('App')) {
              context.report({
                node,
                message: `App component '${elementName}' used in marketing context`
              });
            }
            
            if (isAppFile && elementName.startsWith('Marketing')) {
              context.report({
                node,
                message: `Marketing component '${elementName}' used in app context`
              });
            }
          }
        };
      }
    }
  }
};
```

#### TypeScript Strict Mode for Design System
```typescript
// types/design-system-strict.ts
// Prevent usage of Mantine components directly - force design system usage

declare module '@mantine/core' {
  interface ButtonProps {
    /** @deprecated Use MarketingButton or AppButton from design system */
    __DEPRECATED__USE_DESIGN_SYSTEM_INSTEAD?: never;
  }
  
  interface CardProps {
    /** @deprecated Use MarketingCard or AppCard from design system */
    __DEPRECATED__USE_DESIGN_SYSTEM_INSTEAD?: never;
  }
}

// Force specific component usage based on file path
export type MarketingButtonProps = {
  variant: 'primary' | 'secondary' | 'outline';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  href?: string;
  onClick?: () => void;
};

export type AppButtonProps = {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md';
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit';
};
```

### Layer 4: Development Workflow Integration

#### Pre-commit Hooks
```bash
#!/bin/sh
# .husky/pre-commit

echo "🎨 Validating Design System Compliance..."

# Check for hardcoded colors
echo "Checking for hardcoded colors..."
if grep -r "#[0-9a-fA-F]\{3,6\}\|rgb\|rgba\|hsl\|hsla" --include="*.css" --include="*.tsx" --include="*.jsx" app/; then
  echo "❌ Hardcoded colors found. Use design tokens instead."
  exit 1
fi

# Validate component usage
echo "Validating component usage..."
npm run lint:design-system

# Check design system imports
echo "Checking design system imports..."
if ! grep -q "from.*design-system" app/**/*.{tsx,jsx}; then
  echo "⚠️ No design system components found. Make sure you're using the design system."
fi

echo "✅ Design system validation passed"
```

#### VS Code Extensions Configuration
```json
// .vscode/settings.json
{
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  },
  "emmet.snippets": {
    "marketing-hero": "section.hero-section>(.marketing-badge+h1.marketing-hero-xl+p.marketing-body-lg+.cta-group>(.marketing-cta-primary+.marketing-cta-secondary))",
    "app-card": "div.app-card>(.app-card-header>h3.app-heading)+.app-card-content",
    "ai-processing": "div.app-ai-card>(.app-ai-indicator+.app-progress+.app-confidence)"
  },
  "css.customData": [".vscode/pm33-design-tokens.json"]
}
```

#### CSS Variables Autocomplete
```json
// .vscode/pm33-design-tokens.json
{
  "properties": [
    {
      "name": "--marketing-primary",
      "description": "Primary marketing brand color - use for CTAs and key elements",
      "values": ["#1E40AF"]
    },
    {
      "name": "--app-primary", 
      "description": "Primary app color - use for navigation and key actions",
      "values": ["#1E3A8A"]
    }
  ]
}
```

### Layer 5: Runtime Validation & Monitoring

#### Design System Usage Analytics
```typescript
// utils/design-system-analytics.ts
export const trackDesignSystemUsage = () => {
  if (typeof window !== 'undefined') {
    // Track which design system components are being used
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            const element = node as Element;
            
            // Track marketing components
            if (element.classList.toString().includes('marketing-')) {
              analytics.track('design_system_component_used', {
                type: 'marketing',
                component: element.classList.toString(),
                page: window.location.pathname
              });
            }
            
            // Track app components  
            if (element.classList.toString().includes('app-')) {
              analytics.track('design_system_component_used', {
                type: 'app',
                component: element.classList.toString(),
                page: window.location.pathname
              });
            }
          }
        });
      });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
  }
};
```

#### Development Mode Component Inspector
```tsx
// components/design-system/DesignSystemInspector.tsx
export const DesignSystemInspector: React.FC = () => {
  const [inspecting, setInspecting] = useState(false);
  
  useEffect(() => {
    if (process.env.NODE_ENV !== 'development') return;
    
    const handleClick = (e: MouseEvent) => {
      if (!inspecting) return;
      
      e.preventDefault();
      e.stopPropagation();
      
      const target = e.target as Element;
      const designSystemClasses = Array.from(target.classList)
        .filter(cls => cls.includes('marketing-') || cls.includes('app-'));
      
      if (designSystemClasses.length === 0) {
        console.warn('Element not using design system:', target);
        alert(`Element not using design system:\n${target.tagName}\nClasses: ${target.className}`);
      } else {
        console.log('Design system usage:', designSystemClasses);
      }
    };
    
    if (inspecting) {
      document.addEventListener('click', handleClick, true);
    }
    
    return () => {
      document.removeEventListener('click', handleClick, true);
    };
  }, [inspecting]);
  
  if (process.env.NODE_ENV !== 'development') return null;
  
  return (
    <button
      onClick={() => setInspecting(!inspecting)}
      style={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        zIndex: 9999,
        background: inspecting ? '#DC2626' : '#059669',
        color: 'white',
        border: 'none',
        padding: '8px 12px',
        borderRadius: '4px'
      }}
    >
      {inspecting ? '🔍 Stop Inspecting' : '🔍 Inspect Design System'}
    </button>
  );
};
```

## Implementation Roadmap (Enforced Usage)

### Week 1: Foundation Enforcement
- [ ] Install PostCSS plugin for color validation
- [ ] Set up ESLint rules for design system compliance
- [ ] Configure pre-commit hooks for validation
- [ ] Create DesignSystemProvider wrapper components

### Week 2: Component Migration (FORCED)
- [ ] Replace all existing buttons with MarketingButton/AppButton
- [ ] Replace all cards with MarketingCard/AppCard
- [ ] Add TypeScript strict mode for Mantine component blocking
- [ ] Update all marketing pages to use marketing design system

### Week 3: Validation & Monitoring
- [ ] Enable runtime design system usage tracking
- [ ] Set up development mode component inspector
- [ ] Add Storybook documentation with mandatory examples
- [ ] Configure VS Code extensions for design token autocomplete

## Success Metrics for Design System Adoption

### Technical Metrics:
- **0 hardcoded colors** in production code
- **100% component consistency** between marketing and app
- **0 linting errors** related to design system violations
- **< 5 second** time to find appropriate component in Storybook

### Business Metrics:
- **Consistent brand experience** across all touchpoints
- **50% faster** development of new features using design system
- **90% fewer** design-related bug reports
- **Improved conversion** due to consistent marketing experience

This comprehensive enforcement strategy ensures our design systems aren't just pretty documentation - they become the **only way** to build UI components in PM33.