'use client';

import React from 'react';
import { Container, Group, Text, Stack } from '@mantine/core';
import { IconBolt } from '@tabler/icons-react';
import Link from 'next/link';

export default function Footer() {
  return (
    <footer
      style={{
        background: 'var(--marketing-bg-secondary)',
        padding: '60px 0 40px 0',
        borderTop: '1px solid var(--marketing-glass-border)',
      }}
    >
      <Container size="xl">
        <Stack gap={40}>
          {/* Main Footer Content */}
          <Group justify="space-between" align="start">
            {/* Logo & Description */}
            <Stack gap={16} style={{ maxWidth: '300px' }}>
              <Group gap={12}>
                <IconBolt size={24} color="var(--marketing-primary)" />
                <Text fw={700} size="xl" className="marketing-text-primary">
                  PM33
                </Text>
              </Group>
              <Text size="sm" className="marketing-text-secondary">
                Transform your PM tools into AI-powered strategic engines. 
                Don't replace your workflow—make it 10x smarter.
              </Text>
            </Stack>

            {/* Quick Links */}
            <Group gap={60} align="start">
              <Stack gap={12}>
                <Text fw={600} className="marketing-text-primary">Product</Text>
                <Link href="/features" style={{ textDecoration: 'none' }}>
                  <Text size="sm" className="marketing-text-secondary">Features</Text>
                </Link>
                <Link href="/pricing" style={{ textDecoration: 'none' }}>
                  <Text size="sm" className="marketing-text-secondary">Pricing</Text>
                </Link>
                <Link href="/demo" style={{ textDecoration: 'none' }}>
                  <Text size="sm" className="marketing-text-secondary">Live Demo</Text>
                </Link>
              </Stack>
              
              <Stack gap={12}>
                <Text fw={600} className="marketing-text-primary">Company</Text>
                <Link href="/about" style={{ textDecoration: 'none' }}>
                  <Text size="sm" className="marketing-text-secondary">About</Text>
                </Link>
                <Link href="/contact" style={{ textDecoration: 'none' }}>
                  <Text size="sm" className="marketing-text-secondary">Contact</Text>
                </Link>
                <Link href="/blog" style={{ textDecoration: 'none' }}>
                  <Text size="sm" className="marketing-text-secondary">Blog</Text>
                </Link>
              </Stack>
            </Group>
          </Group>

          {/* Copyright */}
          <Group justify="center" pt={20} style={{ borderTop: '1px solid var(--marketing-glass-border)' }}>
            <Text size="sm" className="marketing-text-secondary">
              © 2025 PM33. All rights reserved.
            </Text>
          </Group>
        </Stack>
      </Container>
    </footer>
  );
}