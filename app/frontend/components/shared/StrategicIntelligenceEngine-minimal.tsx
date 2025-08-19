'use client';

import React, { useState } from 'react';
import { Container, Card, Badge, Title, Text, Group, Stack, Button, ActionIcon, Box } from '@mantine/core';
import { IconBrain, IconTarget, IconChartLine, IconBulb, IconChecklist, IconClock, IconTrendingUp, IconArrowLeft, IconHome } from '@tabler/icons-react';
import Link from 'next/link';

// Strategic Intelligence Workflow Step
interface WorkflowStep {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  timeEstimate: string;
  output?: any;
}

// Strategic Analysis Result
interface StrategicAnalysis {
  situationAssessment: string;
  recommendation: string;
  successMetrics: string[];
  keyRisks: string[];
  resourceRequirements: string;
  timeline: string;
  confidenceScore: number;
  frameworksApplied: string[];
}

const StrategicIntelligenceEngine: React.FC = () => {
  const [strategicQuery, setStrategicQuery] = useState('');
  
  return (
    <Container size={1200} px={24} py={48}>
      {/* Header with PM33 Logo */}
      <Box mb={48}>
        <Group justify="space-between" align="center">
          <Group>
            <ActionIcon
              component={Link}
              href="/"
              size="lg"
              variant="light"
              color="blue"
              aria-label="Back to homepage"
            >
              <IconHome size={18} />
            </ActionIcon>
            <img src="/pm33-logo.png" alt="PM33 Strategic Intelligence Platform" style={{ height: '36px' }} />
            <Stack gap={4}>
              <Title order={1} size="h1" c="dark">
                Strategic Intelligence Engine
              </Title>
              <Text size="lg" c="dimmed">
                Automated bridges from strategy to execution - eliminate manual prioritization overhead
              </Text>
            </Stack>
          </Group>
          <Group gap={16}>
            <Badge size="lg" variant="gradient" gradient={{ from: 'blue', to: 'cyan' }}>
              Workflow 1 of 5
            </Badge>
            <Button
              component={Link}
              href="/command-center"
              variant="outline"
              leftSection={<IconTarget size={16} />}
            >
              Try Command Center
            </Button>
          </Group>
        </Group>
      </Box>

      {/* Strategic Query Input */}
      <Card shadow="lg" padding={32} radius={16}>
        <Stack gap={32}>
          <Stack gap={16}>
            <Title order={2} size="h2">🎯 Strategic Question Input</Title>
            <Text c="dimmed" size="lg">
              Transform strategic decisions into executable workflows with automated priority alignment and resource optimization
            </Text>
          </Stack>

          <textarea
            value={strategicQuery}
            onChange={(e) => setStrategicQuery(e.target.value)}
            placeholder="Enter your strategic question..."
            rows={4}
            aria-label="Strategic question input"
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #dee2e6',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />

          <Group justify="space-between" align="center">
            <Button
              size="lg"
              leftSection={<IconBrain size={20} />}
              disabled={!strategicQuery.trim()}
              variant="gradient"
              gradient={{ from: 'blue', to: 'cyan' }}
            >
              Generate Strategic Intelligence
            </Button>
            <Text size="sm" c="dimmed">
              ⚡ Automated analysis with instant priority scoring
            </Text>
          </Group>
        </Stack>
      </Card>
    </Container>
  );
};

export default StrategicIntelligenceEngine;