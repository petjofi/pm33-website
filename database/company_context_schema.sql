-- PM33 Company Context Learning Schema
-- Database schema for tenant-specific context learning and AI memory

-- =============================================
-- COMPANY CONTEXT STORAGE TABLES
-- =============================================

-- Store company context entries with vector embeddings
CREATE TABLE company_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Context identification
    context_id VARCHAR(255) NOT NULL, -- Unique within tenant
    context_type VARCHAR(100) NOT NULL, -- project, work_item, user, insight, pattern, meeting, decision
    
    -- Content
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    
    -- Vector embedding for similarity search
    embedding_vector JSONB, -- Store as JSON array of floats
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    
    -- Relevance and usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    relevance_score DECIMAL(3,2) DEFAULT 0.5, -- 0.00 to 1.00
    
    -- Context relationships
    parent_context_id VARCHAR(255), -- References another context_id
    related_contexts TEXT[], -- Array of related context IDs
    
    -- Source tracking
    source_integration_id UUID REFERENCES tenant_integrations(id) ON DELETE SET NULL,
    source_type VARCHAR(100), -- integration_sync, manual_entry, ai_generated, meeting_notes
    source_metadata JSONB DEFAULT '{}',
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT true,
    archived_at TIMESTAMP WITH TIME ZONE,
    archive_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, context_id),
    CONSTRAINT valid_context_type CHECK (context_type IN ('project', 'work_item', 'user', 'insight', 'pattern', 'meeting', 'decision', 'strategy', 'risk', 'opportunity')),
    CONSTRAINT valid_source_type CHECK (source_type IN ('integration_sync', 'manual_entry', 'ai_generated', 'meeting_notes', 'document_import')),
    CONSTRAINT valid_relevance_score CHECK (relevance_score BETWEEN 0.00 AND 1.00)
);

-- Enable RLS for company_contexts
ALTER TABLE company_contexts ENABLE ROW LEVEL SECURITY;
CREATE POLICY company_contexts_tenant_policy ON company_contexts
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for performance and vector similarity (when using PgVector)
CREATE INDEX idx_company_contexts_tenant_id ON company_contexts(tenant_id);
CREATE INDEX idx_company_contexts_context_type ON company_contexts(context_type);
CREATE INDEX idx_company_contexts_is_active ON company_contexts(is_active);
CREATE INDEX idx_company_contexts_usage ON company_contexts(usage_count);
CREATE INDEX idx_company_contexts_relevance ON company_contexts(relevance_score);
CREATE INDEX idx_company_contexts_created_at ON company_contexts(created_at);
CREATE INDEX idx_company_contexts_source_integration ON company_contexts(source_integration_id);

-- Full text search index on content
CREATE INDEX idx_company_contexts_content_fts ON company_contexts USING GIN (to_tsvector('english', title || ' ' || content));

-- =============================================
-- CONTEXT INSIGHTS AND LEARNING TABLES
-- =============================================

-- Store AI-generated insights from context analysis
CREATE TABLE context_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Insight identification
    insight_id VARCHAR(255) NOT NULL,
    insight_type VARCHAR(100) NOT NULL, -- pattern, trend, opportunity, risk, recommendation
    
    -- Insight content
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    
    -- Supporting evidence
    supporting_contexts TEXT[] NOT NULL, -- Array of context_ids
    evidence_strength DECIMAL(3,2) DEFAULT 0.5, -- How strong the supporting evidence is
    
    -- Actionable recommendations
    actionable_recommendations JSONB DEFAULT '[]',
    expected_impact VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    implementation_effort VARCHAR(50) DEFAULT 'medium', -- low, medium, high
    timeline_estimate VARCHAR(100), -- immediate, 1-2 weeks, 1-2 months, quarterly
    
    -- AI generation metadata
    generated_by_model VARCHAR(100),
    generation_prompt_hash VARCHAR(64), -- Hash of the prompt used
    generation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Validation and feedback
    validation_status VARCHAR(30) DEFAULT 'pending', -- pending, validated, disputed, implemented, obsolete
    human_feedback_score DECIMAL(2,1), -- 1.0 to 5.0
    human_feedback_notes TEXT,
    validated_by_user_id UUID REFERENCES users(id),
    validated_at TIMESTAMP WITH TIME ZONE,
    
    -- Impact tracking
    implementation_status VARCHAR(30) DEFAULT 'not_started', -- not_started, in_progress, completed, abandoned
    measured_impact_score DECIMAL(3,2), -- Actual measured impact after implementation
    impact_measurement_date TIMESTAMP WITH TIME ZONE,
    roi_estimate DECIMAL(10,2), -- Return on investment estimate
    
    -- Learning and improvement
    insight_version INTEGER DEFAULT 1,
    superseded_by_insight_id VARCHAR(255),
    improvement_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, insight_id),
    CONSTRAINT valid_insight_type CHECK (insight_type IN ('pattern', 'trend', 'opportunity', 'risk', 'recommendation', 'correlation', 'anomaly')),
    CONSTRAINT valid_confidence_score CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    CONSTRAINT valid_expected_impact CHECK (expected_impact IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_implementation_effort CHECK (implementation_effort IN ('low', 'medium', 'high')),
    CONSTRAINT valid_validation_status CHECK (validation_status IN ('pending', 'validated', 'disputed', 'implemented', 'obsolete')),
    CONSTRAINT valid_implementation_status CHECK (implementation_status IN ('not_started', 'in_progress', 'completed', 'abandoned')),
    CONSTRAINT valid_human_feedback CHECK (human_feedback_score BETWEEN 1.0 AND 5.0)
);

-- Enable RLS for context_insights
ALTER TABLE context_insights ENABLE ROW LEVEL SECURITY;
CREATE POLICY context_insights_tenant_policy ON context_insights
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_context_insights_tenant_id ON context_insights(tenant_id);
CREATE INDEX idx_context_insights_type ON context_insights(insight_type);
CREATE INDEX idx_context_insights_confidence ON context_insights(confidence_score);
CREATE INDEX idx_context_insights_validation_status ON context_insights(validation_status);
CREATE INDEX idx_context_insights_implementation_status ON context_insights(implementation_status);
CREATE INDEX idx_context_insights_created_at ON context_insights(created_at);
CREATE INDEX idx_context_insights_expected_impact ON context_insights(expected_impact);

-- =============================================
-- CONTEXT LEARNING PATTERNS AND MEMORY TABLES
-- =============================================

-- Store learned patterns for context-aware AI responses
CREATE TABLE context_learning_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Pattern identification
    pattern_id VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100) NOT NULL, -- workflow, communication, decision_making, problem_solving, strategic_thinking
    pattern_category VARCHAR(100), -- planning, execution, review, crisis_response, opportunity_capture
    
    -- Pattern definition
    pattern_name VARCHAR(500) NOT NULL,
    pattern_description TEXT NOT NULL,
    trigger_conditions JSONB NOT NULL, -- Conditions that activate this pattern
    response_template JSONB NOT NULL, -- Template for AI responses using this pattern
    
    -- Learning metrics
    confidence_level DECIMAL(3,2) NOT NULL, -- How confident we are in this pattern
    usage_frequency INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) DEFAULT 0.5, -- How often this pattern leads to positive outcomes
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- Context associations
    associated_contexts TEXT[], -- Context IDs where this pattern was observed
    context_types TEXT[], -- Types of contexts where this pattern applies
    business_domains TEXT[], -- product, engineering, marketing, sales, etc.
    
    -- Pattern evolution
    learned_from_sessions TEXT[], -- AI coordination session IDs where this was learned
    reinforcement_count INTEGER DEFAULT 1, -- How many times this pattern has been reinforced
    adaptation_history JSONB DEFAULT '[]', -- History of how the pattern has evolved
    
    -- Effectiveness tracking
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    measured_outcomes JSONB DEFAULT '[]', -- Tracked outcomes when this pattern was applied
    
    -- Pattern lifecycle
    is_active BOOLEAN DEFAULT true,
    obsoleted_at TIMESTAMP WITH TIME ZONE,
    obsoleted_reason TEXT,
    replacement_pattern_id VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, pattern_id),
    CONSTRAINT valid_pattern_type CHECK (pattern_type IN ('workflow', 'communication', 'decision_making', 'problem_solving', 'strategic_thinking', 'risk_management')),
    CONSTRAINT valid_confidence_level CHECK (confidence_level BETWEEN 0.00 AND 1.00),
    CONSTRAINT valid_success_rate CHECK (success_rate BETWEEN 0.00 AND 1.00)
);

-- Enable RLS for context_learning_patterns
ALTER TABLE context_learning_patterns ENABLE ROW LEVEL SECURITY;
CREATE POLICY context_learning_patterns_tenant_policy ON context_learning_patterns
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_context_learning_patterns_tenant_id ON context_learning_patterns(tenant_id);
CREATE INDEX idx_context_learning_patterns_type ON context_learning_patterns(pattern_type);
CREATE INDEX idx_context_learning_patterns_confidence ON context_learning_patterns(confidence_level);
CREATE INDEX idx_context_learning_patterns_usage ON context_learning_patterns(usage_frequency);
CREATE INDEX idx_context_learning_patterns_success_rate ON context_learning_patterns(success_rate);
CREATE INDEX idx_context_learning_patterns_active ON context_learning_patterns(is_active);

-- =============================================
-- CONTEXT INTERACTION AND FEEDBACK TABLES
-- =============================================

-- Track how context is used in AI responses
CREATE TABLE context_usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Usage session
    usage_session_id VARCHAR(255) NOT NULL,
    ai_coordination_session_id UUID REFERENCES ai_coordination_sessions(id),
    
    -- Context usage
    context_id VARCHAR(255) NOT NULL,
    context_relevance_score DECIMAL(3,2) NOT NULL, -- How relevant the context was to the query
    usage_type VARCHAR(50) NOT NULL, -- retrieved, referenced, analyzed, synthesized
    
    -- Query and response details
    user_query_hash VARCHAR(64), -- Hash of user query for privacy
    response_section VARCHAR(100), -- Which part of response used this context
    
    -- Effectiveness metrics
    contributed_to_success BOOLEAN, -- Whether this context contributed to a successful response
    user_found_helpful BOOLEAN, -- User feedback on helpfulness
    led_to_action BOOLEAN, -- Whether this context led to user taking action
    
    -- Performance tracking
    retrieval_time_ms INTEGER,
    processing_time_ms INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_relevance_score CHECK (context_relevance_score BETWEEN 0.00 AND 1.00),
    CONSTRAINT valid_usage_type CHECK (usage_type IN ('retrieved', 'referenced', 'analyzed', 'synthesized', 'ignored'))
);

-- Enable RLS for context_usage_tracking
ALTER TABLE context_usage_tracking ENABLE ROW LEVEL SECURITY;
CREATE POLICY context_usage_tracking_tenant_policy ON context_usage_tracking
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_context_usage_tracking_tenant_id ON context_usage_tracking(tenant_id);
CREATE INDEX idx_context_usage_tracking_context_id ON context_usage_tracking(context_id);
CREATE INDEX idx_context_usage_tracking_session ON context_usage_tracking(usage_session_id);
CREATE INDEX idx_context_usage_tracking_relevance ON context_usage_tracking(context_relevance_score);
CREATE INDEX idx_context_usage_tracking_created_at ON context_usage_tracking(created_at);

-- =============================================
-- VIEWS FOR CONTEXT INTELLIGENCE AND MONITORING
-- =============================================

-- Company context learning dashboard
CREATE VIEW context_learning_dashboard AS
SELECT 
    cc.tenant_id,
    
    -- Context inventory
    COUNT(cc.id) as total_contexts,
    COUNT(CASE WHEN cc.is_active THEN 1 END) as active_contexts,
    COUNT(CASE WHEN cc.created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_contexts,
    
    -- Context distribution
    COUNT(CASE WHEN cc.context_type = 'project' THEN 1 END) as project_contexts,
    COUNT(CASE WHEN cc.context_type = 'work_item' THEN 1 END) as work_item_contexts,
    COUNT(CASE WHEN cc.context_type = 'insight' THEN 1 END) as insight_contexts,
    COUNT(CASE WHEN cc.context_type = 'pattern' THEN 1 END) as pattern_contexts,
    
    -- Usage metrics
    AVG(cc.usage_count) as avg_context_usage,
    AVG(cc.relevance_score) as avg_relevance_score,
    
    -- Vector embedding status
    COUNT(CASE WHEN cc.embedding_vector IS NOT NULL THEN 1 END) as contexts_with_embeddings,
    
    -- Data sources
    COUNT(DISTINCT cc.source_integration_id) as connected_integrations,
    
    -- Learning health indicators
    CASE 
        WHEN COUNT(cc.id) > 100 THEN 'excellent'
        WHEN COUNT(cc.id) > 50 THEN 'good'
        WHEN COUNT(cc.id) > 10 THEN 'fair'
        ELSE 'needs_data'
    END as learning_health_status,
    
    -- Context freshness
    MAX(cc.created_at) as last_context_created,
    COUNT(CASE WHEN cc.last_used_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recently_used_contexts

FROM company_contexts cc
GROUP BY cc.tenant_id;

-- Context insight effectiveness tracking
CREATE VIEW context_insights_effectiveness AS
SELECT 
    ci.tenant_id,
    ci.insight_type,
    
    -- Insight metrics
    COUNT(ci.id) as total_insights,
    COUNT(CASE WHEN ci.validation_status = 'validated' THEN 1 END) as validated_insights,
    COUNT(CASE WHEN ci.implementation_status = 'completed' THEN 1 END) as implemented_insights,
    
    -- Quality metrics
    AVG(ci.confidence_score) as avg_confidence,
    AVG(ci.human_feedback_score) as avg_human_feedback,
    AVG(ci.measured_impact_score) as avg_measured_impact,
    
    -- Distribution by impact
    COUNT(CASE WHEN ci.expected_impact = 'critical' THEN 1 END) as critical_impact_insights,
    COUNT(CASE WHEN ci.expected_impact = 'high' THEN 1 END) as high_impact_insights,
    COUNT(CASE WHEN ci.expected_impact = 'medium' THEN 1 END) as medium_impact_insights,
    
    -- ROI tracking
    AVG(ci.roi_estimate) as avg_roi_estimate,
    SUM(CASE WHEN ci.roi_estimate > 0 THEN ci.roi_estimate ELSE 0 END) as total_positive_roi,
    
    -- Time to implementation
    AVG(EXTRACT(EPOCH FROM (ci.impact_measurement_date - ci.created_at))/86400) as avg_days_to_impact

FROM context_insights ci
WHERE ci.created_at >= NOW() - INTERVAL '90 days'
GROUP BY ci.tenant_id, ci.insight_type;

-- Context usage patterns and performance
CREATE VIEW context_usage_patterns AS
SELECT 
    cut.tenant_id,
    cut.context_id,
    cc.context_type,
    cc.title,
    
    -- Usage statistics
    COUNT(cut.id) as total_usage,
    COUNT(CASE WHEN cut.created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as recent_usage,
    AVG(cut.context_relevance_score) as avg_relevance,
    
    -- Effectiveness metrics
    COUNT(CASE WHEN cut.contributed_to_success THEN 1 END) as success_contributions,
    COUNT(CASE WHEN cut.user_found_helpful THEN 1 END) as helpful_usage,
    COUNT(CASE WHEN cut.led_to_action THEN 1 END) as actionable_usage,
    
    -- Performance metrics
    AVG(cut.retrieval_time_ms) as avg_retrieval_time_ms,
    AVG(cut.processing_time_ms) as avg_processing_time_ms,
    
    -- Success rates
    COALESCE(
        COUNT(CASE WHEN cut.contributed_to_success THEN 1 END) * 100.0 / NULLIF(COUNT(cut.id), 0), 
        0
    ) as success_rate_percent,
    
    -- Last usage
    MAX(cut.created_at) as last_used_at

FROM context_usage_tracking cut
JOIN company_contexts cc ON cut.context_id = cc.context_id AND cut.tenant_id = cc.tenant_id
WHERE cut.created_at >= NOW() - INTERVAL '90 days'
GROUP BY cut.tenant_id, cut.context_id, cc.context_type, cc.title
HAVING COUNT(cut.id) > 0
ORDER BY success_rate_percent DESC, total_usage DESC;

-- Comments for documentation
COMMENT ON TABLE company_contexts IS 'Tenant-specific company context with vector embeddings for AI-powered similarity search';
COMMENT ON TABLE context_insights IS 'AI-generated insights from company context analysis with validation and impact tracking';
COMMENT ON TABLE context_learning_patterns IS 'Learned patterns for context-aware AI responses specific to each tenant';
COMMENT ON TABLE context_usage_tracking IS 'Usage tracking and effectiveness measurement for context in AI responses';
COMMENT ON VIEW context_learning_dashboard IS 'Comprehensive dashboard for monitoring context learning health and effectiveness';
COMMENT ON VIEW context_insights_effectiveness IS 'Insight quality and implementation effectiveness tracking';
COMMENT ON VIEW context_usage_patterns IS 'Context usage patterns and performance optimization insights';