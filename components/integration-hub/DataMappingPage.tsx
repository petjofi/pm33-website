/**
 * Component: DataMappingPage
 * Purpose: Integration-specific field mapping with AI-powered confidence scoring
 * Design: PM33 glass morphism with interactive mapping workflow
 * Backend: Integration Hub API - Data mapping endpoints
 */

'use client';

import React, { useState, useEffect } from 'react';
import { PM33Card } from '../PM33Card';
import { ArrowLeft, Database, Target, CheckCircle, AlertTriangle, Brain, Zap, RefreshCw, Download } from 'lucide-react';

interface DataMappingPageProps {
  onBack: () => void;
}

interface FieldMapping {
  sourceField: string;
  targetField: string;
  confidence: number;
  status: 'mapped' | 'pending' | 'review' | 'ignored';
  dataType: 'string' | 'number' | 'date' | 'boolean' | 'array' | 'object';
  examples: string[];
  aiSuggestion?: string;
  notes?: string;
}

interface IntegrationMappingSession {
  integration: string;
  name: string;
  logo: string;
  color: string;
  fieldsDiscovered: number;
  fieldsMapped: number;
  confidence: number;
  lastSync: string;
  mappings: FieldMapping[];
}

export const DataMappingPage = ({ onBack }: DataMappingPageProps) => {
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);
  const [mappingSessions, setMappingSessions] = useState<IntegrationMappingSession[]>([
    {
      integration: 'jira',
      name: 'Jira',
      logo: '🔷',
      color: '#0052CC',
      fieldsDiscovered: 47,
      fieldsMapped: 32,
      confidence: 0.89,
      lastSync: new Date().toISOString(),
      mappings: [
        {
          sourceField: 'summary',
          targetField: 'title',
          confidence: 0.98,
          status: 'mapped',
          dataType: 'string',
          examples: ['Fix login button styling', 'Implement user dashboard'],
          aiSuggestion: 'High confidence match - standard issue title field'
        },
        {
          sourceField: 'storyPoints',
          targetField: 'effort_estimate',
          confidence: 0.95,
          status: 'mapped',
          dataType: 'number',
          examples: ['3', '5', '8', '13'],
          aiSuggestion: 'Story point estimation field - direct mapping recommended'
        },
        {
          sourceField: 'customfield_10001',
          targetField: 'business_value',
          confidence: 0.72,
          status: 'review',
          dataType: 'number',
          examples: ['High', 'Medium', 'Low'],
          aiSuggestion: 'Custom field appears to contain business value - requires review'
        },
        {
          sourceField: 'fixVersions',
          targetField: 'target_release',
          confidence: 0.88,
          status: 'mapped',
          dataType: 'array',
          examples: ['v2.1.0', 'v2.2.0', 'backlog'],
          aiSuggestion: 'Release version mapping with high confidence'
        },
        {
          sourceField: 'customfield_10045',
          targetField: '',
          confidence: 0.45,
          status: 'pending',
          dataType: 'string',
          examples: ['Team Alpha', 'Team Beta', 'Platform'],
          aiSuggestion: 'Low confidence - may be team assignment field'
        }
      ]
    },
    {
      integration: 'linear',
      name: 'Linear',
      logo: '⚡',
      color: '#5E57D9',
      fieldsDiscovered: 23,
      fieldsMapped: 19,
      confidence: 0.94,
      lastSync: new Date(Date.now() - 3600000).toISOString(),
      mappings: [
        {
          sourceField: 'title',
          targetField: 'title',
          confidence: 1.0,
          status: 'mapped',
          dataType: 'string',
          examples: ['Add authentication flow', 'Update API documentation'],
          aiSuggestion: 'Perfect match - exact field name correspondence'
        },
        {
          sourceField: 'estimate',
          targetField: 'effort_estimate',
          confidence: 0.96,
          status: 'mapped',
          dataType: 'number',
          examples: ['1', '2', '3', '5'],
          aiSuggestion: 'Linear point estimation - high confidence mapping'
        },
        {
          sourceField: 'priority',
          targetField: 'priority_score',
          confidence: 0.91,
          status: 'mapped',
          dataType: 'number',
          examples: ['1', '2', '3', '4'],
          aiSuggestion: 'Priority field with numerical scale'
        }
      ]
    },
    {
      integration: 'monday',
      name: 'Monday.com',
      logo: '📅',
      color: '#FF6B35',
      fieldsDiscovered: 34,
      fieldsMapped: 18,
      confidence: 0.76,
      lastSync: new Date(Date.now() - 7200000).toISOString(),
      mappings: [
        {
          sourceField: 'name',
          targetField: 'title',
          confidence: 0.87,
          status: 'mapped',
          dataType: 'string',
          examples: ['Design review session', 'Sprint planning meeting'],
          aiSuggestion: 'Item name field - good match for title'
        },
        {
          sourceField: 'status',
          targetField: 'status',
          confidence: 0.93,
          status: 'mapped',
          dataType: 'string',
          examples: ['Done', 'Working on it', 'Stuck'],
          aiSuggestion: 'Status field with custom labels'
        },
        {
          sourceField: 'timeline',
          targetField: 'due_date',
          confidence: 0.78,
          status: 'review',
          dataType: 'object',
          examples: ['{"from":"2025-01-01","to":"2025-01-15"}'],
          aiSuggestion: 'Timeline object - may need transformation for due date'
        }
      ]
    }
  ]);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showMappingDetails, setShowMappingDetails] = useState<string | null>(null);

  // Analyze field mappings with AI
  const analyzeFieldMappings = async (integration: string) => {
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('/api/integration-hub/data-mapping/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          integration,
          fields: mappingSessions.find(s => s.integration === integration)?.mappings || []
        })
      });
      
      const result = await response.json();
      
      // Simulate AI analysis processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update mappings with AI suggestions
      setMappingSessions(prev => prev.map(session => 
        session.integration === integration ? {
          ...session,
          confidence: Math.min(session.confidence + 0.05, 0.99),
          mappings: session.mappings.map(mapping => ({
            ...mapping,
            confidence: mapping.status === 'pending' ? Math.random() * 0.3 + 0.7 : mapping.confidence,
            aiSuggestion: mapping.status === 'pending' ? 'AI analysis suggests this may be a custom workflow field' : mapping.aiSuggestion
          }))
        } : session
      ));
      
    } catch (error) {
      console.error('AI analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Update field mapping
  const updateMapping = (integration: string, sourceField: string, updates: Partial<FieldMapping>) => {
    setMappingSessions(prev => prev.map(session =>
      session.integration === integration ? {
        ...session,
        mappings: session.mappings.map(mapping =>
          mapping.sourceField === sourceField ? { ...mapping, ...updates } : mapping
        )
      } : session
    ));
  };

  // Export mappings configuration
  const exportMappings = (integration: string) => {
    const session = mappingSessions.find(s => s.integration === integration);
    if (!session) return;
    
    const exportData = {
      integration: session.integration,
      name: session.name,
      exportedAt: new Date().toISOString(),
      fieldMappings: session.mappings.filter(m => m.status === 'mapped').map(m => ({
        source: m.sourceField,
        target: m.targetField,
        dataType: m.dataType,
        confidence: m.confidence
      }))
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${integration}-field-mappings.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'var(--pm33-success)';
    if (confidence >= 0.7) return 'var(--pm33-accent)';
    return 'var(--pm33-warning)';
  };

  // Render integration overview
  const renderIntegrationOverview = () => (
    <div>
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
          Data Mapping
        </h1>
        <p style={{
          fontSize: '18px',
          color: 'var(--pm33-text-secondary)',
          margin: '0'
        }}>
          Integration-specific field mapping with AI-powered confidence scoring
        </p>
      </div>

      {/* Mapping Summary */}
      <PM33Card style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <Database size={24} style={{ color: 'var(--pm33-accent)' }} />
          <h3 style={{
            fontSize: '18px',
            fontWeight: '700',
            margin: '0',
            color: 'var(--pm33-text-primary)'
          }}>
            Mapping Overview
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
              {mappingSessions.reduce((acc, s) => acc + s.fieldsMapped, 0)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
              Fields Mapped
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: 'var(--pm33-text-primary)',
              marginBottom: '4px'
            }}>
              {mappingSessions.reduce((acc, s) => acc + s.fieldsDiscovered, 0)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
              Fields Discovered
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: 'var(--pm33-accent)',
              marginBottom: '4px'
            }}>
              {Math.round(mappingSessions.reduce((acc, s) => acc + s.confidence, 0) / mappingSessions.length * 100)}%
            </div>
            <div style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
              Avg Confidence
            </div>
          </div>
        </div>
      </PM33Card>

      {/* Integration Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '24px'
      }}>
        {mappingSessions.map((session) => (
          <PM33Card key={session.integration} onClick={() => setSelectedIntegration(session.integration)}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '12px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '24px' }}>{session.logo}</span>
                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    margin: '0',
                    color: 'var(--pm33-text-primary)'
                  }}>
                    {session.name}
                  </h3>
                </div>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: getConfidenceColor(session.confidence)
                }}>
                  {Math.round(session.confidence * 100)}%
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <span style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)' }}>
                  Mapping Progress
                </span>
                <span style={{ fontSize: '12px', color: 'var(--pm33-text-primary)', fontWeight: '600' }}>
                  {session.fieldsMapped} / {session.fieldsDiscovered}
                </span>
              </div>
              
              <div style={{
                width: '100%',
                height: '6px',
                background: 'var(--pm33-glass-border)',
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${(session.fieldsMapped / session.fieldsDiscovered) * 100}%`,
                  height: '100%',
                  background: session.color,
                  transition: 'width 0.3s ease'
                }} />
              </div>
            </div>

            {/* Status Indicators */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '8px',
              marginBottom: '16px'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'var(--pm33-success)',
                  marginBottom: '4px'
                }}>
                  {session.mappings.filter(m => m.status === 'mapped').length}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--pm33-text-secondary)' }}>
                  Mapped
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'var(--pm33-warning)',
                  marginBottom: '4px'
                }}>
                  {session.mappings.filter(m => m.status === 'review').length}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--pm33-text-secondary)' }}>
                  Review
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'var(--pm33-text-secondary)',
                  marginBottom: '4px'
                }}>
                  {session.mappings.filter(m => m.status === 'pending').length}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--pm33-text-secondary)' }}>
                  Pending
                </div>
              </div>
            </div>

            {/* Last Sync */}
            <div style={{
              fontSize: '11px',
              color: 'var(--pm33-text-secondary)',
              textAlign: 'center',
              marginBottom: '16px'
            }}>
              Last sync: {new Date(session.lastSync).toLocaleString()}
            </div>

            {/* Action Button */}
            <button
              onClick={() => setSelectedIntegration(session.integration)}
              style={{
                width: '100%',
                padding: '8px 16px',
                background: 'var(--pm33-brand-gradient)',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Configure Mapping
            </button>
          </PM33Card>
        ))}
      </div>
    </div>
  );

  // Render detailed mapping interface
  const renderDetailedMapping = () => {
    const session = mappingSessions.find(s => s.integration === selectedIntegration);
    if (!session) return null;

    return (
      <div>
        <div style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <span style={{ fontSize: '32px' }}>{session.logo}</span>
              <div>
                <h1 style={{
                  fontSize: '2rem',
                  fontWeight: '700',
                  margin: '0',
                  background: 'var(--pm33-brand-gradient)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  {session.name} Mapping
                </h1>
                <p style={{
                  fontSize: '14px',
                  color: 'var(--pm33-text-secondary)',
                  margin: '4px 0 0 0'
                }}>
                  {session.fieldsDiscovered} fields discovered • {Math.round(session.confidence * 100)}% confidence
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => analyzeFieldMappings(session.integration)}
                disabled={isAnalyzing}
                style={{
                  padding: '8px 16px',
                  background: 'var(--pm33-glass-bg)',
                  border: '1px solid var(--pm33-glass-border)',
                  borderRadius: '6px',
                  color: 'var(--pm33-text-primary)',
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {isAnalyzing ? (
                  <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <Brain size={14} />
                )}
                {isAnalyzing ? 'Analyzing...' : 'AI Analysis'}
              </button>
              <button
                onClick={() => exportMappings(session.integration)}
                style={{
                  padding: '8px 16px',
                  background: 'var(--pm33-success)',
                  border: 'none',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Download size={14} />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Field Mappings */}
        <div style={{ display: 'grid', gap: '16px' }}>
          {session.mappings.map((mapping, idx) => (
            <PM33Card key={`${mapping.sourceField}-${idx}`}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '2fr 1fr 2fr 1fr',
                gap: '16px',
                alignItems: 'center'
              }}>
                {/* Source Field */}
                <div>
                  <div style={{
                    fontSize: '12px',
                    color: 'var(--pm33-text-secondary)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: '4px'
                  }}>
                    Source Field
                  </div>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: 'var(--pm33-text-primary)',
                    fontFamily: 'monospace',
                    marginBottom: '8px'
                  }}>
                    {mapping.sourceField}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: 'var(--pm33-text-secondary)',
                    marginBottom: '4px'
                  }}>
                    Type: {mapping.dataType}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: 'var(--pm33-text-secondary)',
                    fontStyle: 'italic'
                  }}>
                    Examples: {mapping.examples.slice(0, 2).join(', ')}
                  </div>
                </div>

                {/* Confidence Score */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: getConfidenceColor(mapping.confidence),
                    marginBottom: '4px'
                  }}>
                    {Math.round(mapping.confidence * 100)}%
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--pm33-text-secondary)' }}>
                    Confidence
                  </div>
                </div>

                {/* Target Field */}
                <div>
                  <div style={{
                    fontSize: '12px',
                    color: 'var(--pm33-text-secondary)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: '4px'
                  }}>
                    Target Field
                  </div>
                  {mapping.status === 'pending' ? (
                    <select
                      value={mapping.targetField}
                      onChange={(e) => updateMapping(session.integration, mapping.sourceField, {
                        targetField: e.target.value,
                        status: e.target.value ? 'mapped' : 'pending'
                      })}
                      style={{
                        width: '100%',
                        padding: '8px',
                        background: 'var(--pm33-glass-bg)',
                        border: '1px solid var(--pm33-glass-border)',
                        borderRadius: '4px',
                        color: 'var(--pm33-text-primary)',
                        fontSize: '14px'
                      }}
                    >
                      <option value="">Select target field...</option>
                      <option value="title">title</option>
                      <option value="description">description</option>
                      <option value="effort_estimate">effort_estimate</option>
                      <option value="priority_score">priority_score</option>
                      <option value="business_value">business_value</option>
                      <option value="target_release">target_release</option>
                      <option value="assignee">assignee</option>
                      <option value="team">team</option>
                      <option value="status">status</option>
                      <option value="due_date">due_date</option>
                    </select>
                  ) : (
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: 'var(--pm33-text-primary)',
                      fontFamily: 'monospace'
                    }}>
                      {mapping.targetField || 'Not mapped'}
                    </div>
                  )}
                </div>

                {/* Status */}
                <div style={{ textAlign: 'center' }}>
                  {mapping.status === 'mapped' && <CheckCircle size={16} style={{ color: 'var(--pm33-success)' }} />}
                  {mapping.status === 'review' && <AlertTriangle size={16} style={{ color: 'var(--pm33-warning)' }} />}
                  {mapping.status === 'pending' && <Target size={16} style={{ color: 'var(--pm33-text-secondary)' }} />}
                  <div style={{
                    fontSize: '10px',
                    color: 'var(--pm33-text-secondary)',
                    marginTop: '4px',
                    textTransform: 'capitalize'
                  }}>
                    {mapping.status}
                  </div>
                </div>
              </div>

              {/* AI Suggestion */}
              {mapping.aiSuggestion && (
                <div style={{
                  marginTop: '12px',
                  padding: '8px 12px',
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <Brain size={14} style={{ color: 'var(--pm33-success)' }} />
                  <span style={{ fontSize: '11px', color: 'var(--pm33-text-secondary)' }}>
                    AI: {mapping.aiSuggestion}
                  </span>
                </div>
              )}
            </PM33Card>
          ))}
        </div>

        {/* Continue Button */}
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '32px' }}>
          <button
            onClick={() => setSelectedIntegration(null)}
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
            Back to Overview
          </button>
        </div>
      </div>
    );
  };

  return (
    <div style={{
      padding: '24px',
      maxWidth: '1400px',
      margin: '0 auto',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '32px'
      }}>
        <button
          onClick={selectedIntegration ? () => setSelectedIntegration(null) : onBack}
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
          {selectedIntegration ? 'Back to Overview' : 'Back to Dashboard'}
        </button>
      </div>

      {selectedIntegration ? renderDetailedMapping() : renderIntegrationOverview()}
    </div>
  );
};