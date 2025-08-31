# PM33 Design Expert MCP API Reference

## For Internal Claude Code Agents

When working on UI/UX projects, internal Claude Code agents can invoke the PM33 Design Expert through the existing MCP interface.

## MCP Function Names

### **`mcp_design_validator`** 
**Primary validation function for real-time design consultation**

```python
# Usage by internal agents:
python mcp_design_validator.py [file_path] [--strict]
```

**Parameters:**
- `file_path`: Path to component/file being validated  
- `--strict`: Enable zero-tolerance enforcement mode
- `--json`: Return structured JSON response for agent parsing
- `--consultation`: Get design guidance instead of just validation

**Returns:**
- Validation report with violations, recommendations, and approval status
- Compliance score (0-100%)
- Specific fix suggestions for each violation
- Design expert approval/rejection decision

---

## Agent-to-Agent Workflow

### **1. Real-Time Validation During Development**
```bash
# Agent validates component before continuing work
python mcp_design_validator.py src/components/UserCard.tsx --strict --json

# Returns structured response:
{
  "passed": false,
  "violations": 3,
  "errors": [...],
  "recommendations": [
    "Add glass morphism with backdrop-filter: blur(20px)",
    "Use PM33 brand gradient for text",
    "Replace shadow-sm with professional shadow-xl"
  ],
  "approval": "REJECTED - Fix violations before proceeding"
}
```

### **2. Design Consultation for New Components**
```bash
# Agent requests design guidance
python mcp_design_validator.py --consultation --element-type="card" --context="dashboard component"

# Returns:
{
  "recommendations": [...],
  "code_examples": [...],
  "design_principles": [...],
  "brand_standards": [...]
}
```

### **3. Pre-Commit Approval Request**
```bash
# Agent requests final approval before commit
python mcp_design_validator.py src/components/ --strict --approval-request

# Returns approval/rejection with detailed feedback
```

---

## Integration Patterns for Internal Agents

### **Pattern 1: Validation-First Development**
```python
# Agent workflow:
1. Create/modify UI component
2. Run: python mcp_design_validator.py [file] --strict --json
3. If violations found: Fix based on recommendations, repeat step 2
4. If passed: Continue with implementation
5. Pre-commit: Request final approval
```

### **Pattern 2: Design Consultation**
```python
# Agent workflow when unsure about design approach:
1. Run: python mcp_design_validator.py --consultation --element-type=[type]
2. Implement following provided code examples and principles
3. Validate implementation with Pattern 1
```

### **Pattern 3: Batch Validation**
```python
# Agent validates multiple files:
python mcp_design_validator.py src/components/ --recursive --strict --json

# Returns aggregated report for all components
```

---

## MCP Response Formats

### **Standard Validation Response**
```json
{
  "component_path": "src/components/Card.tsx",
  "timestamp": "2025-01-XX...",
  "passed": false,
  "total_violations": 5,
  "compliance_score": 72.5,
  "errors": [
    {
      "line_number": 15,
      "rule_id": "PM33_GLASS_MORPHISM", 
      "message": "Missing backdrop-filter blur effect",
      "suggestion": "Add backdrop-filter: blur(20px) for glass morphism",
      "severity": "error"
    }
  ],
  "warnings": [...],
  "recommendations": [
    "Implement glass morphism on all card components",
    "Use PM33 brand colors exclusively",
    "Add gradient text to headlines",
    "Ensure dark/light theme support with proper color contrasts",
    "Add professional hover states and shadows to buttons",
    "Implement consistent navigation with glass morphism"
  ],
  "approval": "REJECTED - 5 violations must be fixed",
  "design_expert_feedback": "Fix glass morphism implementation before proceeding"
}
```

### **Design Consultation Response**
```json
{
  "element_type": "card",
  "context": "dashboard component",
  "recommendations": [
    "Use PM33 glass morphism with backdrop-filter: blur(20px)",
    "Apply brand gradient border or background", 
    "Ensure 16px border-radius for consistency"
  ],
  "code_examples": [
    {
      "language": "tsx",
      "code": "<div className=\"bg-white/95 backdrop-blur-lg border border-white/20 rounded-2xl p-6 shadow-xl\">\n  {children}\n</div>"
    },
    {
      "language": "css", 
      "code": ".pm33-glass-card {\n  background: rgba(255, 255, 255, 0.95);\n  backdrop-filter: blur(20px);\n  border-radius: 16px;\n}"
    }
  ],
  "design_principles": [
    "Glass Morphism: Use backdrop-blur for depth and sophistication",
    "Brand Colors: Stick to #667eea, #764ba2, #10b981 palette",
    "Typography: Inter font family only, with gradient text for headlines",
    "Theme Compliance: Dark backgrounds + light text in dark mode, light backgrounds + dark text in light mode",
    "Button Standards: Professional shadows (shadow-xl), hover states (scale-105), brand colors only",
    "Navigation Consistency: Glass morphism on all nav components with theme awareness"
  ]
}
```

---

## Command Examples for Internal Agents

### **Quick Validation**
```bash
python mcp_design_validator.py HomePage.tsx --json
```

### **Strict Enforcement** 
```bash
python mcp_design_validator.py Dashboard.tsx --strict --json
```

### **Design Consultation**
```bash
python mcp_design_validator.py --consultation --element-type="button" --context="CTA button"
```

### **Batch Validation**
```bash
python mcp_design_validator.py src/ --recursive --strict --json
```

### **Approval Request**
```bash
python mcp_design_validator.py NewComponent.tsx --approval-request --agent-id="claude-frontend-agent"
```

---

## Integration with Agent Workflows

### **Before Creating Components:**
1. Consult design expert: `--consultation --element-type=[type]`
2. Follow provided code examples and principles
3. Implement component
4. Validate: `--strict --json`

### **During Development:**
1. Make changes to component
2. Validate: `--json` (quick check)
3. Fix violations based on recommendations
4. Re-validate until passed

### **Before Committing:**
1. Final validation: `--strict --approval-request`
2. Ensure approval status is "APPROVED"
3. Commit with design expert approval in message

### **Error Handling:**
```python
# Agent should check exit codes:
# 0 = Passed validation
# 1 = Violations found (check JSON for details) 
# 2 = File not found or system error
```

---

## Tracking Integration

All MCP invocations are automatically tracked in:
- `.design-enforcement-logs/metrics.json`
- `.design-enforcement-logs/violations.json` 
- `.design-enforcement-logs/approvals.json`

Agents can check enforcement activity:
```bash
./scripts/enforcer status
./scripts/enforcer report
```

---

## Design Expert Authority

The MCP Design Validator acts with **Design Expert Authority** and:
- ✅ **Approves** compliant code for commit
- ❌ **Rejects** violations with specific fix guidance
- 💡 **Provides** real-time design consultation
- 📊 **Tracks** all agent interactions for quality assurance

**Zero Tolerance Policy**: No violations are acceptable. All code must meet PM33 design standards before approval.