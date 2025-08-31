# PM33 UX Workflow Contract

## Core UX Principles (IMMUTABLE)

### 1. User Action Response Times (MANDATORY)
```javascript
// Required response timing for all user interactions
const UX_RESPONSE_TIMES = {
  immediate_feedback: '< 100ms',    // Visual feedback on click
  loading_indicator: '< 100ms',     // Show loading for longer operations  
  form_validation: '< 200ms',       // Real-time field validation
  search_debounce: '300ms',         // Debounced search input
  page_navigation: '< 100ms',       // Route transitions
  optimistic_update: '0ms'          // Immediate UI update
};
```

### 2. Loading State Patterns (REQUIRED)
**Every async operation MUST have:**
- **Immediate feedback** (< 100ms button state change)
- **Loading indicator** (for operations > 100ms)
- **Skeleton screens** (NOT spinners for content loading)
- **Disabled state** (prevent double-submission)
- **Success confirmation** (clear completion signal)
- **Error handling** (with recovery options)

```javascript
// MANDATORY loading state pattern
const [state, setState] = useState('idle'); // idle, loading, success, error

const handleSubmit = async () => {
  setState('loading');          // ✅ Immediate feedback
  button.disabled = true;       // ✅ Prevent double-click
  
  try {
    const result = await api.submit(data);
    setState('success');         // ✅ Success feedback
    // Show next action         // ✅ User guidance
  } catch (error) {
    setState('error');          // ✅ Error handling
    // Show retry option        // ✅ Recovery path
  }
};
```

### 3. Form Workflow Requirements (ENFORCED)
**All forms must implement:**
```javascript
const FORM_UX_PATTERNS = {
  validation: {
    realtime: true,           // Validate on blur/change
    inline_errors: true,      // Show errors per field
    success_indicators: true   // Show valid fields
  },
  submission: {
    loading_state: true,      // isSubmitting state
    disabled_submit: true,    // Disable during submit
    progress_indicator: true, // For multi-step forms
    success_redirect: true    // Clear next action
  },
  error_handling: {
    field_specific: true,     // Error per field
    general_errors: true,     // Form-level errors
    retry_mechanism: true,    // Allow resubmission
    data_preservation: true   // Don't lose user data
  }
};
```

### 4. Error Handling Patterns (MANDATORY)
**Every error message must include:**
1. **What went wrong** (clear description)
2. **Why it happened** (context if helpful)
3. **How to fix it** (actionable guidance)
4. **Alternative action** (if primary fails)

```javascript
// REQUIRED error message structure
const ErrorMessage = {
  title: "Unable to save your changes",           // What
  description: "Connection timed out",            // Why
  action: "Check your connection and try again",  // How to fix
  alternative: "Save as draft instead",           // Alternative
  buttons: [
    { text: "Try Again", action: retry },
    { text: "Save Draft", action: saveDraft }
  ]
};
```

### 5. Accessibility Requirements (NON-NEGOTIABLE)
**All interactive elements must have:**
- **Keyboard navigation** (tab order, enter/space activation)
- **Screen reader support** (ARIA labels, live regions)
- **Focus management** (visible focus states, focus trapping)
- **Color independence** (don't rely on color alone)

```javascript
// MANDATORY accessibility patterns
const AccessibleButton = (
  <button
    tabIndex={0}                    // ✅ Keyboard accessible
    aria-label="Submit form"        // ✅ Screen reader
    aria-busy={isLoading}          // ✅ Loading announcement
    onKeyDown={handleKeyPress}     // ✅ Keyboard activation
    className="focus:ring-2"       // ✅ Visible focus
  >
    {isLoading ? 'Saving...' : 'Save'}
  </button>
);
```

### 6. Cognitive Load Limits (MILLER'S LAW)
**Strict limits to prevent user overwhelm:**
```javascript
const COGNITIVE_LIMITS = {
  choices_per_screen: 7,        // Max buttons/links visible
  form_fields_per_page: 5,      // Break long forms into steps
  menu_items: 7,                // Navigation menu limit
  onboarding_steps: 3,          // Multi-step process limit
  error_messages: 3,            // Don't overwhelm with errors
  notification_stack: 3         // Max simultaneous notifications
};
```

## UX Workflow State Machine

### Form Submission Flow (REQUIRED)
```
IDLE → VALIDATING → VALID/INVALID → SUBMITTING → SUCCESS/ERROR → NEXT_ACTION

States:
- idle: Form ready for input
- validating: Real-time field validation  
- valid: All fields pass validation
- invalid: Show specific field errors
- submitting: Loading state, disabled form
- success: Clear success + next step
- error: Specific error + recovery options
```

### Data Loading Flow (REQUIRED)
```
LOADING → CONTENT/EMPTY/ERROR → RETRY/REFRESH

States:
- loading: Skeleton screen (not spinner)
- content: Data loaded successfully
- empty: No data + helpful empty state
- error: Clear error + retry mechanism
- retry: Attempt reload with feedback
```

### User Action Flow (REQUIRED)  
```
TRIGGER → IMMEDIATE_FEEDBACK → PROCESSING → RESULT → NEXT_ACTION

States:
- trigger: User clicks/interacts
- immediate_feedback: Visual change < 100ms
- processing: Loading if operation > 100ms  
- result: Success/error with clear messaging
- next_action: Guide user to logical next step
```

## Performance UX Requirements

### Response Time Targets
```javascript
const PERFORMANCE_TARGETS = {
  button_feedback: 16,      // 1 frame at 60fps
  form_validation: 200,     // Feels instant
  search_results: 300,      // After debounce
  page_transitions: 100,    // Route changes
  optimistic_updates: 0,    // Immediate UI update
  skeleton_replacement: 2000 // Max skeleton display time
};
```

### Optimization Patterns (MANDATORY)
- **Debounce search inputs** (300ms)
- **Optimistic updates** (update UI immediately, rollback on error)
- **Skeleton screens** (maintain layout, reduce perceived load time)
- **Progressive loading** (load critical content first)
- **Error boundaries** (graceful failure handling)

## Critical User Journey Validation

### Onboarding Flow (MAX 3 STEPS)
```javascript
const ONBOARDING_REQUIREMENTS = {
  max_steps: 3,
  required_elements: [
    'progress_indicator',     // Show step 1 of 3
    'skip_option',           // Allow skipping non-critical steps
    'save_progress',         // Resume where left off
    'clear_value_proposition', // Why complete this step?
    'back_navigation'        // Allow going back
  ]
};
```

### Checkout Flow (MAX 4 STEPS)
```javascript
const CHECKOUT_REQUIREMENTS = {
  max_steps: 4,
  required_elements: [
    'progress_bar',          // Visual progress through checkout
    'back_navigation',       // Edit previous steps
    'save_cart',            // Don't lose items on error
    'security_badges',       // Build trust
    'total_visible',         // Always show final cost
    'guest_checkout'         // Don't force registration
  ]
};
```

### Error Recovery (1 STEP RESOLUTION)
```javascript
const ERROR_RECOVERY_REQUIREMENTS = {
  max_steps: 1,             // Fix error in single action
  required_elements: [
    'clear_error_message',   // What went wrong
    'why_it_happened',      // Context if helpful  
    'how_to_fix',           // Actionable guidance
    'retry_option',         // Primary recovery action
    'contact_support',      // Escalation path
    'preserve_user_data'    // Don't lose their work
  ]
};
```

## Validation Commands

### MCP Integration
```bash
# Real-time UX validation during development
python mcp_ux_workflow_validator.py Component.tsx --workflow-type form_submission

# UX consultation for new workflows
python mcp_ux_workflow_validator.py --consultation --workflow-type user_action

# Comprehensive UX audit
python mcp_ux_workflow_validator.py src/ --export ux_audit_report.json

# Pre-commit UX approval
python mcp_ux_workflow_validator.py Component.tsx --strict
```

### Workflow-Specific Validation
```bash
# Form workflows
python mcp_ux_workflow_validator.py --workflow-type form_submission

# Data loading patterns
python mcp_ux_workflow_validator.py --workflow-type data_loading

# User interaction flows
python mcp_ux_workflow_validator.py --workflow-type user_action
```

## Automatic Rejection Triggers

### Critical UX Violations (BLOCKING)
- ❌ **Missing loading states** for async operations
- ❌ **No error handling** with user feedback
- ❌ **No keyboard navigation** on interactive elements
- ❌ **Missing immediate feedback** for user actions
- ❌ **More than 7 choices** on single screen
- ❌ **Form not disabled** during submission
- ❌ **No retry mechanism** for failed operations

### Performance Violations (BLOCKING)
- ❌ **Search without debouncing** (causes API spam)
- ❌ **Spinners for content loading** (use skeletons)
- ❌ **No optimistic updates** for user actions
- ❌ **Missing empty states** for data lists
- ❌ **No focus management** in modals/drawers

### Accessibility Violations (BLOCKING)
- ❌ **Missing ARIA labels** on interactive elements
- ❌ **No keyboard navigation** support
- ❌ **Color-only information** (need text/icons too)
- ❌ **Missing focus indicators** on custom elements
- ❌ **No screen reader announcements** for dynamic content

## Integration with Design System

### Combined Validation Flow
```bash
# Both design and UX validation run on every commit
git commit -m "DESIGN-APPROVED UX-APPROVED: New form component"

# Pre-commit hook runs:
# 1. Design contract validation (colors, spacing, shadows)
# 2. UX workflow validation (loading states, error handling)
# 3. Accessibility validation (keyboard, ARIA, focus)
# 4. Performance validation (debouncing, optimistic updates)
```

### Expert Approval Requirements
**ALL UI components must have:**
1. **Design Expert Approval** (visual design, brand compliance)
2. **UX Expert Approval** (workflows, user flows, accessibility)
3. **Combined Validation Pass** (both systems must pass)
4. **Expert Review** of validation reports before commit

## UX Workflow Success Metrics

### Component UX Score (0-100%)
- **Loading States**: 20 points
- **Error Handling**: 20 points  
- **Accessibility**: 20 points
- **User Feedback**: 15 points
- **Performance**: 15 points
- **Cognitive Load**: 10 points

### Passing Criteria
- **✅ 100% Score Required**: Zero tolerance for UX violations
- **⚠️ Warnings Allowed**: Non-critical suggestions for improvement
- **❌ Errors Block Commit**: Must fix before proceeding

---

*This contract ensures every PM33 component delivers exceptional user experience through enforced workflows, accessibility, and performance standards.*