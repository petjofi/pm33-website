"use client";

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, Target, Settings, Upload, FileText, BarChart3, 
  Brain, ChevronRight, X, ArrowRight, Zap, ExternalLink,
  Lightbulb, Clock, Users, TrendingUp, Bot, Activity, Database, MessageSquare
} from 'lucide-react';

interface OnboardingStep {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  status: 'pending' | 'active' | 'completed';
}

interface PM33OnboardingFlowProps {
  theme?: 'light' | 'dark';
  onComplete?: (data: OnboardingData) => void;
  onSkip?: () => void;
}

interface OnboardingData {
  companyInfo: {
    name: string;
    industry: string;
    size: string;
    url?: string;
    mission?: string;
    vision?: string;
  };
  strategicPreferences: {
    framework: 'ICE' | 'RICE' | 'Porter' | 'SWOT';
    priorities: string[];
    maturityLevel: 'beginner' | 'intermediate' | 'advanced';
  };
  integrationSetup: {
    primaryTool: 'jira' | 'linear' | 'monday' | 'asana';
    instanceUrl: string;
    timespan: string;
  };
  completedSteps: string[];
  startedAt: string;
}

export const PM33OnboardingFlow: React.FC<PM33OnboardingFlowProps> = ({
  theme = 'dark',
  onComplete,
  onSkip
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [onboardingData, setOnboardingData] = useState<Partial<OnboardingData>>({
    companyInfo: {},
    strategicPreferences: {},
    integrationSetup: {},
    completedSteps: [],
    startedAt: new Date().toISOString()
  });

  // Multi-source analysis state
  const [analysisState, setAnalysisState] = useState<{
    status: 'idle' | 'processing' | 'success' | 'error';
    sources: Array<{
      id: string;
      type: 'website' | 'document';
      name: string;
      url?: string;
      filename?: string;
      data: any;
      timestamp: string;
      status: 'processing' | 'success' | 'error';
    }>;
    mergedData: any;
    error?: string;
  }>({
    status: 'idle',
    sources: [],
    mergedData: null
  });

  // Strategic Foundation State (NEW)
  const [strategicFoundationState, setStrategicFoundationState] = useState<{
    status: 'idle' | 'extracting' | 'reviewing' | 'generating' | 'approved';
    extractedElements: {
      vision?: string;
      mission?: string;
      objectives: Array<{
        id: string;
        text: string;
        category: 'product' | 'market' | 'operations' | 'financial';
        confidence: number;
        source: 'document' | 'website';
        isSmartCompliant: boolean;
      }>;
      targetMarket?: string;
      valueProposition?: string;
      keyCapabilities: string[];
    };
    clientEdits: {
      vision?: string;
      mission?: string;
      objectives?: Array<{ id: string; text: string; category: string; }>;
      targetMarket?: string;
      valueProposition?: string;
    };
    manifesto?: string;
    approved: boolean;
    validationErrors: string[];
  }>({
    status: 'idle',
    extractedElements: { 
      objectives: [], 
      keyCapabilities: [] 
    },
    clientEdits: {},
    approved: false,
    validationErrors: []
  });

  // Legacy extraction state for compatibility
  const [extractionState, setExtractionState] = useState<{
    method: 'website' | 'document' | null;
    status: 'idle' | 'processing' | 'success' | 'error';
    data: any;
    error?: string;
  }>({
    method: null,
    status: 'idle',
    data: null
  });

  const [websiteUrl, setWebsiteUrl] = useState('');
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [documentUrl, setDocumentUrl] = useState('');
  
  // Import data state
  const [importFilters, setImportFilters] = useState({
    completed: true,
    cancelled: true,
    placeholders: true,
    orphaned: true
  });
  const [importStats, setImportStats] = useState({
    totalItems: 0,
    filteredItems: 0,
    actionableItems: 0,
    estimatedVelocity: '0/sprint'
  });

  // Initialize import stats on component mount
  useEffect(() => {
    // Since no connection has been made yet, show zeros
    setImportStats({
      totalItems: 0,
      filteredItems: 0,
      actionableItems: 0,
      estimatedVelocity: '0/sprint'
    });
  }, []);

  const steps: OnboardingStep[] = [
    {
      id: 'document_ingestion',
      title: 'Strategic Document Ingestion',
      subtitle: 'Multi-format support (PDF, DOCX, TXT, MD, PPT, XLSX)',
      icon: <Upload size={20} />,
      status: currentStep === 0 ? 'active' : completedSteps.includes(0) ? 'completed' : 'pending'
    },
    {
      id: 'ai_extraction',
      title: 'AI Strategic Extraction',
      subtitle: 'Vision, Mission, SMART objectives with confidence scoring',
      icon: <Brain size={20} />,
      status: currentStep === 1 ? 'active' : completedSteps.includes(1) ? 'completed' : 'pending'
    },
    {
      id: 'client_review',
      title: 'Client Review & Refinement',
      subtitle: 'Editable Vision/Mission with SMART objective validation',
      icon: <FileText size={20} />,
      status: currentStep === 2 ? 'active' : completedSteps.includes(2) ? 'completed' : 'pending'
    },
    {
      id: 'manifesto_generation',
      title: 'AI Strategic Manifesto Generation',
      subtitle: 'Professional document with executive formatting',
      icon: <Target size={20} />,
      status: currentStep === 3 ? 'active' : completedSteps.includes(3) ? 'completed' : 'pending'
    },
    {
      id: 'dna_integration',
      title: 'Strategic DNA Integration',
      subtitle: 'Vector database embedding with AI enhancement cards',
      icon: <Database size={20} />,
      status: currentStep === 4 ? 'active' : completedSteps.includes(4) ? 'completed' : 'pending'
    },
    {
      id: 'export_completion',
      title: 'Branded Document Export',
      subtitle: 'Executive PDF, Board Deck, Team Guide with celebration',
      icon: <ExternalLink size={20} />,
      status: currentStep === 5 ? 'active' : completedSteps.includes(5) ? 'completed' : 'pending'
    }
  ];

  const completeCurrentStep = () => {
    if (!completedSteps.includes(currentStep)) {
      setCompletedSteps([...completedSteps, currentStep]);
    }
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const goToStep = (stepIndex: number) => {
    setCurrentStep(stepIndex);
  };

  // Intelligent multi-source analysis merging
  const mergeAnalysisSources = (sources: any[]): any => {
    if (sources.length === 0) return null;
    if (sources.length === 1) return sources[0].data;

    // Merge company info with confidence-based selection
    const mergedCompanyInfo: any = {};
    const infoFields = ['name', 'industry', 'size', 'stage', 'mission', 'vision', 'revenue'];
    
    for (const field of infoFields) {
      const values = sources
        .filter(s => s.data?.companyInfo?.[field])
        .map(s => ({ value: s.data.companyInfo[field], source: s }));
      
      if (values.length > 0) {
        // Prefer document sources over website for detailed info like mission
        if (field === 'mission' || field === 'vision') {
          const docValue = values.find(v => v.source.type === 'document')?.value;
          mergedCompanyInfo[field] = docValue || values[0].value;
        } else {
          // For other fields, take the most detailed/complete value
          mergedCompanyInfo[field] = values.reduce((best, current) => 
            current.value.length > best.value.length ? current : best
          ).value;
        }
      }
    }

    // Merge and deduplicate strategic objectives
    const allObjectives = sources
      .filter(s => s.data?.derivedObjectives)
      .flatMap(s => s.data.derivedObjectives);
    
    const uniqueObjectives = Array.from(new Set(
      allObjectives.map(obj => obj.toLowerCase())
    )).map(obj => 
      allObjectives.find(original => original.toLowerCase() === obj) || obj
    ).slice(0, 5); // Limit to 5 top objectives

    return {
      companyInfo: mergedCompanyInfo,
      derivedObjectives: uniqueObjectives,
      sources: sources.map(s => ({
        type: s.type,
        name: s.name,
        timestamp: s.timestamp
      })),
      confidence: Math.min(0.95, sources.length * 0.3 + 0.5) // Higher confidence with more sources
    };
  };

  // Add new analysis source
  const addAnalysisSource = (type: 'website' | 'document', name: string, data: any, url?: string, filename?: string) => {
    const newSource = {
      id: Date.now().toString(),
      type,
      name,
      url,
      filename,
      data,
      timestamp: new Date().toISOString(),
      status: 'success' as const
    };

    setAnalysisState(prev => {
      const updatedSources = [...prev.sources, newSource];
      const mergedData = mergeAnalysisSources(updatedSources);
      
      return {
        ...prev,
        sources: updatedSources,
        mergedData,
        status: 'success'
      };
    });

    // Update onboarding data with merged analysis
    const mergedResult = mergeAnalysisSources([...analysisState.sources, newSource]);
    if (mergedResult) {
      setOnboardingData(prev => ({
        ...prev,
        companyInfo: {
          ...prev.companyInfo,
          ...mergedResult.companyInfo
        }
      }));
    }
  };

  // Get current display data (merged or legacy)
  const getCurrentDisplayData = () => {
    return analysisState.mergedData || extractionState.data;
  };

  // Remove analysis source
  const removeAnalysisSource = (sourceId: string) => {
    setAnalysisState(prev => {
      const updatedSources = prev.sources.filter(s => s.id !== sourceId);
      const mergedData = updatedSources.length > 0 ? mergeAnalysisSources(updatedSources) : null;
      
      return {
        ...prev,
        sources: updatedSources,
        mergedData,
        status: updatedSources.length > 0 ? 'success' : 'idle'
      };
    });

    // Update onboarding data
    const remainingSources = analysisState.sources.filter(s => s.id !== sourceId);
    const mergedResult = remainingSources.length > 0 ? mergeAnalysisSources(remainingSources) : null;
    
    if (mergedResult) {
      setOnboardingData(prev => ({
        ...prev,
        companyInfo: {
          ...prev.companyInfo,
          ...mergedResult.companyInfo
        }
      }));
    } else {
      // Clear company info if no sources remain
      setOnboardingData(prev => ({
        ...prev,
        companyInfo: {}
      }));
    }
  };

  // Enhanced strategic intelligence extraction from analysis results
  const extractStrategicIntelligence = (data: any, source: 'website' | 'document'): void => {
    setStrategicFoundationState(prev => ({
      ...prev,
      status: 'extracting'
    }));

    // Simulate enhanced AI extraction with SMART objective validation
    setTimeout(() => {
      const extractedObjectives = (data.derivedObjectives || []).map((objective: string, index: number) => ({
        id: `${source}-${Date.now()}-${index}`,
        text: objective,
        category: index % 4 === 0 ? 'product' : index % 4 === 1 ? 'market' : index % 4 === 2 ? 'operations' : 'financial',
        confidence: Math.random() * 0.3 + 0.7, // 70-100% confidence
        source,
        isSmartCompliant: objective.includes('by') && objective.length > 50 // Simple SMART check
      }));

      setStrategicFoundationState(prev => ({
        ...prev,
        status: 'reviewing',
        extractedElements: {
          ...prev.extractedElements,
          vision: data.companyInfo?.vision || prev.extractedElements.vision,
          mission: data.companyInfo?.mission || prev.extractedElements.mission,
          objectives: [...prev.extractedElements.objectives, ...extractedObjectives].slice(0, 5),
          targetMarket: data.companyInfo?.targetMarket || prev.extractedElements.targetMarket,
          valueProposition: data.companyInfo?.valueProposition || prev.extractedElements.valueProposition,
          keyCapabilities: [...prev.extractedElements.keyCapabilities, ...(data.companyInfo?.keyCapabilities || [])].slice(0, 10)
        }
      }));
    }, 1500);
  };

  // Handle website URL analysis with multi-source support
  const handleWebsiteAnalysis = async (url: string) => {
    if (!url.trim()) return;
    
    // Set processing state
    setAnalysisState(prev => ({ ...prev, status: 'processing' }));
    setExtractionState({ method: 'website', status: 'processing', data: null });
    
    try {
      // Normalize URL (add https if missing)
      const normalizedUrl = url.startsWith('http') ? url : `https://${url}`;
      
      const response = await fetch('/api/analyze-website', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: normalizedUrl })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        // Add to multi-source analysis
        addAnalysisSource('website', normalizedUrl, result, normalizedUrl);
        
        // Extract strategic intelligence (NEW)
        extractStrategicIntelligence(result, 'website');
        
        // Update legacy state for compatibility
        setExtractionState({ method: 'website', status: 'success', data: result });
        
        // Clear website URL input
        setWebsiteUrl('');
      } else {
        setAnalysisState(prev => ({ ...prev, status: 'error', error: result.error }));
        setExtractionState({ method: 'website', status: 'error', data: null, error: result.error });
      }
    } catch (error) {
      const errorMsg = 'Failed to analyze website';
      setAnalysisState(prev => ({ ...prev, status: 'error', error: errorMsg }));
      setExtractionState({ method: 'website', status: 'error', data: null, error: errorMsg });
    }
  };

  // Handle document upload and analysis with multi-source support
  const handleDocumentUpload = async (file: File) => {
    // Set processing state
    setAnalysisState(prev => ({ ...prev, status: 'processing' }));
    setExtractionState({ method: 'document', status: 'processing', data: null });
    
    try {
      const formData = new FormData();
      formData.append('document', file);
      
      const response = await fetch('/api/analyze-document', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok) {
        // Add to multi-source analysis
        addAnalysisSource('document', file.name, result, undefined, file.name);
        
        // Extract strategic intelligence from document (NEW)
        extractStrategicIntelligence(result, 'document');
        
        // Update legacy state for compatibility
        setExtractionState({ method: 'document', status: 'success', data: result });
        
        // Clear document file
        setDocumentFile(null);
      } else {
        setAnalysisState(prev => ({ ...prev, status: 'error', error: result.error }));
        setExtractionState({ method: 'document', status: 'error', data: null, error: result.error });
      }
    } catch (error) {
      const errorMsg = 'Failed to analyze document';
      setAnalysisState(prev => ({ ...prev, status: 'error', error: errorMsg }));
      setExtractionState({ method: 'document', status: 'error', data: null, error: errorMsg });
    }
  };

  // Handle document URL analysis
  const handleDocumentUrl = async (url: string) => {
    if (!url.trim()) return;
    
    setExtractionState({ method: 'document', status: 'processing', data: null });
    
    try {
      const response = await fetch('/api/analyze-document-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setExtractionState({ method: 'document', status: 'success', data: result });
        setOnboardingData(prev => ({
          ...prev,
          companyInfo: {
            ...prev.companyInfo,
            ...result.companyInfo
          }
        }));
      } else {
        setExtractionState({ method: 'document', status: 'error', data: null, error: result.error });
      }
    } catch (error) {
      setExtractionState({ method: 'document', status: 'error', data: null, error: 'Failed to analyze document URL' });
    }
  };

  const renderWelcomeStep = () => (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center',
      padding: '48px 32px',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '32px'
      }}>
        <Brain size={40} color="white" />
      </div>
      
      <h2 style={{
        fontSize: '2.25rem',
        fontWeight: '700',
        marginBottom: '1rem',
        fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        color: theme === 'dark' ? '#ffffff' : '#000000'
      }}>
        Welcome to PM33
      </h2>
      
      <p style={{
        fontSize: '18px',
        lineHeight: '1.6',
        marginBottom: '32px',
        color: theme === 'dark' ? '#94a3b8' : '#64748b',
        maxWidth: '500px'
      }}>
        Transform your Product Management workflow with AI-powered PMO capabilities. 
        Let's set up your strategic intelligence system in just 5 minutes.
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '16px',
        marginBottom: '40px',
        width: '100%',
        maxWidth: '400px'
      }}>
        <div style={{
          background: theme === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)' 
            : 'rgba(248, 250, 252, 0.8)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <Bot size={24} color={theme === 'dark' ? '#667eea' : '#4f46e5'} style={{ marginBottom: '8px' }} />
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
          }}>
            4 AI Teams
          </div>
        </div>
        
        <div style={{
          background: theme === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)' 
            : 'rgba(248, 250, 252, 0.8)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <Activity size={24} color={theme === 'dark' ? '#667eea' : '#4f46e5'} style={{ marginBottom: '8px' }} />
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
          }}>
            PMO Power
          </div>
        </div>
      </div>

      <button
        onClick={completeCurrentStep}
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          padding: '16px 32px',
          fontSize: '16px',
          fontWeight: '600',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'transform 0.2s ease'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        Start Setup <ArrowRight size={20} />
      </button>
    </div>
  );

  const renderStrategyStep = () => {
    return (
      <div style={{
        padding: '32px',
        fontFamily: 'Inter, system-ui, sans-serif'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '24px'
        }}>
          <Target size={24} color={theme === 'dark' ? '#667eea' : '#4f46e5'} style={{ marginRight: '12px' }} />
          <h3 style={{
            fontSize: '1.875rem',
            fontWeight: '600',
            margin: 0,
            fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Strategic Foundation System
          </h3>
        </div>

        <p style={{
          fontSize: '16px',
          lineHeight: '1.6',
          marginBottom: '32px',
          color: theme === 'dark' ? '#94a3b8' : '#64748b'
        }}>
          Follow our 6-step Universal Client Journey to transform your strategic documents into powerful Strategic DNA that drives all PM33 AI decisions.
        </p>

        {/* Universal Client Journey Steps Visual Progress */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(6, 1fr)',
          gap: '12px',
          marginBottom: '32px'
        }}>
          {[
            { step: 1, title: 'Document Ingestion', status: 'completed' },
            { step: 2, title: 'AI Extraction', status: 'completed' },
            { step: 3, title: 'Client Review', status: 'active' },
            { step: 4, title: 'Manifesto Generation', status: 'pending' },
            { step: 5, title: 'Strategic DNA', status: 'pending' },
            { step: 6, title: 'Export & Integration', status: 'pending' }
          ].map(({ step, title, status }) => (
            <div
              key={step}
              style={{
                background: status === 'completed' 
                  ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                  : status === 'active'
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(248, 250, 252, 0.8)',
                borderRadius: '12px',
                padding: '16px',
                border: status === 'active' 
                  ? '2px solid #667eea'
                  : theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(148, 163, 184, 0.2)',
                textAlign: 'center' as const,
                position: 'relative' as const
              }}
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: status === 'completed' 
                  ? '#10b981' 
                  : status === 'active'
                  ? '#667eea'
                  : theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(148, 163, 184, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 12px auto',
                color: status === 'completed' || status === 'active' ? 'white' : theme === 'dark' ? '#64748b' : '#94a3b8',
                fontSize: '14px',
                fontWeight: '700'
              }}>
                {step}
              </div>
              <h4 style={{
                fontSize: '12px',
                fontWeight: '600',
                margin: 0,
                color: status === 'completed' || status === 'active' 
                  ? 'white' 
                  : theme === 'dark' ? '#e2e8f0' : '#475569',
                lineHeight: '1.2'
              }}>
                {title}
              </h4>
            </div>
          ))}
        </div>

        {/* Step 1: Strategic Document Ingestion */}
        <div style={{
          background: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.9)',
          borderRadius: '12px',
          padding: '24px',
          border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(148, 163, 184, 0.2)',
          marginBottom: '24px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: '#10b981',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '12px',
              color: 'white',
              fontSize: '12px',
              fontWeight: '700'
            }}>
              1
            </div>
            <h4 style={{
              fontSize: '16px',
              fontWeight: '600',
              margin: 0,
              color: theme === 'dark' ? '#e2e8f0' : '#1e293b'
            }}>
              Strategic Document Ingestion
            </h4>
          </div>
          <p style={{
            fontSize: '14px',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            margin: 0,
            lineHeight: '1.5'
          }}>
            Multi-format support: PDF, DOCX, TXT, MD, PPT, XLSX • Strategic document type detection • Progress indicators for processing
          </p>
        </div>

        {/* Step 5: Strategic DNA Integration */}
        <div style={{
          background: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.9)',
          borderRadius: '12px',
          padding: '24px',
          border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(148, 163, 184, 0.2)',
          marginBottom: '24px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: '#667eea',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '12px',
              color: 'white',
              fontSize: '12px',
              fontWeight: '700'
            }}>
              5
            </div>
            <h4 style={{
              fontSize: '16px',
              fontWeight: '600',
              margin: 0,
              color: theme === 'dark' ? '#e2e8f0' : '#1e293b'
            }}>
              Strategic DNA Integration
            </h4>
          </div>
          <p style={{
            fontSize: '14px',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            margin: '0 0 16px 0',
            lineHeight: '1.5'
          }}>
            Your strategic foundation becomes the DNA for all AI operations:
          </p>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '12px'
          }}>
            {[
              { feature: 'Enhanced Strategic Intelligence', description: 'AI decisions aligned with your vision' },
              { feature: 'Context-Aware Workflows', description: 'Automatic strategic objective integration' },
              { feature: 'Competitive Positioning', description: 'AI recommendations based on your market position' },
              { feature: 'Resource Optimization', description: 'Budget and timeline decisions using your constraints' }
            ].map((item, index) => (
              <div key={index} style={{
                background: theme === 'dark' ? 'rgba(103, 126, 234, 0.1)' : 'rgba(103, 126, 234, 0.05)',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid rgba(103, 126, 234, 0.2)'
              }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#667eea',
                  marginBottom: '4px'
                }}>
                  {item.feature}
                </div>
                <div style={{
                  fontSize: '11px',
                  color: theme === 'dark' ? '#94a3b8' : '#64748b'
                }}>
                  {item.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step 6: Branded Document Export */}
        <div style={{
          background: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.9)',
          borderRadius: '12px',
          padding: '24px',
          border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(148, 163, 184, 0.2)',
          marginBottom: '32px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: '#10b981',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '12px',
              color: 'white',
              fontSize: '12px',
              fontWeight: '700'
            }}>
              6
            </div>
            <h4 style={{
              fontSize: '16px',
              fontWeight: '600',
              margin: 0,
              color: theme === 'dark' ? '#e2e8f0' : '#1e293b'
            }}>
              Branded Document Export
            </h4>
          </div>
          <p style={{
            fontSize: '14px',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            margin: '0 0 16px 0',
            lineHeight: '1.5'
          }}>
            Download professional strategic documents with your branding:
          </p>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '12px'
          }}>
            {[
              { type: 'Executive PDF', description: 'Professional strategic foundation document' },
              { type: 'Board Deck', description: 'Presentation-ready strategic overview' },
              { type: 'Team Guide', description: 'Operational strategic reference' }
            ].map((doc, index) => (
              <div key={index} style={{
                background: theme === 'dark' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.05)',
                borderRadius: '8px',
                padding: '16px',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                textAlign: 'center' as const,
                cursor: 'pointer',
                transition: 'transform 0.2s ease',
              }}>
                <div style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#10b981',
                  marginBottom: '8px'
                }}>
                  {doc.type}
                </div>
                <div style={{
                  fontSize: '11px',
                  color: theme === 'dark' ? '#94a3b8' : '#64748b'
                }}>
                  {doc.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <button
            onClick={() => setCurrentStep(0)}
            style={{
              background: 'transparent',
              color: theme === 'dark' ? '#94a3b8' : '#64748b',
              border: 'none',
              padding: '12px 24px',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            Back
          </button>
          
          <button
            onClick={completeCurrentStep}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            Extract & Continue <ChevronRight size={16} />
          </button>
        </div>
      </div>
    );
  };

  const renderIntegrationStep = () => {
    return (
      <div style={{
        padding: '32px',
        fontFamily: 'Inter, system-ui, sans-serif'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '24px'
        }}>
          <Database size={24} color={theme === 'dark' ? '#667eea' : '#4f46e5'} style={{ marginRight: '12px' }} />
          <h3 style={{
            fontSize: '1.875rem',
            fontWeight: '600',
            margin: 0,
            fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            color: theme === 'dark' ? '#ffffff' : '#000000'
          }}>
            Import Your Data
          </h3>
        </div>

        <p style={{
          fontSize: '16px',
          lineHeight: '1.6',
          marginBottom: '32px',
          color: theme === 'dark' ? '#94a3b8' : '#64748b'
        }}>
          Connect your PM tools with secure OAuth integration. Choose your primary platform:
        </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '16px',
        marginBottom: '32px'
      }}>
        {[
          { name: 'Jira', logo: '🔷', color: '#0052CC', features: ['Issues', 'Epics', 'Sprints'] },
          { name: 'Linear', logo: '⚡', color: '#5E6AD2', features: ['Issues', 'Projects', 'Cycles'] },
          { name: 'Monday', logo: '📋', color: '#FF3D57', features: ['Items', 'Boards', 'Timelines'] },
          { name: 'Asana', logo: '🎯', color: '#F06A6A', features: ['Tasks', 'Projects', 'Goals'] }
        ].map((tool) => (
          <div
            key={tool.name}
            style={{
              background: theme === 'dark' 
                ? 'rgba(255, 255, 255, 0.05)' 
                : 'rgba(248, 250, 252, 0.8)',
              borderRadius: '12px',
              padding: '24px',
              border: theme === 'dark' 
                ? '1px solid rgba(148, 163, 184, 0.15)' 
                : '1px solid rgba(148, 163, 184, 0.25)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'center'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = theme === 'dark' 
                ? '0 10px 25px rgba(0, 0, 0, 0.3)' 
                : '0 10px 25px rgba(0, 0, 0, 0.1)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{
              fontSize: '32px',
              marginBottom: '12px'
            }}>
              {tool.logo}
            </div>
            
            <h4 style={{
              fontSize: '18px',
              fontWeight: '600',
              margin: '0 0 8px 0',
              color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
            }}>
              {tool.name}
            </h4>
            
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '6px',
              marginBottom: '16px'
            }}>
              {tool.features.map((feature) => (
                <span
                  key={feature}
                  style={{
                    fontSize: '12px',
                    padding: '4px 8px',
                    background: theme === 'dark' 
                      ? 'rgba(255, 255, 255, 0.1)' 
                      : 'rgba(248, 250, 252, 0.9)',
                    borderRadius: '12px',
                    color: theme === 'dark' ? '#94a3b8' : '#64748b'
                  }}
                >
                  {feature}
                </span>
              ))}
            </div>

            <button 
              onClick={async () => {
                if (tool.name === 'Jira') {
                  const instanceUrl = prompt('Enter your Jira instance URL:\n(e.g., https://your-company.atlassian.net)', 'https://your-company.atlassian.net');
                  if (!instanceUrl) return;
                  
                  try {
                    // Try real OAuth first
                    const response = await fetch('/api/integrations/jira/connect', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ 
                        action: 'initiate',
                        instanceUrl: instanceUrl
                      })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success && result.authUrl) {
                      // Real OAuth available
                      const proceed = confirm(`🔗 Real Jira OAuth Available!\n\n${result.message}\n\nClick OK to be redirected to Atlassian for authorization.\nClick Cancel to use demo mode instead.`);
                      
                      if (proceed) {
                        window.open(result.authUrl, '_blank');
                        alert('Complete authorization in the popup window, then return here and click "Test Connection" to continue.');
                        return;
                      }
                    } else {
                      // OAuth not configured, show error and offer demo
                      alert(`❌ Real Jira OAuth Not Available\n\n${result.error}\n\n${result.message}\n\nDocumentation: ${result.documentation}\n\nFalling back to demo mode...`);
                    }
                    
                    // Fallback to demo mode
                    const demoResponse = await fetch('/api/integrations/jira/connect', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ 
                        action: 'simulate',
                        instanceUrl: instanceUrl,
                        email: 'demo@company.com'
                      })
                    });
                    
                    if (demoResponse.ok) {
                      const demoResult = await demoResponse.json();
                      if (demoResult.success) {
                        alert(`🎯 Demo Jira Connection Established!\n\n✅ Connected to: ${demoResult.connection.instanceUrl}\n✅ User: ${demoResult.connection.displayName} (${demoResult.connection.email})\n✅ Projects: ${demoResult.stats.totalProjects}\n✅ Issues available: ${demoResult.stats.totalIssues}\n\n${demoResult.message}`);
                        
                        setImportStats({
                          totalItems: demoResult.stats.totalIssues,
                          filteredItems: Math.floor(demoResult.stats.totalIssues * 0.75),
                          actionableItems: Math.floor(demoResult.stats.totalIssues * 0.6),
                          estimatedVelocity: `${Math.ceil(demoResult.stats.totalIssues / 40)}/sprint`
                        });
                        return;
                      }
                    }
                    
                  } catch (error) {
                    alert(`❌ Jira connection failed: ${error.message}`);
                  }
                } else {
                  alert(`🔧 ${tool.name} OAuth integration coming soon!\n\nThis will connect to your ${tool.name} instance and import:\n${tool.features.map(f => `• ${f}`).join('\n')}`);
                }
              }}
              style={{
                background: tool.color,
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                width: '100%'
              }}
            >
              Connect via OAuth
            </button>
          </div>
        ))}
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <button
          onClick={() => setCurrentStep(1)}
          style={{
            background: 'transparent',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            border: 'none',
            padding: '12px 24px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          Back
        </button>
        
        <button
          onClick={completeCurrentStep}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          Import Data <ChevronRight size={16} />
        </button>
      </div>
    </div>
    );
  };

  const renderBacklogStep = () => {
    return (
      <div style={{
        padding: '32px',
        fontFamily: 'Inter, system-ui, sans-serif'
      }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <BarChart3 size={24} color={theme === 'dark' ? '#667eea' : '#4f46e5'} style={{ marginRight: '12px' }} />
        <h3 style={{
          fontSize: '1.875rem',
          fontWeight: '600',
          margin: 0,
          fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          color: theme === 'dark' ? '#ffffff' : '#000000'
        }}>
          Organize Your Backlog
        </h3>
      </div>

      <p style={{
        fontSize: '16px',
        lineHeight: '1.6',
        marginBottom: '32px',
        color: theme === 'dark' ? '#94a3b8' : '#64748b'
      }}>
        Smart filtering to focus on actionable items. Configure your data import preferences:
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 300px',
        gap: '24px',
        marginBottom: '32px'
      }}>
        <div>
          <h4 style={{
            fontSize: '18px',
            fontWeight: '600',
            marginBottom: '16px',
            color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
          }}>
            Import Timeframe
          </h4>
          
          <div style={{
            background: theme === 'dark' 
              ? 'rgba(255, 255, 255, 0.05)' 
              : 'rgba(248, 250, 252, 0.8)',
            borderRadius: '12px',
            padding: '20px',
            border: theme === 'dark' 
              ? '1px solid rgba(148, 163, 184, 0.15)' 
              : '1px solid rgba(148, 163, 184, 0.25)',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: theme === 'dark' ? '#94a3b8' : '#64748b',
                  marginBottom: '8px',
                  display: 'block'
                }}>
                  From Date
                </label>
                <input
                  type="date"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: theme === 'dark' 
                      ? '1px solid rgba(148, 163, 184, 0.2)' 
                      : '1px solid rgba(148, 163, 184, 0.3)',
                    borderRadius: '6px',
                    background: theme === 'dark' 
                      ? 'rgba(15, 23, 42, 0.8)' 
                      : 'rgba(255, 255, 255, 0.9)',
                    color: theme === 'dark' ? '#f1f5f9' : '#1e293b',
                    fontSize: '14px'
                  }}
                />
              </div>
              
              <div>
                <label style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: theme === 'dark' ? '#94a3b8' : '#64748b',
                  marginBottom: '8px',
                  display: 'block'
                }}>
                  To Date
                </label>
                <input
                  type="date"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: theme === 'dark' 
                      ? '1px solid rgba(148, 163, 184, 0.2)' 
                      : '1px solid rgba(148, 163, 184, 0.3)',
                    borderRadius: '6px',
                    background: theme === 'dark' 
                      ? 'rgba(15, 23, 42, 0.8)' 
                      : 'rgba(255, 255, 255, 0.9)',
                    color: theme === 'dark' ? '#f1f5f9' : '#1e293b',
                    fontSize: '14px'
                  }}
                />
              </div>
            </div>
          </div>

          <h4 style={{
            fontSize: '18px',
            fontWeight: '600',
            marginBottom: '16px',
            color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
          }}>
            Exclusion Filters
          </h4>
          
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            {[
              { id: 'completed', label: 'Exclude completed items', description: 'Remove done/closed work items' },
              { id: 'cancelled', label: 'Exclude cancelled items', description: 'Remove abandoned/cancelled work' },
              { id: 'placeholders', label: 'Exclude placeholder items', description: 'Remove items without descriptions' },
              { id: 'orphaned', label: 'Exclude orphaned items', description: 'Remove unassigned/unlinked work items' }
            ].map((filter) => (
              <label
                key={filter.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  background: theme === 'dark' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : 'rgba(248, 250, 252, 0.8)',
                  borderRadius: '8px',
                  padding: '16px',
                  cursor: 'pointer',
                  border: theme === 'dark' 
                    ? '1px solid rgba(148, 163, 184, 0.15)' 
                    : '1px solid rgba(148, 163, 184, 0.25)'
                }}
              >
                <input
                  type="checkbox"
                  checked={importFilters[filter.id as keyof typeof importFilters]}
                  onChange={(e) => {
                    const newFilters = { ...importFilters, [filter.id]: e.target.checked };
                    setImportFilters(newFilters);
                    
                    // Calculate dynamic stats based on filters
                    const baseItems = 1247; // Simulated total from PM tools
                    let filtered = baseItems;
                    
                    if (newFilters.completed) filtered -= 423;
                    if (newFilters.cancelled) filtered -= 67;
                    if (newFilters.placeholders) filtered -= 156;
                    if (newFilters.orphaned) filtered -= 318;
                    
                    const actionable = Math.max(0, filtered);
                    const velocity = Math.ceil(actionable / 8); // Assuming 8 sprints
                    
                    setImportStats({
                      totalItems: baseItems,
                      filteredItems: filtered > 0 ? filtered : 0,
                      actionableItems: actionable,
                      estimatedVelocity: `${velocity}/sprint`
                    });
                  }}
                  style={{
                    marginRight: '12px',
                    marginTop: '2px',
                    accentColor: '#667eea'
                  }}
                />
                <div>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: theme === 'dark' ? '#f1f5f9' : '#1e293b',
                    marginBottom: '4px'
                  }}>
                    {filter.label}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: theme === 'dark' ? '#94a3b8' : '#64748b'
                  }}>
                    {filter.description}
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h4 style={{
            fontSize: '18px',
            fontWeight: '600',
            marginBottom: '8px',
            color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
          }}>
            Import Preview
          </h4>
          
          <p style={{
            fontSize: '12px',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            marginBottom: '16px',
            fontStyle: 'italic'
          }}>
            {importStats.totalItems === 0 ? 
              'Connect a data source above to see import statistics' : 
              'Live preview of your filtered data'
            }
          </p>
          
          <div style={{
            background: theme === 'dark' 
              ? 'rgba(255, 255, 255, 0.05)' 
              : 'rgba(248, 250, 252, 0.8)',
            borderRadius: '12px',
            padding: '20px',
            border: theme === 'dark' 
              ? '1px solid rgba(148, 163, 184, 0.15)' 
              : '1px solid rgba(148, 163, 184, 0.25)'
          }}>
            {[
              { label: 'Total Items Found', value: importStats.totalItems.toLocaleString(), color: '#64748b' },
              { label: 'After Filtering', value: importStats.filteredItems.toLocaleString(), color: '#667eea' },
              { label: 'Actionable Items', value: importStats.actionableItems.toLocaleString(), color: '#10b981' },
              { label: 'Estimated Velocity', value: importStats.estimatedVelocity, color: '#f59e0b' }
            ].map((stat) => (
              <div
                key={stat.label}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 0',
                  borderBottom: theme === 'dark' 
                    ? '1px solid rgba(148, 163, 184, 0.1)' 
                    : '1px solid rgba(148, 163, 184, 0.2)'
                }}
              >
                <span style={{
                  fontSize: '14px',
                  color: theme === 'dark' ? '#94a3b8' : '#64748b'
                }}>
                  {stat.label}
                </span>
                <span style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: stat.color
                }}>
                  {stat.value}
                </span>
              </div>
            ))}
            
            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: theme === 'dark' 
                ? 'rgba(16, 185, 129, 0.1)' 
                : 'rgba(16, 185, 129, 0.1)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center'
            }}>
              <CheckCircle size={16} color="#10b981" style={{ marginRight: '8px' }} />
              <span style={{
                fontSize: '12px',
                color: '#10b981',
                fontWeight: '500'
              }}>
                Ready for PMO Analysis
              </span>
            </div>
          </div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <button
          onClick={() => setCurrentStep(2)}
          style={{
            background: 'transparent',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            border: 'none',
            padding: '12px 24px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          Back
        </button>
        
        <button
          onClick={completeCurrentStep}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          Process Backlog <ChevronRight size={16} />
        </button>
      </div>
    </div>
    );
  };

  const renderActivationStep = () => {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        padding: '48px 32px',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '32px'
      }}>
        <Zap size={40} color="white" />
      </div>
      
      <h2 style={{
        fontSize: '2.25rem',
        fontWeight: '700',
        marginBottom: '1rem',
        fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        color: theme === 'dark' ? '#ffffff' : '#000000'
      }}>
        PMO Ready!
      </h2>
      
      <p style={{
        fontSize: '18px',
        lineHeight: '1.6',
        marginBottom: '32px',
        color: theme === 'dark' ? '#94a3b8' : '#64748b',
        maxWidth: '500px'
      }}>
        Your PM33 AI teams are configured and ready to transform your workflow. 
        Let's launch your PMO capabilities!
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '16px',
        marginBottom: '40px',
        width: '100%',
        maxWidth: '500px'
      }}>
        {[
          { name: 'Strategic Intelligence', icon: <Brain size={20} />, status: 'Ready' },
          { name: 'Workflow Execution', icon: <Settings size={20} />, status: 'Ready' },
          { name: 'Data Intelligence', icon: <BarChart3 size={20} />, status: 'Ready' },
          { name: 'Communication Hub', icon: <MessageSquare size={20} />, status: 'Ready' }
        ].map((team) => (
          <div
            key={team.name}
            style={{
              background: theme === 'dark' 
                ? 'rgba(255, 255, 255, 0.05)' 
                : 'rgba(248, 250, 252, 0.8)',
              borderRadius: '8px',
              padding: '16px 12px',
              textAlign: 'center'
            }}
          >
            <div style={{
              color: theme === 'dark' ? '#10b981' : '#059669',
              marginBottom: '8px'
            }}>
              {team.icon}
            </div>
            <div style={{
              fontSize: '12px',
              fontWeight: '600',
              color: theme === 'dark' ? '#f1f5f9' : '#1e293b',
              marginBottom: '4px'
            }}>
              {team.name}
            </div>
            <div style={{
              fontSize: '10px',
              color: '#10b981',
              fontWeight: '500'
            }}>
              {team.status}
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={() => onComplete?.(onboardingData as OnboardingData)}
        style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          padding: '16px 32px',
          fontSize: '16px',
          fontWeight: '600',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'transform 0.2s ease'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        Launch PMO Dashboard <ArrowRight size={20} />
      </button>
    </div>
    );
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: return renderWelcomeStep();
      case 1: return renderStrategyStep();
      case 2: return renderIntegrationStep();
      case 3: return renderBacklogStep();
      case 4: return renderActivationStep();
      default: return renderWelcomeStep();
    }
  };

  return (
    <>
      {/* Add keyframe animation for loading spinner */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `
      }} />
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: '320px 1fr',
        minHeight: '600px',
        borderRadius: '12px',
        overflow: 'hidden',
        fontFamily: 'Inter, system-ui, sans-serif'
      }}>
        {/* Left Navigation Panel */}
      <div style={{
        background: theme === 'dark' 
          ? 'linear-gradient(180deg, rgba(15, 23, 42, 0.4) 0%, rgba(30, 41, 59, 0.4) 100%)'
          : 'linear-gradient(180deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%)',
        borderRight: theme === 'dark' 
          ? '1px solid rgba(148, 163, 184, 0.15)' 
          : '1px solid rgba(148, 163, 184, 0.25)',
        padding: '32px 24px'
      }}>
        {/* Navigation Steps */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}>
          {steps.map((step, index) => (
            <button
              key={step.id}
              onClick={() => goToStep(index)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '16px',
                background: step.status === 'active' 
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : step.status === 'completed'
                  ? theme === 'dark' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.1)'
                  : 'transparent',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                width: '100%',
                transition: 'all 0.2s ease',
                color: step.status === 'active' 
                  ? 'white'
                  : step.status === 'completed'
                  ? theme === 'dark' ? '#10b981' : '#059669'
                  : theme === 'dark' ? '#94a3b8' : '#64748b'
              }}
              onMouseOver={(e) => {
                if (step.status !== 'active') {
                  e.currentTarget.style.background = theme === 'dark' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : 'rgba(248, 250, 252, 0.8)';
                }
              }}
              onMouseOut={(e) => {
                if (step.status !== 'active') {
                  e.currentTarget.style.background = step.status === 'completed'
                    ? theme === 'dark' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.1)'
                    : 'transparent';
                }
              }}
            >
              <div style={{
                marginRight: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {step.status === 'completed' ? (
                  <CheckCircle size={20} color="#10b981" />
                ) : (
                  step.icon
                )}
              </div>
              
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  marginBottom: '2px'
                }}>
                  {step.title}
                </div>
                <div style={{
                  fontSize: '12px',
                  opacity: 0.8
                }}>
                  {step.subtitle}
                </div>
              </div>
              
              {step.status === 'active' && (
                <ChevronRight size={16} />
              )}
            </button>
          ))}
        </div>

        {/* Progress Indicator */}
        <div style={{
          marginTop: '32px',
          padding: '16px',
          background: theme === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)' 
            : 'rgba(248, 250, 252, 0.8)',
          borderRadius: '8px'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            marginBottom: '8px'
          }}>
            Setup Progress
          </div>
          
          <div style={{
            width: '100%',
            height: '6px',
            background: theme === 'dark' 
              ? 'rgba(148, 163, 184, 0.2)' 
              : 'rgba(148, 163, 184, 0.3)',
            borderRadius: '3px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${(completedSteps.length / steps.length) * 100}%`,
              height: '100%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              transition: 'width 0.3s ease'
            }} />
          </div>
          
          <div style={{
            fontSize: '11px',
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
            marginTop: '8px'
          }}>
            {completedSteps.length} of {steps.length} completed
          </div>
        </div>
      </div>

      {/* Right Content Panel */}
      <div style={{
        background: theme === 'dark' 
          ? 'linear-gradient(180deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.3) 100%)'
          : 'linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
        minHeight: '600px',
        overflow: 'auto'
      }}>
        {renderStepContent()}
      </div>
    </div>
    </>
  );
};