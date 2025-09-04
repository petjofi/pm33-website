/**
 * Integration Hub Page - Main entry point for PM33 Integration workflow
 * 
 * Route: /integration-hub
 * Features: Strategy Setup → Integrations → Data Mapping → AI Enhancements → Settings
 * Backend: Integration Hub API at localhost:8002
 */

'use client';

import React, { useState } from 'react';
import { IntegrationHubDashboard } from '../../components/integration-hub/IntegrationHubDashboard';
import { StrategySetupPage } from '../../components/integration-hub/StrategySetupPage';
import { IntegrationsPage } from '../../components/integration-hub/IntegrationsPage';
import { DataMappingPage } from '../../components/integration-hub/DataMappingPage';
import { AIEnhancementsPage } from '../../components/integration-hub/AIEnhancementsPage';
import { SettingsPage } from '../../components/integration-hub/SettingsPage';
import { ArrowLeft } from 'lucide-react';

export default function IntegrationHubPage() {
  const [currentView, setCurrentView] = useState<string>('dashboard');

  const handleNavigateToStep = (step: string) => {
    setCurrentView(step);
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'strategy':
        return <StrategySetupPage onBack={handleBackToDashboard} />;

      case 'integrations':
        return <IntegrationsPage onBack={handleBackToDashboard} />;

      case 'data-mapping':
        return <DataMappingPage onBack={handleBackToDashboard} />;

      case 'ai-enhancements':
        return <AIEnhancementsPage onBack={handleBackToDashboard} />;

      case 'settings':
        return <SettingsPage onBack={handleBackToDashboard} />;

      default:
        return <IntegrationHubDashboard onNavigateToStep={handleNavigateToStep} />;
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--pm33-bg-primary)'
    }}>
      {renderCurrentView()}
    </div>
  );
}