# PM33 UX Workflow Expert MCP API Reference

## For Internal Claude Code Agents

When working on interactive UI components, internal Claude Code agents can invoke the PM33 UX Workflow Expert through the MCP interface for comprehensive user experience validation.

## MCP Function Names

### **`mcp_ux_workflow_validator`** 
**Primary UX workflow validation function for real-time UX consultation**

```python
# Usage by internal agents:
python mcp_ux_workflow_validator.py [file_path] [--workflow-type] [--strict]
```

**Parameters:**
- `file_path`: Path to component/file being validated  
- `--workflow-type`: Specific workflow pattern (form_submission, data_loading, user_action)
- `--strict`: Enable zero-tolerance enforcement mode
- `--consultation`: Get UX workflow guidance instead of just validation
- `--export`: Export detailed UX report to JSON

**Returns:**
- UX validation report with workflow violations, accessibility issues, and performance problems
- UX score (0-100%) based on user experience completeness
- Specific implementation suggestions for each violation
- UX expert approval/rejection decision with detailed feedback

---

## Agent-to-Agent UX Workflow

### **1. Real-Time UX Validation During Development**
```bash
# Agent validates component UX patterns before continuing work
python mcp_ux_workflow_validator.py src/components/LoginForm.tsx --strict --workflow-type form_submission

# Returns structured response:
{
  "passed": false,
  "ux_score": 72.5,
  "workflow_type": "form_submission",
  "errors": [
    {
      "rule_id": "missing_loading_state",
      "message": "Async operation missing loading state",
      "suggestion": "Add loading state: const [isLoading, setIsLoading] = useState(false)",
      "ux_impact": "Users don't know if action was received",
      "line_number": 45
    }
  ],
  "approval": "REJECTED - Fix UX workflow violations before proceeding"
}
```

### **2. UX Workflow Consultation for New Components**
```bash
# Agent requests UX workflow guidance
python mcp_ux_workflow_validator.py --consultation --workflow-type="form_submission"

# Returns:
{
  "workflow_type": "form_submission",
  "required_patterns": [
    "show_loading_state",
    "disable_submit_button",
    "show_success_or_error",
    "provide_next_action"
  ],
  "implementation_examples": [...],
  "ux_principles": [...],
  "accessibility_requirements": [...]
}
```

### **3. Pre-Commit UX Approval Request**
```bash
# Agent requests final UX approval before commit
python mcp_ux_workflow_validator.py src/components/ --strict --export ux_report.json

# Returns approval/rejection with comprehensive UX feedback
```

---

## Integration Patterns for Internal Agents

### **Pattern 1: UX-First Development**
```python
# Agent workflow:
1. Get UX consultation: python mcp_ux_workflow_validator.py --consultation --workflow-type=[type]
2. Create/modify interactive component following UX patterns
3. Validate: python mcp_ux_workflow_validator.py [file] --strict
4. If violations found: Fix based on UX suggestions, repeat step 3
5. If passed: Continue with implementation
6. Pre-commit: Request final UX approval with both design and UX validators
```

### **Pattern 2: Workflow-Specific Validation**
```python
# Form components:
python mcp_ux_workflow_validator.py ContactForm.tsx --workflow-type form_submission

# Data loading components:
python mcp_ux_workflow_validator.py UserTable.tsx --workflow-type data_loading

# Interactive components:
python mcp_ux_workflow_validator.py ActionButton.tsx --workflow-type user_action
```

### **Pattern 3: Comprehensive UX Audit**
```python
# Agent audits multiple components:
python mcp_ux_workflow_validator.py src/components/ --export comprehensive_ux_audit.json

# Returns aggregated UX report with priority violations
```

---

## MCP Response Formats

### **Standard UX Validation Response**
```json
{
  "component_path": "src/components/CheckoutForm.tsx",
  "timestamp": "2025-01-XX...",
  "workflow_type": "form_submission",
  "passed": false,
  "ux_score": 68.0,
  "total_violations": 8,
  "errors": [
    {
      "line_number": 25,
      "rule_id": "missing_loading_state",
      "message": "Form submission missing loading state",
      "suggestion": "Add const [isSubmitting, setIsSubmitting] = useState(false)",
      "ux_impact": "Users don't know if form was submitted",
      "severity": "error"
    },
    {
      "line_number": 42,
      "rule_id": "button_not_disabled_loading",
      "message": "Submit button not disabled during loading",
      "suggestion": "Add disabled={isSubmitting} to prevent double submission",
      "ux_impact": "Users can submit multiple times causing errors",
      "severity": "error"
    },
    {
      "line_number": 38,
      "rule_id": "missing_keyboard_navigation",
      "message": "Interactive elements missing keyboard navigation",
      "suggestion": "Add tabIndex and onKeyDown handlers",
      "ux_impact": "Keyboard users cannot navigate interface",
      "severity": "error"
    }
  ],
  "warnings": [
    {
      "line_number": 15,
      "rule_id": "too_many_form_fields",
      "message": "Too many form fields: 8 (max: 5)",
      "suggestion": "Break form into multiple steps",
      "ux_impact": "Users feel overwhelmed and abandon form",
      "severity": "warning"
    }
  ],
  "ux_recommendations": [
    "Implement progressive form steps for better completion rates",
    "Add real-time validation with specific error messages per field",
    "Include clear success state with next logical action",
    "Ensure keyboard navigation works for all interactive elements"
  ],
  "approval": "REJECTED - 3 critical UX violations must be fixed",
  "ux_expert_feedback": "Focus on loading states and accessibility before proceeding"
}
```

### **UX Workflow Consultation Response**
```json
{
  "workflow_type": "form_submission",
  "required_patterns": [
    "show_loading_state",
    "disable_submit_button", 
    "show_success_or_error",
    "provide_next_action"
  ],
  "implementation_examples": [
    {
      "pattern": "loading_state",
      "code": "const [isSubmitting, setIsSubmitting] = useState(false);\n\nconst handleSubmit = async () => {\n  setIsSubmitting(true);\n  try {\n    await submitForm();\n    setSuccess(true);\n  } catch (error) {\n    setError(error.message);\n  }\n  setIsSubmitting(false);\n};"
    },
    {
      "pattern": "disabled_button",
      "code": "<button disabled={isSubmitting} type=\"submit\">\n  {isSubmitting ? 'Submitting...' : 'Submit'}\n</button>"
    }
  ],
  "ux_principles": [
    "Every user action needs immediate feedback (< 100ms)",
    "Loading states prevent user confusion during async operations",
    "Error handling must include what, why, and how to fix",
    "Accessibility requires keyboard navigation and screen reader support",
    "Cognitive load limits: max 5 form fields, 7 choices per screen"
  ],
  "accessibility_requirements": [
    "All interactive elements must have keyboard navigation",
    "Form fields need proper labels and error announcements",
    "Loading states should be announced to screen readers",
    "Focus management in modals and complex interactions"
  ],
  "performance_patterns": [
    "Debounce search inputs (300ms delay)",
    "Use skeleton screens instead of spinners for content",
    "Implement optimistic updates for immediate feedback",
    "Provide retry mechanisms for failed operations"
  ]
}
```

---

## Command Examples for Internal Agents

### **UX Workflow Validation**
```bash
# Form component validation
python mcp_ux_workflow_validator.py LoginForm.tsx --workflow-type form_submission

# Data loading validation
python mcp_ux_workflow_validator.py ProductList.tsx --workflow-type data_loading

# User action validation
python mcp_ux_workflow_validator.py DeleteButton.tsx --workflow-type user_action
```

### **UX Consultation**
```bash
# Get form workflow guidance
python mcp_ux_workflow_validator.py --consultation --workflow-type form_submission

# Get data loading patterns
python mcp_ux_workflow_validator.py --consultation --workflow-type data_loading

# General UX consultation
python mcp_ux_workflow_validator.py --consultation
```

### **Comprehensive UX Audit**
```bash
# Audit entire component directory
python mcp_ux_workflow_validator.py src/components/ --export ux_audit.json

# Strict validation (warnings as errors)
python mcp_ux_workflow_validator.py Component.tsx --strict
```

### **Combined Design + UX Validation**
```bash
# Both validators must pass
python mcp_design_validator.py Component.tsx --strict
python mcp_ux_workflow_validator.py Component.tsx --strict
```

---

## Integration with Agent Workflows

### **Before Creating Interactive Components:**
1. Get UX consultation: `--consultation --workflow-type=[workflow]`
2. Follow provided implementation patterns
3. Implement component with required UX patterns
4. Validate: `--strict` mode for comprehensive checking

### **During Development:**
1. Make changes to interactive component
2. Run UX validation: `Component.tsx --json`
3. Fix UX violations based on suggestions
4. Re-validate until UX score is 100%

### **Before Committing:**
1. Final UX validation: `--strict --export`
2. Ensure UX score is 100% (zero violations)
3. Run combined design + UX validation
4. Get expert approval for both design and UX

### **Error Handling:**
```python
# Agent should check exit codes:
# 0 = UX validation passed
# >0 = Number of violations found (check JSON for details)
```

---

## UX Workflow Types

### **Form Submission Workflow**
**Required Patterns:**
- Loading state during submission
- Submit button disabled while loading
- Success/error feedback with clear messaging
- Next action guidance after completion
- Real-time field validation
- Accessibility (keyboard navigation, ARIA labels)

### **Data Loading Workflow**
**Required Patterns:**
- Skeleton screens (not spinners)
- Error state with retry mechanism
- Empty state with helpful guidance
- Loading indicators for operations > 100ms
- Graceful degradation for failed loads

### **User Action Workflow**
**Required Patterns:**
- Immediate visual feedback (< 100ms)
- Optimistic updates where appropriate
- Rollback capability for failed optimistic updates
- Confirmation for destructive actions
- Clear success/error states

---

## UX Expert Authority

The MCP UX Workflow Validator acts with **UX Expert Authority** and:
- ✅ **Approves** components meeting all UX workflow standards
- ❌ **Rejects** components with UX violations and provides specific fixes
- 💡 **Provides** real-time UX consultation and implementation guidance
- 📊 **Tracks** all UX validation activity for quality assurance
- 🎯 **Enforces** accessibility, performance, and cognitive load standards

**Zero Tolerance Policy**: All interactive components must provide excellent user experience. No UX violations are acceptable for production deployment.