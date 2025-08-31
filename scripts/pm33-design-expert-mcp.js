#!/usr/bin/env node

/**
 * PM33 Design Expert MCP Interface
 * Allows internal Claude Code agents to invoke design expert validation
 * during active development work
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class PM33DesignExpertMCP {
  constructor() {
    this.name = 'pm33-design-expert';
    this.version = '1.0.0';
    this.description = 'PM33 Design Expert for real-time UI/UX validation and consultation';
    this.tracker = require('./design-enforcer-tracker.js').DesignEnforcerTracker;
    this.trackerInstance = new this.tracker();
  }

  /**
   * MCP Function: Validate file against PM33 design standards
   */
  async validateFile(filePath, validationType = 'comprehensive') {
    try {
      const result = {
        file: filePath,
        validationType,
        timestamp: new Date().toISOString(),
        violations: [],
        passed: false,
        recommendations: [],
        approval: null
      };

      // Run comprehensive validation
      const validationPromise = new Promise((resolve, reject) => {
        const validator = spawn('python', ['mcp_design_validator.py', filePath, '--strict'], {
          cwd: process.cwd(),
          stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        validator.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        validator.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        validator.on('close', (code) => {
          resolve({ code, stdout, stderr });
        });

        validator.on('error', (error) => {
          reject(error);
        });
      });

      const validationResult = await validationPromise;
      
      // Parse validation output
      result.passed = validationResult.code === 0;
      
      if (!result.passed) {
        // Extract violations from output
        const violationMatches = validationResult.stdout.match(/❌.*?$/gm);
        result.violations = violationMatches ? violationMatches.map(v => v.replace('❌', '').trim()) : [];
        
        // Generate recommendations
        result.recommendations = this.generateRecommendations(result.violations, filePath);
      }

      // Log activity
      this.trackerInstance.logValidation(validationType, filePath, result.violations);

      return {
        success: true,
        result
      };

    } catch (error) {
      return {
        success: false,
        error: error.message,
        result: null
      };
    }
  }

  /**
   * MCP Function: Get design consultation for specific UI element
   */
  async consultDesign(elementType, context, currentImplementation = null) {
    const consultation = {
      elementType,
      context,
      timestamp: new Date().toISOString(),
      recommendations: [],
      codeExamples: [],
      designPrinciples: []
    };

    switch (elementType.toLowerCase()) {
      case 'card':
        consultation.recommendations = [
          'Use PM33 glass morphism with backdrop-filter: blur(20px)',
          'Apply brand gradient border or background',
          'Ensure 16px border-radius for consistency',
          'Add professional shadow (not shadow-sm)',
          'Use 24px internal padding for content'
        ];
        consultation.codeExamples = [
          `// PM33 Glass Card Component
<div className="bg-white/95 dark:bg-gray-900/95 backdrop-blur-lg border border-white/20 rounded-2xl p-6 shadow-xl">
  {children}
</div>`,
          `/* CSS Custom Properties */
.pm33-glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}`
        ];
        break;

      case 'header':
      case 'headline':
        consultation.recommendations = [
          'Apply PM33 brand gradient to text',
          'Use Inter font family exclusively',
          'Implement responsive typography scale',
          'Add proper line-height for readability',
          'Ensure dark/light theme compatibility'
        ];
        consultation.codeExamples = [
          `// PM33 Gradient Headline
<h1 className="text-4xl font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
  PM33 Headline
</h1>`,
          `/* CSS Gradient Text */
.pm33-gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}`
        ];
        break;

      case 'button':
        consultation.recommendations = [
          'Use PM33 brand colors (#667eea, #764ba2, #10b981)',
          'Add hover transform and transition effects',
          'Implement proper focus states for accessibility',
          'Use consistent padding: 12px 24px for standard buttons',
          'Add loading states for better UX'
        ];
        consultation.codeExamples = [
          `// PM33 Primary Button
<button className="bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white px-6 py-3 rounded-lg font-semibold hover:scale-105 transition-transform duration-200 focus:ring-2 focus:ring-[#667eea] focus:ring-opacity-50">
  Action Button
</button>`
        ];
        break;

      default:
        consultation.recommendations = [
          'Follow PM33 8px spacing grid system',
          'Use only approved brand colors',
          'Implement glass morphism where appropriate',
          'Ensure responsive design patterns',
          'Add proper hover and focus states'
        ];
    }

    consultation.designPrinciples = [
      'Glass Morphism: Use backdrop-blur for depth and sophistication',
      'Brand Colors: Stick to #667eea, #764ba2, #10b981 palette',
      'Typography: Inter font family only, with gradient text for headlines',
      'Spacing: 8px grid system for consistent rhythm',
      'Shadows: Professional depth, avoid flat design',
      'Responsive: Mobile-first approach with proper breakpoints'
    ];

    return {
      success: true,
      consultation
    };
  }

  /**
   * MCP Function: Request design expert approval
   */
  async requestApproval(agentId, files, description, implementationPlan = null) {
    const approvalRequest = {
      requestId: `approval-${Date.now()}`,
      agentId,
      files: Array.isArray(files) ? files : [files],
      description,
      implementationPlan,
      timestamp: new Date().toISOString(),
      status: 'pending',
      feedback: [],
      approved: false
    };

    // Validate all files first
    const validationResults = [];
    for (const file of approvalRequest.files) {
      if (fs.existsSync(file)) {
        const result = await this.validateFile(file, 'approval-review');
        validationResults.push(result);
      }
    }

    // Determine approval based on validation results
    const hasViolations = validationResults.some(r => r.result && !r.result.passed);
    
    if (!hasViolations) {
      approvalRequest.approved = true;
      approvalRequest.status = 'approved';
      approvalRequest.feedback = ['All files pass PM33 design standards', 'Implementation approved for commit'];
    } else {
      approvalRequest.approved = false;
      approvalRequest.status = 'rejected';
      approvalRequest.feedback = [
        'Design violations found - see validation results',
        'Fix all violations before requesting re-approval'
      ];
      
      // Add specific violation feedback
      validationResults.forEach(r => {
        if (r.result && !r.result.passed) {
          approvalRequest.feedback.push(`${r.result.file}: ${r.result.violations.length} violations`);
          approvalRequest.feedback.push(...r.result.recommendations);
        }
      });
    }

    // Log approval decision
    this.trackerInstance.logDesignApproval(
      'PM33-Design-Expert',
      `${agentId}: ${description}`,
      approvalRequest.approved
    );

    return {
      success: true,
      approvalRequest,
      validationResults
    };
  }

  /**
   * MCP Function: Get design system guidance
   */
  async getDesignSystem() {
    return {
      success: true,
      designSystem: {
        colors: {
          primary: '#667eea',
          secondary: '#764ba2', 
          success: '#10b981',
          light: '#ffffff',
          dark: '#0a0e27',
          lightSecondary: '#f8fafc',
          darkSecondary: '#1e293b'
        },
        typography: {
          fontFamily: "'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
          sizes: {
            h1: ['48px', '56px', '64px'],
            h2: ['32px', '36px', '40px'],
            h3: ['24px', '28px', '32px'],
            body: ['14px', '16px', '18px']
          },
          gradientText: 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'
        },
        spacing: {
          unit: '8px',
          scale: [4, 8, 12, 16, 24, 32, 48, 64, 80, 96, 128],
          grid: '8px grid system - all spacing should be multiples of 8px'
        },
        glassMorphism: {
          light: 'background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px);',
          dark: 'background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px);',
          border: 'border: 1px solid rgba(255, 255, 255, 0.2);',
          borderRadius: '16px',
          shadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        },
        components: {
          card: 'Glass morphism with backdrop blur, rounded corners, professional shadows',
          button: 'Brand gradient backgrounds, hover transforms, focus states',
          input: 'Glass styling with proper focus indicators',
          navigation: 'Consistent spacing, brand colors, responsive patterns'
        }
      }
    };
  }

  /**
   * Generate contextual recommendations based on violations
   */
  generateRecommendations(violations, filePath) {
    const recommendations = [];
    
    violations.forEach(violation => {
      if (violation.includes('color')) {
        recommendations.push('Use PM33 brand colors: #667eea (primary), #764ba2 (secondary), #10b981 (success)');
      }
      if (violation.includes('font')) {
        recommendations.push('Use Inter font family exclusively for brand consistency');
      }
      if (violation.includes('spacing')) {
        recommendations.push('Follow 8px spacing grid - use multiples of 8px for all spacing');
      }
      if (violation.includes('shadow')) {
        recommendations.push('Use professional shadows, avoid shadow-sm - try shadow-xl or shadow-2xl');
      }
      if (violation.includes('gradient')) {
        recommendations.push('Add gradient text to headlines using PM33 brand gradient');
      }
    });

    // Add file-specific recommendations
    if (filePath.includes('Card') || filePath.includes('card')) {
      recommendations.push('Implement glass morphism with backdrop-filter: blur(20px)');
    }
    if (filePath.includes('Button') || filePath.includes('button')) {
      recommendations.push('Add hover:scale-105 transform for interactive feedback');
    }

    return recommendations;
  }

  /**
   * MCP Function: Get current enforcement metrics
   */
  async getMetrics() {
    try {
      const metrics = this.trackerInstance.loadMetrics();
      return {
        success: true,
        metrics
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        metrics: null
      };
    }
  }
}

// CLI Interface for MCP testing
async function main() {
  const mcp = new PM33DesignExpertMCP();
  const command = process.argv[2];
  
  switch (command) {
    case 'validate':
      const filePath = process.argv[3];
      if (!filePath) {
        console.log('Usage: node pm33-design-expert-mcp.js validate <filePath>');
        process.exit(1);
      }
      const result = await mcp.validateFile(filePath);
      console.log(JSON.stringify(result, null, 2));
      break;

    case 'consult':
      const elementType = process.argv[3];
      const context = process.argv[4] || 'general';
      if (!elementType) {
        console.log('Usage: node pm33-design-expert-mcp.js consult <elementType> [context]');
        process.exit(1);
      }
      const consultation = await mcp.consultDesign(elementType, context);
      console.log(JSON.stringify(consultation, null, 2));
      break;

    case 'approve':
      const agentId = process.argv[3];
      const files = process.argv[4] ? process.argv[4].split(',') : [];
      const description = process.argv[5] || 'Approval request';
      if (!agentId || files.length === 0) {
        console.log('Usage: node pm33-design-expert-mcp.js approve <agentId> <files> [description]');
        process.exit(1);
      }
      const approval = await mcp.requestApproval(agentId, files, description);
      console.log(JSON.stringify(approval, null, 2));
      break;

    case 'design-system':
      const designSystem = await mcp.getDesignSystem();
      console.log(JSON.stringify(designSystem, null, 2));
      break;

    case 'metrics':
      const metrics = await mcp.getMetrics();
      console.log(JSON.stringify(metrics, null, 2));
      break;

    default:
      console.log('🎨 PM33 Design Expert MCP Interface');
      console.log('');
      console.log('Available commands:');
      console.log('  validate <file>                 Validate file against design standards');
      console.log('  consult <element> [context]     Get design consultation');
      console.log('  approve <agent> <files> [desc]  Request design approval');
      console.log('  design-system                   Get complete design system guide');
      console.log('  metrics                         Get enforcement metrics');
      console.log('');
      console.log('Examples:');
      console.log('  node pm33-design-expert-mcp.js validate src/HomePage.tsx');
      console.log('  node pm33-design-expert-mcp.js consult card "dashboard component"');
      console.log('  node pm33-design-expert-mcp.js approve agent-1 "src/Card.tsx" "New card component"');
      break;
  }
}

// Export for MCP usage
module.exports = { PM33DesignExpertMCP };

// Run CLI if called directly
if (require.main === module) {
  main().catch(console.error);
}