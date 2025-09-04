/**
 * PM33 Onboarding Modal - Enterprise Glass Morphism Overlay
 * Modal overlay version of the onboarding flow for dashboard integration
 * Full PM33 Design System compliance with CSS custom properties
 * WCAG 2.1 AA accessibility compliant with focus management
 */

"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { X } from 'lucide-react';
import { PM33OnboardingFlow } from './PM33OnboardingFlow';
import { useOnboarding } from '@/lib/hooks/useOnboarding';

/**
 * Design System Token Types
 */
type PM33ThemeMode = 'light' | 'dark';

interface PM33DesignTokens {
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  fontWeight: {
    normal: string;
    medium: string;
    semibold: string;
    bold: string;
  };
  borderRadius: {
    sm: string;
    base: string;
    lg: string;
    full: string;
  };
  transition: {
    fast: string;
    base: string;
    slow: string;
  };
}

interface PM33OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete?: (data: any) => void;
  theme?: PM33ThemeMode;
}

export const PM33OnboardingModal: React.FC<PM33OnboardingModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  theme = 'dark'
}) => {
  const {
    data,
    currentStep,
    isCompleted,
    saveOnboardingData,
    trackDropoff
  } = useOnboarding();

  const [isClosing, setIsClosing] = useState(false);
  const [isKeyboardUser, setIsKeyboardUser] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const firstFocusableRef = useRef<HTMLButtonElement>(null);
  const lastFocusableRef = useRef<HTMLButtonElement>(null);
  
  // Design tokens access
  const designTokens: PM33DesignTokens = {
    spacing: {
      xs: 'var(--pm33-spacing-xs)',
      sm: 'var(--pm33-spacing-sm)',
      md: 'var(--pm33-spacing-md)',
      lg: 'var(--pm33-spacing-lg)',
      xl: 'var(--pm33-spacing-xl)',
      '2xl': 'var(--pm33-spacing-2xl)',
      '3xl': 'var(--pm33-spacing-3xl)',
      '4xl': 'var(--pm33-spacing-4xl)'
    },
    fontSize: {
      xs: 'var(--pm33-font-size-xs)',
      sm: 'var(--pm33-font-size-sm)',
      base: 'var(--pm33-font-size-base)',
      lg: 'var(--pm33-font-size-lg)',
      xl: 'var(--pm33-font-size-xl)',
      '2xl': 'var(--pm33-font-size-2xl)',
      '3xl': 'var(--pm33-font-size-3xl)',
      '4xl': 'var(--pm33-font-size-4xl)'
    },
    fontWeight: {
      normal: 'var(--pm33-font-weight-normal)',
      medium: 'var(--pm33-font-weight-medium)',
      semibold: 'var(--pm33-font-weight-semibold)',
      bold: 'var(--pm33-font-weight-bold)'
    },
    borderRadius: {
      sm: 'var(--pm33-radius-sm)',
      base: 'var(--pm33-radius-base)',
      lg: 'var(--pm33-radius-lg)',
      full: 'var(--pm33-radius-full)'
    },
    transition: {
      fast: 'var(--pm33-transition-fast)',
      base: 'var(--pm33-transition-base)',
      slow: 'var(--pm33-transition-slow)'
    }
  };

  // Enhanced keyboard navigation and accessibility
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isOpen) return;
    
    setIsKeyboardUser(true);
    
    if (e.key === 'Escape') {
      handleSkipOnboarding();
      return;
    }
    
    // Focus trap implementation
    if (e.key === 'Tab') {
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (focusableElements && focusableElements.length > 0) {
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
        
        if (e.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    }
  }, [isOpen]);
  
  // Handle mouse interactions to detect mouse users
  const handleMouseMove = useCallback(() => {
    setIsKeyboardUser(false);
  }, []);
  
  useEffect(() => {
    if (!isOpen) return;

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousemove', handleMouseMove);
    
    // Prevent body scrolling when modal is open
    document.body.style.overflow = 'hidden';
    document.body.classList.add('pm33-modal-open');
    
    // Set initial focus to first focusable element
    setTimeout(() => {
      firstFocusableRef.current?.focus();
    }, 100);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.body.style.overflow = 'unset';
      document.body.classList.remove('pm33-modal-open');
    };
  }, [isOpen, handleKeyDown, handleMouseMove]);

  // Auto-save progress when modal is closed
  useEffect(() => {
    if (!isOpen && data.progress?.startedAt) {
      saveOnboardingData();
    }
  }, [isOpen, data.progress?.startedAt, saveOnboardingData]);

  const handleOnboardingComplete = async (onboardingData: any) => {
    try {
      // Save final onboarding data
      await saveOnboardingData();
      
      // Send completion data to backend
      const response = await fetch('/api/onboarding', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'complete_onboarding',
          data: onboardingData
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Onboarding completed:', result);
        
        // Track completion analytics
        if (typeof window !== 'undefined' && window.posthog) {
          window.posthog.capture('onboarding_completed', {
            time_to_complete: Math.round((Date.now() - new Date(data.progress?.startedAt || Date.now()).getTime()) / 60000),
            company_name: onboardingData.companyInfo?.name,
            industry: onboardingData.companyInfo?.industry,
            company_size: onboardingData.companyInfo?.size,
            primary_tool: onboardingData.integrationSetup?.primaryTool,
            strategic_framework: onboardingData.strategicPreferences?.framework,
            completed_steps: onboardingData.completedSteps?.length || 0,
            completion_method: 'modal'
          });
        }
      }

      // Call completion handler and close modal
      if (onComplete) {
        onComplete(onboardingData);
      }
      
      setIsClosing(true);
      setTimeout(() => {
        onClose();
        setIsClosing(false);
      }, 300);
      
    } catch (error) {
      console.error('Onboarding completion error:', error);
      // Still close modal on error
      onClose();
    }
  };

  const handleSkipOnboarding = () => {
    // Track skip analytics
    trackDropoff(`step_${currentStep}`, 'user_skip_modal');
    
    // Show confirmation dialog
    const confirmed = window.confirm(
      'Are you sure you want to skip PMO transformation setup? You can always complete it later from your settings.'
    );
    
    if (confirmed) {
      // Mark as skipped in localStorage
      localStorage.setItem('pm33-onboarding-skipped', 'true');
      
      // Close modal
      setIsClosing(true);
      setTimeout(() => {
        onClose();
        setIsClosing(false);
      }, 300);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleSkipOnboarding();
    }
  };

  if (!isOpen && !isClosing) return null;

  return (
    <div 
      data-testid="onboarding-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-modal-title"
      className={`pm33-modal-overlay ${isKeyboardUser ? 'pm33-keyboard-user' : ''}`}
      ref={modalRef}
      style={{
        transition: designTokens.transition.slow,
        opacity: isOpen && !isClosing ? 1 : 0,
        pointerEvents: isOpen ? 'auto' : 'none'
      }}
      onClick={handleBackdropClick}
    >
      <style>
        {`
          @keyframes pm33-pulse {
            0%, 100% { opacity: 0.8; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.05); }
          }
          
          @keyframes pm33-modal-enter {
            from { opacity: 0; transform: scale(0.9) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
          }
          
          .pm33-modal-open {
            overflow: hidden;
          }
          
          .pm33-modal-content {
            animation: pm33-modal-enter ${designTokens.transition.slow};
          }
          
          .pm33-keyboard-user button:focus-visible {
            box-shadow: var(--pm33-focus-ring);
            outline-offset: 2px;
          }
        `}
      </style>

      {/* Modal Backdrop with Glass Morphism */}
      <div 
        data-testid="modal-backdrop"
        style={{
          position: 'absolute',
          inset: '0',
          background: 'var(--pm33-bg-modal)',
          backdropFilter: 'var(--pm33-blur-light)',
          WebkitBackdropFilter: 'var(--pm33-blur-light)'
        }} 
      />
      
      {/* Animated Background Elements */}
      <div style={{
        position: 'absolute',
        inset: '0',
        overflow: 'hidden',
        pointerEvents: 'none'
      }}>
        <div style={{
          position: 'absolute',
          top: '-160px',
          right: '-320px',
          width: '320px',
          height: '320px',
          background: theme === 'dark' ? 'rgba(147, 51, 234, 0.15)' : 'rgba(196, 181, 253, 0.08)',
          borderRadius: '50%',
          filter: 'blur(40px)',
          animation: 'pm33-pulse 4s ease-in-out infinite'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-160px',
          left: '-320px',
          width: '320px',
          height: '320px',
          background: theme === 'dark' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(147, 197, 253, 0.08)',
          borderRadius: '50%',
          filter: 'blur(40px)',
          animation: 'pm33-pulse 4s ease-in-out infinite 2s'
        }} />
        <div style={{
          position: 'absolute',
          top: '160px',
          left: '160px',
          width: '320px',
          height: '320px',
          background: theme === 'dark' ? 'rgba(236, 72, 153, 0.15)' : 'rgba(252, 165, 165, 0.08)',
          borderRadius: '50%',
          filter: 'blur(40px)',
          animation: 'pm33-pulse 4s ease-in-out infinite 4s'
        }} />
      </div>

      {/* Modal Container */}
      <div 
        className="pm33-modal-content"
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '1152px',
          margin: `0 ${designTokens.spacing.md}`,
          maxHeight: '90vh',
          transition: designTokens.transition.slow,
          transform: isOpen && !isClosing ? 'scale(1) translateY(0)' : 'scale(0.95) translateY(16px)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div 
          className="pm33-modal-content"
          style={{
            overflow: 'hidden',
            minHeight: '600px',
            display: 'flex',
            flexDirection: 'column'
          }}>
          {/* Modal Header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: designTokens.spacing.lg,
            borderBottom: `1px solid ${theme === 'dark' ? 'rgba(148, 163, 184, 0.15)' : 'rgba(148, 163, 184, 0.25)'}`,
            background: theme === 'dark' 
              ? 'rgba(255, 255, 255, 0.015)' 
              : 'rgba(255, 255, 255, 0.4)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: designTokens.spacing.md }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: designTokens.spacing.md }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: designTokens.borderRadius.base,
                  background: 'var(--pm33-brand-gradient)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: theme === 'dark' 
                    ? '0 4px 12px rgba(59, 130, 246, 0.3)' 
                    : '0 2px 8px rgba(59, 130, 246, 0.15)'
                }}>
                  <span style={{ 
                    color: 'white', 
                    fontWeight: designTokens.fontWeight.bold, 
                    fontSize: designTokens.fontSize.lg
                  }}>PM</span>
                </div>
                <div>
                  <h1 
                    id="onboarding-modal-title"
                    className="pm33-heading-2"
                    style={{
                      margin: '0 0 8px 0'
                    }}
                  >
                    PM33 PMO Transformation Setup
                  </h1>
                  <p 
                    className="pm33-caption"
                    style={{
                      margin: '0',
                      textTransform: 'none'
                    }}>
                    Transform your workflow into PMO-level intelligence
                  </p>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: designTokens.spacing.md }}>
              {/* Step Progress Indicator */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: designTokens.spacing.sm,
                padding: `${designTokens.spacing.sm} ${designTokens.spacing.md}`,
                background: 'var(--pm33-glass-bg)',
                borderRadius: designTokens.borderRadius.sm,
                border: `1px solid ${theme === 'dark' ? 'var(--pm33-glass-border)' : 'rgba(148, 163, 184, 0.15)'}`
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                  color: theme === 'dark' ? '#94a3b8' : '#64748b'
                }}>
                  Step {currentStep + 1} of 6
                </span>
                <div 
                  role="progressbar"
                  aria-valuenow={currentStep + 1}
                  aria-valuemin={1}
                  aria-valuemax={6}
                  aria-label={`Onboarding progress: Step ${currentStep + 1} of 6`}
                  style={{
                    width: '64px',
                    background: theme === 'dark' ? 'rgba(148, 163, 184, 0.25)' : '#e5e7eb',
                    borderRadius: designTokens.borderRadius.sm,
                    height: '6px',
                    overflow: 'hidden'
                  }}
                >
                  <div 
                    data-testid="progress-bar"
                    style={{
                      background: 'var(--pm33-brand-gradient)',
                      height: '6px',
                      borderRadius: designTokens.borderRadius.sm,
                      transition: 'all 0.5s ease',
                      width: `${((currentStep + 1) / 6) * 100}%`,
                      boxShadow: theme === 'dark' 
                        ? '0 0 8px rgba(59, 130, 246, 0.4)' 
                        : '0 0 4px rgba(59, 130, 246, 0.2)'
                    }} 
                  />
                </div>
              </div>

              {/* Close Button */}
              <button
                ref={firstFocusableRef}
                onClick={handleSkipOnboarding}
                className="pm33-button-secondary"
                style={{
                  padding: '8px'
                }}
                aria-label="Skip onboarding setup"
                title="Skip Setup (Press Esc)"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Modal Content */}
          <div style={{
            flex: '1',
            overflowY: 'auto',
            padding: designTokens.spacing.xl
          }}>
            <PM33OnboardingFlow
              theme={theme}
              onComplete={handleOnboardingComplete}
              onSkip={handleSkipOnboarding}
            />
          </div>

          {/* Modal Footer */}
          <div style={{
            padding: designTokens.spacing.lg,
            borderTop: `1px solid ${theme === 'dark' ? 'rgba(148, 163, 184, 0.15)' : 'rgba(148, 163, 184, 0.25)'}`,
            background: theme === 'dark' 
              ? 'rgba(15, 23, 42, 0.25)' 
              : 'rgba(255, 255, 255, 0.25)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: designTokens.fontSize.sm
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: designTokens.spacing.lg,
                color: 'var(--pm33-text-muted)'
              }}>
                <span>© 2025 PM33 Platform</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: designTokens.spacing.md }}>
                  <span>Need help?</span>
                  <a 
                    href="mailto:support@pm-33.com" 
                    style={{
                      color: 'var(--pm33-brand-primary)',
                      textDecoration: 'none',
                      transition: designTokens.transition.base,
                      fontWeight: designTokens.fontWeight.medium
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.textDecoration = 'underline';
                      e.currentTarget.style.color = 'var(--pm33-brand-primary-hover)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.textDecoration = 'none';
                      e.currentTarget.style.color = 'var(--pm33-brand-primary)';
                    }}
                  >
                    Contact Support
                  </a>
                </div>
              </div>
              
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: designTokens.spacing.md,
                fontSize: designTokens.fontSize.xs,
                color: 'var(--pm33-text-disabled)'
              }}>
                <span>Press <kbd style={{
                  padding: `2px ${designTokens.spacing.sm}`,
                  background: 'var(--pm33-glass-bg)',
                  borderRadius: designTokens.borderRadius.sm,
                  fontSize: designTokens.fontSize.xs,
                  fontFamily: 'var(--font-mono)',
                  border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`
                }}>Esc</kbd> to close</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PM33OnboardingModal;