'use client';

import React, { useState, useEffect } from 'react';
import { Container, Grid, Card, Badge, Title, Text, Progress, Group, Stack, Button, Stepper, Alert, Tabs, ActionIcon, Box } from '@mantine/core';
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
    <Container size="xl" px="md" py="xl">
      {/* Header with PM33 Logo */}
      <Stack mb="xl">
        <Group justify="space-between">
          <Group>
            <ActionIcon
              component={Link}
              href="/"
              size="xl"
              variant="light"
              color="blue"
              aria-label="Back to homepage"
            >
              <IconHome size={20} />
            </ActionIcon>
            <img src="/pm33-logo.png" alt="PM33 Strategic Intelligence Platform" style={{ height: '40px' }} />
            <div>
              <Title order={1} size="h1" c="dark">
                Strategic Intelligence Engine
              </Title>
              <Text size="lg" c="dimmed">
                Automated bridges from strategy to execution - eliminate manual prioritization overhead
              </Text>
            </div>
          </Group>
          <Group gap="md">
            <Badge size="xl" variant="gradient" gradient={{ from: 'blue', to: 'cyan' }}>
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
      </Stack>

      {!activeWorkflow ? (
        /* Strategic Query Input */
        <Card shadow="lg" padding="xl" radius="md">
          <Stack gap="lg">
            <div>
              <Title order={2} mb="md">🎯 Strategic Question Input</Title>
              <Text c="dimmed" mb="lg">
                Transform strategic decisions into executable workflows with automated priority alignment and resource optimization
              </Text>
            </div>

            <textarea
              value={strategicQuery}
              onChange={(e) => setStrategicQuery(e.target.value)}
              placeholder="Enter your strategic question..."
              rows={4}
              aria-label="Strategic question input"
              aria-describedby="strategic-query-help"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #dee2e6',
                fontSize: '14px'
              }}
            />
            <Text id="strategic-query-help" size="xs" c="dimmed">
              Ask questions about strategic decisions, prioritization, competitive responses, or resource allocation
            </Text>

            <Group justify="space-between">
              <Button
                size="lg"
                leftSection={<IconBrain size={20} />}
                onClick={() => startStrategicAnalysis(strategicQuery)}
                disabled={!strategicQuery.trim()}
                gradient={{ from: 'blue', to: 'cyan' }}
                variant="gradient"
                aria-label="Generate strategic intelligence analysis"
              >
                Generate Strategic Intelligence
              </Button>
              <Text size="sm" c="dimmed">
                ⚡ Automated analysis with instant priority scoring
              </Text>
            </Group>

            <div>
              <Text size="sm" fw={600} mb="sm">💡 Strategic automation scenarios:</Text>
              <Stack gap="xs">
                {predefinedQueries.map((query, index) => (
                  <Button
                    key={index}
                    variant="light"
                    size="sm"
                    onClick={() => setStrategicQuery(query)}
                    style={{ height: 'auto', padding: '8px 12px' }}
                    aria-label={`Use example question: ${query.substring(0, 50)}...`}
                  >
                    <Text size="xs" style={{ textAlign: 'left', whiteSpace: 'normal' }}>
                      {query}
                    </Text>
                  </Button>
                ))}
              </Stack>
            </div>
          </Stack>
        </Card>
      ) : (
        /* Active Strategic Analysis Workflow */
        <Grid>
          <Grid.Col span={{ base: 12, md: 4 }}>
            {/* Workflow Progress */}
            <Card 
              shadow="md" 
              padding="lg" 
              radius="md" 
              style={{ position: 'sticky', top: '20px' }}
              role="region"
              aria-label="Analysis progress tracker"
            >
              <Title order={3} mb="md">🧠 Analysis Progress</Title>
              
              <Stepper active={currentStep} orientation="vertical" size="sm">
                {workflowSteps.map((step, index) => (
                  <Stepper.Step
                    key={step.id}
                    label={step.name}
                    description={`Est: ${step.timeEstimate}`}
                    loading={step.status === 'processing'}
                    color={
                      step.status === 'completed' ? 'green' :
                      step.status === 'processing' ? 'blue' :
                      step.status === 'error' ? 'red' : 'gray'
                    }
                  >
                    {step.status === 'processing' && (
                      <Stack gap="xs" mt="xs">
                        <Progress value={step.progress} size="sm" />
                        <Text size="xs" c="dimmed">
                          {Math.round(step.progress)}% complete
                        </Text>
                      </Stack>
                    )}
                    {step.status === 'completed' && step.output && (
                      <Badge size="sm" color="green" mt="xs">
                        ✓ Complete
                      </Badge>
                    )}
                  </Stepper.Step>
                ))}
              </Stepper>

              {analysisResult && (
                <Alert color="green" title="Analysis Complete" mt="lg">
                  <Stack gap="sm">
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
            <Card shadow="md" padding="lg" radius="md">
              <Title order={3} mb="md">📋 Strategic Analysis: {strategicQuery}</Title>
              
              {analysisResult ? (
                <Tabs defaultValue="overview">
                  <Tabs.List>
                    <Tabs.Tab value="overview" leftSection={<IconTarget size={16} />}>
                      Strategic Overview
                    </Tabs.Tab>
                    <Tabs.Tab value="recommendations" leftSection={<IconBulb size={16} />}>
                      Recommendations
                    </Tabs.Tab>
                    <Tabs.Tab value="execution" leftSection={<IconChecklist size={16} />}>
                      Execution Plan
                    </Tabs.Tab>
                    <Tabs.Tab value="metrics" leftSection={<IconChartLine size={16} />}>
                      Success Metrics
                    </Tabs.Tab>
                  </Tabs.List>

                  <Tabs.Panel value="overview" pt="md">
                    <Stack gap="md">
                      <div>
                        <Text fw={600} mb="xs">📊 Situation Assessment</Text>
                        <Text size="sm" c="dimmed">{analysisResult.situationAssessment}</Text>
                      </div>
                      
                      <Group>
                        <Badge size="lg" color="blue" variant="light">
                          Confidence Score: {analysisResult.confidenceScore}%
                        </Badge>
                        <Badge size="lg" color="green" variant="light">
                          {analysisResult.frameworksApplied.length} Frameworks Applied
                        </Badge>
                      </Group>

                      <div>
                        <Text fw={600} mb="xs">🛠️ Frameworks Applied</Text>
                        <Stack gap="xs">
                          {analysisResult.frameworksApplied.map((framework, index) => (
                            <Badge key={index} variant="outline" size="sm">
                              {framework}
                            </Badge>
                          ))}
                        </Stack>
                      </div>
                    </Stack>
                  </Tabs.Panel>

                  <Tabs.Panel value="recommendations" pt="md">
                    <Stack gap="md">
                      <div>
                        <Text fw={600} mb="xs">💡 Strategic Recommendation</Text>
                        <Text size="sm">{analysisResult.recommendation}</Text>
                      </div>
                      
                      <div>
                        <Text fw={600} mb="xs">⚠️ Key Risks & Mitigations</Text>
                        <Stack gap="xs">
                          {analysisResult.keyRisks.map((risk, index) => (
                            <Alert key={index} color="yellow" variant="light" size="sm">
                              {risk}
                            </Alert>
                          ))}
                        </Stack>
                      </div>

                      <div>
                        <Text fw={600} mb="xs">📅 Timeline</Text>
                        <Text size="sm" c="dimmed">{analysisResult.timeline}</Text>
                      </div>
                    </Stack>
                  </Tabs.Panel>

                  <Tabs.Panel value="execution" pt="md">
                    <Stack gap="md">
                      <div>
                        <Text fw={600} mb="xs">👥 Resource Requirements</Text>
                        <Text size="sm" c="dimmed">{analysisResult.resourceRequirements}</Text>
                      </div>
                      
                      <Group justify="space-between">
                        <Button leftSection={<IconTrendingUp size={16} />} variant="light">
                          Generate Executable Tasks
                        </Button>
                        <Button leftSection={<IconChecklist size={16} />} variant="light">
                          Sync to Roadmap
                        </Button>
                      </Group>
                    </Stack>
                  </Tabs.Panel>

                  <Tabs.Panel value="metrics" pt="md">
                    <div>
                      <Text fw={600} mb="md">🎯 Success Metrics</Text>
                      <Stack gap="sm">
                        {analysisResult.successMetrics.map((metric, index) => (
                          <Card key={index} padding="sm" withBorder>
                            <Text size="sm">{metric}</Text>
                          </Card>
                        ))}
                      </Stack>
                    </div>
                  </Tabs.Panel>
                </Tabs>
              ) : (
                <Stack gap="md">
                  <Text c="dimmed">Strategic analysis in progress...</Text>
                  {workflowSteps.map((step, index) => (
                    step.status === 'completed' && step.output ? (
                      <Card key={step.id} padding="sm" withBorder>
                        <Text fw={600} size="sm" mb="xs">✓ {step.name}</Text>
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