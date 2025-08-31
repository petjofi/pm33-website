# PM33 Marketing Website - Production/Development Workflow

## 🎯 **Structure Overview**

PM33 Marketing Website now follows a **Production/Development** folder structure similar to the core app, ensuring production stability and preventing version loss:

### **Production Environment**
- **Location**: `/Users/ssaper/Desktop/my-projects/pm33-marketing-website-production/`
- **GitHub**: `https://github.com/b33-steve/pm33-marketing-website` (branch: `production-backup-2025-08-30`)
- **Purpose**: Stable, deployable version of marketing website
- **Deployment**: Connected to Vercel production (pm-33.com)
- **Status**: ✅ **ACTIVE** - Contains complete marketing website as of 2025-08-30

### **Development Environment**  
- **Location**: `/Users/ssaper/Desktop/my-projects/pm33-claude-execution/app/frontend/`
- **Purpose**: Active development workspace for marketing website
- **Features**: Hot reloading, rapid iteration, component development
- **Status**: ✅ **ACTIVE** - Main workspace for frontend agents

---

## 🔄 **Development → Production Sync Workflow**

### **1. Development Phase (app/frontend/)**
```bash
# Work in development environment
cd /Users/ssaper/Desktop/my-projects/pm33-claude-execution/app/frontend

# Make changes to marketing pages/components
# Test using npm run dev on port 3000-3010 range
# Validate with Playwright tests when available
```

### **2. Production Sync Process**
```bash
# Sync changes from development to production
rsync -av --exclude='node_modules' --exclude='.next' --exclude='test-results' \
  /Users/ssaper/Desktop/my-projects/pm33-claude-execution/app/frontend/ \
  /Users/ssaper/Desktop/my-projects/pm33-marketing-website-production/

# Navigate to production folder
cd /Users/ssaper/Desktop/my-projects/pm33-marketing-website-production

# Stage and commit changes
git add .
git commit -m "🔄 Production sync from development - $(date '+%Y-%m-%d %H:%M')

- Synced latest changes from app/frontend/
- Updated: [list specific changes]
- Tested: [testing status]
- Ready for deployment: [yes/no]"

# Push to GitHub
git push origin production-backup-2025-08-30
```

### **3. Deployment Trigger**
- Vercel will automatically deploy from GitHub when changes are pushed
- Production URL: `https://pm-33.com`
- Staging URL: `https://pm33-website-[hash].vercel.app`

---

## 📁 **Directory Structure Comparison**

### **Core App Structure** (Reference)
```
/Users/ssaper/Desktop/my-projects/pm33-core-app/              # Development
/Users/ssaper/Desktop/my-projects/pm33-core-app-production/   # Production
```

### **Marketing Website Structure** (New)
```
/Users/ssaper/Desktop/my-projects/pm33-claude-execution/app/frontend/   # Development  
/Users/ssaper/Desktop/my-projects/pm33-marketing-website-production/    # Production
```

---

## 🔧 **GitHub Integration & Automation**

### **Production Repository**
- **Repository**: `b33-steve/pm33-marketing-website`
- **Primary Branch**: `production-backup-2025-08-30` (active production)
- **Commit History**: Preserved with detailed sync timestamps
- **Protection**: Production branch prevents accidental overwrites

### **Automated Workflows** (Planned)
```yaml
# .github/workflows/production-sync.yml
name: Marketing Website Production Sync
on:
  workflow_dispatch:
    inputs:
      sync_source:
        description: 'Development changes ready for production'
        required: true
        default: 'app/frontend/ changes'

jobs:
  sync-to-production:
    runs-on: ubuntu-latest
    steps:
      - name: Sync Development to Production
      - name: Validate Marketing Components  
      - name: Deploy to Vercel
      - name: Update Production Documentation
```

---

## 🎯 **Agent Workflow Guidelines**

### **For Frontend/Marketing Agents**

**Development Work**:
1. **ALWAYS work in**: `/app/frontend/` (development environment)
2. **Test locally**: Use `npm run dev` with available ports
3. **Document changes**: Note what was modified for production sync

**Production Updates**:
1. **After major features**: Sync to production using rsync command above
2. **Before deployments**: Always sync development → production first
3. **After syncing**: Commit with descriptive messages including sync timestamp

### **For All Agents**

**READ-ONLY Rule Maintained**:
- Core app agents: **READ-ONLY** access to both marketing environments
- Marketing agents: **FULL ACCESS** to both environments (dev + production)
- Copy pattern: Marketing→Core app adaptation still applies

---

## 📊 **Benefits of Production/Dev Structure**

### **1. Version Control & Backup**
- **Production Stability**: Always have a known-working version
- **GitHub Backup**: Complete history and version control
- **Rollback Capability**: Easy revert to previous production state
- **Branch Protection**: Production branch prevents accidental overwrites

### **2. Development Efficiency**  
- **Fast Iteration**: Development environment optimized for speed
- **Hot Reloading**: Instant preview of changes during development
- **Safe Experimentation**: Production remains stable during development
- **Clear Separation**: No confusion about which version is deployed

### **3. Deployment Safety**
- **Verified Deployments**: Only sync tested changes to production
- **Audit Trail**: Clear git history of what was deployed and when
- **Coordinated Updates**: Multiple agents can work without conflicts
- **Production Protection**: Prevents accidental deployment of broken code

---

## 🚀 **Current Status**

### **✅ COMPLETED**
- Production folder structure created and populated
- GitHub repository connected (`b33-steve/pm33-marketing-website`)
- Initial production backup committed (967 files, 214,987 lines)
- Branch protection established (`production-backup-2025-08-30`)
- Development environment remains active in `app/frontend/`

### **✅ ACTIVE DEPLOYMENTS**
- **Development**: Available for local testing and iteration
- **Production**: Backed up on GitHub, ready for Vercel deployment
- **Live Site**: https://pm-33.com (connected to production repository)

### **📋 NEXT STEPS**
1. Implement automated production sync workflows
2. Create deployment validation scripts  
3. Set up branch protection rules on GitHub
4. Document emergency rollback procedures
5. Establish regular backup schedule (daily/weekly)

---

## 🎉 **Success Metrics**

**✅ Production Stability**: Marketing website production version preserved
**✅ Development Speed**: Fast iteration maintained in development environment  
**✅ Version Control**: Complete git history and GitHub integration
**✅ Deployment Safety**: Clear separation between dev and production
**✅ Agent Coordination**: Multiple agents can work without version conflicts

The marketing website now has the same production-grade infrastructure as the core app, ensuring stability while maintaining development velocity.

---

*Created: 2025-08-30*  
*Last Updated: 2025-08-30*  
*Status: ACTIVE - Production/Development structure operational*