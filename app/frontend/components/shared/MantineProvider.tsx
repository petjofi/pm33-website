'use client';

import { MantineProvider, createTheme } from '@mantine/core';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';
import '@mantine/dropzone/styles.css';
import '@mantine/spotlight/styles.css';

const theme = createTheme({
  /** PM33 Strategic Intelligence Theme */
  primaryColor: 'blue',
  colors: {
    // Strategic gradient colors
    strategic: [
      '#f0f6ff',
      '#d9ecff',
      '#a6d5ff',
      '#73beff',
      '#4da7ff',
      '#2693ff',
      '#1a84ff',
      '#0070f3',
      '#005bd8',
      '#0046b3'
    ]
  },
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  headings: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  },
  spacing: {
    xs: '8px',
    sm: '12px',
    md: '16px',
    lg: '20px',
    xl: '24px',
  },
  radius: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '20px',
  },
  shadows: {
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  }
});

interface MantineWrapperProps {
  children: React.ReactNode;
}

export default function MantineWrapper({ children }: MantineWrapperProps) {
  return (
    <MantineProvider theme={theme} defaultColorScheme="light">
      {children}
    </MantineProvider>
  );
}