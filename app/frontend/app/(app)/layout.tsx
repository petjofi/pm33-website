import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../globals.css";
import MantineWrapper from "../../components/shared/MantineProvider";
import { DesignSystemProvider } from "../../components/app/DesignSystemProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "PM33 Strategic Intelligence Platform",
  description: "PMO-level strategic intelligence at your fingertips. Supercharge your product management workflow with AI-powered insights.",
};

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <style>{`
          /* App-Specific Color Tokens - REQUIRED USE ONLY */
          :root {
            /* Primary App Colors (Refined) */
            --app-primary: #1E3A8A;           /* Strategic blue - navigation, key actions */
            --app-primary-hover: #1D4ED8;     /* Interactive states */
            --app-primary-light: #DBEAFE;     /* Subtle backgrounds */
            --app-primary-ghost: #F0F7FF;     /* Minimal backgrounds */
            
            /* Success States (Understated) */
            --app-success: #047857;           /* Success indicators */
            --app-success-light: #D1FAE5;     /* Success backgrounds */
            --app-success-ghost: #F0FDF4;     /* Subtle success */
            
            /* Warning States (Professional) */
            --app-warning: #B45309;           /* Attention indicators */
            --app-warning-light: #FED7AA;     /* Warning backgrounds */
            --app-warning-ghost: #FFFBEB;     /* Subtle warnings */
            
            /* Error States (Controlled) */
            --app-error: #DC2626;             /* Error indicators */
            --app-error-light: #FECACA;       /* Error backgrounds */
            --app-error-ghost: #FEF2F2;       /* Subtle errors */
            
            /* App Text Hierarchy */
            --app-text-primary: #0F172A;      /* Headings, key content */
            --app-text-secondary: #475569;    /* Body text */
            --app-text-tertiary: #64748B;     /* Supporting text */
            --app-text-muted: #94A3B8;        /* Captions, metadata */
            
            /* App Backgrounds (Clean) */
            --app-bg-primary: #FFFFFF;        /* Main content areas */
            --app-bg-secondary: #F8FAFC;      /* Sidebar, secondary panels */
            --app-bg-tertiary: #F1F5F9;       /* Input backgrounds, cards */
            --app-bg-accent: #E2E8F0;         /* Borders, dividers */
          }
        `}</style>
      </head>
      <body
        className={`${inter.variable} antialiased app-context`}
        style={{
          fontFamily: 'var(--font-inter)',
          color: 'var(--app-text-primary)',
          backgroundColor: 'var(--app-bg-secondary)'
        }}
      >
        <MantineWrapper>
          <DesignSystemProvider context="app">
            {children}
          </DesignSystemProvider>
        </MantineWrapper>
      </body>
    </html>
  );
}