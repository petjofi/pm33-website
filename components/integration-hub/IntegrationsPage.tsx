/**
 * Component: IntegrationsPage
 * Purpose: OAuth flows and API management for Jira, Linear, Monday, and Asana
 * Design: PM33 glass morphism with integration workflow
 * Backend: Integration Hub API - OAuth endpoints
 */

'use client';

import React, { useState, useEffect } from 'react';
import { PM33Card } from '../PM33Card';
import { ArrowLeft, Settings, CheckCircle, AlertCircle, Loader, ExternalLink, Shield, Zap } from 'lucide-react';

interface IntegrationsPageProps {
  onBack: () => void;
}

interface Integration {
  id: string;
  name: string;
  description: string;
  status: 'disconnected' | 'connecting' | 'connected' | 'error';
  logo: string;
  features: string[];
  color: string;
  lastSync?: string;
  errorMessage?: string;
}

interface ConnectionTest {
  integration: string;
  status: 'testing' | 'success' | 'failed';
  details?: {
    projects?: number;
    users?: number;
    lastActivity?: string;
  };
  error?: string;
}

export const IntegrationsPage = ({ onBack }: IntegrationsPageProps) => {
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'jira',
      name: 'Jira',
      description: 'Agile project management and issue tracking',
      status: 'disconnected',
      logo: '🔷',
      color: '#0052CC',
      features: [
        'Epic and story management',
        'Sprint tracking',
        'Custom field mapping',
        'Workflow automation'
      ]
    },
    {
      id: 'linear',
      name: 'Linear',
      description: 'Modern project management for product teams',
      status: 'disconnected',
      logo: '⚡',
      color: '#5E57D9',
      features: [
        'Issue tracking',
        'Project roadmaps',
        'Team workflows',
        'Product requirements'
      ]
    },
    {
      id: 'monday',
      name: 'Monday.com',
      description: 'Work management platform',
      status: 'disconnected',
      logo: '📅',
      color: '#FF6B35',
      features: [
        'Board management',
        'Timeline tracking',
        'Resource allocation',
        'Progress monitoring'
      ]
    },
    {
      id: 'asana',
      name: 'Asana',
      description: 'Team collaboration and project tracking',
      status: 'disconnected',
      logo: '🎯',
      color: '#F06A6A',
      features: [
        'Task management',
        'Project portfolios',
        'Team coordination',
        'Goal tracking'
      ]
    }
  ]);

  const [connectionTests, setConnectionTests] = useState<ConnectionTest[]>([]);
  const [showApiKeyModal, setShowApiKeyModal] = useState<string | null>(null);
  const [apiCredentials, setApiCredentials] = useState<{ [key: string]: { url: string; token: string; email?: string } }>({});

  // Test integration connection
  const testConnection = async (integrationId: string) => {
    setConnectionTests(prev => [...prev.filter(t => t.integration !== integrationId), {
      integration: integrationId,
      status: 'testing'
    }]);

    try {
      const credentials = apiCredentials[integrationId];
      if (!credentials) {
        throw new Error('No credentials provided');
      }

      const response = await fetch('/api/integration-hub/integrations/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          integration: integrationId,
          credentials
        })
      });

      const result = await response.json();

      if (result.success) {
        setConnectionTests(prev => [...prev.filter(t => t.integration !== integrationId), {
          integration: integrationId,
          status: 'success',
          details: result.details
        }]);

        setIntegrations(prev => prev.map(integration =>
          integration.id === integrationId
            ? { ...integration, status: 'connected', lastSync: new Date().toISOString() }
            : integration
        ));
      } else {
        throw new Error(result.error || 'Connection test failed');
      }
    } catch (error) {
      setConnectionTests(prev => [...prev.filter(t => t.integration !== integrationId), {
        integration: integrationId,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      }]);

      setIntegrations(prev => prev.map(integration =>
        integration.id === integrationId
          ? { ...integration, status: 'error', errorMessage: error instanceof Error ? error.message : 'Connection failed' }
          : integration
      ));
    }
  };

  // Handle OAuth flow initiation
  const initiateOAuth = async (integrationId: string) => {
    setIntegrations(prev => prev.map(integration =>
      integration.id === integrationId
        ? { ...integration, status: 'connecting' }
        : integration
    ));

    try {
      const response = await fetch('/api/integration-hub/integrations/oauth/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ integration: integrationId })
      });

      const result = await response.json();

      if (result.authUrl) {
        // Open OAuth flow in new window
        window.open(result.authUrl, '_blank', 'width=600,height=600');
      } else {
        throw new Error('OAuth URL not provided');
      }
    } catch (error) {
      setIntegrations(prev => prev.map(integration =>
        integration.id === integrationId
          ? { ...integration, status: 'error', errorMessage: 'OAuth initiation failed' }
          : integration
      ));
    }
  };

  // API Key configuration modal
  const renderApiKeyModal = () => {
    if (!showApiKeyModal) return null;

    const integration = integrations.find(i => i.id === showApiKeyModal);
    if (!integration) return null;

    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div style={{
          background: 'var(--pm33-glass-bg)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--pm33-glass-border)',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '500px',
          width: '90%',
          maxHeight: '80vh',
          overflow: 'auto'
        }}>
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '700',
              margin: '0 0 8px 0',
              color: 'var(--pm33-text-primary)'
            }}>
              Connect {integration.name}
            </h3>
            <p style={{
              fontSize: '14px',
              color: 'var(--pm33-text-secondary)',
              margin: '0'
            }}>
              Enter your API credentials to establish a secure connection
            </p>
          </div>

          <div style={{ display: 'grid', gap: '16px', marginBottom: '24px' }}>
            <div>
              <label style={{
                display: 'block',
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                API URL
              </label>
              <input
                type="text"
                placeholder={`https://your-company.atlassian.net (for Jira)`}
                value={apiCredentials[showApiKeyModal]?.url || ''}
                onChange={(e) => setApiCredentials(prev => ({
                  ...prev,
                  [showApiKeyModal]: { ...prev[showApiKeyModal], url: e.target.value }
                }))}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: 'var(--pm33-glass-bg)',
                  border: '1px solid var(--pm33-glass-border)',
                  borderRadius: '8px',
                  color: 'var(--pm33-text-primary)',
                  fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{
                display: 'block',
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                API Token
              </label>
              <input
                type="password"
                placeholder="Enter your API token or personal access token"
                value={apiCredentials[showApiKeyModal]?.token || ''}
                onChange={(e) => setApiCredentials(prev => ({
                  ...prev,
                  [showApiKeyModal]: { ...prev[showApiKeyModal], token: e.target.value }
                }))}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: 'var(--pm33-glass-bg)',
                  border: '1px solid var(--pm33-glass-border)',
                  borderRadius: '8px',
                  color: 'var(--pm33-text-primary)',
                  fontSize: '14px'
                }}
              />
            </div>

            {integration.id === 'jira' && (
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '12px',
                  color: 'var(--pm33-text-secondary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  marginBottom: '8px'
                }}>
                  Email (for Jira)
                </label>
                <input
                  type="email"
                  placeholder="your-email@company.com"
                  value={apiCredentials[showApiKeyModal]?.email || ''}
                  onChange={(e) => setApiCredentials(prev => ({
                    ...prev,
                    [showApiKeyModal]: { ...prev[showApiKeyModal], email: e.target.value }
                  }))}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: 'var(--pm33-glass-bg)',
                    border: '1px solid var(--pm33-glass-border)',
                    borderRadius: '8px',
                    color: 'var(--pm33-text-primary)',
                    fontSize: '14px'
                  }}
                />
              </div>
            )}
          </div>

          <div style={{
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <Shield size={16} style={{ color: 'var(--pm33-success)' }} />
              <span style={{
                fontSize: '12px',
                color: 'var(--pm33-success)',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Security Notice
              </span>
            </div>
            <p style={{
              fontSize: '12px',
              color: 'var(--pm33-text-secondary)',
              margin: '0'
            }}>
              Credentials are encrypted and stored securely. PM33 uses read-only permissions where possible.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => setShowApiKeyModal(null)}
              style={{
                padding: '8px 16px',
                background: 'transparent',
                border: '1px solid var(--pm33-glass-border)',
                borderRadius: '6px',
                color: 'var(--pm33-text-secondary)',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              onClick={() => {
                testConnection(showApiKeyModal);
                setShowApiKeyModal(null);
              }}
              disabled={!apiCredentials[showApiKeyModal]?.url || !apiCredentials[showApiKeyModal]?.token}
              style={{
                padding: '8px 16px',
                background: 'var(--pm33-brand-gradient)',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                opacity: (!apiCredentials[showApiKeyModal]?.url || !apiCredentials[showApiKeyModal]?.token) ? 0.5 : 1
              }}
            >
              Test Connection
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Get connection test for integration
  const getConnectionTest = (integrationId: string) => {
    return connectionTests.find(test => test.integration === integrationId);
  };

  // Render integration status
  const renderStatus = (integration: Integration) => {
    const test = getConnectionTest(integration.id);
    
    if (test?.status === 'testing') {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Loader size={16} style={{ color: 'var(--pm33-accent)', animation: 'spin 1s linear infinite' }} />
          <span style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>Testing...</span>
        </div>
      );
    }

    if (test?.status === 'success' || integration.status === 'connected') {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={16} style={{ color: 'var(--pm33-success)' }} />
          <span style={{ fontSize: '12px', color: 'var(--pm33-success)', fontWeight: '600' }}>Connected</span>
        </div>
      );
    }

    if (test?.status === 'failed' || integration.status === 'error') {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={16} style={{ color: 'var(--pm33-warning)' }} />
          <span style={{ fontSize: '12px', color: 'var(--pm33-warning)', fontWeight: '600' }}>Failed</span>
        </div>
      );
    }

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: 'var(--pm33-text-secondary)'
        }} />
        <span style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>Not Connected</span>
      </div>
    );
  };

  return (
    <div style={{
      padding: '24px',
      maxWidth: '1200px',
      margin: '0 auto',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {renderApiKeyModal()}
      
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '32px'
      }}>
        <button
          onClick={onBack}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'transparent',
            border: 'none',
            color: 'var(--pm33-text-secondary)',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>
      </div>

      <div style={{ marginBottom: '32px', textAlign: 'center' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: '700',
          margin: '0 0 16px 0',
          background: 'var(--pm33-brand-gradient)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Integrations
        </h1>
        <p style={{
          fontSize: '18px',
          color: 'var(--pm33-text-secondary)',
          margin: '0'
        }}>
          Connect your PM tools for unified data intelligence and workflow automation
        </p>
      </div>

      {/* Integration Summary */}
      <PM33Card style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <Zap size={24} style={{ color: 'var(--pm33-accent)' }} />
          <h3 style={{
            fontSize: '18px',
            fontWeight: '700',
            margin: '0',
            color: 'var(--pm33-text-primary)'
          }}>
            Integration Status
          </h3>
        </div>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: 'var(--pm33-success)',
              marginBottom: '4px'
            }}>
              {integrations.filter(i => i.status === 'connected').length}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
              Connected
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: 'var(--pm33-text-primary)',
              marginBottom: '4px'
            }}>
              {integrations.length}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
              Available
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: 'var(--pm33-accent)',
              marginBottom: '4px'
            }}>
              {integrations.reduce((acc, i) => acc + i.features.length, 0)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
              Features
            </div>
          </div>
        </div>
      </PM33Card>

      {/* Integration Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '24px'
      }}>
        {integrations.map((integration) => {
          const test = getConnectionTest(integration.id);
          
          return (
            <PM33Card key={integration.id}>
              <div style={{ marginBottom: '20px' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '12px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '24px' }}>{integration.logo}</span>
                    <h3 style={{
                      fontSize: '18px',
                      fontWeight: '700',
                      margin: '0',
                      color: 'var(--pm33-text-primary)'
                    }}>
                      {integration.name}
                    </h3>
                  </div>
                  {renderStatus(integration)}
                </div>
                
                <p style={{
                  fontSize: '14px',
                  color: 'var(--pm33-text-secondary)',
                  margin: '0 0 16px 0'
                }}>
                  {integration.description}
                </p>
              </div>

              {/* Features List */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{
                  fontSize: '12px',
                  color: 'var(--pm33-text-secondary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  margin: '0 0 8px 0'
                }}>
                  Features
                </h4>
                <div style={{ display: 'grid', gap: '6px' }}>
                  {integration.features.map((feature, idx) => (
                    <div key={idx} style={{
                      fontSize: '12px',
                      color: 'var(--pm33-text-primary)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <div style={{
                        width: '4px',
                        height: '4px',
                        borderRadius: '50%',
                        background: integration.color
                      }} />
                      {feature}
                    </div>
                  ))}
                </div>
              </div>

              {/* Connection Details */}
              {test?.details && (
                <div style={{
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '8px',
                  padding: '12px',
                  marginBottom: '16px'
                }}>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
                    {test.details.projects && (
                      <div>
                        <span style={{ color: 'var(--pm33-text-secondary)' }}>Projects: </span>
                        <span style={{ color: 'var(--pm33-success)', fontWeight: '600' }}>
                          {test.details.projects}
                        </span>
                      </div>
                    )}
                    {test.details.users && (
                      <div>
                        <span style={{ color: 'var(--pm33-text-secondary)' }}>Users: </span>
                        <span style={{ color: 'var(--pm33-success)', fontWeight: '600' }}>
                          {test.details.users}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Error Display */}
              {(test?.error || integration.errorMessage) && (
                <div style={{
                  background: 'rgba(251, 191, 36, 0.1)',
                  border: '1px solid rgba(251, 191, 36, 0.3)',
                  borderRadius: '8px',
                  padding: '12px',
                  marginBottom: '16px'
                }}>
                  <p style={{
                    fontSize: '12px',
                    color: 'var(--pm33-warning)',
                    margin: '0'
                  }}>
                    {test?.error || integration.errorMessage}
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px' }}>
                {integration.status === 'connected' ? (
                  <>
                    <button
                      style={{
                        flex: 1,
                        padding: '8px 16px',
                        background: 'var(--pm33-glass-bg)',
                        border: '1px solid var(--pm33-glass-border)',
                        borderRadius: '6px',
                        color: 'var(--pm33-text-secondary)',
                        fontSize: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      <Settings size={14} style={{ marginRight: '6px' }} />
                      Settings
                    </button>
                    <button
                      onClick={() => testConnection(integration.id)}
                      style={{
                        flex: 1,
                        padding: '8px 16px',
                        background: 'var(--pm33-success)',
                        border: 'none',
                        borderRadius: '6px',
                        color: 'white',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer'
                      }}
                    >
                      Test Connection
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setShowApiKeyModal(integration.id)}
                    disabled={integration.status === 'connecting'}
                    style={{
                      width: '100%',
                      padding: '8px 16px',
                      background: integration.status === 'connecting' ? 'var(--pm33-glass-border)' : 'var(--pm33-brand-gradient)',
                      border: 'none',
                      borderRadius: '6px',
                      color: 'white',
                      fontSize: '12px',
                      fontWeight: '600',
                      cursor: integration.status === 'connecting' ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {integration.status === 'connecting' ? 'Connecting...' : 'Connect'}
                  </button>
                )}
              </div>
            </PM33Card>
          );
        })}
      </div>

      {/* Continue Button */}
      {integrations.some(i => i.status === 'connected') && (
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '32px' }}>
          <button
            onClick={onBack}
            style={{
              padding: '12px 32px',
              background: 'var(--pm33-brand-gradient)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Continue to Data Mapping
          </button>
        </div>
      )}
    </div>
  );
};