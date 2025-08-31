'use client';

import React, { useState } from 'react';
import { Container, Group, Text, Button, ActionIcon } from '@mantine/core';
import { IconSun, IconMoon, IconBolt } from '@tabler/icons-react';
import Link from 'next/link';

export default function Navigation() {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.body.setAttribute('data-theme', newTheme);
  };

  return (
    <nav
      className="pm33-nav-glass"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        padding: 'var(--pm33-spacing-md) 0',
      }}
    >
      <Container size="xl">
        <Group justify="space-between">
          {/* Logo */}
          <Group gap={12}>
            <IconBolt size={24} color="var(--marketing-primary)" />
            <Text fw={700} size="xl" className="marketing-text-primary">
              PM33
            </Text>
          </Group>

          {/* Navigation Links */}
          <Group gap={24} visibleFrom="md">
            <Link href="/pricing" style={{ textDecoration: 'none' }}>
              <Text className="marketing-text-primary" style={{ cursor: 'pointer' }}>
                Pricing
              </Text>
            </Link>
            <Link href="/features" style={{ textDecoration: 'none' }}>
              <Text className="marketing-text-primary" style={{ cursor: 'pointer' }}>
                Features
              </Text>
            </Link>
            <Link href="/about" style={{ textDecoration: 'none' }}>
              <Text className="marketing-text-primary" style={{ cursor: 'pointer' }}>
                About
              </Text>
            </Link>
          </Group>

          {/* CTA + Theme Toggle */}
          <Group gap={12}>
            <ActionIcon
              variant="subtle"
              size="lg"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <IconMoon size={20} />
              ) : (
                <IconSun size={20} />
              )}
            </ActionIcon>
            <Button
              component={Link}
              href="/trial"
              size="md"
              style={{
                background: 'var(--marketing-gradient-primary)',
                color: 'white',
              }}
            >
              Start Free Trial
            </Button>
          </Group>
        </Group>
      </Container>
    </nav>
  );
}