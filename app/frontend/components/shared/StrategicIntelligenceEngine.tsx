'use client';

import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Card, 
  Badge, 
  Title, 
  Text, 
  Progress, 
  Group, 
  Stack, 
  Button, 
  Alert, 
  ActionIcon, 
  Box
} from '@mantine/core';
import { 
  IconBrain, 
  IconTarget, 
  IconChartLine, 
  IconBulb, 
  IconChecklist, 
  IconClock, 
  IconTrendingUp, 
  IconArrowLeft, 
  IconHome 
} from '@tabler/icons-react';
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
  const [activeWorkflow, setActiveWorkflow] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<StrategicAnalysis | null>(null);
  const [strategicQuery, setStrategicQuery] = useState('');

  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([
    {
      id: 'context-integration',
      name: 'AI Context Integration',
      status: 'pending',
      progress: 0,
      timeEstimate: '30 seconds',
      output: null
    },
    {
      id: 'multi-framework',
      name: 'Multi-Framework Analysis',
      status: 'pending', 
      progress: 0,
      timeEstimate: '2 minutes',
      output: null
    },
    {
      id: 'confidence-scoring',
      name: 'Confidence-Scored Recommendations',
      status: 'pending',
      progress: 0,
      timeEstimate: '1 minute',
      output: null
    },
    {
      id: 'predictive-modeling',
      name: 'Predictive Outcome Modeling',
      status: 'pending',
      progress: 0,
      timeEstimate: '2 minutes',
      output: null
    },
    {
      id: 'action-plan',
      name: 'Executable Action Plan Generation',
      status: 'pending',
      progress: 0,
      timeEstimate: '1.5 minutes',
      output: null
    },
    {
      id: 'integration',
      name: 'Roadmap Integration',
      status: 'pending',
      progress: 0,
      timeEstimate: '1 minute',
      output: null
    },
    {
      id: 'audit-trail',
      name: 'Strategic Decision Audit Trail',
      status: 'pending',
      progress: 0,
      timeEstimate: '30 seconds',
      output: null
    }
  ]);

  const startStrategicAnalysis = async (query: string) => {
    setActiveWorkflow('strategic-intelligence');
    setStrategicQuery(query);
    setCurrentStep(0);
    
    // Reset workflow steps
    setWorkflowSteps(steps => steps.map(step => ({
      ...step,
      status: 'pending',
      progress: 0,
      output: null
    })));

    // Simulate the strategic intelligence workflow
    for (let i = 0; i < workflowSteps.length; i++) {
      await processWorkflowStep(i);
    }
  };

  const processWorkflowStep = async (stepIndex: number) => {
    return new Promise<void>((resolve) => {
      setCurrentStep(stepIndex);
      
      // Set step to processing
      setWorkflowSteps(steps => steps.map((step, index) => 
        index === stepIndex 
          ? { ...step, status: 'processing', progress: 0 }
          : step
      ));

      // Simulate progress
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 15 + 5;
        if (progress >= 100) {
          progress = 100;
          clearInterval(progressInterval);
          
          // Complete the step with mock output
          setWorkflowSteps(steps => steps.map((step, index) => 
            index === stepIndex 
              ? { 
                  ...step, 
                  status: 'completed', 
                  progress: 100,
                  output: getMockStepOutput(step.id)
                }
              : step
          ));
          
          // If final step, generate complete analysis
          if (stepIndex === workflowSteps.length - 1) {
            generateStrategicAnalysis();
          }
          
          resolve();
        } else {
          setWorkflowSteps(steps => steps.map((step, index) => 
            index === stepIndex 
              ? { ...step, progress }
              : step
          ));
        }
      }, 200);
    });
  };

  const getMockStepOutput = (stepId: string) => {
    const outputs = {
      'context-integration': {
        company_context: 'PM33 - Strategic AI Co-Pilot',
        market_conditions: 'Growing PM tools market, AI adoption accelerating',
        competitive_landscape: '15+ competitors, fragmented market',
        historical_decisions: '3 strategic decisions analyzed'
      },
      'multi-framework': {
        ice_score: 8.2,
        rice_score: 156,
        frameworks_applied: ['ICE', 'RICE', 'Blue Ocean Strategy', 'Competitive Response Matrix'],
        strategic_fit_score: 89
      },
      'confidence-scoring': {
        recommendation_confidence: 87,
        reasoning_chain: 'Based on market analysis, competitive positioning, and resource constraints',
        risk_factors: ['Technical complexity', 'Market timing', 'Resource availability']
      },
      'predictive-modeling': {
        success_probability: 78,
        timeline_estimate: '12-16 weeks',
        resource_estimate: '$120K-180K',
        risk_score: 'Medium-High'
      },
      'action-plan': {
        tasks_generated: 12,
        strategic_alignment: 94,
        resource_allocation: 'Optimized across 3 teams',
        dependencies_mapped: 8
      },
      'integration': {
        roadmap_integration: 'Q2 2025 strategic initiative',
        task_sync_status: 'Ready for Jira integration',
        stakeholder_notifications: 'Prepared for 4 stakeholders'
      },
      'audit-trail': {
        decision_id: `strategic_${Date.now()}`,
        frameworks_used: 4,
        confidence_level: 'High',
        reviewable: true
      }
    };
    
    return outputs[stepId as keyof typeof outputs] || {};
  };

  const generateStrategicAnalysis = () => {
    const mockAnalysis: StrategicAnalysis = {
      situationAssessment: "Current competitive positioning shows PM33 has strong differentiation in AI-powered strategic analysis, but faces pressure from new feature launches by competitors. Market opportunity exists for proactive competitive response.",
      recommendation: "Implement accelerated differentiation strategy focusing on unique AI strategic intelligence capabilities that competitors cannot easily replicate. Position PM33 as the 'Strategic Intelligence Platform' rather than traditional PM tool.",
      successMetrics: [
        "Strategic decision speed: <10 minutes (vs 8-hour industry average)",
        "Strategic confidence score: >85% for key decisions", 
        "Competitive response time: <48 hours",
        "Strategic outcome accuracy: >78% prediction rate",
        "PM strategic capability improvement: 10x productivity gain"
      ],
      keyRisks: [
        "Technical complexity of advanced AI models",
        "Market education required for strategic intelligence positioning",
        "Resource allocation across multiple strategic initiatives",
        "Competitive counter-positioning risk"
      ],
      resourceRequirements: "3 engineers (AI/ML focus), 1 product strategist, 1 competitive intelligence analyst. Estimated budget: $120K-180K over 12-16 weeks.",
      timeline: "Phase 1 (4 weeks): Strategic positioning & messaging. Phase 2 (8 weeks): Advanced AI capabilities. Phase 3 (4 weeks): Market launch & competitive response.",
      confidenceScore: 87,
      frameworksApplied: ["ICE Framework (Score: 8.2)", "RICE Framework (Score: 156)", "Blue Ocean Strategy", "Competitive Response Matrix", "Strategic Positioning Canvas"]
    };

    setAnalysisResult(mockAnalysis);
  };

  const predefinedQueries = [
    "Our competitor launched a similar feature. How should we reprioritize our roadmap and update team sprint goals?",
    "We have budget for 3 engineers OR $150K marketing spend. Which drives faster revenue growth?",
    "Our user retention dropped to 65%. What strategic initiatives should automatically move to top of our backlog?",
    "Engineering velocity is 20% below target. How should we reallocate resources and adjust roadmap timelines?",
    "Sales wants 5 new features but we can only deliver 2 this quarter. How do we prioritize with automated scoring?"
  ];

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

      {!activeWorkflow ? (
        /* Strategic Query Input */
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
                onClick={() => startStrategicAnalysis(strategicQuery)}
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

            <Stack gap={16}>
              <Text size="sm" fw={600}>💡 Strategic automation scenarios:</Text>
              <Stack gap={8}>
                {predefinedQueries.map((query, index) => (
                  <Button
                    key={index}
                    variant="light"
                    size="sm"
                    onClick={() => setStrategicQuery(query)}
                    style={{ height: 'auto', padding: '12px 16px', textAlign: 'left' }}
                  >
                    <Text size="sm" style={{ whiteSpace: 'normal' }}>
                      {query}
                    </Text>
                  </Button>
                ))}
              </Stack>
            </Stack>
          </Stack>
        </Card>
      ) : (
        /* Active Strategic Analysis Workflow */
        <Grid gutter={32}>
          <Grid.Col span={{ base: 12, md: 4 }}>
            {/* Workflow Progress */}
            <Card shadow="md" padding={24} radius={16} style={{ position: 'sticky', top: '20px' }}>
              <Title order={3} size="h3" mb={24}>🧠 Analysis Progress</Title>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {workflowSteps.map((step, index) => (
                  <Card key={step.id} padding={16} withBorder>
                    <Group justify="space-between" align="center">
                      <Group gap={8}>
                        <Badge 
                          color={
                            step.status === 'completed' ? 'green' :
                            step.status === 'processing' ? 'blue' :
                            step.status === 'error' ? 'red' : 'gray'
                          }
                          variant={step.status === 'processing' ? 'filled' : 'light'}
                        >
                          {step.status === 'completed' ? '✓' : step.status === 'processing' ? '⏳' : '⏸'}
                        </Badge>
                        <Stack gap={0}>
                          <Text size="sm" fw={600}>{step.name}</Text>
                          <Text size="xs" c="dimmed">Est: {step.timeEstimate}</Text>
                        </Stack>
                      </Group>
                    </Group>
                    {step.status === 'processing' && (
                      <Stack gap={8} mt={8}>
                        <Progress value={step.progress} size="sm" />
                        <Text size="xs" c="dimmed">
                          {Math.round(step.progress)}% complete
                        </Text>
                      </Stack>
                    )}
                  </Card>
                ))}
              </div>

              {analysisResult && (
                <Alert color="green" title="Analysis Complete" mt={24}>
                  <Stack gap={16}>
                    <Text size="sm">
                      Strategic analysis completed with {analysisResult.confidenceScore}% confidence score
                    </Text>
                    <Group>
                      <Button
                        component={Link}
                        href="/command-center"
                        variant="light"
                        color="green"
                        leftSection={<IconTarget size={16} />}
                        size="sm"
                      >
                        Execute in Command Center
                      </Button>
                      <Button
                        variant="light"
                        color="blue"
                        size="sm"
                        onClick={() => {
                          setActiveWorkflow(null);
                          setAnalysisResult(null);
                          setStrategicQuery('');
                        }}
                      >
                        Try Another Analysis
                      </Button>
                    </Group>
                  </Stack>
                </Alert>
              )}
            </Card>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 8 }}>
            {/* Real-time Analysis Results */}
            <Card shadow="md" padding={24} radius={16}>
              <Title order={3} size="h3" mb={24}>📋 Strategic Analysis: {strategicQuery}</Title>
              
              {analysisResult ? (
                <Stack gap={32}>
                  <Card padding={24} withBorder>
                    <Title order={4} size="h4" mb={16}>📊 Strategic Overview</Title>
                    <Stack gap={24}>
                      <Stack gap={8}>
                        <Text fw={600} size="sm">📊 Situation Assessment</Text>
                        <Text size="sm" c="dimmed">{analysisResult.situationAssessment}</Text>
                      </Stack>
                      
                      <Group>
                        <Badge size="lg" color="blue" variant="light">
                          Confidence Score: {analysisResult.confidenceScore}%
                        </Badge>
                        <Badge size="lg" color="green" variant="light">
                          {analysisResult.frameworksApplied.length} Frameworks Applied
                        </Badge>
                      </Group>

                      <Stack gap={8}>
                        <Text fw={600} size="sm">🛠️ Frameworks Applied</Text>
                        <Group gap={8}>
                          {analysisResult.frameworksApplied.map((framework, index) => (
                            <Badge key={index} variant="outline" size="sm">
                              {framework}
                            </Badge>
                          ))}
                        </Group>
                      </Stack>
                    </Stack>
                  </Card>
                  
                  <Card padding={24} withBorder>
                    <Title order={4} size="h4" mb={16}>💡 Recommendations</Title>
                    <Stack gap={24}>
                      <Stack gap={8}>
                        <Text fw={600} size="sm">💡 Strategic Recommendation</Text>
                        <Text size="sm">{analysisResult.recommendation}</Text>
                      </Stack>
                      
                      <Stack gap={8}>
                        <Text fw={600} size="sm">⚠️ Key Risks & Mitigations</Text>
                        <Stack gap={8}>
                          {analysisResult.keyRisks.map((risk, index) => (
                            <Alert key={index} color="yellow" variant="light" size="sm">
                              {risk}
                            </Alert>
                          ))}
                        </Stack>
                      </Stack>

                      <Stack gap={8}>
                        <Text fw={600} size="sm">📅 Timeline</Text>
                        <Text size="sm" c="dimmed">{analysisResult.timeline}</Text>
                      </Stack>
                    </Stack>
                  </Card>
                  
                  <Card padding={24} withBorder>
                    <Title order={4} size="h4" mb={16}>🎯 Success Metrics</Title>
                    <Stack gap={16}>
                      <Text fw={600} size="sm">🎯 Success Metrics</Text>
                      <Stack gap={12}>
                        {analysisResult.successMetrics.map((metric, index) => (
                          <Card key={index} padding={16} withBorder>
                            <Text size="sm">{metric}</Text>
                          </Card>
                        ))}
                      </Stack>
                    </Stack>
                  </Card>
                </Stack>
              ) : (
                <Stack gap={16}>
                  <Text c="dimmed">Strategic analysis in progress...</Text>
                  {workflowSteps.map((step, index) => (
                    step.status === 'completed' && step.output ? (
                      <Card key={step.id} padding={16} withBorder>
                        <Text fw={600} size="sm" mb={8}>✓ {step.name}</Text>
                        <Text size="xs" c="dimmed">
                          {JSON.stringify(step.output, null, 2)}
                        </Text>
                      </Card>
                    ) : null
                  ))}
                </Stack>
              )}
            </Card>
          </Grid.Col>
        </Grid>
      )}
    </Container>
  );
};

export default StrategicIntelligenceEngine;