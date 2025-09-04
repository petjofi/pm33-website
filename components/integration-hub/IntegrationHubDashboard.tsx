/**
 * Integration Hub Dashboard - Main entry point for PM33 Integration workflow
 * 
 * Workflow: Strategy Setup → Integrations → Data Mapping → Data Filtering → AI Enhancements → Settings
 * Backend: http://localhost:8002/api/integration-hub/
 * 
 * Design Compliance:
 * - Uses PM33Card with glass morphism
 * - Theme-aware CSS variables
 * - Progressive disclosure UX patterns
 * - Integration-centric approach
 */

'use client';

import React, { useState, useEffect } from 'react';
import { PM33Card } from '../PM33Card';
import { 
  Brain, 
  Settings, 
  Database, 
  Zap, 
  CheckCircle, 
  Clock,
  AlertTriangle,
  TrendingUp,
  Activity,
  GitBranch,
  Users,
  BarChart3
} from 'lucide-react';

interface IntegrationSession {
  id: string;
  user_id: string;
  status: 'active' | 'completed' | 'error';
  current_step: number;
  workflow_steps: Array<{
    id: number;
    phase: string;
    title: string;
    status: 'pending' | 'in_progress' | 'completed' | 'error';
    estimated_minutes: number;
  }>;
  progress_summary: {
    current_step: number;
    total_steps: number;
    progress_percentage: number;
    phase: string;
    estimated_time_remaining: number;
  };
}

interface IntegrationHubDashboardProps {
  theme?: 'light' | 'dark';
  onNavigateToStep?: (step: string) => void;
}

export const IntegrationHubDashboard: React.FC<IntegrationHubDashboardProps> = ({
  theme = 'dark',
  onNavigateToStep
}) => {
  const [session, setSession] = useState<IntegrationSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<any>(null);

  // Initialize integration session on component mount
  useEffect(() => {
    initializeSession();
    fetchHealthStatus();
    
    // Set up polling for health status every 30 seconds
    const healthInterval = setInterval(fetchHealthStatus, 30000);
    
    return () => clearInterval(healthInterval);
  }, []);

  const initializeSession = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/integration-hub/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'dashboard_user',
          session_type: 'onboarding'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to initialize integration session');
      }

      const data = await response.json();
      
      // Get full session status
      const statusResponse = await fetch(`/api/integration-hub/sessions/${data.session_id}`);
      if (statusResponse.ok) {
        const sessionData = await statusResponse.json();
        setSession({
          id: sessionData.session_id,
          user_id: sessionData.session_data.user_id,
          status: sessionData.session_data.status,
          current_step: sessionData.session_data.current_step,
          workflow_steps: sessionData.session_data.workflow_steps,
          progress_summary: sessionData.progress_summary
        });
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize session');
    } finally {
      setLoading(false);
    }
  };

  const fetchHealthStatus = async () => {
    try {
      const response = await fetch('http://localhost:8002/health');
      if (response.ok) {
        const data = await response.json();
        setHealthStatus(data);
      }
    } catch (err) {
      console.warn('Health status fetch failed:', err);
    }
  };

  const getCurrentPhaseSteps = () => {
    if (!session) return [];
    
    const currentPhase = session.progress_summary.phase;
    return session.workflow_steps.filter(step => step.phase === currentPhase);
  };

  const getPhaseProgress = () => {
    if (!session) return {};
    
    const phases = ['Setup', 'Discovery', 'Intelligence', 'Optimization', 'Launch'];
    const progress: { [key: string]: number } = {};
    
    phases.forEach(phase => {
      const phaseSteps = session.workflow_steps.filter(step => step.phase === phase);
      const completedSteps = phaseSteps.filter(step => step.status === 'completed').length;
      progress[phase] = phaseSteps.length > 0 ? (completedSteps / phaseSteps.length) * 100 : 0;
    });
    
    return progress;
  };

  const navigateToStep = (stepName: string) => {
    onNavigateToStep?.(stepName);
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        color: 'var(--text-primary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <Activity 
            size={48} 
            style={{ 
              animation: 'spin 2s linear infinite',
              marginBottom: 'var(--space-md)',
              color: 'var(--color-primary)' 
            }} 
          />
          <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: '600' }}>
            Initializing Integration Hub...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <PM33Card>
        <div style={{ textAlign: 'center', color: 'var(--text-primary)' }}>
          <AlertTriangle size={48} color="#ef4444" style={{ marginBottom: 'var(--space-md)' }} />
          <h3 style={{ margin: '0 0 var(--space-sm) 0', color: '#ef4444' }}>Connection Error</h3>
          <p style={{ margin: '0 0 var(--space-md) 0', color: 'var(--text-secondary)' }}>
            {error}
          </p>
          <button
            onClick={initializeSession}
            disabled={loading}
            className="btn-primary"
            style={{
              background: 'var(--gradient-primary)',
              color: 'var(--gradient-text)',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-sm) var(--space-lg)',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Retry Connection
          </button>
        </div>
      </PM33Card>
    );
  }

  return (
    <div style={{
      padding: 'var(--space-lg)',
      maxWidth: '1200px',
      margin: '0 auto',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h1 className="text-gradient" style={{
          fontSize: 'var(--font-size-4xl)',
          fontWeight: '700',
          margin: '0 0 var(--space-sm) 0'
        }}>
          Integration Hub
        </h1>
        <p style={{
          fontSize: 'var(--font-size-base)',
          color: 'var(--text-secondary)',
          margin: 0
        }}>
          Enterprise-grade data intelligence platform for strategic PM workflows
        </p>
      </div>

      {/* Progress Overview */}
      {session && (
        <PM33Card style={{ marginBottom: '24px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px'
          }}>
            <div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                margin: '0 0 4px 0',
                color: 'var(--pm33-text-primary)'
              }}>
                Workflow Progress
              </h3>
              <p style={{
                fontSize: '14px',
                color: 'var(--pm33-text-secondary)',
                margin: 0
              }}>
                Phase: {session.progress_summary.phase} • {session.progress_summary.estimated_time_remaining} minutes remaining
              </p>
            </div>
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: 'var(--pm33-text-primary)'
              }}>
                {Math.round(session.progress_summary.progress_percentage)}%
              </div>
              <TrendingUp size={20} color="var(--pm33-brand)" />
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{
            width: '100%',
            height: '8px',
            background: 'var(--pm33-glass-border)',
            borderRadius: '4px',
            overflow: 'hidden',
            marginBottom: '16px'
          }}>
            <div style={{
              width: `${session.progress_summary.progress_percentage}%`,
              height: '100%',
              background: 'var(--pm33-brand-gradient)',
              transition: 'width 0.3s ease'
            }} />
          </div>

          {/* Phase Progress */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(5, 1fr)',
            gap: '12px'
          }}>
            {Object.entries(getPhaseProgress()).map(([phase, progress]) => (
              <div key={phase} style={{
                textAlign: 'center',
                padding: '8px',
                background: progress > 0 ? 'var(--pm33-glass-bg)' : 'transparent',
                borderRadius: '8px',
                border: progress > 0 ? '1px solid var(--pm33-glass-border)' : '1px solid transparent'
              }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: progress === 100 ? '#10b981' : progress > 0 ? 'var(--pm33-brand)' : 'var(--pm33-text-secondary)',
                  marginBottom: '4px'
                }}>
                  {phase}
                </div>
                <div style={{
                  fontSize: '10px',
                  color: 'var(--pm33-text-secondary)'
                }}>
                  {Math.round(progress)}%
                </div>
              </div>
            ))}
          </div>
        </PM33Card>
      )}

      {/* Main Workflow Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        {/* Strategy Setup */}
        <PM33Card 
          onClick={() => navigateToStep('strategy')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'var(--pm33-brand-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <Brain size={24} color="white" />
            </div>
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '600',
                margin: '0 0 4px 0',
                color: 'var(--pm33-text-primary)'
              }}>
                Strategy Setup
              </h4>
              <p style={{
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                margin: 0
              }}>
                Company intelligence & strategic context
              </p>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{
              fontSize: '14px',
              color: 'var(--pm33-text-secondary)'
            }}>
              AI-powered analysis
            </span>
            {session && session.progress_summary.phase === 'Intelligence' && (
              <CheckCircle size={16} color="#10b981" />
            )}
          </div>
        </PM33Card>

        {/* Integrations */}
        <PM33Card 
          onClick={() => navigateToStep('integrations')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <GitBranch size={24} color="white" />
            </div>
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '600',
                margin: '0 0 4px 0',
                color: 'var(--pm33-text-primary)'
              }}>
                Integrations
              </h4>
              <p style={{
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                margin: 0
              }}>
                Jira, Linear, Monday, Asana
              </p>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{
              fontSize: '14px',
              color: 'var(--pm33-text-secondary)'
            }}>
              OAuth & API management
            </span>
            {healthStatus && (
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: healthStatus.initialized ? '#10b981' : '#ef4444'
              }} />
            )}
          </div>
        </PM33Card>

        {/* Data Mapping */}
        <PM33Card 
          onClick={() => navigateToStep('data-mapping')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <Database size={24} color="white" />
            </div>
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '600',
                margin: '0 0 4px 0',
                color: 'var(--pm33-text-primary)'
              }}>
                Data Mapping
              </h4>
              <p style={{
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                margin: 0
              }}>
                AI-powered field mapping
              </p>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{
              fontSize: '14px',
              color: 'var(--pm33-text-secondary)'
            }}>
              Confidence scoring
            </span>
            <BarChart3 size={16} color="var(--pm33-brand)" />
          </div>
        </PM33Card>

        {/* AI Enhancements */}
        <PM33Card 
          onClick={() => navigateToStep('ai-enhancements')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <Zap size={24} color="white" />
            </div>
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '600',
                margin: '0 0 4px 0',
                color: 'var(--pm33-text-primary)'
              }}>
                AI Enhancements
              </h4>
              <p style={{
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                margin: 0
              }}>
                Story points & hierarchy
              </p>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{
              fontSize: '14px',
              color: 'var(--pm33-text-secondary)'
            }}>
              Strategic planning ready
            </span>
            <Activity size={16} color="#f59e0b" />
          </div>
        </PM33Card>

        {/* Settings */}
        <PM33Card 
          onClick={() => navigateToStep('settings')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <Settings size={24} color="white" />
            </div>
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '600',
                margin: '0 0 4px 0',
                color: 'var(--pm33-text-primary)'
              }}>
                Settings
              </h4>
              <p style={{
                fontSize: '12px',
                color: 'var(--pm33-text-secondary)',
                margin: 0
              }}>
                Health monitoring & config
              </p>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{
              fontSize: '14px',
              color: 'var(--pm33-text-secondary)'
            }}>
              Real-time monitoring
            </span>
            <Users size={16} color="#6b7280" />
          </div>
        </PM33Card>
      </div>

      {/* Current Phase Quick Actions */}
      {session && getCurrentPhaseSteps().length > 0 && (
        <PM33Card>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            margin: '0 0 16px 0',
            color: 'var(--pm33-text-primary)'
          }}>
            Current Phase: {session.progress_summary.phase}
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '12px'
          }}>
            {getCurrentPhaseSteps().map((step) => (
              <div
                key={step.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: step.status === 'completed' 
                    ? 'rgba(16, 185, 129, 0.1)' 
                    : step.status === 'in_progress'
                    ? 'var(--pm33-glass-bg)'
                    : 'transparent',
                  border: '1px solid var(--pm33-glass-border)',
                  borderRadius: '8px'
                }}
              >
                <div style={{ marginRight: '12px' }}>
                  {step.status === 'completed' && <CheckCircle size={16} color="#10b981" />}
                  {step.status === 'in_progress' && <Clock size={16} color="var(--pm33-brand)" />}
                  {step.status === 'pending' && <div style={{
                    width: '16px',
                    height: '16px',
                    borderRadius: '50%',
                    border: '2px solid var(--pm33-glass-border)'
                  }} />}
                </div>
                
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: 'var(--pm33-text-primary)',
                    marginBottom: '2px'
                  }}>
                    {step.title}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: 'var(--pm33-text-secondary)'
                  }}>
                    ~{step.estimated_minutes} min
                  </div>
                </div>
              </div>
            ))}
          </div>
        </PM33Card>
      )}

      {/* Add keyframe animation */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `
      }} />
    </div>
  );
};

export default IntegrationHubDashboard;