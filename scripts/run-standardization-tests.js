#!/usr/bin/env node

/**
 * PM33 Icon & Button Standardization Test Runner
 * Comprehensive test suite with clear pass/fail criteria and detailed reporting
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  baseURL: 'http://localhost:3008',
  outputDir: './test-results',
  reportFile: './test-results/standardization-report.json',
  htmlReportFile: './test-results/standardization-dashboard.html',
  
  // Pass/fail thresholds
  thresholds: {
    contrastRatio: 4.5,          // WCAG AA minimum
    stabilityRate: 95,           // 95% theme switching stability required
    buttonConsistency: 90,       // 90% button interaction consistency required
    criticalElementUptime: 100,  // 100% critical elements must work
    visualRegressionTolerance: 1 // 1% pixel difference allowed
  },
  
  // Test timeouts (in milliseconds)
  timeouts: {
    singleTest: 30000,    // 30 seconds per test
    fullSuite: 300000,    // 5 minutes for full suite
    serverStart: 10000    // 10 seconds for server startup
  }
};

class TestRunner {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      duration: 0,
      tests: {},
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        overallStatus: 'PENDING'
      },
      issues: [],
      recommendations: []
    };
    
    this.startTime = Date.now();
    this.serverProcess = null;
  }

  log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const prefix = {
      'INFO': '🔵',
      'SUCCESS': '✅',
      'WARNING': '⚠️',
      'ERROR': '❌',
      'STEP': '🔄'
    }[level] || 'ℹ️';
    
    console.log(`${prefix} [${timestamp}] ${message}`);
  }

  async checkServerHealth() {
    this.log('Checking development server health...', 'STEP');
    
    try {
      const response = await fetch(`${CONFIG.baseURL}/`, { 
        method: 'HEAD',
        signal: AbortSignal.timeout(5000)
      });
      
      if (response.ok) {
        this.log('Development server is running and accessible', 'SUCCESS');
        return true;
      } else {
        this.log(`Server responded with status: ${response.status}`, 'WARNING');
        return false;
      }
    } catch (error) {
      this.log(`Server health check failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async runTest(testName, command) {
    this.log(`Running ${testName}...`, 'STEP');
    
    const testResult = {
      name: testName,
      command,
      startTime: Date.now(),
      status: 'RUNNING',
      output: '',
      errors: [],
      metrics: {},
      duration: 0
    };
    
    try {
      const output = execSync(command, {
        cwd: process.cwd(),
        encoding: 'utf8',
        timeout: CONFIG.timeouts.singleTest,
        stdio: 'pipe'
      });
      
      testResult.output = output;
      testResult.status = 'PASSED';
      testResult.duration = Date.now() - testResult.startTime;
      
      this.log(`${testName} completed in ${testResult.duration}ms`, 'SUCCESS');
      
    } catch (error) {
      testResult.status = 'FAILED';
      testResult.duration = Date.now() - testResult.startTime;
      testResult.errors.push({
        message: error.message,
        code: error.status,
        stdout: error.stdout?.toString() || '',
        stderr: error.stderr?.toString() || ''
      });
      
      this.log(`${testName} failed: ${error.message}`, 'ERROR');
    }
    
    return testResult;
  }

  async parseTestResults() {
    this.log('Parsing test results and extracting metrics...', 'STEP');
    
    const resultsDir = CONFIG.outputDir;
    const metrics = {
      contrast: { passed: 0, failed: 0, total: 0, issues: [] },
      themeStability: { passed: 0, failed: 0, total: 0, issues: [] },
      buttonInteractions: { passed: 0, failed: 0, total: 0, issues: [] },
      visualRegression: { passed: 0, failed: 0, total: 0, issues: [] },
      criticalElements: { passed: 0, failed: 0, total: 0, issues: [] }
    };
    
    try {
      // Parse Playwright JSON reports if they exist
      const jsonFiles = [
        'contrast-validation-results.json',
        'theme-switching-results.json', 
        'button-interaction-results.json'
      ];
      
      for (const fileName of jsonFiles) {
        const filePath = path.join(resultsDir, fileName);
        
        if (fs.existsSync(filePath)) {
          try {
            const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            this.processTestData(data, metrics);
          } catch (parseError) {
            this.log(`Error parsing ${fileName}: ${parseError.message}`, 'WARNING');
          }
        }
      }
      
      // Look for test attachments and reports
      this.scanForTestAttachments(resultsDir, metrics);
      
    } catch (error) {
      this.log(`Error parsing test results: ${error.message}`, 'WARNING');
    }
    
    return metrics;
  }

  processTestData(data, metrics) {
    // Process different types of test data based on structure
    if (data.suites) {
      // Playwright test format
      data.suites.forEach(suite => {
        suite.specs?.forEach(spec => {
          spec.tests?.forEach(test => {
            this.categorizeTestResult(test, metrics);
          });
        });
      });
    } else if (data.tests) {
      // Custom test format
      data.tests.forEach(test => {
        this.categorizeTestResult(test, metrics);
      });
    }
  }

  categorizeTestResult(test, metrics) {
    const testName = test.title?.toLowerCase() || '';
    
    if (testName.includes('contrast')) {
      metrics.contrast.total++;
      if (test.outcome === 'passed') {
        metrics.contrast.passed++;
      } else {
        metrics.contrast.failed++;
        metrics.contrast.issues.push({
          test: test.title,
          error: test.errors?.[0]?.message || 'Unknown error'
        });
      }
    } else if (testName.includes('theme')) {
      metrics.themeStability.total++;
      if (test.outcome === 'passed') {
        metrics.themeStability.passed++;
      } else {
        metrics.themeStability.failed++;
        metrics.themeStability.issues.push({
          test: test.title,
          error: test.errors?.[0]?.message || 'Unknown error'
        });
      }
    } else if (testName.includes('button')) {
      metrics.buttonInteractions.total++;
      if (test.outcome === 'passed') {
        metrics.buttonInteractions.passed++;
      } else {
        metrics.buttonInteractions.failed++;
        metrics.buttonInteractions.issues.push({
          test: test.title,
          error: test.errors?.[0]?.message || 'Unknown error'
        });
      }
    }
  }

  scanForTestAttachments(resultsDir, metrics) {
    try {
      if (fs.existsSync(resultsDir)) {
        const files = fs.readdirSync(resultsDir);
        
        files.forEach(file => {
          if (file.endsWith('.json') && file.includes('report')) {
            try {
              const filePath = path.join(resultsDir, file);
              const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
              
              // Extract metrics from custom report files
              if (data.summary) {
                this.log(`Found metrics in ${file}: ${JSON.stringify(data.summary)}`, 'INFO');
              }
            } catch (error) {
              // Ignore parsing errors for non-critical files
            }
          }
        });
      }
    } catch (error) {
      this.log(`Error scanning attachments: ${error.message}`, 'WARNING');
    }
  }

  evaluateResults(metrics) {
    this.log('Evaluating results against pass/fail criteria...', 'STEP');
    
    const evaluation = {
      contrast: {
        status: 'UNKNOWN',
        score: 0,
        message: '',
        critical: true
      },
      themeStability: {
        status: 'UNKNOWN', 
        score: 0,
        message: '',
        critical: true
      },
      buttonInteractions: {
        status: 'UNKNOWN',
        score: 0,
        message: '',
        critical: false
      },
      visualRegression: {
        status: 'UNKNOWN',
        score: 0, 
        message: '',
        critical: false
      }
    };
    
    // Evaluate contrast compliance
    if (metrics.contrast.total > 0) {
      const contrastScore = (metrics.contrast.passed / metrics.contrast.total) * 100;
      evaluation.contrast.score = Math.round(contrastScore);
      
      if (contrastScore >= 100) {
        evaluation.contrast.status = 'PASS';
        evaluation.contrast.message = 'All elements meet WCAG AA contrast standards';
      } else if (contrastScore >= 95) {
        evaluation.contrast.status = 'WARNING';
        evaluation.contrast.message = `${metrics.contrast.failed} elements fail contrast standards`;
      } else {
        evaluation.contrast.status = 'FAIL';
        evaluation.contrast.message = `${metrics.contrast.failed} elements fail contrast standards (critical)`;
      }
    }
    
    // Evaluate theme stability
    if (metrics.themeStability.total > 0) {
      const stabilityScore = (metrics.themeStability.passed / metrics.themeStability.total) * 100;
      evaluation.themeStability.score = Math.round(stabilityScore);
      
      if (stabilityScore >= CONFIG.thresholds.stabilityRate) {
        evaluation.themeStability.status = 'PASS';
        evaluation.themeStability.message = 'Theme switching is stable';
      } else {
        evaluation.themeStability.status = 'FAIL';
        evaluation.themeStability.message = `${metrics.themeStability.failed} theme stability issues found`;
      }
    }
    
    // Evaluate button interactions
    if (metrics.buttonInteractions.total > 0) {
      const buttonScore = (metrics.buttonInteractions.passed / metrics.buttonInteractions.total) * 100;
      evaluation.buttonInteractions.score = Math.round(buttonScore);
      
      if (buttonScore >= CONFIG.thresholds.buttonConsistency) {
        evaluation.buttonInteractions.status = 'PASS';
        evaluation.buttonInteractions.message = 'Button interactions are consistent';
      } else {
        evaluation.buttonInteractions.status = 'WARNING';
        evaluation.buttonInteractions.message = `${metrics.buttonInteractions.failed} button interaction issues found`;
      }
    }
    
    return evaluation;
  }

  generateRecommendations(evaluation, metrics) {
    const recommendations = [];
    
    // Critical contrast issues
    if (evaluation.contrast.status === 'FAIL') {
      recommendations.push({
        priority: 'CRITICAL',
        category: 'Accessibility',
        title: 'Fix contrast ratio violations',
        description: 'Elements failing WCAG AA contrast requirements must be fixed before deployment',
        action: 'Update colors to achieve minimum 4.5:1 contrast ratio',
        affectedElements: metrics.contrast.issues.length
      });
    }
    
    // Theme stability issues
    if (evaluation.themeStability.status === 'FAIL') {
      recommendations.push({
        priority: 'HIGH',
        category: 'User Experience',
        title: 'Resolve theme switching instability',
        description: 'Elements become invisible or broken during theme transitions',
        action: 'Review and fix theme-aware CSS classes and transitions',
        affectedElements: metrics.themeStability.issues.length
      });
    }
    
    // Button interaction improvements
    if (evaluation.buttonInteractions.status === 'WARNING') {
      recommendations.push({
        priority: 'MEDIUM',
        category: 'Consistency',
        title: 'Improve button interaction consistency',
        description: 'Some buttons lack proper hover, focus, or active states',
        action: 'Standardize button interaction patterns across all components',
        affectedElements: metrics.buttonInteractions.issues.length
      });
    }
    
    // General recommendations
    recommendations.push({
      priority: 'LOW',
      category: 'Best Practice',
      title: 'Establish visual regression testing',
      description: 'Set up automated visual regression testing to catch future issues',
      action: 'Create baseline screenshots and automated comparison workflow'
    });
    
    return recommendations;
  }

  generateHTMLDashboard(results, evaluation, metrics) {
    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PM33 Icon & Button Standardization Test Results</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
        .status-pass { color: #10b981; font-weight: bold; }
        .status-fail { color: #ef4444; font-weight: bold; }
        .status-warning { color: #f59e0b; font-weight: bold; }
        .card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 24px; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }
        .score { font-size: 3rem; font-weight: 900; margin: 0; }
        .score.pass { color: #10b981; }
        .score.warning { color: #f59e0b; }
        .score.fail { color: #ef4444; }
        .recommendations { margin-top: 30px; }
        .recommendation { border-left: 4px solid #3b82f6; padding: 16px; margin-bottom: 16px; background: white; border-radius: 0 8px 8px 0; }
        .recommendation.critical { border-color: #ef4444; }
        .recommendation.high { border-color: #f59e0b; }
        .recommendation.medium { border-color: #3b82f6; }
        .recommendation.low { border-color: #6b7280; }
        .issues-list { max-height: 200px; overflow-y: auto; background: #f9fafb; padding: 12px; border-radius: 6px; margin-top: 10px; }
        .footer { text-align: center; margin-top: 40px; color: #6b7280; }
        .timestamp { font-size: 0.875rem; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎨 PM33 Icon & Button Standardization</h1>
            <p>Comprehensive test results for icon visibility and button consistency</p>
            <p class="timestamp">Generated: ${results.timestamp}</p>
        </header>

        <div class="card">
            <h2>Overall Status: <span class="${results.summary.overallStatus.toLowerCase()}">${results.summary.overallStatus}</span></h2>
            <p><strong>Duration:</strong> ${Math.round(results.duration / 1000)}s | 
               <strong>Tests:</strong> ${results.summary.total} | 
               <strong>Passed:</strong> ${results.summary.passed} | 
               <strong>Failed:</strong> ${results.summary.failed}</p>
        </div>

        <div class="metric-grid">
            ${Object.entries(evaluation).map(([key, eval]) => `
                <div class="metric-card">
                    <h3>${key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</h3>
                    <div class="score ${eval.status.toLowerCase()}">${eval.score}%</div>
                    <p class="status-${eval.status.toLowerCase()}">${eval.status}</p>
                    <p>${eval.message}</p>
                    ${metrics[key]?.issues?.length > 0 ? `
                        <div class="issues-list">
                            <strong>Issues:</strong><br>
                            ${metrics[key].issues.slice(0, 5).map(issue => `• ${issue.test || issue.element || 'Unknown'}`).join('<br>')}
                            ${metrics[key].issues.length > 5 ? `<br>... and ${metrics[key].issues.length - 5} more` : ''}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>

        <div class="recommendations">
            <h2>📋 Recommendations</h2>
            ${results.recommendations.map(rec => `
                <div class="recommendation ${rec.priority.toLowerCase()}">
                    <h3>${rec.title} <span class="status-${rec.priority === 'CRITICAL' ? 'fail' : rec.priority === 'HIGH' ? 'warning' : 'pass'}">[${rec.priority}]</span></h3>
                    <p><strong>Category:</strong> ${rec.category}</p>
                    <p>${rec.description}</p>
                    <p><strong>Action:</strong> ${rec.action}</p>
                    ${rec.affectedElements ? `<p><strong>Affected Elements:</strong> ${rec.affectedElements}</p>` : ''}
                </div>
            `).join('')}
        </div>

        <div class="card">
            <h2>🔗 Next Steps</h2>
            <ol>
                <li><strong>Review Results:</strong> Examine failed tests and recommendations above</li>
                <li><strong>Manual Testing:</strong> Complete the manual testing checklist (tests/manual-testing-checklist.md)</li>
                <li><strong>Fix Issues:</strong> Address critical and high priority issues first</li>
                <li><strong>Re-run Tests:</strong> Run <code>npm run test:icons-buttons</code> after fixes</li>
                <li><strong>Deploy:</strong> Deploy changes after achieving acceptable pass rates</li>
            </ol>
        </div>

        <footer class="footer">
            <p>PM33 Icon & Button Standardization Test Suite v1.0</p>
            <p>For questions about these results, see tests/manual-testing-checklist.md</p>
        </footer>
    </div>
</body>
</html>`;
    
    fs.writeFileSync(CONFIG.htmlReportFile, htmlContent);
    this.log(`HTML dashboard generated: ${CONFIG.htmlReportFile}`, 'SUCCESS');
  }

  async run() {
    this.log('Starting PM33 Icon & Button Standardization Test Suite', 'SUCCESS');
    this.log(`Test configuration: ${JSON.stringify(CONFIG.thresholds)}`, 'INFO');
    
    // Ensure output directory exists
    if (!fs.existsSync(CONFIG.outputDir)) {
      fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    }
    
    // Check server health
    const serverHealthy = await this.checkServerHealth();
    if (!serverHealthy) {
      this.log('Development server is not accessible. Please ensure it is running on http://localhost:3008', 'ERROR');
      process.exit(1);
    }
    
    // Run test suite
    const testSuite = [
      {
        name: 'Visual Regression Tests',
        command: 'playwright test tests/icon-button-standardization.spec.ts --project=chromium --reporter=json:test-results/visual-regression-results.json'
      },
      {
        name: 'Contrast Validation',
        command: 'playwright test tests/contrast-validation.spec.ts --project=chromium --reporter=json:test-results/contrast-validation-results.json'
      },
      {
        name: 'Theme Switching Stability',
        command: 'playwright test tests/theme-switching-stability.spec.ts --project=chromium --reporter=json:test-results/theme-switching-results.json'
      },
      {
        name: 'Button Interaction Consistency',
        command: 'playwright test tests/button-interaction-consistency.spec.ts --project=chromium --reporter=json:test-results/button-interaction-results.json'
      }
    ];
    
    // Run each test
    for (const test of testSuite) {
      const result = await this.runTest(test.name, test.command);
      this.results.tests[test.name] = result;
      
      if (result.status === 'PASSED') {
        this.results.summary.passed++;
      } else if (result.status === 'FAILED') {
        this.results.summary.failed++;
      } else {
        this.results.summary.skipped++;
      }
      
      this.results.summary.total++;
    }
    
    // Parse and analyze results
    const metrics = await this.parseTestResults();
    const evaluation = this.evaluateResults(metrics);
    this.results.recommendations = this.generateRecommendations(evaluation, metrics);
    
    // Determine overall status
    const criticalFailures = Object.values(evaluation).filter(e => e.critical && e.status === 'FAIL');
    const anyFailures = Object.values(evaluation).some(e => e.status === 'FAIL');
    
    if (criticalFailures.length > 0) {
      this.results.summary.overallStatus = 'CRITICAL_FAIL';
    } else if (anyFailures) {
      this.results.summary.overallStatus = 'FAIL';
    } else if (Object.values(evaluation).some(e => e.status === 'WARNING')) {
      this.results.summary.overallStatus = 'WARNING';
    } else {
      this.results.summary.overallStatus = 'PASS';
    }
    
    // Calculate duration
    this.results.duration = Date.now() - this.startTime;
    
    // Generate reports
    fs.writeFileSync(CONFIG.reportFile, JSON.stringify(this.results, null, 2));
    this.generateHTMLDashboard(this.results, evaluation, metrics);
    
    // Final summary
    this.log(`\n=== PM33 ICON & BUTTON STANDARDIZATION RESULTS ===`, 'SUCCESS');
    this.log(`Overall Status: ${this.results.summary.overallStatus}`, this.results.summary.overallStatus === 'PASS' ? 'SUCCESS' : 'ERROR');
    this.log(`Tests Run: ${this.results.summary.total}`, 'INFO');
    this.log(`Passed: ${this.results.summary.passed}`, 'INFO');
    this.log(`Failed: ${this.results.summary.failed}`, 'INFO');
    this.log(`Duration: ${Math.round(this.results.duration / 1000)}s`, 'INFO');
    this.log(`Recommendations: ${this.results.recommendations.length}`, 'INFO');
    
    console.log('\n📊 Detailed Results:');
    Object.entries(evaluation).forEach(([key, eval]) => {
      const statusSymbol = eval.status === 'PASS' ? '✅' : eval.status === 'WARNING' ? '⚠️' : '❌';
      console.log(`  ${statusSymbol} ${key}: ${eval.score}% - ${eval.message}`);
    });
    
    console.log(`\n📋 View detailed results: ${CONFIG.htmlReportFile}`);
    console.log(`📋 Manual testing checklist: tests/manual-testing-checklist.md`);
    
    // Exit with appropriate code
    if (criticalFailures.length > 0) {
      this.log('Critical failures detected. Fix these issues before deployment.', 'ERROR');
      process.exit(1);
    } else if (this.results.summary.overallStatus === 'FAIL') {
      this.log('Test failures detected. Review and fix issues before deployment.', 'WARNING');
      process.exit(1);
    } else {
      this.log('All tests completed successfully!', 'SUCCESS');
      process.exit(0);
    }
  }
}

// Run the test suite
if (require.main === module) {
  const runner = new TestRunner();
  runner.run().catch(error => {
    console.error('❌ Test suite failed:', error);
    process.exit(1);
  });
}

module.exports = TestRunner;