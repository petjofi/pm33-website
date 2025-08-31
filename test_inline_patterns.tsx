/**
 * Test Component for MCP Design Validator - Inline Coding Patterns
 * This file tests the new inline coding policy enforcement
 */

import React, { useState } from 'react';

// ❌ SHOULD FAIL - Theme-conditional inline styles  
const BadThemeComponent = ({ theme }: { theme: 'light' | 'dark' }) => {
  return (
    <div style={{
      background: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(248, 250, 252, 0.95)',
      color: theme === 'dark' ? '#cbd5e1' : '#64748b',
      border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid #e5e7eb'
    }}>
      This should be flagged by MCP validator
    </div>
  );
};

// ❌ SHOULD FAIL - Hardcoded design values
const BadHardcodedComponent = () => {
  return (
    <div style={{
      padding: '24px',          // Should use var(--pm33-spacing-md)
      fontSize: '16px',         // Should use var(--pm33-text-base) 
      borderRadius: '8px',      // Should use var(--pm33-radius-md)
      margin: '32px',           // Should use var(--pm33-spacing-lg)
      gap: '16px'              // Should use var(--pm33-spacing-sm)
    }}>
      Hardcoded values should fail
    </div>
  );
};

// ❌ SHOULD FAIL - Brand color hardcoding
const BadBrandColorsComponent = () => {
  return (
    <button style={{
      background: '#667eea',        // Should use var(--pm33-brand)
      color: '#764ba2',            // Should use design tokens
      borderColor: '#10b981'       // Should use var(--pm33-success)
    }}>
      Brand colors hardcoded
    </button>
  );
};

// ❌ SHOULD FAIL - Component-specific CSS without pm33- prefix
const BadCSSComponent = () => {
  return (
    <>
      <style>
      {`
        .my-component {              // Should be .pm33-my-component
          background: red;           // Should use design tokens
          padding: 20px;             // Should use spacing grid
        }
      `}
      </style>
      <div className="my-component">Bad CSS</div>
    </>
  );
};

// ✅ SHOULD PASS - Mathematical calculations
const GoodMathComponent = ({ progress, total }: { progress: number, total: number }) => {
  const [offset, setOffset] = useState(0);
  const [angle, setAngle] = useState(0);
  
  return (
    <div style={{
      width: `${((progress + 1) / total) * 100}%`,           // Progress calculation
      transform: `translateX(${offset}px) rotate(${angle}deg)`, // Animation calculation
      zIndex: 1000 + progress,                               // Dynamic layering
      opacity: progress > 0 ? 1 : 0,                        // State-based opacity
      left: `${offset * 2}px`                               // Dynamic positioning
    }}>
      Mathematical calculations allowed
    </div>
  );
};

// ✅ SHOULD PASS - Component-specific keyframes
const GoodAnimationComponent = () => {
  return (
    <>
      <style>
      {`
        @keyframes pm33-loading-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pm33-modal-enter {
          from { opacity: 0; transform: scale(0.95) translateY(20px); }
          to { opacity: 1; transform: scale(1) translateY(0); }
        }
        .pm33-loading { 
          animation: pm33-loading-spin 1s linear infinite; 
        }
      `}
      </style>
      <div className="pm33-loading">Animation keyframes allowed</div>
    </>
  );
};

// ✅ SHOULD PASS - Performance-critical transforms
const GoodPerformanceComponent = ({ x, y, isAnimating }: { x: number, y: number, isAnimating: boolean }) => {
  return (
    <div style={{
      transform: `translate3d(${x}px, ${y}px, 0)`,      // Hardware acceleration
      willChange: isAnimating ? 'transform' : 'auto',   // Performance optimization
      backfaceVisibility: 'hidden',                     // Prevent flickering
      transformOrigin: `${x}% ${y}%`                    // Dynamic transform origin
    }}>
      Performance transforms allowed
    </div>
  );
};

// ✅ SHOULD PASS - Accessibility-required styles
const GoodAccessibilityComponent = ({ screenReaderOnly, isAriaHidden }: { screenReaderOnly: boolean, isAriaHidden: boolean }) => {
  return (
    <div style={{
      clipPath: screenReaderOnly ? 'inset(50%)' : 'none',     // Screen reader control
      position: screenReaderOnly ? 'absolute' : 'static',
      visibility: isAriaHidden ? 'hidden' : 'visible'         // Dynamic ARIA states
    }}>
      Accessibility patterns allowed
    </div>
  );
};

// ✅ SHOULD PASS - Small component-specific SVG
const GoodSVGComponent = () => {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2L2 7v10c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7l-10-5z"/>
    </svg>
  );
};

// ✅ SHOULD PASS - Correct CSS class usage
const GoodDesignTokenComponent = () => {
  return (
    <div className="pm33-glass-card pm33-modal-content">
      <h1 className="pm33-heading-1">Correct Design Tokens</h1>
      <p className="pm33-body-text">Using CSS classes with design tokens</p>
      <button className="pm33-button-primary">Brand button</button>
    </div>
  );
};

export default function TestComponent() {
  return (
    <div className="pm33-glass-card">
      <h1 className="pm33-heading-1">MCP Validator Test Cases</h1>
      <p className="pm33-body-text">This component tests inline coding policy enforcement</p>
    </div>
  );
}