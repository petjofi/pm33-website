# 🚨 PM33 Design Contract Enforcement System

## **MANDATORY FOR ALL AGENTS - NO EXCEPTIONS**

This system **BLOCKS** any UI code that violates PM33 design standards. All agents must run validation before committing code.

---

## 🎯 **Quick Start - Validate Before Commit**

```bash
# Single component validation
python mcp_design_validator.py components/ui/card.tsx

# Full directory validation  
python mcp_design_validator.py app/frontend/components

# Strict mode (warnings = errors)
python mcp_design_validator.py . --strict

# Run all validations
npm run validate:all
```

---

## 🛡️ **Enforcement Rules (BLOCKING)**

### ❌ **BLOCKED** - Code Rejected:
- Missing glass morphism on cards
- Non-brand colors (#667eea, #764ba2, #10b981 only)
- Flat shadows (shadow-sm forbidden)
- Missing gradient text on headlines
- Touch targets under 16px
- Non-8px-grid spacing

### ✅ **APPROVED** - Code Accepted:
- Glass morphism on ALL cards
- Professional shadows (shadow-glass, shadow-premium)
- Gradient text on headlines
- Hover states on interactive elements
- Brand colors only
- 8px spacing grid compliance

---

## 🔧 **System Components**

### 1. **Design Validator** (`mcp_design_validator.py`)
- **Purpose**: Real-time validation of UI components
- **Usage**: `python mcp_design_validator.py [path]`
- **Enforcement**: BLOCKS non-compliant code

### 2. **Git Pre-Commit Hook** (`.husky/pre-commit`)
- **Purpose**: Prevents bad code from entering repository
- **Automatic**: Runs on every `git commit`
- **Enforcement**: BLOCKS commits with violations

### 3. **Visual Regression Tests** (`playwright.config.ts`)
- **Purpose**: 95% visual similarity to approved designs
- **Usage**: `npm run test:visual`
- **Enforcement**: BLOCKS visual regressions

### 4. **Component Auditor** (`scripts/audit_components.py`)
- **Purpose**: Analyzes component consistency and usage
- **Usage**: `npm run audit:components`
- **Enforcement**: Reports violations and recommendations

---

## 📊 **Validation Process**

### Step 1: **Component Validation**
```bash
# Agent runs before any UI work
python mcp_design_validator.py components/ui/NewComponent.tsx
```

**Output:**
```
🔍 Validating: components/ui/NewComponent.tsx
❌ FAIL NewComponent.tsx (45.0%)

❌ ERRORS (BLOCKING):
- Missing glass morphism on card
- No gradient text on headline
- Using shadow-sm (forbidden)

⚠️ WARNINGS:
- Missing hover states
- Non-grid spacing detected

🚨 BLOCKED: Fix all errors before proceeding
```

### Step 2: **Git Protection**
```bash
git commit -m "Add new component"
# Automatic pre-commit validation runs
# If violations found: COMMIT BLOCKED
```

### Step 3: **Visual Verification**
```bash
npm run test:visual
# Compares against approved screenshots
# 95% similarity required
```

---

## 🎨 **Design Contract Rules**

### **Glass Morphism (MANDATORY)**
```css
/* ✅ CORRECT */
.glass-card {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* ❌ VIOLATION */
.card {
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

### **Gradient Text (MANDATORY)**
```css
/* ✅ CORRECT */
.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ❌ VIOLATION */
.headline {
  color: black;
}
```

### **Professional Shadows (MANDATORY)**
```css
/* ✅ CORRECT */
.shadow-premium {
  box-shadow: 0 20px 60px rgba(30, 58, 138, 0.15);
}

/* ❌ VIOLATION */
.shadow-sm {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
```

---

## 🚀 **NPM Scripts**

```json
{
  "scripts": {
    "validate:design": "python mcp_design_validator.py app/frontend/components",
    "validate:single": "python mcp_design_validator.py",
    "validate:strict": "python mcp_design_validator.py . --strict", 
    "test:visual": "npx playwright test --grep 'visual'",
    "audit:components": "python scripts/audit_components.py",
    "validate:all": "npm run validate:design && npm run test:visual && npm run audit:components"
  }
}
```

---

## 📋 **Agent Checklist**

### **Before Starting UI Work:**
- [ ] Read design contract (`PM33_DESIGN_CONTRACT.md`)
- [ ] Check existing components for reuse
- [ ] Plan glass morphism implementation
- [ ] Identify required gradients

### **During Development:**
- [ ] Use only approved brand colors
- [ ] Implement glass morphism on all cards
- [ ] Add gradient text to headlines
- [ ] Include hover states on interactive elements
- [ ] Follow 8px spacing grid

### **Before Committing:**
- [ ] Run: `python mcp_design_validator.py [component]`
- [ ] Fix ALL errors (0 errors required)
- [ ] Address warnings for 80%+ compliance
- [ ] Test visual appearance matches standards

### **Quality Gates:**
- [ ] Compliance score ≥ 80%
- [ ] Zero design contract errors
- [ ] Visual similarity ≥ 95%
- [ ] Component audit passes

---

## 🔧 **Troubleshooting**

### **Validation Fails:**
```bash
# Get detailed violation report
python mcp_design_validator.py components/ui/problem.tsx --export report.json

# Check specific rule violations
grep -n "shadow-sm" components/ui/problem.tsx
grep -n "backdrop-blur" components/ui/problem.tsx
```

### **Visual Tests Fail:**
```bash
# Update approved screenshots (only if design intentionally changed)
npx playwright test --update-snapshots

# Check diff images in test-results/
open test-results/
```

### **Git Commit Blocked:**
```bash
# Fix all violations then retry
python mcp_design_validator.py .
# Fix issues
git add .
git commit -m "Fixed design violations"
```

---

## 🎯 **Success Criteria**

### **Component Passes When:**
- ✅ 0 design contract errors
- ✅ Compliance score ≥ 80%
- ✅ Glass morphism on cards
- ✅ Gradient text on headlines
- ✅ Professional shadows
- ✅ Brand colors only
- ✅ Hover states present
- ✅ Visual similarity ≥ 95%

### **Component Blocked When:**
- ❌ Any design contract errors
- ❌ Missing glass morphism
- ❌ Flat shadows (shadow-sm)
- ❌ Non-brand colors
- ❌ Visual similarity < 95%

---

## 📈 **Monitoring & Reports**

### **Real-time Validation:**
```bash
# Component compliance dashboard
python mcp_design_validator.py . --export dashboard.json
```

### **Historical Tracking:**
- `validation_report.json` - Latest validation results
- `component_audit_report.json` - Component analysis
- `test-results/visual-results.json` - Visual test outcomes

### **Quality Metrics:**
- **Component Compliance Rate**: % passing validation
- **Design Debt**: Number of violations per component  
- **Visual Consistency**: % matching approved designs
- **Brand Adherence**: % using approved colors only

---

**🚨 ENFORCEMENT AUTHORITY: This system overrides all other development preferences. Design contract compliance is NON-NEGOTIABLE.**

*Generated by PM33 Design Contract Enforcement System*