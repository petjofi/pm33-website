# PM33 Design System

## Overview
PM33 uses a premium glass morphism design system with theme-aware components, professional enterprise UX, and Safari-compatible backdrop blur effects. The system prioritizes clarity, sophistication, and usability for product management professionals.

---

## 🎨 Color Palette

### Primary Colors
```css
/* PM33 Brand Colors */
--pm33-primary: #3b82f6        /* Blue - Primary actions */
--pm33-primary-hover: #2563eb  /* Blue hover state */
--pm33-secondary: #8b5cf6      /* Purple - Secondary actions */
--pm33-accent: #667eea         /* Purple gradient start */
--pm33-accent-end: #764ba2     /* Purple gradient end */
```

### Theme Colors

#### Dark Theme
```css
/* Backgrounds */
--dark-bg-primary: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)
--dark-bg-card: rgba(255, 255, 255, 0.05)
--dark-bg-nav: rgba(15, 12, 41, 0.95)

/* Text Colors */
--dark-text-primary: #ffffff
--dark-text-secondary: #cbd5e1
--dark-text-muted: #94a3b8
--dark-text-disabled: #64748b

/* Borders */
--dark-border: rgba(255, 255, 255, 0.1)
--dark-border-hover: rgba(255, 255, 255, 0.2)
```

#### Light Theme
```css
/* Backgrounds */
--light-bg-primary: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)
--light-bg-card: rgba(248, 250, 252, 0.95)
--light-bg-nav: rgba(255, 255, 255, 0.95)

/* Text Colors */
--light-text-primary: #000000
--light-text-secondary: #1e293b
--light-text-muted: #64748b
--light-text-disabled: #94a3b8

/* Borders */
--light-border: rgba(0, 0, 0, 0.1)
--light-border-hover: rgba(0, 0, 0, 0.2)
```

### Status Colors
```css
/* Success */
--success: #10b981
--success-bg: rgba(16, 185, 129, 0.1)

/* Warning */
--warning: #f59e0b
--warning-bg: rgba(245, 158, 11, 0.1)

/* Error */
--error: #ef4444
--error-bg: rgba(239, 68, 68, 0.1)

/* Info */
--info: #3b82f6
--info-bg: rgba(59, 130, 246, 0.1)
```

---

## 📝 Typography

### Font Stack
```css
font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

### Font Sizes & Weights
```css
/* Headings */
--text-4xl: 2.25rem    /* 36px - Page titles */
--text-3xl: 1.875rem   /* 30px - Section headers */
--text-2xl: 1.5rem     /* 24px - Card titles */
--text-xl: 1.25rem     /* 20px - Subheadings */
--text-lg: 1.125rem    /* 18px - Large body text */

/* Body Text */
--text-base: 1rem      /* 16px - Standard body */
--text-sm: 0.875rem    /* 14px - Small text */
--text-xs: 0.75rem     /* 12px - Captions, badges */

/* Font Weights */
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

### Typography Usage Examples
```tsx
// Page Title
<h1 style={{
  fontSize: '2.25rem',
  fontWeight: '700',
  color: theme === 'dark' ? '#ffffff' : '#000000',
  marginBottom: '1rem'
}}>
  Strategic Intelligence
</h1>

// Card Title
<h3 style={{
  fontSize: '1.25rem',
  fontWeight: '600',
  color: theme === 'dark' ? '#ffffff' : '#1e293b'
}}>
  Market Analysis
</h3>

// Body Text
<p style={{
  fontSize: '0.875rem',
  color: theme === 'dark' ? '#cbd5e1' : '#64748b',
  lineHeight: '1.5'
}}>
  Analysis description text
</p>

// Badge/Category Text
<span style={{
  fontSize: '0.75rem',
  fontWeight: '600',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: '#3b82f6'
}}>
  COMPETITIVE
</span>
```

---

## 🪟 Glass Morphism System

### Core Glass Morphism Recipe

#### Dark Theme Glass
```css
.glass-dark {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
```

#### Light Theme Glass
```css
.glass-light {
  background: rgba(248, 250, 252, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: none;
  border-radius: 12px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.8);
}
```

### Glass Morphism Variants

#### Navigation Glass
```css
/* Dark Navigation */
background: rgba(15, 12, 41, 0.95);
backdrop-filter: blur(20px);
border-bottom: 1px solid rgba(255, 255, 255, 0.1);

/* Light Navigation */
background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(20px);
border-bottom: 1px solid rgba(0, 0, 0, 0.1);
```

#### Card Glass with Hover Effect
```tsx
const cardStyle = {
  background: theme === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(248, 250, 252, 0.95)',
  backdropFilter: 'blur(20px)',
  WebkitBackdropFilter: 'blur(20px)',
  border: theme === 'dark' 
    ? '1px solid rgba(255, 255, 255, 0.1)'
    : 'none',
  borderRadius: '12px',
  boxShadow: theme === 'dark'
    ? '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
    : '0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.8)',
  transition: 'all 0.2s ease'
}

// Hover enhancement
const cardHoverStyle = {
  ...cardStyle,
  transform: 'translateY(-2px)',
  boxShadow: theme === 'dark'
    ? '0 12px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
    : '0 4px 16px rgba(0, 0, 0, 0.12), 0 1px 0 rgba(255, 255, 255, 0.9)'
}
```

#### Button Glass
```tsx
const buttonGlassStyle = {
  background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
  backdropFilter: 'blur(20px)',
  WebkitBackdropFilter: 'blur(20px)',
  border: 'none',
  borderRadius: '8px',
  color: 'white',
  padding: '12px 24px',
  fontWeight: '600',
  cursor: 'pointer',
  transition: 'all 0.2s ease'
}
```

---

## 📐 Spacing System

### Standard Spacing Scale
```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
--space-16: 4rem     /* 64px */
```

### Layout Spacing Guidelines
```tsx
// Card padding
padding: '1.5rem' // 24px - Standard card padding

// Grid gaps
gap: '1.5rem' // 24px - Standard grid gap

// Section margins
marginBottom: '2rem' // 32px - Between major sections

// Element spacing
marginBottom: '1rem' // 16px - Between related elements
marginBottom: '0.5rem' // 8px - Between closely related elements
```

---

## 🎭 Animation Standards

### Transition Timing
```css
/* Standard transitions */
transition: all 0.2s ease;

/* Slower transitions for complex changes */
transition: all 0.3s ease;

/* Quick micro-interactions */
transition: all 0.15s ease;
```

### Common Animation Patterns

#### Hover Lift Effect
```tsx
// Base state
transform: 'translateY(0px)'

// Hover state
transform: 'translateY(-2px)'
```

#### Scale Animation
```tsx
// Base state
transform: 'scale(1)'

// Hover state
transform: 'scale(1.02)'
```

#### Opacity Fade
```tsx
// Base state
opacity: 0.7

// Hover/Active state
opacity: 1
```

#### Box Shadow Growth
```tsx
// Base shadow
boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'

// Hover shadow
boxShadow: '0 12px 40px rgba(0, 0, 0, 0.4)'
```

---

## 🔧 Theme Implementation

### Theme Provider Pattern
```tsx
interface ThemeProps {
  theme: 'light' | 'dark'
  onThemeChange: (theme: 'light' | 'dark') => void
}

const useTheme = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const savedTheme = localStorage.getItem('pm33-theme') as 'light' | 'dark' || 'dark'
    setTheme(savedTheme)
    document.body.className = savedTheme
  }, [])

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme)
    localStorage.setItem('pm33-theme', newTheme)
    document.body.className = newTheme
  }

  return { theme, handleThemeChange, mounted }
}
```

### Theme-Aware Styling Helper
```tsx
const getThemeStyles = (theme: 'light' | 'dark') => ({
  background: theme === 'dark' 
    ? 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)'
    : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)',
  color: theme === 'dark' ? '#ffffff' : '#000000',
  cardBg: theme === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(248, 250, 252, 0.95)',
  textSecondary: theme === 'dark' ? '#cbd5e1' : '#64748b',
  border: theme === 'dark' 
    ? 'rgba(255, 255, 255, 0.1)' 
    : 'rgba(0, 0, 0, 0.1)'
})
```

---

## 📱 Responsive Design

### Breakpoint System
```css
/* Mobile First Approach */
--breakpoint-sm: 640px   /* Small devices */
--breakpoint-md: 768px   /* Medium devices */
--breakpoint-lg: 1024px  /* Large devices */
--breakpoint-xl: 1280px  /* Extra large devices */
```

### Responsive Grid Patterns
```tsx
// Auto-fit grid for cards
display: 'grid'
gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))'
gap: '1.5rem'

// 2-column layout with responsive collapse
display: 'grid'
gridTemplateColumns: window.innerWidth > 768 ? '1fr 1fr' : '1fr'
gap: '1.5rem'

// 3-column layout
display: 'grid'
gridTemplateColumns: window.innerWidth > 1024 
  ? '1fr 1fr 1fr' 
  : window.innerWidth > 768 
    ? '1fr 1fr' 
    : '1fr'
gap: '1.5rem'
```

### Mobile Adaptations
```tsx
// Mobile-friendly navigation
const isMobile = window.innerWidth < 768

const navStyle = {
  padding: isMobile ? '16px' : '24px',
  flexDirection: isMobile ? 'column' : 'row',
  gap: isMobile ? '8px' : '4px'
}

// Mobile card adjustments
const cardStyle = {
  padding: isMobile ? '1rem' : '1.5rem',
  borderRadius: isMobile ? '8px' : '12px'
}
```

---

## 🎯 Component Categories

### Navigation Components
- **PM33TopNav**: Primary navigation with logo, nav items, theme toggle
- **Breadcrumbs**: Page hierarchy navigation
- **TabNavigation**: Section switching within pages

### Layout Components
- **PM33Card**: Core glass morphism card with flexible content
- **GridLayout**: Responsive grid container
- **SplitLayout**: Two-column layout with responsive collapse

### Data Display
- **PM33MetricCard**: Key performance indicator display
- **PM33ActionCard**: Clickable action items with categories
- **StatusBadge**: Status indicators with theme-aware colors
- **ProgressBar**: Progress visualization

### Interactive Elements
- **GlassButton**: Primary and secondary button variants
- **ThemeToggle**: Light/dark theme switching
- **SearchInput**: Glass morphism search interface
- **FilterTabs**: Content filtering tabs

---

## 🎨 Brand Guidelines

### Logo Usage
```tsx
// Theme-aware logo
<img 
  src={theme === 'dark' ? '/pm33-logo-dark.png' : '/pm33-logo-light.png'}
  alt="PM33"
  style={{ height: '32px', width: 'auto' }}
/>
```

### BETA Badge
```tsx
const betaBadgeStyle = {
  background: 'linear-gradient(45deg, #667eea, #764ba2)',
  color: 'white',
  fontSize: '0.625rem',
  padding: '2px 6px',
  borderRadius: '4px',
  fontWeight: '600'
}
```

### Professional Messaging
- **Primary**: "PMO Transformation Platform"
- **Tagline**: "Transform into a PMO with AI"
- **User Identity**: "Steve Saper - PM33 Founder"
- **Status**: "BETA" badge on all primary branding

---

## 🔍 Accessibility Standards

### Color Contrast
- **Dark theme**: White text on dark backgrounds meets WCAG AAA
- **Light theme**: Dark text on light backgrounds meets WCAG AAA
- **Interactive elements**: Minimum 4.5:1 contrast ratio

### Focus States
```tsx
// Keyboard focus indicators
const focusStyle = {
  outline: `2px solid ${theme === 'dark' ? '#ffffff' : '#3b82f6'}`,
  outlineOffset: '2px'
}
```

### Semantic HTML
- Use proper heading hierarchy (h1 → h2 → h3)
- Button elements for interactive actions
- Navigation elements for navigation structures
- Main elements for primary content areas

---

## 🚀 Implementation Quick Start

### New Component Template
```tsx
'use client'

import { useState, useEffect, CSSProperties, ReactNode } from 'react'

interface ComponentProps {
  theme?: 'light' | 'dark'
  children: ReactNode
  className?: string
  style?: CSSProperties
}

export default function Component({
  theme = 'light',
  children,
  className = '',
  style = {}
}: ComponentProps) {
  const baseStyle: CSSProperties = {
    // Glass morphism base
    background: theme === 'dark' 
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(248, 250, 252, 0.95)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    
    // Theme-aware styling
    color: theme === 'dark' ? '#ffffff' : '#000000',
    border: theme === 'dark' 
      ? '1px solid rgba(255, 255, 255, 0.1)'
      : 'none',
    borderRadius: '12px',
    
    // Transitions
    transition: 'all 0.2s ease',
    
    // Merge with custom styles
    ...style
  }

  return (
    <div className={`component ${className}`} style={baseStyle}>
      {children}
    </div>
  )
}
```

### Page Template
```tsx
'use client'

import { useState, useEffect } from 'react'
import PM33TopNav from '@/components/layouts/PM33TopNav'

export default function Page() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const savedTheme = localStorage.getItem('pm33-theme') as 'light' | 'dark' || 'dark'
    setTheme(savedTheme)
    document.body.className = savedTheme
  }, [])

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme)
    localStorage.setItem('pm33-theme', newTheme)
    document.body.className = newTheme
  }

  if (!mounted) return null

  return (
    <div style={{
      background: theme === 'dark' 
        ? 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)'
        : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)',
      minHeight: '100vh',
      color: theme === 'dark' ? '#ffffff' : '#000000',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <PM33TopNav 
        theme={theme} 
        onThemeChange={handleThemeChange}
        currentPage="page-id"
      />
      
      <main style={{ padding: '24px' }}>
        {/* Page content */}
      </main>
    </div>
  )
}
```

---

*PM33 Design System v2.0 - Glass Morphism Enterprise Edition*
*Last Updated: Current session*