# PM33 Component System Documentation

## Overview
The PM33 component system uses inline CSS styling with glass morphism effects for a consistent, professional enterprise UI. All components are theme-aware (light/dark) and follow PM33 design standards.

## Architecture Pattern
- **No External UI Libraries**: Pure inline CSS styling for maximum control
- **Theme System**: Light/dark theme switching with localStorage persistence
- **Glass Morphism**: backdrop-filter blur effects with Safari compatibility
- **Professional UX**: Hover effects, transitions, and enterprise-grade interactions

---

## 🧭 Navigation Components

### PM33TopNav
**Primary navigation bar with logo, nav items, theme toggle, and user profile**

```tsx
import PM33TopNav from '@/components/layouts/PM33TopNav'

<PM33TopNav 
  theme="dark" 
  onThemeChange={(theme) => setTheme(theme)}
  currentPage="dashboard" 
/>
```

**Props:**
- `theme`: `'light' | 'dark'` - Current theme
- `onThemeChange`: `(theme: 'light' | 'dark') => void` - Theme change handler
- `currentPage?`: `string` - Active page identifier for highlighting

**Features:**
- PM33 logo with BETA badge (theme-aware)
- Navigation items: Command Center, Strategic Intelligence, Project Delivery, Analytics
- Single theme toggle button with smooth transitions
- Steve Saper - PM33 Founder profile button
- Persistent theme via localStorage
- Responsive hover states and active indicators

**Design System:**
```css
/* Glass morphism navigation */
background: rgba(15, 12, 41, 0.95) /* dark */ | rgba(255, 255, 255, 0.95) /* light */
backdrop-filter: blur(20px)
border-bottom: 1px solid rgba(255, 255, 255, 0.1) /* dark */ | rgba(0, 0, 0, 0.1) /* light */
```

---

## 🎴 Card Components

### PM33Card
**Core glass morphism card component with flexible content slots**

```tsx
import PM33Card from '@/components/ui/PM33Card'

<PM33Card 
  theme="dark" 
  hoverable 
  clickable 
  onClick={() => console.log('Clicked')}
  header={<h3>Card Title</h3>}
  footer={<button>Action</button>}
>
  <p>Card content goes here</p>
</PM33Card>
```

**Props:**
- `children`: `ReactNode` - Main card content
- `theme?`: `'light' | 'dark'` - Theme variant (default: 'light')
- `className?`: `string` - Additional CSS classes
- `style?`: `CSSProperties` - Custom styles
- `header?`: `ReactNode` - Optional header content
- `footer?`: `ReactNode` - Optional footer content
- `hoverable?`: `boolean` - Enable hover effects (default: true)
- `clickable?`: `boolean` - Enable pointer cursor (default: false)
- `onClick?`: `() => void` - Click handler

**Glass Morphism Specs:**
```css
/* Dark theme */
background: rgba(255, 255, 255, 0.05)
backdrop-filter: blur(20px)
border: 1px solid rgba(255, 255, 255, 0.1)
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)

/* Light theme */
background: rgba(248, 250, 252, 0.95)
backdrop-filter: blur(20px)
border: none
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.8)
```

### PM33ActionCard
**Specialized card for action items with category, title, and description**

```tsx
import { PM33ActionCard } from '@/components/ui/PM33Card'

<PM33ActionCard
  category="COMPETITIVE"
  categoryColor="#3b82f6"
  title="Market Analysis"
  description="Analyze competitor pricing strategies"
  theme="dark"
  onClick={() => console.log('Action clicked')}
/>
```

**Props:**
- `title`: `string` - Action title
- `description`: `string` - Action description
- `category`: `string` - Category badge text
- `categoryColor?`: `string` - Category badge color (default: '#3b82f6')
- `theme?`: `'light' | 'dark'` - Theme variant
- `onClick?`: `() => void` - Click handler

### PM33MetricCard
**Specialized card for displaying metrics with icon, title, value, and subtitle**

```tsx
import { PM33MetricCard } from '@/components/ui/PM33Card'

<PM33MetricCard
  icon={<BarChart3 size={20} />}
  title="Monthly Recurring Revenue"
  value="$47K"
  subtitle="+12% from last month"
  theme="dark"
/>
```

**Props:**
- `icon`: `ReactNode` - Icon component (typically Lucide icon)
- `title`: `string` - Metric title
- `value`: `string | ReactNode` - Main metric value
- `subtitle?`: `string` - Optional subtitle/comparison
- `theme?`: `'light' | 'dark'` - Theme variant

### GlassCard (Legacy)
**Simple glass morphism card using Tailwind classes (legacy component)**

```tsx
import GlassCard from '@/components/ui/GlassCard'

<GlassCard className="custom-class">
  <p>Content</p>
</GlassCard>
```

**Note:** Use PM33Card instead for new implementations as it provides better theme control and features.

---

## 📱 Page Templates

### Dashboard Page Structure
**Main command center layout with PM33TopNav and grid system**

```tsx
// Basic dashboard structure
export default function Dashboard() {
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
        currentPage="dashboard"
      />
      
      <main style={{ padding: '24px' }}>
        {/* Page content */}
      </main>
    </div>
  )
}
```

---

## 🎨 Design System Standards

### Glass Morphism Specifications

**Dark Theme Glass:**
```css
background: rgba(255, 255, 255, 0.05)
backdrop-filter: blur(20px)
-webkit-backdrop-filter: blur(20px) /* Safari */
border: 1px solid rgba(255, 255, 255, 0.1)
border-radius: 12px
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)
```

**Light Theme Glass:**
```css
background: rgba(248, 250, 252, 0.95)
backdrop-filter: blur(20px)
-webkit-backdrop-filter: blur(20px) /* Safari */
border: none
border-radius: 12px
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.8)
```

### Hover Effects
```css
/* Standard hover transition */
transition: all 0.2s ease
transform: translateY(-2px) /* on hover */
box-shadow: /* enhanced shadow on hover */
```

### Theme Implementation
```tsx
// Theme persistence pattern
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
```

---

## 🧩 Component Integration Examples

### Strategic Intelligence Page
```tsx
export default function IntelligencePage() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [selectedFramework, setSelectedFramework] = useState('ICE')
  
  const frameworks = [
    { id: 'ICE', name: 'Impact • Confidence • Ease' },
    { id: 'RICE', name: 'Reach • Impact • Confidence • Effort' },
    { id: 'PORTER', name: 'Porter\'s Five Forces' },
    { id: 'SWOT', name: 'Strengths • Weaknesses • Opportunities • Threats' }
  ]

  return (
    <div style={{
      background: theme === 'dark' 
        ? 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)'
        : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)',
      minHeight: '100vh'
    }}>
      <PM33TopNav theme={theme} onThemeChange={handleThemeChange} currentPage="intelligence" />
      
      <main style={{ padding: '24px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <PM33Card theme={theme}>
          <h2>Strategic Framework Selection</h2>
          {frameworks.map(framework => (
            <PM33ActionCard
              key={framework.id}
              category="FRAMEWORK"
              title={framework.id}
              description={framework.name}
              theme={theme}
              onClick={() => setSelectedFramework(framework.id)}
            />
          ))}
        </PM33Card>
        
        <PM33Card theme={theme}>
          <h2>Analysis Results</h2>
          <p>Selected: {selectedFramework}</p>
        </PM33Card>
      </main>
    </div>
  )
}
```

### Analytics Dashboard Grid
```tsx
export default function AnalyticsPage() {
  const metrics = [
    { icon: <Users size={20} />, title: 'Active Users', value: '2,847', subtitle: '+15% this month' },
    { icon: <BarChart3 size={20} />, title: 'MRR', value: '$47K', subtitle: '+12% from last month' },
    { icon: <Target size={20} />, title: 'Conversion', value: '4.2%', subtitle: '+0.8% this week' }
  ]

  return (
    <main style={{ 
      padding: '24px',
      display: 'grid', 
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '24px'
    }}>
      {metrics.map((metric, index) => (
        <PM33MetricCard
          key={index}
          icon={metric.icon}
          title={metric.title}
          value={metric.value}
          subtitle={metric.subtitle}
          theme={theme}
        />
      ))}
    </main>
  )
}
```

---

## 🔧 Development Guidelines

### Component Creation Checklist
- [ ] Inline CSS styling (no Tailwind/Mantine in new components)
- [ ] Theme awareness (light/dark variants)
- [ ] Glass morphism effects with Safari compatibility
- [ ] Hover effects and smooth transitions
- [ ] TypeScript interfaces for all props
- [ ] JSDoc comments with description and features
- [ ] Responsive design considerations
- [ ] Accessibility (semantic HTML, ARIA labels)

### Styling Best Practices
1. **Use inline styles** for component-specific styling
2. **Theme-aware colors** using ternary operators
3. **Glass morphism** with backdrop-filter and WebkitBackdropFilter
4. **Smooth transitions** with `transition: 'all 0.2s ease'`
5. **Consistent spacing** using rem units (0.5rem, 1rem, 1.5rem, 2rem)
6. **Professional shadows** with multiple box-shadow values
7. **Interactive states** with hover/focus effects

### Common Patterns
```tsx
// Theme-aware background
background: theme === 'dark' 
  ? 'rgba(255, 255, 255, 0.05)'
  : 'rgba(248, 250, 252, 0.95)'

// Theme-aware text color
color: theme === 'dark' ? '#ffffff' : '#000000'

// Theme-aware border
border: theme === 'dark' 
  ? '1px solid rgba(255, 255, 255, 0.1)'
  : 'none'

// Glass morphism essentials
backdropFilter: 'blur(20px)'
WebkitBackdropFilter: 'blur(20px)'
```

---

## 📁 File Organization

```
components/
├── layouts/
│   └── PM33TopNav.tsx        # Main navigation component
├── ui/
│   ├── PM33Card.tsx          # Core card component with variants
│   ├── GlassCard.tsx         # Legacy glass card (use PM33Card instead)
│   └── [other-ui-components]
├── shared/
│   └── [shared-components]
└── templates/
    └── PM33DashboardTemplate.tsx
```

---

## 🚨 Migration Notes

### From Mantine to PM33 Components
- Replace `<Card>` with `<PM33Card>`
- Replace Mantine theme providers with inline theme props
- Convert Mantine color props to theme-aware inline styles
- Update hover effects to use onMouseEnter/onMouseLeave patterns

### Legacy Component Updates
- `GlassCard` → `PM33Card` (better features and theme control)
- Tailwind classes → inline styles for consistency
- Theme context → direct theme props for better performance

---

*Last Updated: Current session*
*Component System Version: 2.0 - Inline Styling with Glass Morphism*