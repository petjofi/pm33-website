#!/usr/bin/env node

/**
 * PM33 Content Factory File Watcher
 * 
 * Monitors the PM33/final drafts directory for changes and automatically
 * triggers sync process when new content is detected
 * 
 * Usage: node scripts/content-factory-watcher.js
 * Service: Runs continuously, monitoring file changes
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Configuration
const WATCH_CONFIG = {
  // Content factory paths to monitor
  CONTENT_FACTORY_ROOT: '/Users/ssaper/Desktop/my-projects/PM33',
  FINAL_DRAFTS_DIR: 'final drafts',
  WATCH_EXTENSIONS: ['.md'],
  
  // Sync settings
  AUTO_SYNC_ENABLED: true,
  AUTO_DEPLOY_ENABLED: true,
  DEBOUNCE_DELAY: 5000, // Wait 5 seconds before triggering sync
  
  // Logging
  LOG_FILE: path.join(__dirname, '../logs/content-factory-watcher.log'),
  ENABLE_LOGGING: true
};

class ContentFactoryWatcher {
  constructor() {
    this.watchedFiles = new Set();
    this.syncTimeout = null;
    this.isWatching = false;
  }

  /**
   * Start monitoring the content factory
   */
  async start() {
    console.log('🔍 PM33 Content Factory Watcher Starting...');
    console.log(`📂 Monitoring: ${WATCH_CONFIG.CONTENT_FACTORY_ROOT}`);
    console.log('─'.repeat(50));

    try {
      await this.validatePaths();
      await this.scanExistingContent();
      await this.setupFileWatchers();
      
      this.isWatching = true;
      console.log('✅ Content Factory Watcher is running');
      console.log('🎯 Auto-sync enabled: New content will automatically deploy');
      console.log('📝 Press Ctrl+C to stop watching');
      console.log('─'.repeat(50));

      // Keep the process alive
      process.on('SIGINT', () => this.stop());
      process.on('SIGTERM', () => this.stop());

    } catch (error) {
      console.error('❌ Failed to start Content Factory Watcher:', error.message);
      process.exit(1);
    }
  }

  /**
   * Validate that all required paths exist
   */
  async validatePaths() {
    const finalDraftsPath = path.join(WATCH_CONFIG.CONTENT_FACTORY_ROOT, WATCH_CONFIG.FINAL_DRAFTS_DIR);
    
    if (!fs.existsSync(WATCH_CONFIG.CONTENT_FACTORY_ROOT)) {
      throw new Error(`Content factory not found at: ${WATCH_CONFIG.CONTENT_FACTORY_ROOT}`);
    }
    
    if (!fs.existsSync(finalDraftsPath)) {
      console.log('⚠️  Final drafts directory not found, creating...');
      fs.mkdirSync(finalDraftsPath, { recursive: true });
    }

    // Create logs directory if needed
    const logsDir = path.dirname(WATCH_CONFIG.LOG_FILE);
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }
  }

  /**
   * Scan existing content to build initial watchlist
   */
  async scanExistingContent() {
    const finalDraftsPath = path.join(WATCH_CONFIG.CONTENT_FACTORY_ROOT, WATCH_CONFIG.FINAL_DRAFTS_DIR);
    
    // Scan product-sites directory
    const productSitesPath = path.join(finalDraftsPath, 'product-sites');
    if (fs.existsSync(productSitesPath)) {
      this.scanDirectory(productSitesPath, 'product-sites');
    }
    
    // Scan blogs directory
    const blogsPath = path.join(finalDraftsPath, 'blogs');
    if (fs.existsSync(blogsPath)) {
      this.scanDirectory(blogsPath, 'blogs');
    }

    console.log(`📄 Found ${this.watchedFiles.size} existing content files`);
  }

  /**
   * Scan a directory and add markdown files to watch list
   */
  scanDirectory(dirPath, category) {
    try {
      const files = fs.readdirSync(dirPath);
      
      files.forEach(file => {
        const filePath = path.join(dirPath, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isFile() && WATCH_CONFIG.WATCH_EXTENSIONS.some(ext => file.endsWith(ext))) {
          this.watchedFiles.add(filePath);
          this.log(`📝 Watching: ${category}/${file}`);
        }
      });
    } catch (error) {
      this.log(`⚠️  Error scanning ${dirPath}: ${error.message}`);
    }
  }

  /**
   * Setup file system watchers
   */
  async setupFileWatchers() {
    const finalDraftsPath = path.join(WATCH_CONFIG.CONTENT_FACTORY_ROOT, WATCH_CONFIG.FINAL_DRAFTS_DIR);
    
    // Watch the entire final drafts directory recursively
    fs.watch(finalDraftsPath, { recursive: true }, (eventType, filename) => {
      if (filename && WATCH_CONFIG.WATCH_EXTENSIONS.some(ext => filename.endsWith(ext))) {
        const fullPath = path.join(finalDraftsPath, filename);
        this.handleFileChange(eventType, fullPath, filename);
      }
    });
  }

  /**
   * Handle file system changes
   */
  handleFileChange(eventType, fullPath, filename) {
    this.log(`🔄 File ${eventType}: ${filename}`);
    
    if (eventType === 'rename') {
      if (fs.existsSync(fullPath)) {
        // New file created
        this.log(`✨ New content detected: ${filename}`);
        this.watchedFiles.add(fullPath);
        this.scheduleSyncOperation('new_file', filename);
      } else {
        // File deleted
        this.log(`🗑️  Content deleted: ${filename}`);
        this.watchedFiles.delete(fullPath);
        this.scheduleSyncOperation('delete_file', filename);
      }
    } else if (eventType === 'change') {
      // File modified
      if (this.watchedFiles.has(fullPath)) {
        this.log(`📝 Content updated: ${filename}`);
        this.scheduleSyncOperation('update_file', filename);
      }
    }
  }

  /**
   * Schedule sync operation with debouncing
   */
  scheduleSyncOperation(operation, filename) {
    // Clear existing timeout to debounce multiple rapid changes
    if (this.syncTimeout) {
      clearTimeout(this.syncTimeout);
    }

    this.syncTimeout = setTimeout(async () => {
      if (WATCH_CONFIG.AUTO_SYNC_ENABLED) {
        await this.triggerSync(operation, filename);
      } else {
        this.log(`🔄 Sync disabled - would have synced due to: ${operation} on ${filename}`);
      }
    }, WATCH_CONFIG.DEBOUNCE_DELAY);
  }

  /**
   * Trigger the sync process
   */
  async triggerSync(operation, filename) {
    this.log(`🚀 Triggering content sync due to: ${operation} on ${filename}`);
    console.log(`\n🔄 Content change detected: ${filename}`);
    console.log('🚀 Starting automated sync process...');

    try {
      const syncProcess = spawn('node', ['scripts/sync-content-factory.js', 'sync'], {
        cwd: path.join(__dirname, '..'),
        stdio: 'pipe'
      });

      let output = '';
      syncProcess.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        console.log(text.trim());
      });

      syncProcess.stderr.on('data', (data) => {
        const text = data.toString();
        console.error(text.trim());
        this.log(`❌ Sync error: ${text}`);
      });

      syncProcess.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Automated sync completed successfully');
          this.log(`✅ Sync completed successfully for: ${filename}`);
        } else {
          console.error(`❌ Sync failed with code ${code}`);
          this.log(`❌ Sync failed with code ${code} for: ${filename}`);
        }
        console.log('🔍 Continuing to monitor for content changes...\n');
      });

    } catch (error) {
      console.error('❌ Failed to trigger sync:', error.message);
      this.log(`❌ Failed to trigger sync: ${error.message}`);
    }
  }

  /**
   * Stop the watcher
   */
  stop() {
    console.log('\n🛑 Stopping Content Factory Watcher...');
    this.isWatching = false;
    
    if (this.syncTimeout) {
      clearTimeout(this.syncTimeout);
    }
    
    this.log('🛑 Content Factory Watcher stopped');
    console.log('✅ Content Factory Watcher stopped');
    process.exit(0);
  }

  /**
   * Log message to console and file
   */
  log(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}`;
    
    if (WATCH_CONFIG.ENABLE_LOGGING) {
      try {
        fs.appendFileSync(WATCH_CONFIG.LOG_FILE, logEntry + '\n');
      } catch (error) {
        // If logging fails, continue silently
      }
    }
  }

  /**
   * Show current status
   */
  status() {
    console.log('\n📊 Content Factory Watcher Status:');
    console.log(`🔍 Watching: ${this.isWatching ? 'Active' : 'Inactive'}`);
    console.log(`📄 Files monitored: ${this.watchedFiles.size}`);
    console.log(`🚀 Auto-sync: ${WATCH_CONFIG.AUTO_SYNC_ENABLED ? 'Enabled' : 'Disabled'}`);
    console.log(`📂 Content Factory: ${WATCH_CONFIG.CONTENT_FACTORY_ROOT}`);
    console.log(`📝 Log file: ${WATCH_CONFIG.LOG_FILE}`);
    console.log('');
  }
}

// Command line interface
async function main() {
  const command = process.argv[2] || 'start';
  const watcher = new ContentFactoryWatcher();

  switch (command) {
    case 'start':
      await watcher.start();
      break;
      
    case 'status':
      watcher.status();
      break;
      
    case 'help':
      console.log(`
🔍 PM33 Content Factory Watcher

Commands:
  start    - Start monitoring content factory (default)
  status   - Show current watcher status
  help     - Show this help information

Usage:
  node scripts/content-factory-watcher.js [command]

Examples:
  node scripts/content-factory-watcher.js start
  node scripts/content-factory-watcher.js status

Features:
  🔄 Real-time monitoring of content factory changes
  🚀 Automatic sync when new content is detected
  📝 Comprehensive logging of all activities
  ⏱️  Debounced sync operations (5 second delay)
  🎯 Monitors .md files in product-sites/ and blogs/
      `);
      break;
      
    default:
      console.log(`Unknown command: ${command}`);
      console.log('Run "node scripts/content-factory-watcher.js help" for usage information');
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = ContentFactoryWatcher;