'use client';

import React from 'react';
import { 
  Container, 
  Grid, 
  Card, 
  Title, 
  Text, 
  Group, 
  Stack, 
  Badge, 
  SimpleGrid, 
  Box,
  Progress,
  ActionIcon,
  RingProgress
} from '@mantine/core';
import { 
  IconBrain, 
  IconTrendingUp, 
  IconUsers, 
  IconTarget,
  IconChevronRight,
  IconSpark,
  IconRocket,
  IconClock
} from '@tabler/icons-react';
import AppNavigation from '../../../components/app/AppNavigation';
import { useDesignSystem } from '../../../components/app/DesignSystemProvider';

export default function DashboardPage() {
  const { theme } = useDesignSystem();

  const metrics = [
    {
      title: 'Strategic Intelligence Score',
      value: 87,
      change: '+12%',
      icon: IconBrain,
      color: 'blue'
    },
    {
      title: 'Project Velocity',
      value: 94,
      change: '+8%',
      icon: IconRocket,
      color: 'green'
    },
    {
      title: 'Team Efficiency',
      value: 76,
      change: '+15%',
      icon: IconUsers,
      color: 'purple'
    },
    {
      title: 'Strategic Alignment',
      value: 82,
      change: '+5%',
      icon: IconTarget,
      color: 'orange'
    }
  ];

  const recentInsights = [
    {
      title: 'Resource Optimization Opportunity',
      description: 'AI identified 23% efficiency gain in Sprint Planning workflow',
      priority: 'High',
      time: '2 hours ago'
    },
    {
      title: 'Strategic Risk Assessment',
      description: 'Market analysis suggests pivot in Q2 feature prioritization',
      priority: 'Medium',
      time: '4 hours ago'
    },
    {
      title: 'Team Performance Insight',
      description: 'Cross-team collaboration improved 34% after process optimization',
      priority: 'Low',
      time: '6 hours ago'
    }
  ];

  return (
    <Box style={{ minHeight: '100vh', backgroundColor: theme.colors.bgSecondary }}>
      <AppNavigation />
      
      <Container size={1200} py={32}>
        <Stack gap={32}>
          {/* Header */}
          <Stack gap={8}>
            <Title order={1} fw={700} style={{ color: theme.colors.textPrimary, fontSize: '28px' }}>
              Strategic Intelligence Dashboard
            </Title>
            <Text size="lg" style={{ color: theme.colors.textSecondary }}>
              PMO-level insights and strategic intelligence at your fingertips
            </Text>
          </Stack>

          {/* Metrics Grid */}
          <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing={24}>
            {metrics.map((metric, index) => {
              const IconComponent = metric.icon;
              return (
                <Card 
                  key={index}
                  p={24}
                  radius={12}
                  shadow="sm"
                  style={{ 
                    backgroundColor: theme.colors.bgPrimary,
                    border: `1px solid ${theme.colors.bgAccent}`
                  }}
                >
                  <Stack gap={16}>
                    <Group justify="space-between">
                      <ActionIcon
                        size={40}
                        radius={10}
                        variant="light"
                        color={metric.color}
                      >
                        <IconComponent size={20} />
                      </ActionIcon>
                      <Badge
                        size="sm"
                        color="green"
                        variant="light"
                      >
                        {metric.change}
                      </Badge>
                    </Group>
                    
                    <Stack gap={8}>
                      <Text size="sm" fw={500} style={{ color: theme.colors.textTertiary }}>
                        {metric.title}
                      </Text>
                      <Group gap={12} align="end">
                        <Text size="xl" fw={700} style={{ color: theme.colors.textPrimary }}>
                          {metric.value}%
                        </Text>
                        <RingProgress
                          size={32}
                          thickness={3}
                          sections={[{ value: metric.value, color: metric.color }]}
                        />
                      </Group>
                    </Stack>
                  </Stack>
                </Card>
              );
            })}
          </SimpleGrid>

          {/* Main Content Grid */}
          <Grid>
            <Grid.Col span={{ base: 12, lg: 8 }}>
              <Card 
                p={32}
                radius={12}
                shadow="sm"
                style={{ 
                  backgroundColor: theme.colors.bgPrimary,
                  border: `1px solid ${theme.colors.bgAccent}`,
                  height: '400px'
                }}
              >
                <Stack gap={24}>
                  <Group justify="space-between">
                    <Stack gap={4}>
                      <Title order={3} fw={600} style={{ color: theme.colors.textPrimary }}>
                        Strategic Performance Trends
                      </Title>
                      <Text size="sm" style={{ color: theme.colors.textTertiary }}>
                        AI-powered insights across all strategic dimensions
                      </Text>
                    </Stack>
                    <ActionIcon variant="subtle" color="gray" size="lg">
                      <IconChevronRight size={16} />
                    </ActionIcon>
                  </Group>
                  
                  <Box 
                    style={{ 
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: theme.colors.bgSecondary,
                      borderRadius: '8px',
                      border: `2px dashed ${theme.colors.bgAccent}`
                    }}
                  >
                    <Stack align="center" gap={16}>
                      <IconSpark size={48} style={{ color: theme.colors.textMuted }} />
                      <Text size="lg" fw={500} style={{ color: theme.colors.textSecondary }}>
                        Interactive Intelligence Chart
                      </Text>
                      <Text size="sm" style={{ color: theme.colors.textMuted }}>
                        Real-time strategic performance visualization
                      </Text>
                    </Stack>
                  </Box>
                </Stack>
              </Card>
            </Grid.Col>

            <Grid.Col span={{ base: 12, lg: 4 }}>
              <Card 
                p={24}
                radius={12}
                shadow="sm"
                style={{ 
                  backgroundColor: theme.colors.bgPrimary,
                  border: `1px solid ${theme.colors.bgAccent}`,
                  height: '400px'
                }}
              >
                <Stack gap={24} h="100%">
                  <Group justify="space-between">
                    <Stack gap={4}>
                      <Title order={4} fw={600} style={{ color: theme.colors.textPrimary }}>
                        Recent AI Insights
                      </Title>
                      <Text size="sm" style={{ color: theme.colors.textTertiary }}>
                        Strategic intelligence alerts
                      </Text>
                    </Stack>
                  </Group>
                  
                  <Stack gap={16} style={{ flex: 1 }}>
                    {recentInsights.map((insight, index) => (
                      <Card
                        key={index}
                        p={16}
                        radius={8}
                        style={{ 
                          backgroundColor: theme.colors.bgSecondary,
                          border: `1px solid ${theme.colors.bgAccent}`
                        }}
                      >
                        <Stack gap={8}>
                          <Group justify="space-between">
                            <Badge
                              size="xs"
                              color={insight.priority === 'High' ? 'red' : insight.priority === 'Medium' ? 'yellow' : 'gray'}
                              variant="light"
                            >
                              {insight.priority}
                            </Badge>
                            <Group gap={4}>
                              <IconClock size={12} style={{ color: theme.colors.textMuted }} />
                              <Text size="xs" style={{ color: theme.colors.textMuted }}>
                                {insight.time}
                              </Text>
                            </Group>
                          </Group>
                          <Text size="sm" fw={600} style={{ color: theme.colors.textPrimary }}>
                            {insight.title}
                          </Text>
                          <Text size="xs" style={{ color: theme.colors.textTertiary }}>
                            {insight.description}
                          </Text>
                        </Stack>
                      </Card>
                    ))}
                  </Stack>
                </Stack>
              </Card>
            </Grid.Col>
          </Grid>
        </Stack>
      </Container>
    </Box>
  );
}