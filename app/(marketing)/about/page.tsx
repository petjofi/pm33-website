'use client';

import React from 'react';
import { Container, Title, Text, Button, Group, Stack, Badge, SimpleGrid, Box, Grid } from '@mantine/core';
import { IconTarget, IconUsers, IconBrain, IconTrendingUp, IconHeart, IconBulb, IconClock, IconAward, IconBuilding, IconCheck } from '@tabler/icons-react';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <Box style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      {/* Hero Section with Rich Metrics */}
      <Box py={80} style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#ffffff' }}>
        <Container size="xl">
          <Grid gutter={48}>
            <Grid.Col span={{ base: 12, lg: 7 }}>
              <Stack gap={24}>
                <Badge 
                  size="lg" 
                  variant="light" 
                  style={{ 
                    background: 'rgba(255, 255, 255, 0.1)', 
                    color: '#ffffff', 
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    backdropFilter: 'blur(20px)',
                    WebkitBackdropFilter: 'blur(20px)'
                  }}
                >
                  Our Story & Mission
                </Badge>
                
                <Title order={1} size={56} ta="left" lh={1.2} style={{ color: '#ffffff' }}>
                  Built by PMs,
                  <br />
                  <span className="pm33-text-brand">For PMs</span>
                </Title>
                
                <Text size="xl" style={{ color: 'rgba(255, 255, 255, 0.9)' }} maw={600}>
                  We're product managers who got tired of spending 80% of our time on busywork instead of strategy. 
                  So we built the AI assistant we always wanted - one that enhances your existing tools instead of replacing them.
                </Text>
              </Stack>
            </Grid.Col>
            
            <Grid.Col span={{ base: 12, lg: 5 }}>
              <SimpleGrid cols={{ base: 2, sm: 2 }} spacing={16}>
                {[
                  { icon: IconUsers, stat: "2,500+", label: "PMs using PM33" },
                  { icon: IconClock, stat: "72hrs", label: "Saved per PM monthly" },
                  { icon: IconTarget, stat: "40%", label: "More features shipped" },
                  { icon: IconAward, stat: "89%", label: "Team satisfaction" }
                ].map((metric, index) => (
                  <div key={index} className="glass-card" style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    padding: 'var(--space-md)',
                    textAlign: 'center',
                    borderRadius: 'var(--radius-lg)',
                    backdropFilter: 'blur(20px)',
                    WebkitBackdropFilter: 'blur(20px)',
                    boxShadow: '0 8px 32px rgba(31, 38, 135, 0.15)',
                    transition: 'transform var(--duration-normal) var(--ease-smooth)',
                    height: '120px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Stack align="center" gap={8}>
                      <metric.icon size={20} color="white" />
                      <Text size={24} fw={700} style={{ color: '#ffffff' }}>{metric.stat}</Text>
                      <Text size="xs" style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{metric.label}</Text>
                    </Stack>
                  </div>
                ))}
              </SimpleGrid>
            </Grid.Col>
          </Grid>
        </Container>
      </Box>

      {/* Mission Section */}
      <Box py={80} style={{ backgroundColor: 'var(--bg-primary)' }}>
        <Container size="xl">
          <Stack align="center" gap={48} mb={64}>
            <Title order={2} size={42} ta="center" className="text-gradient">
              Our Mission
            </Title>
            <Text size="xl" ta="center" maw={800} style={{ color: 'var(--text-secondary)' }}>
              To free product managers from busywork so they can focus on what matters most: strategic thinking and customer impact.
            </Text>
          </Stack>

          <SimpleGrid cols={{ base: 1, lg: 3 }} spacing={32}>
            {[
              {
                icon: IconHeart,
                title: "PM-First Approach",
                description: "Every feature is designed by product managers who understand the daily challenges of the role. We don't build for engineers or marketers - we build for PMs."
              },
              {
                icon: IconTarget,
                title: "Enhancement Philosophy", 
                description: "We believe in making your existing tools smarter, not forcing you to abandon workflows that already work. Integration over replacement, always."
              },
              {
                icon: IconBulb,
                title: "Community-Driven Innovation",
                description: "Our roadmap is shaped by the PM community. Every feature request, every use case, every workflow optimization comes from real PMs doing real work."
              }
            ].map((value, index) => (
              <div key={index} className="glass-card-premium" style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                padding: 'var(--space-xl)',
                textAlign: 'center',
                borderRadius: 'var(--radius-lg)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                boxShadow: '0 8px 32px rgba(31, 38, 135, 0.15)',
                transition: 'transform var(--duration-normal) var(--ease-smooth)'
              }}>
                <Stack align="center" gap={20}>
                  <div style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    width: '64px',
                    height: '64px',
                    borderRadius: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 8px 32px rgba(30, 58, 138, 0.25)'
                  }}>
                    <value.icon size={32} color="#ffffff" />
                  </div>
                  <Title order={3} size={24} style={{ color: 'var(--text-primary)' }}>{value.title}</Title>
                  <Text style={{ color: 'var(--text-secondary)' }} lh={1.6}>{value.description}</Text>
                </Stack>
              </div>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* Founder Story Section */}
      <Box py={80} style={{ backgroundColor: 'var(--bg-secondary)' }}>
        <Container size="xl">
          <Grid gutter={48}>
            <Grid.Col span={{ base: 12, lg: 6 }}>
              <Stack gap={32}>
                <Title order={2} size={32} className="text-gradient">
                  The Story Behind PM33
                </Title>
                
                <Stack gap={24}>
                  <Text size="lg" style={{ color: 'var(--text-primary)' }}>
                    <strong>The frustration was real.</strong> As senior PMs at fast-growing startups, we were spending 
                    4+ hours daily on documentation, status updates, and data synthesis instead of customer research 
                    and strategic planning.
                  </Text>
                  
                  <Text size="lg" style={{ color: 'var(--text-primary)' }}>
                    We tried every PM tool on the market. Each promised to solve our problems, but they all had the 
                    same fatal flaw: <strong>they wanted us to abandon our existing workflows</strong> and migrate 
                    everything to their platform.
                  </Text>
                  
                  <Text size="lg" style={{ color: 'var(--text-primary)' }}>
                    That's when we realized the solution wasn't another PM tool - it was an <strong>AI layer that 
                    makes existing tools smarter</strong>. Why force teams to learn new systems when you can enhance 
                    the ones they already know?
                  </Text>
                  
                  <Text size="lg" style={{ color: 'var(--text-primary)' }}>
                    Six months later, PM33 was born. Today, over 2,500 product managers use it to reclaim 70+ hours 
                    monthly for strategic work.
                  </Text>
                </Stack>
                
                <div className="glass-card" style={{
                  background: 'rgba(16, 185, 129, 0.05)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  padding: 'var(--space-xl)',
                  borderRadius: 'var(--radius-lg)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  boxShadow: '0 8px 32px rgba(31, 38, 135, 0.15)'
                }}>
                  <Text size="lg" fw={600} style={{ color: '#4A9B9E' }} mb={12}>"Our North Star"</Text>
                  <Text size="lg" fs="italic" style={{ color: 'var(--text-primary)' }} mb={16}>
                    "Every hour we save a PM from busywork is an hour they can spend understanding their customers better."
                  </Text>
                  <Text size="md" fw={500} style={{ color: 'var(--text-secondary)' }}>— PM33 Founding Team</Text>
                </div>
              </Stack>
            </Grid.Col>
            
            <Grid.Col span={{ base: 12, lg: 6 }}>
              <Stack gap={24}>
                <div className="glass-card" style={{
                  background: 'rgba(239, 68, 68, 0.05)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  padding: 'var(--space-xl)',
                  borderRadius: 'var(--radius-lg)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  boxShadow: '0 8px 32px rgba(31, 38, 135, 0.15)'
                }}>
                  <Title order={3} size={20} mb={16} style={{ color: 'var(--text-primary)' }}>Before PM33</Title>
                  <Stack gap={12}>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-secondary)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>4+ hours daily on documentation</Text>
                    </Group>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-secondary)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>Scattered data across 8+ tools</Text>
                    </Group>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-secondary)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>Manual synthesis and reporting</Text>
                    </Group>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-secondary)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>Strategic time: 20% of day</Text>
                    </Group>
                  </Stack>
                </div>
                
                <div className="glass-card" style={{
                  background: 'rgba(16, 185, 129, 0.05)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  padding: 'var(--space-xl)',
                  borderRadius: 'var(--radius-lg)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  boxShadow: '0 8px 32px rgba(31, 38, 135, 0.15)'
                }}>
                  <Title order={3} size={20} mb={16} style={{ color: 'var(--text-primary)' }}>After PM33</Title>
                  <Stack gap={12}>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-success)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>15 minutes for comprehensive PRDs</Text>
                    </Group>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-success)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>Unified intelligence across all tools</Text>
                    </Group>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-success)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>AI-powered insights and recommendations</Text>
                    </Group>
                    <Group gap={12}>
                      <Box w={12} h={12} style={{ background: 'var(--pm33-success)', borderRadius: '50%' }}></Box>
                      <Text style={{ color: 'var(--text-secondary)' }}>Strategic time: 70% of day</Text>
                    </Group>
                  </Stack>
                </div>
              </Stack>
            </Grid.Col>
          </Grid>
        </Container>
      </Box>

      {/* Team Values Section */}
      <Box py={80} style={{ backgroundColor: 'var(--bg-primary)' }}>
        <Container size="xl">
          <Stack align="center" gap={48} mb={64}>
            <Title order={2} size={42} ta="center" className="text-gradient">
              How We Work
            </Title>
            <Text size="xl" ta="center" maw={800} style={{ color: 'var(--text-secondary)' }}>
              Our values shape every product decision and customer interaction.
            </Text>
          </Stack>

          <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing={24}>
            {[
              { 
                title: "PM Empathy",
                description: "We're all practicing PMs. Every decision comes from real experience managing products and teams."
              },
              {
                title: "No BS Approach", 
                description: "Clear communication, honest pricing, no hidden fees. We say what we mean and deliver what we promise."
              },
              {
                title: "Community First",
                description: "The PM community shapes our roadmap. We build what PMs actually need, not what we think they should want."
              },
              {
                title: "Continuous Learning",
                description: "Product management evolves fast. We stay current with the latest frameworks, tools, and methodologies."
              }
            ].map((value, index) => (
              <div key={index} className="glass-card" style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                padding: 'var(--space-lg)',
                textAlign: 'center',
                borderRadius: 'var(--radius-lg)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                boxShadow: '0 8px 32px rgba(31, 38, 135, 0.15)',
                transition: 'transform var(--duration-normal) var(--ease-smooth)'
              }}>
                <Title order={4} size={18} style={{ color: 'var(--text-primary)' }} mb={12}>{value.title}</Title>
                <Text size="sm" style={{ color: 'var(--text-secondary)' }} lh={1.5}>{value.description}</Text>
              </div>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box py={80} style={{ 
        background: 'linear-gradient(135deg, var(--pm33-navy) 0%, var(--pm33-teal) 100%)', 
        color: '#ffffff'
      }}>
        <Container size="xl">
          <Stack align="center" gap={32} ta="center">
            <Title order={2} size={48} style={{ color: '#ffffff' }}>
              Join the PM Community Revolution
            </Title>
            <Text size="xl" style={{ color: 'rgba(255, 255, 255, 0.9)' }} maw={600}>
              Be part of the movement that's freeing product managers from busywork. 
              Start your transformation today.
            </Text>
            
            <Group gap={24} justify="center">
              <Button 
                component={Link} 
                href="/trial" 
                size="lg" 
                variant="gradient"
                gradient={{ from: 'indigo', to: 'purple' }}
                className="pm33-button-primary"
              >
                Start Your Free Trial
              </Button>
              <Button 
                component={Link} 
                href="/contact" 
                size="lg" 
                className="pm33-button-secondary"
              >
                Get in Touch
              </Button>
            </Group>
            
            <Text style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
              Join 2,500+ product managers who've already made the switch
            </Text>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
}