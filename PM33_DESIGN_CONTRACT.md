# PM33 Design Contract

## Visual Identity (IMMUTABLE)
```css
/* Primary Brand Colors */
--pm33-primary: #667eea;        /* Purple-blue primary */
--pm33-secondary: #764ba2;      /* Deep purple secondary */
--pm33-success: #10b981;        /* Teal success/accent */

/* Theme Backgrounds */
--pm33-bg-light: #ffffff;       /* Pure white light background */
--pm33-bg-dark: #0a0e27;        /* Deep navy dark background */

/* Brand Gradient (Core Identity) */
--pm33-brand-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## Non-Negotiable Design Elements

### 1. Glass Morphism on ALL Cards (MANDATORY)
```css
.pm33-glass {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background: rgba(248, 250, 252, 0.95); /* Light mode */
  background: rgba(255, 255, 255, 0.05); /* Dark mode */
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  border-radius: 16px;
}
```

### 2. Gradient Text for Headlines (REQUIRED)
```css
.pm33-gradient-text {
  background: var(--pm33-brand-gradient);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 600;
}
```

### 3. Theme Toggle Compliance (MANDATORY)
**Dark Mode Requirements:**
- Backgrounds: Dark colors (`#0a0e27`, `#1e293b`, `rgba(0,0,0,0.9)`)
- Text: Light colors (`#ffffff`, `#e2e8f0`, `#f8fafc`)
- Never: Light backgrounds or dark text in dark mode

**Light Mode Requirements:**
- Backgrounds: Light colors (`#ffffff`, `#f8fafc`, `rgba(255,255,255,0.95)`)
- Text: Dark colors (`#000000`, `#1a202c`, `#2d3748`)
- Never: Dark backgrounds or light text in light mode

```css
/* Theme-aware component example */
.pm33-card {
  background: rgba(255, 255, 255, 0.95); /* Light mode */
  color: #1a202c; /* Dark text for light mode */
}

[data-theme="dark"] .pm33-card {
  background: rgba(0, 0, 0, 0.9); /* Dark mode */
  color: #ffffff; /* Light text for dark mode */
}
```

### 4. Navigation Consistency (REQUIRED)
**All navigation components must have:**
- Glass morphism: `backdrop-filter: blur(20px)`
- Theme awareness: Different backgrounds for dark/light
- Consistent positioning: `top-0 z-50 fixed`
- Brand colors only: No off-brand colors

```css
.pm33-nav {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .pm33-nav {
  background: rgba(0, 0, 0, 0.9);
}
```

### 5. Button Standards (ENFORCED)
**All buttons must have:**
- PM33 brand colors: `#667eea`, `#764ba2`, `#10b981`
- Hover states: `hover:scale-105` or `hover:opacity-90`
- Professional shadows: `shadow-xl` or `shadow-2xl` (never `shadow-sm`)
- Theme support: Light/dark variants for all colors

```css
.pm33-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.pm33-button:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
}
```

### 6. 16px Minimum Touch Targets (ACCESSIBILITY)
- All interactive elements: minimum 16px
- Primary actions: 44px × 44px preferred
- Adjacent element spacing: minimum 8px

### 4. 8px Spacing Grid (CONSISTENCY)
```css
--pm33-spacing-unit: 8px;
--pm33-spacing-xs: 4px;   /* 0.5x */
--pm33-spacing-sm: 8px;   /* 1x */
--pm33-spacing-md: 24px;  /* 3x */
--pm33-spacing-lg: 32px;  /* 4x */
--pm33-spacing-xl: 48px;  /* 6x */
```

### 5. Professional Shadows (NEVER FLAT)
```css
--pm33-shadow-light: 0 8px 32px rgba(0, 0, 0, 0.08);
--pm33-shadow-dark: 0 8px 32px rgba(0, 0, 0, 0.3);
--pm33-shadow-hover: 0 12px 40px rgba(102, 126, 234, 0.15);
```

## Component Hierarchy Standards

### Hero Sections
- **Background**: MUST use full gradient background
- **Overlay**: `rgba(0,0,0,0.2)` with `backdrop-blur(10px)`
- **Content**: Glass morphism container
- **Headline**: 56px white with gradient text variant
- **CTA**: White glass morphism with `hover: scale(1.05)`

### Cards
- **Style**: Glass morphism + hover effects
- **Hover**: `translateY(-4px)` and shadow increase
- **Content**: High contrast text (WCAG AA minimum)

### Buttons
- **Primary**: Gradient background with white text
- **Secondary**: Glass morphism with theme-aware text
- **Interactive**: 200ms ease transitions

### Text Hierarchy
- **High contrast**: WCAG AA minimum (4.5:1 normal, 3:1 large)
- **Light mode**: Dark text on light backgrounds
- **Dark mode**: Light text on dark backgrounds

## Reference-Based Implementation Specifications

### Exact Card Design Implementation
```bash
"Implement this exact card design:
- Glass background: rgba(255,255,255,0.1)
- Blur: 20px backdrop-filter
- Border: 1px solid rgba(255,255,255,0.2)
- Shadow: 0 8px 32px rgba(31,38,135,0.15)
- Hover: transform scale(1.02) + translateY(-4px)
- Border radius: 16px
- Padding: 24px"
```

## Component-First Development Order

### Phase 1: Core Components (Build BEFORE pages)
1. **PM33Card.tsx**: Glass morphism card with hover effects
2. **PM33Button.tsx**: Gradient and glass button variants
3. **PM33Layout.tsx**: 8px grid system layout container
4. **PM33Typography.tsx**: Gradient text and contrast utilities

### Phase 2: Page Implementation (Use ONLY core components)
```bash
"Build homepage using ONLY these components:
- PM33Card for all content blocks
- PM33Button for all CTAs
- PM33Layout for grid structure
- PM33Typography for text hierarchy"
```

## Design System Constraints

### Allowed Colors (IMMUTABLE)
```typescript
export const ALLOWED_COLORS = {
  text: ['#0F172A', '#475569', '#FFFFFF', '#E2E8F0'],
  background: ['#FFFFFF', '#F8FAFC', '#667eea', '#764ba2', '#0a0e27'],
  borders: ['rgba(255,255,255,0.1)', 'rgba(0,0,0,0.1)'],
  // NO OTHER COLORS ALLOWED WITHOUT EXPLICIT PERMISSION
} as const;
```

### Required Styles (MANDATORY)
```typescript
export const REQUIRED_STYLES = {
  card: 'pm33-glass backdrop-blur border shadow-lg rounded-2xl',
  button: 'gradient-bg or glass-variant with hover-scale',
  section: 'py-20 px-8 max-w-6xl mx-auto',
  headline: 'pm33-gradient-text font-semibold',
} as const;
```

## Visual Quality Gates (MUST PASS ALL)

### Before Committing Any UI Code:
- [ ] **Premium Feel**: Matches Linear.app/Vercel.com quality standards
- [ ] **Glass Morphism**: All cards have backdrop blur effects
- [ ] **Gradients**: Headlines and CTAs use brand gradients
- [ ] **Proper Spacing**: Never cramped, follows 8px grid
- [ ] **Typography Hierarchy**: Clear visual hierarchy with contrast
- [ ] **Smooth Animations**: 200ms ease transitions on interactions
- [ ] **High Contrast**: WCAG AA compliant text contrast
- [ ] **Hover States**: All interactive elements have hover feedback

## Style Preservation Rules

### NEVER REMOVE:
- Glass morphism effects (`backdrop-filter`)
- Gradient backgrounds (`linear-gradient`)
- Shadow depths (`box-shadow`)
- Hover animations (`transform`, `scale`)
- Border radius (`border-radius: 16px`)
- Professional spacing (`padding`, `margin` on 8px grid)

### NEVER ADD:
- Flat colors without gradients or glass effects
- Sharp corners (always `border-radius: 16px` minimum)
- Basic HTML styling without CSS enhancements
- Generic shadows (always use brand shadow variables)
- Static elements without hover states
- Non-grid spacing values

## Implementation Example Template

```bash
"Create a homepage that matches this EXACT specification:

HERO SECTION:
- Background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
- Overlay: rgba(0,0,0,0.2) with backdrop-blur(10px)
- Content container: glass morphism card (pm33-glass class)
- Headline: 56px, gradient text using pm33-gradient-text
- CTA buttons: Glass morphism with hover scale(1.05)

FEATURES SECTION:
- Grid: 3 columns desktop, 1 mobile with 24px gaps
- Each card: Glass morphism with 20px blur
- Hover: translateY(-4px) + shadow increase
- Icons: 48px with gradient background circle

CONSTRAINTS:
- Use ONLY design system colors
- Follow 8px spacing grid exactly
- All cards MUST have glass morphism
- All headlines MUST have gradient text
- All interactions MUST have hover states

FORBIDDEN:
- Flat design elements
- Non-brand colors
- Missing hover states
- Sharp corners
- Generic shadows"
```

## Quality Control Framework

### Required Checklist (TypeScript Interface)
```typescript
interface QualityChecklist {
  visualImpact: boolean;      // Wow factor on first view?
  brandConsistency: boolean;  // Uses exact brand colors?
  glassMorphism: boolean;     // All cards have backdrop blur?
  gradients: boolean;         // Headlines and CTAs use gradients?
  animations: boolean;        // Smooth 200ms transitions?
  accessibility: boolean;     // WCAG AA contrast compliance?
  responsive: boolean;        // Works on mobile/tablet/desktop?
  hoverStates: boolean;       // All interactive elements respond?
  spacing: boolean;           // Follows 8px grid system?
  shadows: boolean;          // Professional depth, never flat?
}
```

### Iterative Refinement Process
```bash
Step 1: "Build basic structure with correct 8px grid layout"
Step 2: "Add glass morphism to ALL cards with exact blur values"
Step 3: "Add gradients to headlines and CTA buttons"
Step 4: "Add hover animations (scale + translateY)"
Step 5: "Add professional shadow depth and visual hierarchy"
Step 6: "Verify WCAG AA contrast ratios"
Step 7: "Test responsive behavior on all viewports"
```

---

## Contract Enforcement

**This design contract is BINDING for all PM33 development work.**

### Violations = Immediate Fix Required
1. **Flat cards** without glass morphism
2. **Plain text headlines** missing gradient treatment
3. **Touch targets** under 16px
4. **Non-grid spacing** breaking 8px system
5. **Flat design** elements without shadows
6. **Poor contrast** ratios below WCAG AA
7. **Missing hover states** on interactive elements

### Quality Verification Process
Every component must pass design contract validation:
1. **Visual inspection** against specification
2. **Contrast testing** for accessibility
3. **Interaction testing** for hover states
4. **Responsive testing** across viewports
5. **Brand consistency** verification

**Authority**: This contract overrides any conflicting design decisions. When in doubt, prioritize contract compliance over feature speed.