#!/usr/bin/env node

/**
 * PM33 Design Enforcer Activity Tracker
 * Monitors and reports all design validation activity
 */

const fs = require('fs');
const path = require('path');

class DesignEnforcerTracker {
  constructor() {
    this.logDir = path.join(process.cwd(), '.design-enforcement-logs');
    this.metricsFile = path.join(this.logDir, 'metrics.json');
    this.violationsFile = path.join(this.logDir, 'violations.json');
    this.approvalsFile = path.join(this.logDir, 'approvals.json');
    
    this.ensureLogDirectory();
    this.initializeMetrics();
  }

  ensureLogDirectory() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
      console.log('📊 Created design enforcement tracking directory');
    }
  }

  initializeMetrics() {
    const defaultMetrics = {
      totalValidations: 0,
      totalViolations: 0,
      totalApprovals: 0,
      blockedCommits: 0,
      enforcementStartDate: new Date().toISOString(),
      lastActivity: null,
      validationsByType: {
        typography: 0,
        spacing: 0,
        colors: 0,
        layouts: 0,
        visual: 0,
        'ux-workflow': 0,
        'user-flows': 0,
        'accessibility': 0,
        'performance': 0
      },
      violationsByType: {
        typography: 0,
        spacing: 0,
        colors: 0,
        layouts: 0,
        visual: 0,
        'ux-workflow': 0,
        'user-flows': 0,
        'accessibility': 0,
        'performance': 0
      },
      complianceRate: 100,
      averageViolationsPerCommit: 0
    };

    if (!fs.existsSync(this.metricsFile)) {
      this.saveMetrics(defaultMetrics);
    }
  }

  loadMetrics() {
    try {
      const data = fs.readFileSync(this.metricsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.warn('⚠️  Could not load metrics, using defaults');
      return this.initializeMetrics();
    }
  }

  saveMetrics(metrics) {
    fs.writeFileSync(this.metricsFile, JSON.stringify(metrics, null, 2));
  }

  logValidation(type, filePath, violations = []) {
    const metrics = this.loadMetrics();
    const timestamp = new Date().toISOString();
    
    // Update metrics
    metrics.totalValidations++;
    metrics.validationsByType[type] = (metrics.validationsByType[type] || 0) + 1;
    metrics.lastActivity = timestamp;
    
    if (violations.length > 0) {
      metrics.totalViolations += violations.length;
      metrics.violationsByType[type] = (metrics.violationsByType[type] || 0) + violations.length;
    }
    
    // Calculate compliance rate
    metrics.complianceRate = ((metrics.totalValidations - metrics.totalViolations) / metrics.totalValidations) * 100;
    metrics.averageViolationsPerCommit = metrics.totalViolations / Math.max(metrics.totalValidations, 1);
    
    this.saveMetrics(metrics);
    
    // Log detailed violation data
    if (violations.length > 0) {
      this.logViolations(type, filePath, violations, timestamp);
    }
    
    console.log(`📊 Logged ${type} validation: ${violations.length} violations in ${filePath}`);
  }

  logViolations(type, filePath, violations, timestamp) {
    const violationEntry = {
      timestamp,
      type,
      filePath,
      violations,
      count: violations.length
    };
    
    let allViolations = [];
    if (fs.existsSync(this.violationsFile)) {
      try {
        const data = fs.readFileSync(this.violationsFile, 'utf8');
        allViolations = JSON.parse(data);
      } catch (error) {
        console.warn('⚠️  Could not load violation history');
      }
    }
    
    allViolations.push(violationEntry);
    
    // Keep only last 1000 violations to prevent file bloat
    if (allViolations.length > 1000) {
      allViolations = allViolations.slice(-1000);
    }
    
    fs.writeFileSync(this.violationsFile, JSON.stringify(allViolations, null, 2));
  }

  logCommitBlock(reason, violations) {
    const metrics = this.loadMetrics();
    metrics.blockedCommits++;
    metrics.lastActivity = new Date().toISOString();
    this.saveMetrics(metrics);
    
    console.log(`🚨 Logged blocked commit: ${reason} (${violations} violations)`);
  }

  logDesignApproval(approver, commitMessage, approved = true) {
    const metrics = this.loadMetrics();
    const timestamp = new Date().toISOString();
    
    if (approved) {
      metrics.totalApprovals++;
    }
    metrics.lastActivity = timestamp;
    this.saveMetrics(metrics);
    
    // Log approval details
    const approvalEntry = {
      timestamp,
      approver,
      commitMessage,
      approved,
      action: approved ? 'APPROVED' : 'REJECTED'
    };
    
    let allApprovals = [];
    if (fs.existsSync(this.approvalsFile)) {
      try {
        const data = fs.readFileSync(this.approvalsFile, 'utf8');
        allApprovals = JSON.parse(data);
      } catch (error) {
        console.warn('⚠️  Could not load approval history');
      }
    }
    
    allApprovals.push(approvalEntry);
    
    // Keep only last 500 approvals
    if (allApprovals.length > 500) {
      allApprovals = allApprovals.slice(-500);
    }
    
    fs.writeFileSync(this.approvalsFile, JSON.stringify(allApprovals, null, 2));
    
    console.log(`✅ Logged design approval: ${approved ? 'APPROVED' : 'REJECTED'} by ${approver}`);
  }

  generateReport(detailed = false) {
    const metrics = this.loadMetrics();
    
    console.log('\n' + '='.repeat(70));
    console.log('📊 PM33 DESIGN ENFORCER ACTIVITY REPORT');
    console.log('='.repeat(70));
    
    console.log(`🚀 Enforcement Active Since: ${new Date(metrics.enforcementStartDate).toLocaleString()}`);
    console.log(`⏰ Last Activity: ${metrics.lastActivity ? new Date(metrics.lastActivity).toLocaleString() : 'Never'}`);
    console.log('');
    
    // Overall metrics
    console.log('📈 OVERALL METRICS:');
    console.log(`   Total Validations: ${metrics.totalValidations}`);
    console.log(`   Total Violations: ${metrics.totalViolations}`);
    console.log(`   Total Approvals: ${metrics.totalApprovals}`);
    console.log(`   Blocked Commits: ${metrics.blockedCommits}`);
    console.log(`   Compliance Rate: ${metrics.complianceRate.toFixed(1)}%`);
    console.log(`   Avg Violations/Commit: ${metrics.averageViolationsPerCommit.toFixed(2)}`);
    console.log('');
    
    // Validation breakdown
    console.log('🔍 VALIDATION BREAKDOWN:');
    Object.entries(metrics.validationsByType).forEach(([type, count]) => {
      const violations = metrics.violationsByType[type] || 0;
      const successRate = count > 0 ? ((count - violations) / count * 100).toFixed(1) : 100;
      console.log(`   ${type.charAt(0).toUpperCase() + type.slice(1)}: ${count} checks, ${violations} violations (${successRate}% success)`);
    });
    console.log('');
    
    // Recent activity
    if (detailed) {
      this.showRecentActivity();
    }
    
    // Health indicators
    console.log('🏥 ENFORCER HEALTH:');
    if (metrics.complianceRate >= 95) {
      console.log('   ✅ EXCELLENT - Design standards consistently maintained');
    } else if (metrics.complianceRate >= 85) {
      console.log('   ⚠️  GOOD - Some violations but generally compliant');
    } else {
      console.log('   🚨 NEEDS ATTENTION - High violation rate requires review');
    }
    
    if (metrics.averageViolationsPerCommit <= 0.5) {
      console.log('   ✅ LOW VIOLATION RATE - Team following design standards');
    } else if (metrics.averageViolationsPerCommit <= 2) {
      console.log('   ⚠️  MODERATE VIOLATION RATE - Room for improvement');
    } else {
      console.log('   🚨 HIGH VIOLATION RATE - Design training needed');
    }
    
    console.log('');
    console.log(`📁 Detailed logs available in: ${this.logDir}`);
    console.log('='.repeat(70));
  }

  showRecentActivity() {
    console.log('📅 RECENT ACTIVITY:');
    
    // Show recent violations
    if (fs.existsSync(this.violationsFile)) {
      try {
        const violations = JSON.parse(fs.readFileSync(this.violationsFile, 'utf8'));
        const recent = violations.slice(-5);
        
        if (recent.length > 0) {
          console.log('   Recent Violations:');
          recent.forEach(v => {
            console.log(`   ${new Date(v.timestamp).toLocaleString()}: ${v.count} ${v.type} violations in ${path.basename(v.filePath)}`);
          });
        }
      } catch (error) {
        console.log('   No recent violations data available');
      }
    }
    
    // Show recent approvals
    if (fs.existsSync(this.approvalsFile)) {
      try {
        const approvals = JSON.parse(fs.readFileSync(this.approvalsFile, 'utf8'));
        const recent = approvals.slice(-5);
        
        if (recent.length > 0) {
          console.log('   Recent Approvals:');
          recent.forEach(a => {
            console.log(`   ${new Date(a.timestamp).toLocaleString()}: ${a.action} by ${a.approver}`);
          });
        }
      } catch (error) {
        console.log('   No recent approvals data available');
      }
    }
    
    console.log('');
  }

  exportData() {
    const timestamp = new Date().toISOString().split('T')[0];
    const exportFile = path.join(this.logDir, `export-${timestamp}.json`);
    
    const exportData = {
      metrics: this.loadMetrics(),
      violations: fs.existsSync(this.violationsFile) ? JSON.parse(fs.readFileSync(this.violationsFile, 'utf8')) : [],
      approvals: fs.existsSync(this.approvalsFile) ? JSON.parse(fs.readFileSync(this.approvalsFile, 'utf8')) : [],
      exportDate: new Date().toISOString()
    };
    
    fs.writeFileSync(exportFile, JSON.stringify(exportData, null, 2));
    console.log(`📤 Exported all data to: ${exportFile}`);
    
    return exportFile;
  }

  clearOldLogs(daysToKeep = 30) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
    
    // Clear old violations
    if (fs.existsSync(this.violationsFile)) {
      try {
        let violations = JSON.parse(fs.readFileSync(this.violationsFile, 'utf8'));
        violations = violations.filter(v => new Date(v.timestamp) > cutoffDate);
        fs.writeFileSync(this.violationsFile, JSON.stringify(violations, null, 2));
        console.log(`🧹 Cleaned old violation logs (kept ${violations.length} recent entries)`);
      } catch (error) {
        console.warn('⚠️  Could not clean violation logs');
      }
    }
    
    // Clear old approvals
    if (fs.existsSync(this.approvalsFile)) {
      try {
        let approvals = JSON.parse(fs.readFileSync(this.approvalsFile, 'utf8'));
        approvals = approvals.filter(a => new Date(a.timestamp) > cutoffDate);
        fs.writeFileSync(this.approvalsFile, JSON.stringify(approvals, null, 2));
        console.log(`🧹 Cleaned old approval logs (kept ${approvals.length} recent entries)`);
      } catch (error) {
        console.warn('⚠️  Could not clean approval logs');
      }
    }
  }
}

// CLI Usage
function main() {
  const tracker = new DesignEnforcerTracker();
  const command = process.argv[2];
  
  switch (command) {
    case 'report':
      const detailed = process.argv.includes('--detailed');
      tracker.generateReport(detailed);
      break;
      
    case 'export':
      tracker.exportData();
      break;
      
    case 'clean':
      const days = parseInt(process.argv[3]) || 30;
      tracker.clearOldLogs(days);
      break;
      
    case 'log-validation':
      const type = process.argv[3];
      const filePath = process.argv[4];
      const violationCount = parseInt(process.argv[5]) || 0;
      if (type && filePath) {
        const violations = Array(violationCount).fill({ message: 'Validation violation' });
        tracker.logValidation(type, filePath, violations);
      } else {
        console.log('Usage: node design-enforcer-tracker.js log-validation <type> <filePath> [violationCount]');
      }
      break;
      
    case 'log-approval':
      const approver = process.argv[3];
      const message = process.argv[4];
      const approved = process.argv[5] !== 'false';
      if (approver && message) {
        tracker.logDesignApproval(approver, message, approved);
      } else {
        console.log('Usage: node design-enforcer-tracker.js log-approval <approver> <message> [true/false]');
      }
      break;
      
    default:
      console.log('📊 PM33 Design Enforcer Tracker');
      console.log('');
      console.log('Commands:');
      console.log('  report [--detailed]     Show activity report');
      console.log('  export                  Export all data to JSON');
      console.log('  clean [days]            Clean logs older than N days (default: 30)');
      console.log('  log-validation <type> <file> [violations]  Log validation activity');
      console.log('  log-approval <approver> <message> [approved]  Log design approval');
      console.log('');
      console.log('Examples:');
      console.log('  node design-enforcer-tracker.js report');
      console.log('  node design-enforcer-tracker.js report --detailed');
      console.log('  node design-enforcer-tracker.js export');
      console.log('  node design-enforcer-tracker.js clean 14');
      break;
  }
}

// Export for integration with other scripts
module.exports = { DesignEnforcerTracker };

// Run CLI if called directly
if (require.main === module) {
  main();
}