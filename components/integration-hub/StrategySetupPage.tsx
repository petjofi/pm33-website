/**
 * Component: StrategySetupPage
 * Purpose: Company intelligence processing and strategic context generation
 * Design: PM33 glass morphism with AI-powered analysis workflow
 * Backend: Integration Hub API - Strategy endpoints
 */

'use client';

import React, { useState, useEffect } from 'react';
import { PM33Card } from '../PM33Card';
import { ArrowLeft, Brain, FileText, Target, Zap, Upload, CheckCircle } from 'lucide-react';

interface StrategySetupPageProps {
  onBack: () => void;
}

interface CompanyAnalysis {
  industry: string;
  size: string;
  maturity: string;
  challenges: string[];
  opportunities: string[];
  strategicGoals: string[];
}

interface DocumentProcessingStatus {
  total: number;
  processed: number;
  status: 'idle' | 'processing' | 'complete' | 'error';
  files: Array<{
    name: string;
    status: 'pending' | 'processing' | 'complete' | 'error';
    insights?: string[];
  }>;
}

export const StrategySetupPage = ({ onBack }: StrategySetupPageProps) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [companyAnalysis, setCompanyAnalysis] = useState<CompanyAnalysis | null>(null);
  const [documentProcessing, setDocumentProcessing] = useState<DocumentProcessingStatus>({
    total: 0,
    processed: 0,
    status: 'idle',
    files: []
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  // Simulate company intelligence processing
  const analyzeCompanyContext = async () => {
    setIsAnalyzing(true);
    
    try {
      // Call Integration Hub backend for company analysis
      const response = await fetch('/api/integration-hub/strategy/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          documents: uploadedFiles.map(f => ({ name: f.name, size: f.size })),
          context: 'initial_setup'
        })
      });
      
      const result = await response.json();
      
      // Simulate processing with realistic AI analysis
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setCompanyAnalysis({
        industry: 'Technology/SaaS',
        size: 'Mid-Market (100-500 employees)',
        maturity: 'Growth Stage',
        challenges: [
          'Cross-functional alignment across multiple teams',
          'Scaling product development processes',
          'Data-driven decision making gaps',
          'Strategic planning execution visibility'
        ],
        opportunities: [
          'AI-powered workflow automation',
          'Enhanced PMO capabilities',
          'Predictive analytics for planning',
          'Integrated tool ecosystem optimization'
        ],
        strategicGoals: [
          'Reduce planning cycle time by 40%',
          'Improve cross-team visibility',
          'Implement data-driven prioritization',
          'Scale PM processes for growth'
        ]
      });
      
      setCurrentStep(3);
    } catch (error) {
      console.error('Company analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Document upload handler
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
    
    // Update document processing status
    setDocumentProcessing(prev => ({
      ...prev,
      total: prev.total + files.length,
      files: [...prev.files, ...files.map(f => ({ name: f.name, status: 'pending' as const }))]
    }));
  };

  // Process uploaded documents
  const processDocuments = async () => {
    setDocumentProcessing(prev => ({ ...prev, status: 'processing' }));
    
    // Simulate document processing
    for (let i = 0; i < documentProcessing.files.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setDocumentProcessing(prev => ({
        ...prev,
        processed: i + 1,
        files: prev.files.map((file, idx) => 
          idx === i ? {
            ...file,
            status: 'complete',
            insights: [
              'Strategic objectives identified',
              'Key performance metrics extracted',
              'Stakeholder mapping completed'
            ]
          } : file
        )
      }));
    }
    
    setDocumentProcessing(prev => ({ ...prev, status: 'complete' }));
    setCurrentStep(2);
  };

  const renderDocumentUpload = () => (
    <PM33Card style={{ textAlign: 'center' }}>
      <div style={{ marginBottom: '32px' }}>
        <FileText size={48} style={{ color: 'var(--pm33-accent)', margin: '0 auto 16px' }} />
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          margin: '0 0 16px 0',
          background: 'var(--pm33-brand-gradient)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Document Intelligence
        </h2>
        <p style={{
          fontSize: '16px',
          color: 'var(--pm33-text-secondary)',
          margin: '0 0 32px 0'
        }}>
          Upload strategy documents, roadmaps, and planning materials for AI analysis
        </p>
      </div>

      <div style={{
        border: '2px dashed var(--pm33-glass-border)',
        borderRadius: '12px',
        padding: '48px 24px',
        marginBottom: '24px',
        background: 'var(--pm33-glass-bg)',
        transition: 'all 0.3s ease'
      }}>
        <Upload size={32} style={{ color: 'var(--pm33-text-secondary)', margin: '0 auto 16px' }} />
        <input
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.md"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          id="document-upload"
        />
        <label
          htmlFor="document-upload"
          style={{
            display: 'inline-block',
            padding: '12px 24px',
            background: 'var(--pm33-brand-gradient)',
            color: 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            border: 'none'
          }}
        >
          Select Documents
        </label>
        <p style={{
          fontSize: '12px',
          color: 'var(--pm33-text-secondary)',
          marginTop: '12px'
        }}>
          PDF, Word, Text, Markdown files accepted
        </p>
      </div>

      {uploadedFiles.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ margin: '0 0 16px 0', color: 'var(--pm33-text-primary)' }}>
            Uploaded Files ({uploadedFiles.length})
          </h4>
          <div style={{ display: 'grid', gap: '8px' }}>
            {uploadedFiles.map((file, idx) => (
              <div key={idx} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '8px 12px',
                background: 'var(--pm33-glass-bg)',
                borderRadius: '6px',
                fontSize: '14px'
              }}>
                <FileText size={16} />
                <span style={{ flex: 1, color: 'var(--pm33-text-primary)' }}>{file.name}</span>
                <span style={{ color: 'var(--pm33-text-secondary)', fontSize: '12px' }}>
                  {Math.round(file.size / 1024)}KB
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {uploadedFiles.length > 0 && documentProcessing.status === 'idle' && (
        <button
          onClick={processDocuments}
          style={{
            padding: '12px 24px',
            background: 'var(--pm33-success)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Process Documents
        </button>
      )}
    </PM33Card>
  );

  const renderDocumentProcessing = () => (
    <PM33Card style={{ textAlign: 'center' }}>
      <div style={{ marginBottom: '32px' }}>
        <Brain size={48} style={{ color: 'var(--pm33-accent)', margin: '0 auto 16px' }} />
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          margin: '0 0 16px 0',
          background: 'var(--pm33-brand-gradient)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          AI Document Analysis
        </h2>
        <p style={{
          fontSize: '16px',
          color: 'var(--pm33-text-secondary)',
          margin: '0 0 32px 0'
        }}>
          Processing {documentProcessing.total} documents with strategic intelligence AI
        </p>
      </div>

      <div style={{
        background: 'var(--pm33-glass-bg)',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <span style={{ color: 'var(--pm33-text-primary)', fontWeight: '600' }}>
            Processing Progress
          </span>
          <span style={{ color: 'var(--pm33-text-secondary)', fontSize: '14px' }}>
            {documentProcessing.processed} / {documentProcessing.total}
          </span>
        </div>
        
        <div style={{
          width: '100%',
          height: '8px',
          background: 'var(--pm33-glass-border)',
          borderRadius: '4px',
          overflow: 'hidden',
          marginBottom: '24px'
        }}>
          <div style={{
            width: `${(documentProcessing.processed / documentProcessing.total) * 100}%`,
            height: '100%',
            background: 'var(--pm33-brand-gradient)',
            transition: 'width 0.5s ease'
          }} />
        </div>

        <div style={{ display: 'grid', gap: '8px' }}>
          {documentProcessing.files.map((file, idx) => (
            <div key={idx} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 12px',
              background: file.status === 'complete' ? 'rgba(16, 185, 129, 0.1)' : 'var(--pm33-glass-bg)',
              borderRadius: '6px',
              fontSize: '14px'
            }}>
              {file.status === 'complete' ? 
                <CheckCircle size={16} style={{ color: 'var(--pm33-success)' }} /> :
                <FileText size={16} style={{ color: 'var(--pm33-text-secondary)' }} />
              }
              <span style={{ flex: 1, color: 'var(--pm33-text-primary)' }}>{file.name}</span>
              <span style={{
                color: file.status === 'complete' ? 'var(--pm33-success)' : 'var(--pm33-text-secondary)',
                fontSize: '12px',
                textTransform: 'capitalize'
              }}>
                {file.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {documentProcessing.status === 'complete' && (
        <button
          onClick={analyzeCompanyContext}
          style={{
            padding: '12px 24px',
            background: 'var(--pm33-brand-gradient)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Generate Company Analysis
        </button>
      )}
    </PM33Card>
  );

  const renderCompanyAnalysis = () => (
    <div style={{ display: 'grid', gap: '24px' }}>
      <PM33Card>
        <div style={{ marginBottom: '24px' }}>
          <Target size={32} style={{ color: 'var(--pm33-accent)', marginBottom: '16px' }} />
          <h3 style={{
            fontSize: '20px',
            fontWeight: '700',
            margin: '0 0 16px 0',
            background: 'var(--pm33-brand-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Company Profile
          </h3>
        </div>
        
        <div style={{ display: 'grid', gap: '16px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px'
          }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Industry
              </label>
              <p style={{ margin: '4px 0 0 0', color: 'var(--pm33-text-primary)', fontWeight: '600' }}>
                {companyAnalysis?.industry}
              </p>
            </div>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Size
              </label>
              <p style={{ margin: '4px 0 0 0', color: 'var(--pm33-text-primary)', fontWeight: '600' }}>
                {companyAnalysis?.size}
              </p>
            </div>
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--pm33-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Maturity Stage
            </label>
            <p style={{ margin: '4px 0 0 0', color: 'var(--pm33-text-primary)', fontWeight: '600' }}>
              {companyAnalysis?.maturity}
            </p>
          </div>
        </div>
      </PM33Card>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <PM33Card>
          <h4 style={{
            fontSize: '16px',
            fontWeight: '700',
            margin: '0 0 16px 0',
            color: 'var(--pm33-warning)'
          }}>
            Key Challenges
          </h4>
          <div style={{ display: 'grid', gap: '8px' }}>
            {companyAnalysis?.challenges.map((challenge, idx) => (
              <div key={idx} style={{
                padding: '8px 12px',
                background: 'rgba(251, 191, 36, 0.1)',
                borderRadius: '6px',
                fontSize: '14px',
                color: 'var(--pm33-text-primary)'
              }}>
                {challenge}
              </div>
            ))}
          </div>
        </PM33Card>

        <PM33Card>
          <h4 style={{
            fontSize: '16px',
            fontWeight: '700',
            margin: '0 0 16px 0',
            color: 'var(--pm33-success)'
          }}>
            Opportunities
          </h4>
          <div style={{ display: 'grid', gap: '8px' }}>
            {companyAnalysis?.opportunities.map((opportunity, idx) => (
              <div key={idx} style={{
                padding: '8px 12px',
                background: 'rgba(16, 185, 129, 0.1)',
                borderRadius: '6px',
                fontSize: '14px',
                color: 'var(--pm33-text-primary)'
              }}>
                {opportunity}
              </div>
            ))}
          </div>
        </PM33Card>
      </div>

      <PM33Card>
        <div style={{ marginBottom: '16px' }}>
          <Zap size={24} style={{ color: 'var(--pm33-accent)', display: 'inline', marginRight: '8px' }} />
          <h4 style={{
            fontSize: '16px',
            fontWeight: '700',
            margin: '0',
            display: 'inline',
            background: 'var(--pm33-brand-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Strategic Goals
          </h4>
        </div>
        <div style={{ display: 'grid', gap: '8px' }}>
          {companyAnalysis?.strategicGoals.map((goal, idx) => (
            <div key={idx} style={{
              padding: '12px 16px',
              background: 'var(--pm33-glass-bg)',
              borderRadius: '8px',
              fontSize: '14px',
              color: 'var(--pm33-text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <CheckCircle size={16} style={{ color: 'var(--pm33-success)' }} />
              {goal}
            </div>
          ))}
        </div>
      </PM33Card>

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '24px' }}>
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
          Continue to Integrations
        </button>
      </div>
    </div>
  );

  return (
    <div style={{
      padding: '24px',
      maxWidth: '1200px',
      margin: '0 auto',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
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
          Strategy Setup
        </h1>
        <p style={{
          fontSize: '18px',
          color: 'var(--pm33-text-secondary)',
          margin: '0'
        }}>
          Company intelligence processing and strategic context generation
        </p>
      </div>

      {/* Progress Indicator */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '48px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          {[
            { step: 1, label: 'Upload', active: currentStep >= 1 },
            { step: 2, label: 'Process', active: currentStep >= 2 },
            { step: 3, label: 'Analyze', active: currentStep >= 3 }
          ].map(({ step, label, active }, idx, arr) => (
            <React.Fragment key={step}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: active ? 'var(--pm33-brand-gradient)' : 'var(--pm33-glass-border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: active ? 'white' : 'var(--pm33-text-secondary)',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {step}
                </div>
                <span style={{
                  fontSize: '12px',
                  color: active ? 'var(--pm33-text-primary)' : 'var(--pm33-text-secondary)',
                  fontWeight: active ? '600' : '400'
                }}>
                  {label}
                </span>
              </div>
              {idx < arr.length - 1 && (
                <div style={{
                  width: '48px',
                  height: '2px',
                  background: currentStep > step ? 'var(--pm33-brand-gradient)' : 'var(--pm33-glass-border)',
                  marginBottom: '24px'
                }} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step Content */}
      {currentStep === 1 && renderDocumentUpload()}
      {currentStep === 2 && renderDocumentProcessing()}
      {currentStep === 3 && companyAnalysis && renderCompanyAnalysis()}

      {/* Loading State for Analysis */}
      {isAnalyzing && (
        <PM33Card style={{ textAlign: 'center' }}>
          <Brain size={48} style={{ 
            color: 'var(--pm33-accent)', 
            margin: '0 auto 16px',
            animation: 'pulse 2s infinite'
          }} />
          <h3 style={{
            fontSize: '20px',
            fontWeight: '700',
            margin: '0 0 16px 0',
            background: 'var(--pm33-brand-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Generating Strategic Analysis
          </h3>
          <p style={{
            fontSize: '16px',
            color: 'var(--pm33-text-secondary)',
            margin: '0'
          }}>
            AI teams are processing your company context and generating strategic insights...
          </p>
        </PM33Card>
      )}
    </div>
  );
};