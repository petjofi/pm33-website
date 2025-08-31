---
name: 🎨 Design Validation Bug
about: Bug related to MCP design validator, UX workflow validator, or PM33 design system compliance
title: '[DESIGN] '
labels: ['design-bug', 'mcp-validation', 'urgent']
assignees: ''

---

## 🎨 **Design Validation Issue Type**
- [ ] MCP Design Validator (`mcp_design_validator.py`) error or false positive
- [ ] UX Workflow Validator (`mcp_ux_workflow_validator.py`) error or false positive
- [ ] PM33 Design Contract violation
- [ ] Glass morphism implementation bug
- [ ] Theme switching (light/dark mode) issue
- [ ] Brand color usage violation
- [ ] Component design inconsistency

## 🚨 **Validation Failure Details**

### **MCP Validator Output**
```bash
# Paste the exact output from the MCP validator command
```

### **Command Used**
```bash
# Example: python mcp_design_validator.py components/ui/card.tsx --strict --json
```

### **Expected vs Actual Behavior**
**Expected:**


**Actual:**


## 🔍 **Component Information**

### **File Path**
File(s) affected: 

### **Component Type**
- [ ] PM33Card variant (ActionCard, MetricCard)
- [ ] Navigation component (PM33TopNav)
- [ ] Form component
- [ ] Dashboard component
- [ ] Marketing component
- [ ] Shared component

### **Design System Violation**
Which PM33 design standards are being violated?
- [ ] Missing glass morphism on cards
- [ ] Non-brand colors (only #667eea, #764ba2, #10b981 allowed)
- [ ] Flat shadows (shadow-sm forbidden)
- [ ] Missing gradient text on headlines
- [ ] Theme awareness issues
- [ ] CSS design tokens not used
- [ ] Safari compatibility issues (WebkitBackdropFilter)

## 🎯 **Professional Standards Impact**

### **Quality Gate Failure**
- [ ] Does not match Linear.app/Stripe.com quality
- [ ] Less than 95% similarity to approved designs
- [ ] Fails professional enterprise standards
- [ ] WCAG 2.1 AA accessibility issues

### **User Experience Impact**
- [ ] Missing loading states for async operations
- [ ] No error handling with user feedback
- [ ] Missing keyboard navigation
- [ ] Cognitive overload (>7 choices per screen)
- [ ] Form not disabled during submission

## 🛠️ **Environment Information**

### **Development Environment**
- **OS**: 
- **Node Version**: 
- **Python Version**: 
- **Browser**: 
- **MCP Validator Version**: 

### **Repository Context**
- **Branch**: 
- **Last Working Commit**: 
- **Recent Changes**: 

## 📱 **Reproduction Steps**
1. 
2. 
3. 

**Minimal reproduction case (if applicable):**
```tsx
// Paste minimal code that reproduces the issue
```

## 🎨 **Design Expert Consultation Needed**
- [ ] This issue requires PM33 Design Expert review
- [ ] Component specification unclear
- [ ] Design contract interpretation needed
- [ ] New design pattern approval required

## 🔧 **Proposed Solution**
**How do you think this should be fixed?**


## 📚 **Related Documentation**
- [ ] PM33_DESIGN_CONTRACT.md
- [ ] COMPONENT_SYSTEM.md
- [ ] DESIGN_SYSTEM.md  
- [ ] MCP_DESIGN_EXPERT_API.md
- [ ] MCP_UX_WORKFLOW_API.md

## ⚡ **Priority Level**
- [ ] **Critical**: Blocks deployment, breaks core functionality
- [ ] **High**: Affects user experience significantly
- [ ] **Medium**: Design inconsistency that should be fixed
- [ ] **Low**: Minor visual issue

## ✅ **Acceptance Criteria for Fix**
- [ ] MCP design validator passes with 0 errors
- [ ] UX workflow validator passes with 0 errors
- [ ] Component matches approved PM33 design specifications
- [ ] Professional quality standards maintained (Linear.app/Stripe.com level)
- [ ] All design contract requirements fulfilled