import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import PM33TopNav from '../components/layouts/PM33TopNav'

const meta: Meta<typeof PM33TopNav> = {
  title: 'PM33/PM33TopNav',
  component: PM33TopNav,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  argTypes: {
    theme: {
      control: { type: 'select' },
      options: ['light', 'dark'],
    },
    currentPage: {
      control: { type: 'select' },
      options: ['dashboard', 'intelligence', 'delivery', 'analytics'],
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

// Wrapper component to handle theme state
const ThemeWrapper = ({ theme: initialTheme, currentPage }: { theme: 'light' | 'dark', currentPage: string }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>(initialTheme)

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme)
  }

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
        currentPage={currentPage}
      />
      <div style={{ padding: '24px' }}>
        <h1 style={{ 
          fontSize: '2rem', 
          fontWeight: '700',
          marginBottom: '16px'
        }}>
          PM33 Navigation Demo
        </h1>
        <p style={{ 
          fontSize: '1rem',
          color: theme === 'dark' ? '#cbd5e1' : '#64748b',
          marginBottom: '24px'
        }}>
          This is a demonstration of the PM33TopNav component. Try switching themes and clicking navigation items.
        </p>
        <div style={{
          background: theme === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)'
            : 'rgba(248, 250, 252, 0.95)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: theme === 'dark' 
            ? '1px solid rgba(255, 255, 255, 0.1)'
            : 'none',
          borderRadius: '12px',
          padding: '24px'
        }}>
          <h3 style={{ 
            fontSize: '1.25rem', 
            fontWeight: '600',
            marginBottom: '12px'
          }}>
            Navigation Features
          </h3>
          <ul style={{ 
            listStyle: 'none', 
            padding: 0,
            margin: 0
          }}>
            <li style={{ marginBottom: '8px' }}>✅ PM33 logo with BETA badge</li>
            <li style={{ marginBottom: '8px' }}>✅ Four main navigation items</li>
            <li style={{ marginBottom: '8px' }}>✅ Theme toggle (light/dark)</li>
            <li style={{ marginBottom: '8px' }}>✅ User profile: Steve Saper - PM33 Founder</li>
            <li style={{ marginBottom: '8px' }}>✅ Active page highlighting</li>
            <li style={{ marginBottom: '8px' }}>✅ Responsive hover states</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Dark theme stories
export const DarkTheme: Story = {
  render: (args) => (
    <ThemeWrapper theme="dark" currentPage="dashboard" />
  ),
}

export const LightTheme: Story = {
  render: (args) => (
    <ThemeWrapper theme="light" currentPage="dashboard" />
  ),
}

export const DashboardActive: Story = {
  render: (args) => (
    <ThemeWrapper theme="dark" currentPage="dashboard" />
  ),
}

export const IntelligenceActive: Story = {
  render: (args) => (
    <ThemeWrapper theme="dark" currentPage="intelligence" />
  ),
}

export const DeliveryActive: Story = {
  render: (args) => (
    <ThemeWrapper theme="dark" currentPage="delivery" />
  ),
}

export const AnalyticsActive: Story = {
  render: (args) => (
    <ThemeWrapper theme="dark" currentPage="analytics" />
  ),
}

// Light theme variants
export const LightThemeDashboard: Story = {
  render: (args) => (
    <ThemeWrapper theme="light" currentPage="dashboard" />
  ),
}

export const LightThemeIntelligence: Story = {
  render: (args) => (
    <ThemeWrapper theme="light" currentPage="intelligence" />
  ),
}