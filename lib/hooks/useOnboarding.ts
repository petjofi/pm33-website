/**
 * PM33 Onboarding State Management Hook
 * Manages onboarding flow state with persistence and progress tracking
 */

import { useState, useEffect, useCallback } from 'react';

export interface OnboardingData {
  // Company Information
  companyInfo: {
    name: string;
    industry: string;
    size: string;
    website?: string;
    mission?: string;
    vision?: string;
  };
  
  // Strategic Preferences
  strategicPreferences: {
    framework: 'ICE' | 'RICE' | 'Porter' | 'SWOT';
    priorities: string[];
    maturityLevel: 'beginner' | 'intermediate' | 'advanced';
  };
  
  // Integration Setup
  integrationSetup: {
    primaryTool: 'jira' | 'linear' | 'monday' | 'asana';
    instanceUrl: string;
    credentials?: {
      token?: string;
      username?: string;
      apiKey?: string;
    };
    timespan: '1-month' | '3-months' | '6-months' | '12-months' | 'all-time';
    selectedFields?: string[];
  };
  
  // Progress Tracking
  progress: {
    completedSteps: string[];
    currentStep: number;
    startedAt: string;
    completedAt?: string;
    estimatedCompletionTime: number;
    actualCompletionTime?: number;
  };
  
  // AI Team Coordination
  aiTeamStatus: {
    strategic: 'inactive' | 'initializing' | 'active' | 'processing';
    data: 'inactive' | 'initializing' | 'active' | 'processing';
    workflow: 'inactive' | 'initializing' | 'active' | 'processing';
    communication: 'inactive' | 'initializing' | 'active' | 'processing';
  };
  
  // Data Import Status
  importStatus: {
    status: 'pending' | 'importing' | 'mapping' | 'analyzing' | 'completed' | 'failed';
    totalItems: number;
    processedItems: number;
    aiInsights: number;
    strategicItemsIdentified: number;
    errors: string[];
  };
}

export interface UseOnboardingReturn {
  // State
  data: Partial<OnboardingData>;
  currentStep: number;
  isCompleted: boolean;
  isLoading: boolean;
  
  // Actions
  updateCompanyInfo: (info: Partial<OnboardingData['companyInfo']>) => void;
  updateStrategicPreferences: (prefs: Partial<OnboardingData['strategicPreferences']>) => void;
  updateIntegrationSetup: (setup: Partial<OnboardingData['integrationSetup']>) => void;
  updateProgress: (progress: Partial<OnboardingData['progress']>) => void;
  updateAITeamStatus: (status: Partial<OnboardingData['aiTeamStatus']>) => void;
  updateImportStatus: (status: Partial<OnboardingData['importStatus']>) => void;
  
  // Step Management
  goToStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  completeStep: (stepId: string) => void;
  
  // Persistence
  saveOnboardingData: () => Promise<void>;
  loadOnboardingData: () => Promise<void>;
  clearOnboardingData: () => void;
  
  // Validation
  validateStep: (step: number) => { isValid: boolean; errors: string[] };
  isStepCompleted: (stepId: string) => boolean;
  
  // Analytics
  trackStepCompletion: (stepId: string, timeSpent: number) => void;
  trackDropoff: (stepId: string, reason?: string) => void;
}

const ONBOARDING_STORAGE_KEY = 'pm33-onboarding-data';
const ONBOARDING_STEPS = [
  'welcome',
  'strategy', 
  'connect',
  'import',
  'organize',
  'roadmap',
  'recommendations'
];

export const useOnboarding = (): UseOnboardingReturn => {
  const [data, setData] = useState<Partial<OnboardingData>>({
    progress: {
      completedSteps: [],
      currentStep: 0,
      startedAt: new Date().toISOString(),
      estimatedCompletionTime: 15 // minutes
    },
    aiTeamStatus: {
      strategic: 'inactive',
      data: 'inactive',
      workflow: 'inactive',
      communication: 'inactive'
    },
    importStatus: {
      status: 'pending',
      totalItems: 0,
      processedItems: 0,
      aiInsights: 0,
      strategicItemsIdentified: 0,
      errors: []
    }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  // Initialize onboarding data from localStorage
  useEffect(() => {
    loadOnboardingData();
  }, []);

  // Auto-save data changes
  useEffect(() => {
    if (data.progress?.startedAt) {
      const timeoutId = setTimeout(() => {
        saveOnboardingData();
      }, 1000);
      return () => clearTimeout(timeoutId);
    }
  }, [data]);

  const updateCompanyInfo = useCallback((info: Partial<OnboardingData['companyInfo']>) => {
    setData(prev => ({
      ...prev,
      companyInfo: { ...prev.companyInfo, ...info }
    }));
  }, []);

  const updateStrategicPreferences = useCallback((prefs: Partial<OnboardingData['strategicPreferences']>) => {
    setData(prev => ({
      ...prev,
      strategicPreferences: { ...prev.strategicPreferences, ...prefs }
    }));
  }, []);

  const updateIntegrationSetup = useCallback((setup: Partial<OnboardingData['integrationSetup']>) => {
    setData(prev => ({
      ...prev,
      integrationSetup: { ...prev.integrationSetup, ...setup }
    }));
  }, []);

  const updateProgress = useCallback((progress: Partial<OnboardingData['progress']>) => {
    setData(prev => ({
      ...prev,
      progress: { ...prev.progress, ...progress }
    }));
  }, []);

  const updateAITeamStatus = useCallback((status: Partial<OnboardingData['aiTeamStatus']>) => {
    setData(prev => ({
      ...prev,
      aiTeamStatus: { ...prev.aiTeamStatus, ...status }
    }));
  }, []);

  const updateImportStatus = useCallback((status: Partial<OnboardingData['importStatus']>) => {
    setData(prev => ({
      ...prev,
      importStatus: { ...prev.importStatus, ...status }
    }));
  }, []);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < ONBOARDING_STEPS.length) {
      setCurrentStep(step);
      updateProgress({ currentStep: step });
    }
  }, [updateProgress]);

  const nextStep = useCallback(() => {
    if (currentStep < ONBOARDING_STEPS.length - 1) {
      const newStep = currentStep + 1;
      setCurrentStep(newStep);
      updateProgress({ currentStep: newStep });
    }
  }, [currentStep, updateProgress]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      const newStep = currentStep - 1;
      setCurrentStep(newStep);
      updateProgress({ currentStep: newStep });
    }
  }, [currentStep, updateProgress]);

  const completeStep = useCallback((stepId: string) => {
    const currentCompletedSteps = data.progress?.completedSteps || [];
    if (!currentCompletedSteps.includes(stepId)) {
      const newCompletedSteps = [...currentCompletedSteps, stepId];
      updateProgress({ 
        completedSteps: newCompletedSteps,
        ...(newCompletedSteps.length === ONBOARDING_STEPS.length ? {
          completedAt: new Date().toISOString(),
          actualCompletionTime: Math.round((Date.now() - new Date(data.progress?.startedAt || Date.now()).getTime()) / 60000)
        } : {})
      });
      
      // Track completion analytics
      trackStepCompletion(stepId, 0);
    }
  }, [data.progress, updateProgress]);

  const saveOnboardingData = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);
      
      // Save to localStorage
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(data));
      
      // Save to backend API (if available)
      if (data.progress?.startedAt) {
        try {
          await fetch('/api/onboarding', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'save_progress',
              data: data
            })
          });
        } catch (error) {
          console.warn('Failed to save onboarding data to backend:', error);
        }
      }
    } catch (error) {
      console.error('Failed to save onboarding data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [data]);

  const loadOnboardingData = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);
      
      // Load from localStorage first
      const savedData = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (savedData) {
        const parsedData = JSON.parse(savedData);
        setData(parsedData);
        setCurrentStep(parsedData.progress?.currentStep || 0);
      }
      
      // Load from backend API (if available)
      try {
        const response = await fetch('/api/onboarding');
        if (response.ok) {
          const backendData = await response.json();
          if (backendData.success && backendData.data) {
            setData(backendData.data);
            setCurrentStep(backendData.data.progress?.currentStep || 0);
          }
        }
      } catch (error) {
        console.warn('Failed to load onboarding data from backend:', error);
      }
    } catch (error) {
      console.error('Failed to load onboarding data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearOnboardingData = useCallback(() => {
    localStorage.removeItem(ONBOARDING_STORAGE_KEY);
    setData({
      progress: {
        completedSteps: [],
        currentStep: 0,
        startedAt: new Date().toISOString(),
        estimatedCompletionTime: 15
      },
      aiTeamStatus: {
        strategic: 'inactive',
        data: 'inactive',
        workflow: 'inactive',
        communication: 'inactive'
      },
      importStatus: {
        status: 'pending',
        totalItems: 0,
        processedItems: 0,
        aiInsights: 0,
        strategicItemsIdentified: 0,
        errors: []
      }
    });
    setCurrentStep(0);
  }, []);

  const validateStep = useCallback((step: number): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    switch (step) {
      case 0: // Welcome - always valid
        break;
        
      case 1: // Strategy
        if (!data.companyInfo?.name?.trim()) {
          errors.push('Company name is required');
        }
        if (!data.strategicPreferences?.framework) {
          errors.push('Strategic framework selection is required');
        }
        break;
        
      case 2: // Connect Tools
        if (!data.integrationSetup?.primaryTool) {
          errors.push('Primary PM tool selection is required');
        }
        if (!data.integrationSetup?.instanceUrl?.trim()) {
          errors.push('Instance URL is required');
        }
        break;
        
      case 3: // Import Data
        if (data.importStatus?.status === 'failed') {
          errors.push('Data import failed - please retry');
        }
        break;
        
      case 4: // Organize Backlog
        if (data.importStatus?.aiInsights === 0) {
          errors.push('Backlog organization incomplete');
        }
        break;
        
      case 5: // Build Roadmap
        if (data.importStatus?.strategicItemsIdentified === 0) {
          errors.push('No strategic items identified for roadmap');
        }
        break;
        
      case 6: // Recommendations - always valid when reached
        break;
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }, [data]);

  const isStepCompleted = useCallback((stepId: string): boolean => {
    return data.progress?.completedSteps?.includes(stepId) || false;
  }, [data.progress?.completedSteps]);

  const trackStepCompletion = useCallback((stepId: string, timeSpent: number) => {
    // Analytics tracking for step completion
    if (typeof window !== 'undefined' && window.posthog) {
      window.posthog.capture('onboarding_step_completed', {
        step_id: stepId,
        step_index: ONBOARDING_STEPS.indexOf(stepId),
        time_spent_seconds: timeSpent,
        total_steps: ONBOARDING_STEPS.length,
        completion_rate: ((data.progress?.completedSteps?.length || 0) / ONBOARDING_STEPS.length) * 100,
        company_size: data.companyInfo?.size,
        industry: data.companyInfo?.industry,
        primary_tool: data.integrationSetup?.primaryTool,
        strategic_framework: data.strategicPreferences?.framework
      });
    }
  }, [data]);

  const trackDropoff = useCallback((stepId: string, reason?: string) => {
    // Analytics tracking for onboarding dropoff
    if (typeof window !== 'undefined' && window.posthog) {
      window.posthog.capture('onboarding_dropoff', {
        step_id: stepId,
        step_index: ONBOARDING_STEPS.indexOf(stepId),
        reason: reason || 'user_exit',
        steps_completed: data.progress?.completedSteps?.length || 0,
        total_steps: ONBOARDING_STEPS.length,
        time_to_dropoff: Math.round((Date.now() - new Date(data.progress?.startedAt || Date.now()).getTime()) / 60000),
        company_size: data.companyInfo?.size,
        industry: data.companyInfo?.industry
      });
    }
  }, [data]);

  const isCompleted = (data.progress?.completedSteps?.length || 0) === ONBOARDING_STEPS.length;

  return {
    // State
    data,
    currentStep,
    isCompleted,
    isLoading,
    
    // Actions
    updateCompanyInfo,
    updateStrategicPreferences,
    updateIntegrationSetup,
    updateProgress,
    updateAITeamStatus,
    updateImportStatus,
    
    // Step Management
    goToStep,
    nextStep,
    prevStep,
    completeStep,
    
    // Persistence
    saveOnboardingData,
    loadOnboardingData,
    clearOnboardingData,
    
    // Validation
    validateStep,
    isStepCompleted,
    
    // Analytics
    trackStepCompletion,
    trackDropoff
  };
};

export default useOnboarding;