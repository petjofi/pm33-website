/**
 * Component: SettingsPage
 * Purpose: Integration management, health monitoring, sync configuration
 * Design: PM33 glass morphism with settings management interface
 * Backend: Integration Hub API - Settings and configuration endpoints
 */

'use client';

import React, { useState, useEffect } from 'react';
import { PM33Card } from '../PM33Card';
import { ArrowLeft, Settings, Activity, Shield, Bell, Database, Zap, CheckCircle, AlertCircle, RefreshCw, Download, Upload, Trash2, Edit3 } from 'lucide-react';

interface SettingsPageProps {
  onBack: () => void;
}

interface IntegrationSettings {
  id: string;
  name: string;
  logo: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSync: string;
  syncFrequency: 'realtime' | 'hourly' | 'daily' | 'weekly';
  dataRetention: number; // days
  permissions: string[];
  healthScore: number;
  errorCount: number;
  syncedItems: number;
}

interface SystemSettings {
  notifications: {
    email: boolean;
    push: boolean;
    syncErrors: boolean;
    weeklyReports: boolean;
  };
  dataManagement: {
    autoBackup: boolean;
    retentionPeriod: number;
    exportFormat: 'json' | 'csv' | 'xlsx';
  };
  security: {
    apiKeyRotation: boolean;
    accessLogging: boolean;
    encryptionLevel: 'standard' | 'enhanced';
  };
  performance: {
    cacheEnabled: boolean;
    maxConcurrentSyncs: number;
    timeoutSeconds: number;
  };
}

export const SettingsPage = ({ onBack }: SettingsPageProps) => {
  const [integrations, setIntegrations] = useState<IntegrationSettings[]>([
    {
      id: 'jira',
      name: 'Jira',
      logo: '🔷',
      status: 'connected',
      lastSync: new Date(Date.now() - 1800000).toISOString(),
      syncFrequency: 'hourly',
      dataRetention: 90,
      permissions: ['read', 'write', 'admin'],
      healthScore: 0.92,
      errorCount: 2,
      syncedItems: 1247
    },
    {
      id: 'linear',
      name: 'Linear',
      logo: '⚡',
      status: 'connected',
      lastSync: new Date(Date.now() - 900000).toISOString(),
      syncFrequency: 'realtime',
      dataRetention: 60,
      permissions: ['read', 'write'],
      healthScore: 0.98,
      errorCount: 0,
      syncedItems: 856
    },
    {
      id: 'monday',
      name: 'Monday.com',
      logo: '📅',
      status: 'error',
      lastSync: new Date(Date.now() - 7200000).toISOString(),
      syncFrequency: 'daily',
      dataRetention: 120,
      permissions: ['read'],
      healthScore: 0.45,
      errorCount: 15,
      syncedItems: 423
    },
    {
      id: 'asana',
      name: 'Asana',
      logo: '🎯',
      status: 'disconnected',
      lastSync: new Date(Date.now() - 86400000).toISOString(),
      syncFrequency: 'weekly',
      dataRetention: 30,
      permissions: [],
      healthScore: 0.0,
      errorCount: 0,
      syncedItems: 0
    }
  ]);

  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    notifications: {
      email: true,
      push: false,
      syncErrors: true,
      weeklyReports: true
    },
    dataManagement: {
      autoBackup: true,
      retentionPeriod: 365,
      exportFormat: 'json'
    },
    security: {
      apiKeyRotation: true,
      accessLogging: true,
      encryptionLevel: 'enhanced'
    },
    performance: {
      cacheEnabled: true,
      maxConcurrentSyncs: 3,
      timeoutSeconds: 30
    }
  });

  const [activeTab, setActiveTab] = useState<'integrations' | 'system' | 'backup'>('integrations');
  const [isTestingConnection, setIsTestingConnection] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  // Test integration connection
  const testConnection = async (integrationId: string) => {
    setIsTestingConnection(integrationId);
    
    try {
      const response = await fetch('/api/integration-hub/integrations/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ integration: integrationId })
      });
      
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate test time
      
      setIntegrations(prev => prev.map(integration =>
        integration.id === integrationId
          ? { ...integration, status: 'connected' as const, healthScore: 0.95, errorCount: 0 }
          : integration
      ));
    } catch (error) {
      console.error('Connection test failed:', error);
    } finally {
      setIsTestingConnection(null);
    }
  };

  // Force sync integration
  const forceSync = async (integrationId: string) => {
    try {
      const response = await fetch(`/api/integration-hub/integrations/${integrationId}/sync`, {
        method: 'POST'
      });
      
      if (response.ok) {
        setIntegrations(prev => prev.map(integration =>
          integration.id === integrationId
            ? { ...integration, lastSync: new Date().toISOString() }
            : integration
        ));
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  };

  // Export configuration
  const exportConfiguration = async () => {
    setIsExporting(true);
    
    try {
      const config = {
        integrations: integrations.map(i => ({
          id: i.id,
          name: i.name,
          syncFrequency: i.syncFrequency,
          dataRetention: i.dataRetention,
          permissions: i.permissions
        })),
        systemSettings,
        exportedAt: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pm33-integration-settings-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  // Render integration settings tab
  const renderIntegrationsTab = () => (
    <div style={{ display: 'grid', gap: 'var(--space-lg)' }}>
      {integrations.map((integration) => (
        <PM33Card key={integration.id}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 2fr 1fr',
            gap: 'var(--space-lg)',
            alignItems: 'center'
          }}>
            {/* Integration Info */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
              <span style={{ fontSize: 'var(--font-size-2xl)' }}>{integration.logo}</span>
              <div>
                <h4 style={{
                  fontSize: 'var(--font-size-lg)',
                  fontWeight: '600',
                  margin: '0 0 var(--space-xs) 0',
                  color: 'var(--text-primary)'
                }}>
                  {integration.name}
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                  {integration.status === 'connected' && <CheckCircle size={16} style={{ color: 'var(--color-secondary)' }} />}
                  {integration.status === 'error' && <AlertCircle size={16} style={{ color: '#ef4444' }} />}
                  {integration.status === 'disconnected' && <div style={{
                    width: '16px',
                    height: '16px',
                    borderRadius: '50%',
                    background: 'var(--text-muted)'
                  }} />}
                  <span style={{
                    fontSize: 'var(--font-size-sm)',
                    color: integration.status === 'connected' ? 'var(--color-secondary)' :
                           integration.status === 'error' ? '#ef4444' : 'var(--text-muted)',
                    textTransform: 'capitalize',
                    fontWeight: '500'
                  }}>
                    {integration.status}
                  </span>
                </div>
              </div>
            </div>

            {/* Configuration */}
            <div style={{ display: 'grid', gap: 'var(--space-sm)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                  Sync Frequency:
                </span>
                <select
                  value={integration.syncFrequency}
                  onChange={(e) => setIntegrations(prev => prev.map(i =>
                    i.id === integration.id ? { ...i, syncFrequency: e.target.value as any } : i
                  ))}
                  className="input-modern"
                  style={{
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    padding: 'var(--space-xs)',
                    color: 'var(--text-primary)',
                    fontSize: 'var(--font-size-sm)'
                  }}
                >
                  <option value="realtime">Real-time</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                  Data Retention:
                </span>
                <input
                  type="number"
                  value={integration.dataRetention}
                  onChange={(e) => setIntegrations(prev => prev.map(i =>
                    i.id === integration.id ? { ...i, dataRetention: parseInt(e.target.value) } : i
                  ))}
                  className="input-modern"
                  style={{
                    width: '80px',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    padding: 'var(--space-xs)',
                    color: 'var(--text-primary)',
                    fontSize: 'var(--font-size-sm)'
                  }}
                />
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: 'var(--space-sm)',
                background: integration.status === 'connected' ? 'rgba(16, 185, 129, 0.1)' :
                           integration.status === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg-secondary)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid',
                borderColor: integration.status === 'connected' ? 'rgba(16, 185, 129, 0.3)' :
                            integration.status === 'error' ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-color)'
              }}>
                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                  Health Score:
                </span>
                <span style={{
                  fontSize: 'var(--font-size-sm)',
                  fontWeight: '600',
                  color: integration.healthScore >= 0.8 ? 'var(--color-secondary)' :
                         integration.healthScore >= 0.5 ? '#f59e0b' : '#ef4444'
                }}>
                  {Math.round(integration.healthScore * 100)}%
                </span>
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              <button
                onClick={() => testConnection(integration.id)}
                disabled={isTestingConnection === integration.id}
                className="btn-glass"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 'var(--space-xs)',
                  padding: 'var(--space-xs) var(--space-sm)',
                  fontSize: 'var(--font-size-sm)',
                  opacity: isTestingConnection === integration.id ? 0.5 : 1
                }}
              >
                {isTestingConnection === integration.id ? (
                  <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <Activity size={14} />
                )}
                Test
              </button>
              
              {integration.status === 'connected' && (
                <button
                  onClick={() => forceSync(integration.id)}
                  className="btn-secondary"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 'var(--space-xs)',
                    padding: 'var(--space-xs) var(--space-sm)',
                    fontSize: 'var(--font-size-sm)'
                  }}
                >
                  <RefreshCw size={14} />
                  Sync
                </button>
              )}
              
              <button
                className="btn-glass"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 'var(--space-xs)',
                  padding: 'var(--space-xs) var(--space-sm)',
                  fontSize: 'var(--font-size-sm)'
                }}
              >
                <Edit3 size={14} />
                Edit
              </button>
            </div>
          </div>

          {/* Stats Row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 'var(--space-md)',
            marginTop: 'var(--space-md)',
            paddingTop: 'var(--space-md)',
            borderTop: '1px solid var(--border-color)'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: 'var(--font-size-lg)',
                fontWeight: '600',
                color: 'var(--text-primary)',
                marginBottom: 'var(--space-xs)'
              }}>
                {integration.syncedItems.toLocaleString()}
              </div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                Synced Items
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: 'var(--font-size-lg)',
                fontWeight: '600',
                color: integration.errorCount === 0 ? 'var(--color-secondary)' : '#ef4444',
                marginBottom: 'var(--space-xs)'
              }}>
                {integration.errorCount}
              </div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                Errors
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: 'var(--font-size-lg)',
                fontWeight: '600',
                color: 'var(--text-primary)',
                marginBottom: 'var(--space-xs)'
              }}>
                {new Date(integration.lastSync).toLocaleTimeString()}
              </div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                Last Sync
              </div>
            </div>
          </div>
        </PM33Card>
      ))}
    </div>
  );

  // Render system settings tab
  const renderSystemTab = () => (
    <div style={{ display: 'grid', gap: 'var(--space-lg)' }}>
      {/* Notifications */}
      <PM33Card>
        <h3 style={{
          fontSize: 'var(--font-size-xl)',
          fontWeight: '600',
          margin: '0 0 var(--space-lg) 0',
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <Bell size={20} style={{ color: 'var(--color-accent)' }} />
          Notifications
        </h3>
        
        <div style={{ display: 'grid', gap: 'var(--space-md)' }}>
          {Object.entries(systemSettings.notifications).map(([key, value]) => (
            <div key={key} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 'var(--space-sm)',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)'
            }}>
              <span style={{
                fontSize: 'var(--font-size-base)',
                color: 'var(--text-primary)',
                textTransform: 'capitalize'
              }}>
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </span>
              <input
                type="checkbox"
                checked={value}
                onChange={(e) => setSystemSettings(prev => ({
                  ...prev,
                  notifications: { ...prev.notifications, [key]: e.target.checked }
                }))}
                style={{
                  width: '20px',
                  height: '20px',
                  cursor: 'pointer'
                }}
              />
            </div>
          ))}
        </div>
      </PM33Card>

      {/* Security */}
      <PM33Card>
        <h3 style={{
          fontSize: 'var(--font-size-xl)',
          fontWeight: '600',
          margin: '0 0 var(--space-lg) 0',
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <Shield size={20} style={{ color: 'var(--color-primary)' }} />
          Security
        </h3>
        
        <div style={{ display: 'grid', gap: 'var(--space-md)' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 'var(--space-sm)',
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-sm)'
          }}>
            <span style={{ fontSize: 'var(--font-size-base)', color: 'var(--text-primary)' }}>
              Encryption Level
            </span>
            <select
              value={systemSettings.security.encryptionLevel}
              onChange={(e) => setSystemSettings(prev => ({
                ...prev,
                security: { ...prev.security, encryptionLevel: e.target.value as any }
              }))}
              className="input-modern"
              style={{
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: 'var(--space-xs)',
                color: 'var(--text-primary)',
                fontSize: 'var(--font-size-sm)'
              }}
            >
              <option value="standard">Standard</option>
              <option value="enhanced">Enhanced</option>
            </select>
          </div>
          
          {['apiKeyRotation', 'accessLogging'].map(key => (
            <div key={key} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 'var(--space-sm)',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)'
            }}>
              <span style={{
                fontSize: 'var(--font-size-base)',
                color: 'var(--text-primary)',
                textTransform: 'capitalize'
              }}>
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </span>
              <input
                type="checkbox"
                checked={systemSettings.security[key as keyof typeof systemSettings.security] as boolean}
                onChange={(e) => setSystemSettings(prev => ({
                  ...prev,
                  security: { ...prev.security, [key]: e.target.checked }
                }))}
                style={{
                  width: '20px',
                  height: '20px',
                  cursor: 'pointer'
                }}
              />
            </div>
          ))}
        </div>
      </PM33Card>
    </div>
  );

  return (
    <div style={{
      padding: 'var(--space-lg)',
      maxWidth: '1400px',
      margin: '0 auto',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: 'var(--space-xl)'
      }}>
        <button
          onClick={onBack}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-sm)',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            fontSize: 'var(--font-size-sm)'
          }}
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>
      </div>

      <div style={{ marginBottom: 'var(--space-xl)', textAlign: 'center' }}>
        <h1 className="text-gradient" style={{
          fontSize: 'var(--font-size-4xl)',
          fontWeight: '700',
          margin: '0 0 var(--space-sm) 0'
        }}>
          Settings
        </h1>
        <p style={{
          fontSize: 'var(--font-size-lg)',
          color: 'var(--text-secondary)',
          margin: '0'
        }}>
          Health monitoring, sync configuration, and integration management
        </p>
      </div>

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        marginBottom: 'var(--space-xl)'
      }}>
        <div style={{
          display: 'flex',
          background: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-xs)'
        }}>
          {[
            { id: 'integrations', label: 'Integrations', icon: <Database size={16} /> },
            { id: 'system', label: 'System', icon: <Settings size={16} /> },
            { id: 'backup', label: 'Backup', icon: <Download size={16} /> }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-xs)',
                padding: 'var(--space-sm) var(--space-lg)',
                background: activeTab === tab.id ? 'var(--gradient-primary)' : 'transparent',
                color: activeTab === tab.id ? 'var(--gradient-text)' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all var(--duration-normal) var(--ease-smooth)'
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'integrations' && renderIntegrationsTab()}
      {activeTab === 'system' && renderSystemTab()}
      {activeTab === 'backup' && (
        <PM33Card style={{ textAlign: 'center' }}>
          <Zap size={48} style={{ 
            color: 'var(--color-accent)', 
            margin: '0 auto var(--space-md)' 
          }} />
          <h3 style={{
            fontSize: 'var(--font-size-xl)',
            fontWeight: '600',
            margin: '0 0 var(--space-sm) 0',
            color: 'var(--text-primary)'
          }}>
            Configuration Backup
          </h3>
          <p style={{
            fontSize: 'var(--font-size-base)',
            color: 'var(--text-secondary)',
            margin: '0 0 var(--space-lg) 0'
          }}>
            Export your integration settings and configuration for backup or migration
          </p>
          <button
            onClick={exportConfiguration}
            disabled={isExporting}
            className="btn-primary"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-sm)',
              margin: '0 auto',
              opacity: isExporting ? 0.5 : 1
            }}
          >
            {isExporting ? (
              <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
            ) : (
              <Download size={16} />
            )}
            {isExporting ? 'Exporting...' : 'Export Configuration'}
          </button>
        </PM33Card>
      )}
    </div>
  );
};