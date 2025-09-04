# PM33 App Wireframes with Demo Mode Specifications

## 🎯 Navigation & Layout System

### Top Navigation Bar
```
┌─────────────────────────────────────────────────────────────┐
│ PM33 [Logo] │ Chat │ Dashboard │ Tasks │ Data │ Settings    │
│                                                    [DEMO] ⚪ │
└─────────────────────────────────────────────────────────────┘
```

**Demo Mode Toggle:**
- **ON**: Shows dotted borders, "DEMO" badges, realistic but enhanced data
- **OFF**: Clean presentation mode, hides all demo indicators

---

## 📱 Page Wireframes

### 1. Dashboard Page (`/dashboard`)

```
┌─────────────────────────────────────────────────────────────┐
│ PM33 [Logo] │ Chat │ [Dashboard] │ Tasks │ Data │ Settings  │
│                                                    [DEMO] ⚪ │
├─────────────────────────────────────────────────────────────┤
│ Dashboard                              Last sync: 2 min ago │
│ Real-time overview                                          │
├─────────────────────────────────────────────────────────────┤
│ Key Metrics                                                │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────┐ │
│ │   23    │ │   87%   │ │  156    │ │    8hr → 10min     │ │
│ │Questions│ │Confidence│ │ Tasks   │ │   Time Savings     │ │
│ │This Week│ │ Average │ │Generated│ │      (-95%)        │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Recent Activity Feed                               [DEMO]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔴 LIVE  Activity Stream                               │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 15:23 │ Resource optimization alert                     │ │
│ │       │ Engineering at 94% - suggest priority shift    │ │
│ │ 15:18 │ Competitive intel: Feature X launch detected   │ │
│ │ 15:12 │ Strategic task completed: +12% engagement      │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ ┌───────────────┐ ┌───────────────┐                    │ │
│ │ │ View All (47) │ │ Take Action   │                    │ │
│ │ └───────────────┘ └───────────────┘                    │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Quick Actions                                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ 💬 Ask Question │ │ 📊 View Tasks   │ │ ⚙️ Integrations │ │
│ │ Strategic chat  │ │ 23 pending      │ │ 3 connected     │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Demo Mode Indicators:**
- Activity feed shows "[DEMO]" badge
- Metrics have subtle dotted borders
- "Realistic but enhanced" data (23 questions vs 2-3 typical)

---

### 2. Chat Page (`/chat`)

```
┌─────────────────────────────────────────────────────────────┐
│ PM33 [Logo] │ [Chat] │ Dashboard │ Tasks │ Data │ Settings  │
│                                                    [DEMO] ⚪ │
├─────────────────────────────────────────────────────────────┤
│ Chat                                   Questions today: 23  │
│ Strategic questions and AI analysis                         │
├─────────────────────────────────────────────────────────────┤
│ Quick Templates                                            │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Competitive     │ │ Resource        │ │ Feature         │ │
│ │ Response        │ │ Allocation      │ │ Priority        │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🎯 Ask your strategic question                          │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Should we focus on new features or fix tech debt?   │ │ │
│ │ │                                              [Ask] │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Recent Analysis                                   [DEMO]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📊 "Competitive Response to Feature Launch X"          │ │
│ │ Confidence: 94% │ Framework: Porter's Five Forces      │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ Recommendation: Fast-follower strategy with diff.      │ │
│ │ Timeline: 6 weeks │ Tasks: 8 │ ROI: $156K impact      │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│ │ │View Details │ │Export Plan  │ │Create Tasks         │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💰 "Resource allocation: Engineering vs Marketing"      │ │
│ │ Confidence: 87% │ Analysis: Cost-benefit with ROI      │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ Recommendation: 60% eng, 40% marketing for Q4          │ │
│ │ Impact: +23% efficiency │ Savings: $89K identified     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Demo Mode Indicators:**
- "Recent Analysis" section has "[DEMO]" badge
- Analysis cards show enhanced confidence scores (94% vs typical 70-80%)
- ROI numbers are compelling but realistic ($156K, $89K)

---

### 3. Tasks Page (`/tasks`)

```
┌─────────────────────────────────────────────────────────────┐
│ PM33 [Logo] │ Chat │ Dashboard │ [Tasks] │ Data │ Settings  │
│                                                    [DEMO] ⚪ │
├─────────────────────────────────────────────────────────────┤
│ Tasks                                   Generated: 156 total │
│ Workflow execution and progress                             │
├─────────────────────────────────────────────────────────────┤
│ Filters: All Status ▼ │ All Priority ▼ │ All Projects ▼    │
├─────────────────────────────────────────────────────────────┤
│ Active Tasks (23)                                 [DEMO]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔴 HIGH │ Feature X Competitive Response                │ │
│ │ Strategic Context: Fast-follower with differentiation   │ │
│ │ ├─ Define differentiation strategy        [In Progress] │ │
│ │ ├─ Analyze competitor feature gaps        [Pending]     │ │
│ │ ├─ Create engineering requirements        [Pending]     │ │
│ │ └─ Design competitive advantage features  [Not Started] │ │
│ │ Timeline: 6 weeks │ Confidence: 94% │ Impact: High      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🟡 MED │ Q4 Resource Optimization                       │ │
│ │ Strategic Context: 60% engineering, 40% marketing      │ │
│ │ ├─ Audit current resource allocation      [Completed]   │ │
│ │ ├─ Model engineering capacity scenarios   [In Progress] │ │
│ │ ├─ Calculate marketing ROI projections    [In Progress] │ │
│ │ └─ Present recommendations to leadership  [Not Started] │ │
│ │ Timeline: 3 weeks │ Confidence: 87% │ Savings: $89K     │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Integration Status                                         │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                        │
│ │ Jira    │ │ Slack   │ │ Linear  │                        │
│ │🟢 Synced│ │🟢 Active│ │⚪ Setup │                        │
│ │156 items│ │47 msgs  │ │pending  │                        │
│ └─────────┘ └─────────┘ └─────────┘                        │
├─────────────────────────────────────────────────────────────┤
│ Quick Actions                                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ ➕ Create Task  │ │ 🔄 Sync Tools   │ │ 📊 View Progress│ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Demo Mode Indicators:**
- Task list shows "[DEMO]" badge
- Enhanced task volumes (156 total vs typical 20-30)
- Strategic context preserved in task descriptions
- Integration status shows realistic but optimized sync numbers

---

### 4. Data Page (`/data`)

```
┌─────────────────────────────────────────────────────────────┐
│ PM33 [Logo] │ Chat │ Dashboard │ Tasks │ [Data] │ Settings  │
│                                                    [DEMO] ⚪ │
├─────────────────────────────────────────────────────────────┤
│ Data                                    Last update: 30s ago │
│ Analytics and insights                                      │
├─────────────────────────────────────────────────────────────┤
│ Performance Overview                                       │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────┐ │
│ │Decision │ │Resource │ │Strategic│ │Time to Decision      │ │
│ │Confiden.│ │Efficien.│ │Alignmt. │ │                     │ │
│ │   94%   │ │  +23%   │ │   87%   │ │8hr → 10min (-95%)   │ │
│ │ ↑ +12%  │ │ ↑ +8%   │ │ ↑ +15%  │ │ ↑ 47x improvement    │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Question Categories (Last 30 Days)               [DEMO]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Pie Chart Visualization]                               │ │
│ │ • Competitive Response: 34% (8 questions)              │ │
│ │ • Resource Allocation: 28% (6 questions)               │ │
│ │ • Feature Prioritization: 22% (5 questions)            │ │
│ │ • Market Positioning: 16% (4 questions)                │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ROI Impact Measurement                           [DEMO]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Value Delivered This Month                              │ │
│ │                                                         │ │
│ │ Time Savings: 47 hours saved (vs consultant analysis)  │ │
│ │ Cost Avoidance: $7,050 (consultant fees not paid)      │ │
│ │ Resource Optimization: $156K savings identified        │ │
│ │ Decision Speed: 47x faster strategic analysis          │ │
│ │                                                         │ │
│ │ Strategic Outcomes:                                     │ │
│ │ • Decision confidence: 60% → 94% average               │ │
│ │ • Task completion rate: 91% strategic alignment        │ │
│ │ • Resource efficiency: +23% improvement               │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Integration Health                                         │
│ • Jira: 99.2% reliability, 156 tasks synced               │
│ • Slack: 47 strategic updates sent, 96% engagement        │ │
│ • Analytics: Real-time data, 99.8% accuracy               │
└─────────────────────────────────────────────────────────────┘
```

**Demo Mode Indicators:**
- Chart sections show "[DEMO]" badges
- Enhanced metrics showing compelling ROI (47x improvement, $156K savings)
- Perfect integration health scores (99.2%, 99.8%)

---

### 5. Settings Page (`/settings`)

```
┌─────────────────────────────────────────────────────────────┐
│ PM33 [Logo] │ Chat │ Dashboard │ Tasks │ Data │ [Settings]  │
│                                                    [DEMO] ⚪ │
├─────────────────────────────────────────────────────────────┤
│ Settings                                                    │
│ Account | Integrations | Preferences | Billing             │
├─────────────────────────────────────────────────────────────┤
│ Account Information                                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Profile                                                 │ │
│ │ Name: [John Smith              ]                       │ │
│ │ Email: [john@company.com        ]                       │ │
│ │ Role: [Senior PM               ]                        │ │
│ │ Company: [TechCorp             ]                        │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Connected Integrations                            [DEMO]   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✅ Jira                    🟢 Connected │ Configure     │ │
│ │ Project: TECH • Sync: 156 items • 99.2% reliability    │ │
│ │                                                         │ │
│ │ ✅ Slack                   🟢 Connected │ Configure     │ │
│ │ #product-strategy • 47 messages sent • 96% engagement  │ │
│ │                                                         │ │
│ │ ⚪ Linear                  ➕ Connect                    │ │
│ │ Add Linear for enhanced strategic intelligence          │ │
│ │                                                         │ │
│ │ ⚪ Mixpanel                ➕ Connect                    │ │
│ │ Analytics integration for data-driven decisions        │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ AI Preferences                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Default Frameworks:                                     │ │
│ │ ☑️ ICE Framework  ☑️ RICE  ☑️ Porter's  ☐ Custom      │ │
│ │                                                         │ │
│ │ Confidence Threshold: [85%] (Minimum for auto-tasks)   │ │
│ │ Response Detail: [Comprehensive ▼]                     │ │
│ │ Auto-Task Generation: [Enabled ▼]                      │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Subscription: Scale $199/month (156 operations)  [DEMO] │
│ Usage: 23 questions, 2.3M operations, 12GB storage        │
└─────────────────────────────────────────────────────────────┘
```

**Demo Mode Indicators:**
- Integration section shows "[DEMO]" badge
- Enhanced usage numbers (23 questions vs typical 5-10)
- Perfect reliability scores for integrations
- Subscription shows "[DEMO]" to indicate not real billing

---

## 🎨 Demo Mode Visual Specifications

### Demo Indicator Styling
```css
/* Dotted border for demo content */
.demo-content {
  border: 2px dotted #ffd43b;
  position: relative;
  border-radius: 8px;
}

/* Demo badge positioning */
.demo-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ffd43b;
  color: #1a1a1a;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

/* Demo toggle button */
.demo-toggle {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 20px;
  color: white;
  padding: 8px 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.demo-toggle.off {
  opacity: 0.6;
}
```

### Demo Data Guidelines

**Enhanced but Realistic:**
- **Questions per week**: 23 (vs typical 3-5)
- **Confidence scores**: 87-94% (vs typical 70-80%)
- **Task generation**: 156 total (vs typical 20-30)
- **ROI numbers**: $156K, $89K, $7K (compelling but believable)
- **Time improvements**: 47x faster (8hr → 10min)
- **Integration reliability**: 99.2%, 99.8% (vs typical 95-98%)

**Strategic Context Preservation:**
- Show framework names (Porter's Five Forces, ICE, RICE)
- Include strategic reasoning in task descriptions
- Display confidence intervals and success probabilities
- Maintain connection between decisions and outcomes

---

## 🚀 Implementation Priority

### Phase 1: Core Navigation + Demo Toggle
1. Top navigation bar with simplified labels
2. Demo mode toggle functionality
3. Basic page routing

### Phase 2: Dashboard + Chat (Key Demo Pages)
1. Dashboard with live activity feed
2. Chat interface with strategic templates
3. Demo mode visual indicators

### Phase 3: Tasks + Data (Workflow Proof)
1. Task list with strategic context
2. Data analytics with ROI measurement
3. Integration status displays

### Phase 4: Settings + Polish
1. Settings with integration setup
2. Visual refinements and responsiveness
3. Performance optimization

**Success Criteria:** Each page should demonstrate PMO-level capabilities while clearly showing what's enhanced demo data vs real functionality.