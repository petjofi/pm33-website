import type { Meta, StoryObj } from '@storybook/react'
import { Target, BarChart3, Users } from 'lucide-react'
import PM33Card, { PM33ActionCard, PM33MetricCard } from '../components/ui/PM33Card'

const meta: Meta<typeof PM33Card> = {
  title: 'PM33/PM33Card',
  component: PM33Card,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    theme: {
      control: { type: 'select' },
      options: ['light', 'dark'],
    },
    hoverable: {
      control: { type: 'boolean' },
    },
    clickable: {
      control: { type: 'boolean' },
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

// Basic PM33Card stories
export const LightTheme: Story = {
  args: {
    theme: 'light',
    children: (
      <div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem', fontWeight: '600' }}>
          Light Theme Card
        </h3>
        <p style={{ margin: 0, color: '#64748b' }}>
          This is a PM33Card in light theme with glass morphism effects.
        </p>
      </div>
    ),
  },
}

export const DarkTheme: Story = {
  args: {
    theme: 'dark',
    children: (
      <div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem', fontWeight: '600', color: '#ffffff' }}>
          Dark Theme Card
        </h3>
        <p style={{ margin: 0, color: '#cbd5e1' }}>
          This is a PM33Card in dark theme with glass morphism effects.
        </p>
      </div>
    ),
  },
}

export const WithHeader: Story = {
  args: {
    theme: 'dark',
    header: (
      <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700', color: '#ffffff' }}>
        Card Header
      </h2>
    ),
    children: (
      <p style={{ margin: 0, color: '#cbd5e1' }}>
        This card has a header section with a divider.
      </p>
    ),
  },
}

export const WithFooter: Story = {
  args: {
    theme: 'dark',
    children: (
      <p style={{ margin: 0, color: '#cbd5e1' }}>
        This card has a footer section with actions.
      </p>
    ),
    footer: (
      <div style={{ display: 'flex', gap: '8px' }}>
        <button style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          padding: '8px 16px',
          fontSize: '0.875rem',
          fontWeight: '500',
          cursor: 'pointer'
        }}>
          Primary Action
        </button>
        <button style={{
          background: 'transparent',
          color: '#cbd5e1',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '6px',
          padding: '8px 16px',
          fontSize: '0.875rem',
          fontWeight: '500',
          cursor: 'pointer'
        }}>
          Secondary
        </button>
      </div>
    ),
  },
}

export const Clickable: Story = {
  args: {
    theme: 'dark',
    clickable: true,
    onClick: () => alert('Card clicked!'),
    children: (
      <div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem', fontWeight: '600', color: '#ffffff' }}>
          Clickable Card
        </h3>
        <p style={{ margin: 0, color: '#cbd5e1' }}>
          This card is clickable. Try clicking it!
        </p>
      </div>
    ),
  },
}

// PM33ActionCard stories
export const ActionCard: Story = {
  render: (args) => (
    <PM33ActionCard
      category="COMPETITIVE"
      categoryColor="#3b82f6"
      title="Market Analysis"
      description="Analyze competitor pricing strategies and market positioning to identify opportunities."
      theme="dark"
      onClick={() => alert('Action card clicked!')}
    />
  ),
}

export const ActionCardLight: Story = {
  render: (args) => (
    <PM33ActionCard
      category="RESOURCE"
      categoryColor="#10b981"
      title="Resource Optimization"
      description="Optimize team allocation and budget distribution across product initiatives."
      theme="light"
      onClick={() => alert('Action card clicked!')}
    />
  ),
}

export const ActionCardRisk: Story = {
  render: (args) => (
    <PM33ActionCard
      category="RISK"
      categoryColor="#ef4444"
      title="Risk Assessment"
      description="Identify and mitigate potential risks in the current product roadmap."
      theme="dark"
      onClick={() => alert('Action card clicked!')}
    />
  ),
}

// PM33MetricCard stories
export const MetricCard: Story = {
  render: (args) => (
    <PM33MetricCard
      icon={<BarChart3 size={20} />}
      title="Monthly Recurring Revenue"
      value="$47K"
      subtitle="+12% from last month"
      theme="dark"
    />
  ),
}

export const MetricCardLight: Story = {
  render: (args) => (
    <PM33MetricCard
      icon={<Users size={20} />}
      title="Active Users"
      value="2,847"
      subtitle="+15% this month"
      theme="light"
    />
  ),
}

export const MetricCardTarget: Story = {
  render: (args) => (
    <PM33MetricCard
      icon={<Target size={20} />}
      title="Conversion Rate"
      value="4.2%"
      subtitle="+0.8% this week"
      theme="dark"
    />
  ),
}

// Grid showcase
export const CardGrid: Story = {
  render: (args) => (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '24px',
      maxWidth: '1200px',
      padding: '24px',
      background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
      borderRadius: '12px'
    }}>
      <PM33MetricCard
        icon={<BarChart3 size={20} />}
        title="Monthly Recurring Revenue"
        value="$47K"
        subtitle="+12% from last month"
        theme="dark"
      />
      <PM33MetricCard
        icon={<Users size={20} />}
        title="Active Users"
        value="2,847"
        subtitle="+15% this month"
        theme="dark"
      />
      <PM33MetricCard
        icon={<Target size={20} />}
        title="Conversion Rate"
        value="4.2%"
        subtitle="+0.8% this week"
        theme="dark"
      />
      <PM33ActionCard
        category="COMPETITIVE"
        categoryColor="#3b82f6"
        title="Market Analysis"
        description="Analyze competitor pricing strategies and market positioning."
        theme="dark"
      />
      <PM33ActionCard
        category="RESOURCE"
        categoryColor="#10b981"
        title="Resource Optimization"
        description="Optimize team allocation and budget distribution."
        theme="dark"
      />
      <PM33ActionCard
        category="RISK"
        categoryColor="#ef4444"
        title="Risk Assessment"
        description="Identify and mitigate potential roadmap risks."
        theme="dark"
      />
    </div>
  ),
}