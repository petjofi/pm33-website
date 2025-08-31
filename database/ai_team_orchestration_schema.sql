-- PM33 AI Team Orchestration Schema
-- Database schema for AI team coordination, task management, and portfolio analysis

-- =============================================
-- PORTFOLIO ANALYSIS AND INSIGHTS TABLES
-- =============================================

-- Store comprehensive portfolio analyses for historical tracking
CREATE TABLE portfolio_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Analysis metadata
    analysis_type VARCHAR(100) DEFAULT 'comprehensive',
    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Analysis results (JSON storage for flexibility)
    analysis_data JSONB NOT NULL,
    
    -- Key metrics for indexing and querying
    portfolio_health_score DECIMAL(3,2), -- 0.00 to 1.00
    strategic_alignment_score DECIMAL(3,2), -- 0.00 to 1.00
    total_projects INTEGER DEFAULT 0,
    high_impact_projects INTEGER DEFAULT 0,
    at_risk_projects INTEGER DEFAULT 0,
    
    -- Processing metadata
    ai_engines_used TEXT[], -- Array of AI engines involved
    processing_duration_seconds DECIMAL(8,3),
    data_sources_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_health_score CHECK (portfolio_health_score BETWEEN 0.00 AND 1.00),
    CONSTRAINT valid_alignment_score CHECK (strategic_alignment_score BETWEEN 0.00 AND 1.00)
);

-- Enable RLS for portfolio_analyses
ALTER TABLE portfolio_analyses ENABLE ROW LEVEL SECURITY;
CREATE POLICY portfolio_analyses_tenant_policy ON portfolio_analyses
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for performance
CREATE INDEX idx_portfolio_analyses_tenant_id ON portfolio_analyses(tenant_id);
CREATE INDEX idx_portfolio_analyses_timestamp ON portfolio_analyses(analysis_timestamp);
CREATE INDEX idx_portfolio_analyses_health_score ON portfolio_analyses(portfolio_health_score);
CREATE INDEX idx_portfolio_analyses_at_risk ON portfolio_analyses(at_risk_projects);

-- =============================================
-- AI TEAM COORDINATION TABLES
-- =============================================

-- Track AI team tasks and coordination
CREATE TABLE ai_team_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Task identification
    task_id VARCHAR(100) NOT NULL, -- Internal task identifier
    parent_request_id UUID, -- Links related tasks from same request
    
    -- AI team assignment
    team_type VARCHAR(50) NOT NULL, -- strategic_intelligence, workflow_execution, data_intelligence, communication
    ai_engine VARCHAR(50), -- anthropic, openai, together, etc.
    
    -- Task details
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium', -- critical, high, medium, low
    
    -- Task context and dependencies
    context_data JSONB DEFAULT '{}',
    dependencies TEXT[], -- Array of task IDs this depends on
    expected_output VARCHAR(500),
    
    -- Execution tracking
    status VARCHAR(30) DEFAULT 'pending', -- pending, assigned, in_progress, completed, failed
    assigned_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results and performance
    result_data JSONB DEFAULT '{}',
    execution_time_seconds DECIMAL(8,3),
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, task_id),
    CONSTRAINT valid_team_type CHECK (team_type IN ('strategic_intelligence', 'workflow_execution', 'data_intelligence', 'communication')),
    CONSTRAINT valid_priority CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'failed', 'cancelled'))
);

-- Enable RLS for ai_team_tasks
ALTER TABLE ai_team_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY ai_team_tasks_tenant_policy ON ai_team_tasks
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_ai_team_tasks_tenant_id ON ai_team_tasks(tenant_id);
CREATE INDEX idx_ai_team_tasks_request_id ON ai_team_tasks(parent_request_id);
CREATE INDEX idx_ai_team_tasks_team_type ON ai_team_tasks(team_type);
CREATE INDEX idx_ai_team_tasks_status ON ai_team_tasks(status);
CREATE INDEX idx_ai_team_tasks_created_at ON ai_team_tasks(created_at);

-- Store AI team coordination sessions
CREATE TABLE ai_coordination_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Session identification
    session_id VARCHAR(100) NOT NULL,
    original_request TEXT NOT NULL,
    
    -- Coordination strategy
    coordination_plan JSONB NOT NULL, -- Planning and team assignment details
    primary_team VARCHAR(50) NOT NULL,
    supporting_teams TEXT[],
    task_sequence VARCHAR(20) DEFAULT 'parallel', -- parallel, sequential
    
    -- Execution tracking
    session_status VARCHAR(30) DEFAULT 'planning', -- planning, executing, synthesizing, completed, failed
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results and metrics
    final_response TEXT,
    workflow_generated JSONB DEFAULT '{}',
    total_execution_time DECIMAL(8,3),
    teams_engaged INTEGER,
    tasks_created INTEGER,
    tasks_completed INTEGER,
    tasks_failed INTEGER,
    
    -- Cost tracking
    total_tokens_used INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,6) DEFAULT 0,
    
    -- Quality metrics
    user_satisfaction_score DECIMAL(2,1), -- 1.0 to 5.0
    response_quality_score DECIMAL(3,2), -- 0.00 to 1.00
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, session_id),
    CONSTRAINT valid_session_status CHECK (session_status IN ('planning', 'executing', 'synthesizing', 'completed', 'failed')),
    CONSTRAINT valid_task_sequence CHECK (task_sequence IN ('parallel', 'sequential')),
    CONSTRAINT valid_satisfaction_score CHECK (user_satisfaction_score BETWEEN 1.0 AND 5.0),
    CONSTRAINT valid_quality_score CHECK (response_quality_score BETWEEN 0.00 AND 1.00)
);

-- Enable RLS for ai_coordination_sessions
ALTER TABLE ai_coordination_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY ai_coordination_sessions_tenant_policy ON ai_coordination_sessions
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_ai_coordination_sessions_tenant_id ON ai_coordination_sessions(tenant_id);
CREATE INDEX idx_ai_coordination_sessions_status ON ai_coordination_sessions(session_status);
CREATE INDEX idx_ai_coordination_sessions_created_at ON ai_coordination_sessions(created_at);
CREATE INDEX idx_ai_coordination_sessions_primary_team ON ai_coordination_sessions(primary_team);

-- =============================================
-- AI TEAM PERFORMANCE AND LEARNING TABLES
-- =============================================

-- Track AI team performance metrics over time
CREATE TABLE ai_team_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Team identification
    team_type VARCHAR(50) NOT NULL,
    measurement_period DATE NOT NULL, -- Daily aggregation
    
    -- Performance metrics
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    avg_execution_time DECIMAL(8,3) DEFAULT 0,
    avg_token_usage INTEGER DEFAULT 0,
    avg_cost_per_task DECIMAL(10,6) DEFAULT 0,
    
    -- Quality metrics
    success_rate DECIMAL(5,4) DEFAULT 1.0, -- 0.0000 to 1.0000
    avg_response_quality DECIMAL(3,2) DEFAULT 1.0,
    user_satisfaction_avg DECIMAL(2,1) DEFAULT 5.0,
    
    -- Learning indicators
    pattern_recognition_score DECIMAL(3,2) DEFAULT 0.5,
    context_utilization_score DECIMAL(3,2) DEFAULT 0.5,
    cross_team_collaboration_score DECIMAL(3,2) DEFAULT 0.5,
    
    -- Improvement tracking
    week_over_week_improvement DECIMAL(5,4) DEFAULT 0,
    identified_strengths TEXT[],
    improvement_areas TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, team_type, measurement_period),
    CONSTRAINT valid_team_type_perf CHECK (team_type IN ('strategic_intelligence', 'workflow_execution', 'data_intelligence', 'communication')),
    CONSTRAINT valid_success_rate CHECK (success_rate BETWEEN 0.0000 AND 1.0000)
);

-- Enable RLS for ai_team_performance
ALTER TABLE ai_team_performance ENABLE ROW LEVEL SECURITY;
CREATE POLICY ai_team_performance_tenant_policy ON ai_team_performance
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_ai_team_performance_tenant_id ON ai_team_performance(tenant_id);
CREATE INDEX idx_ai_team_performance_team_type ON ai_team_performance(team_type);
CREATE INDEX idx_ai_team_performance_period ON ai_team_performance(measurement_period);

-- Store AI team learned patterns and insights
CREATE TABLE ai_team_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Knowledge categorization
    team_type VARCHAR(50) NOT NULL,
    knowledge_type VARCHAR(100) NOT NULL, -- pattern, insight, best_practice, common_issue
    category VARCHAR(100), -- strategic_analysis, workflow_optimization, data_pattern, communication_style
    
    -- Knowledge content
    title VARCHAR(500) NOT NULL,
    description TEXT,
    knowledge_data JSONB NOT NULL,
    
    -- Relevance and confidence
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    usage_frequency INTEGER DEFAULT 0,
    success_correlation DECIMAL(3,2) DEFAULT 0.5, -- How often this knowledge leads to success
    
    -- Context and applicability
    applicable_scenarios TEXT[],
    prerequisites JSONB DEFAULT '{}',
    success_indicators TEXT[],
    
    -- Learning metadata
    learned_from_session_id UUID,
    reinforcement_count INTEGER DEFAULT 1,
    last_applied_at TIMESTAMP WITH TIME ZONE,
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT true,
    obsolete_reason TEXT,
    superseded_by_id UUID REFERENCES ai_team_knowledge(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_team_type_knowledge CHECK (team_type IN ('strategic_intelligence', 'workflow_execution', 'data_intelligence', 'communication')),
    CONSTRAINT valid_knowledge_type CHECK (knowledge_type IN ('pattern', 'insight', 'best_practice', 'common_issue', 'optimization')),
    CONSTRAINT valid_confidence_score CHECK (confidence_score BETWEEN 0.00 AND 1.00)
);

-- Enable RLS for ai_team_knowledge
ALTER TABLE ai_team_knowledge ENABLE ROW LEVEL SECURITY;
CREATE POLICY ai_team_knowledge_tenant_policy ON ai_team_knowledge
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_ai_team_knowledge_tenant_id ON ai_team_knowledge(tenant_id);
CREATE INDEX idx_ai_team_knowledge_team_type ON ai_team_knowledge(team_type);
CREATE INDEX idx_ai_team_knowledge_type ON ai_team_knowledge(knowledge_type);
CREATE INDEX idx_ai_team_knowledge_confidence ON ai_team_knowledge(confidence_score);
CREATE INDEX idx_ai_team_knowledge_active ON ai_team_knowledge(is_active);

-- =============================================
-- STRATEGIC INSIGHTS AND RECOMMENDATIONS TABLES
-- =============================================

-- Store strategic insights generated by AI teams
CREATE TABLE strategic_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Insight classification
    insight_type VARCHAR(100) NOT NULL, -- competitive_analysis, market_opportunity, resource_optimization, risk_assessment
    category VARCHAR(100) NOT NULL, -- strategic, operational, tactical
    priority VARCHAR(20) NOT NULL, -- critical, high, medium, low
    
    -- Insight content
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    key_findings JSONB DEFAULT '[]',
    supporting_data JSONB DEFAULT '{}',
    
    -- Strategic context
    applicable_projects UUID[], -- References to integration_projects
    affected_stakeholders TEXT[],
    business_impact_areas TEXT[],
    
    -- Recommendations
    recommended_actions JSONB DEFAULT '[]',
    expected_outcomes TEXT[],
    success_metrics TEXT[],
    timeline_estimate VARCHAR(100),
    resource_requirements JSONB DEFAULT '{}',
    
    -- Confidence and validation
    confidence_score DECIMAL(3,2) NOT NULL,
    validation_status VARCHAR(30) DEFAULT 'pending', -- pending, validated, disputed, implemented
    validation_notes TEXT,
    
    -- AI generation metadata
    generated_by_session_id UUID REFERENCES ai_coordination_sessions(id),
    ai_teams_involved TEXT[],
    generation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Lifecycle and impact tracking
    status VARCHAR(30) DEFAULT 'active', -- active, implemented, obsolete, rejected
    implementation_started_at TIMESTAMP WITH TIME ZONE,
    implementation_completed_at TIMESTAMP WITH TIME ZONE,
    measured_impact_score DECIMAL(3,2), -- Actual impact after implementation
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_insight_priority CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    CONSTRAINT valid_insight_category CHECK (category IN ('strategic', 'operational', 'tactical')),
    CONSTRAINT valid_validation_status CHECK (validation_status IN ('pending', 'validated', 'disputed', 'implemented')),
    CONSTRAINT valid_insight_status CHECK (status IN ('active', 'implemented', 'obsolete', 'rejected')),
    CONSTRAINT valid_insight_confidence CHECK (confidence_score BETWEEN 0.00 AND 1.00)
);

-- Enable RLS for strategic_insights
ALTER TABLE strategic_insights ENABLE ROW LEVEL SECURITY;
CREATE POLICY strategic_insights_tenant_policy ON strategic_insights
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_strategic_insights_tenant_id ON strategic_insights(tenant_id);
CREATE INDEX idx_strategic_insights_type ON strategic_insights(insight_type);
CREATE INDEX idx_strategic_insights_priority ON strategic_insights(priority);
CREATE INDEX idx_strategic_insights_status ON strategic_insights(status);
CREATE INDEX idx_strategic_insights_confidence ON strategic_insights(confidence_score);
CREATE INDEX idx_strategic_insights_created_at ON strategic_insights(created_at);

-- =============================================
-- VIEWS FOR MONITORING AND REPORTING
-- =============================================

-- Comprehensive AI team performance dashboard
CREATE VIEW ai_team_dashboard AS
SELECT 
    atp.tenant_id,
    atp.team_type,
    atp.measurement_period,
    
    -- Performance metrics
    atp.tasks_completed,
    atp.tasks_failed,
    atp.success_rate,
    atp.avg_execution_time,
    atp.avg_cost_per_task,
    
    -- Quality metrics
    atp.avg_response_quality,
    atp.user_satisfaction_avg,
    
    -- Recent activity (last 7 days)
    COALESCE(recent_activity.recent_tasks, 0) as recent_task_count,
    COALESCE(recent_activity.recent_sessions, 0) as recent_coordination_sessions,
    
    -- Knowledge base size
    COALESCE(knowledge_count.total_knowledge, 0) as knowledge_base_size,
    COALESCE(knowledge_count.active_knowledge, 0) as active_knowledge_count,
    
    -- Strategic impact
    COALESCE(insight_count.insights_generated, 0) as insights_generated_today

FROM ai_team_performance atp

LEFT JOIN (
    SELECT 
        tenant_id,
        team_type,
        COUNT(*) as recent_tasks,
        COUNT(DISTINCT parent_request_id) as recent_sessions
    FROM ai_team_tasks
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY tenant_id, team_type
) recent_activity ON atp.tenant_id = recent_activity.tenant_id 
                 AND atp.team_type = recent_activity.team_type

LEFT JOIN (
    SELECT 
        tenant_id,
        team_type,
        COUNT(*) as total_knowledge,
        SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_knowledge
    FROM ai_team_knowledge
    GROUP BY tenant_id, team_type
) knowledge_count ON atp.tenant_id = knowledge_count.tenant_id 
                  AND atp.team_type = knowledge_count.team_type

LEFT JOIN (
    SELECT 
        si.tenant_id,
        UNNEST(si.ai_teams_involved) as team_type,
        COUNT(*) as insights_generated
    FROM strategic_insights si
    WHERE si.generation_timestamp::date = CURRENT_DATE
    GROUP BY si.tenant_id, team_type
) insight_count ON atp.tenant_id = insight_count.tenant_id 
                AND atp.team_type = insight_count.team_type

WHERE atp.measurement_period >= CURRENT_DATE - INTERVAL '30 days';

-- Portfolio health and AI insights summary
CREATE VIEW portfolio_intelligence_summary AS
SELECT 
    pa.tenant_id,
    pa.analysis_timestamp,
    pa.portfolio_health_score,
    pa.strategic_alignment_score,
    pa.total_projects,
    pa.at_risk_projects,
    
    -- AI coordination activity
    COALESCE(coord_activity.active_sessions, 0) as active_coordination_sessions,
    COALESCE(coord_activity.completed_sessions, 0) as completed_sessions_today,
    
    -- Strategic insights
    COALESCE(insight_summary.total_insights, 0) as total_strategic_insights,
    COALESCE(insight_summary.high_priority_insights, 0) as high_priority_insights,
    COALESCE(insight_summary.implemented_insights, 0) as implemented_insights,
    
    -- Team performance summary
    COALESCE(team_performance.avg_team_performance, 0) as avg_ai_team_performance,
    COALESCE(team_performance.best_performing_team, 'none') as best_performing_team

FROM portfolio_analyses pa

LEFT JOIN (
    SELECT 
        tenant_id,
        SUM(CASE WHEN session_status IN ('planning', 'executing', 'synthesizing') THEN 1 ELSE 0 END) as active_sessions,
        SUM(CASE WHEN session_status = 'completed' AND created_at::date = CURRENT_DATE THEN 1 ELSE 0 END) as completed_sessions
    FROM ai_coordination_sessions
    GROUP BY tenant_id
) coord_activity ON pa.tenant_id = coord_activity.tenant_id

LEFT JOIN (
    SELECT 
        tenant_id,
        COUNT(*) as total_insights,
        SUM(CASE WHEN priority IN ('critical', 'high') THEN 1 ELSE 0 END) as high_priority_insights,
        SUM(CASE WHEN status = 'implemented' THEN 1 ELSE 0 END) as implemented_insights
    FROM strategic_insights
    WHERE status = 'active'
    GROUP BY tenant_id
) insight_summary ON pa.tenant_id = insight_summary.tenant_id

LEFT JOIN (
    SELECT 
        tenant_id,
        AVG(success_rate) as avg_team_performance,
        (SELECT team_type FROM ai_team_performance atp2 
         WHERE atp2.tenant_id = atp1.tenant_id 
         ORDER BY success_rate DESC LIMIT 1) as best_performing_team
    FROM ai_team_performance atp1
    WHERE measurement_period >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY tenant_id
) team_performance ON pa.tenant_id = team_performance.tenant_id

WHERE pa.analysis_timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY pa.analysis_timestamp DESC;

-- Comments for documentation
COMMENT ON TABLE portfolio_analyses IS 'Comprehensive portfolio analyses with AI team insights and strategic recommendations';
COMMENT ON TABLE ai_team_tasks IS 'Individual tasks executed by specialized AI teams';
COMMENT ON TABLE ai_coordination_sessions IS 'Multi-AI team coordination sessions for complex strategic requests';
COMMENT ON TABLE ai_team_performance IS 'Performance metrics and learning indicators for AI teams';
COMMENT ON TABLE ai_team_knowledge IS 'Learned patterns and insights from AI team execution';
COMMENT ON TABLE strategic_insights IS 'Strategic insights and recommendations generated by AI teams';
COMMENT ON VIEW ai_team_dashboard IS 'Comprehensive AI team performance and activity monitoring';
COMMENT ON VIEW portfolio_intelligence_summary IS 'Portfolio health combined with AI-driven strategic intelligence';