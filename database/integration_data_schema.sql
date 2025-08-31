-- PM33 Integration Data Storage Schema
-- Extended schema for storing PM tool data with tenant isolation

-- =============================================
-- PM TOOL DATA STORAGE TABLES
-- =============================================

-- Store synced projects/workspaces from PM tools
CREATE TABLE integration_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Project identification
    external_id VARCHAR(255) NOT NULL, -- ID from source system
    external_key VARCHAR(100), -- Key/identifier from source system
    name VARCHAR(500) NOT NULL,
    description TEXT,
    project_type VARCHAR(100),
    
    -- Project metadata
    lead_name VARCHAR(255),
    lead_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    url TEXT,
    
    -- PM33 processing
    ai_summary TEXT, -- AI-generated project summary
    strategic_context JSONB DEFAULT '{}', -- Strategic intelligence context
    
    -- Sync tracking
    source_created_at TIMESTAMP WITH TIME ZONE,
    source_updated_at TIMESTAMP WITH TIME ZONE,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_id, external_id)
);

-- Enable RLS for integration_projects
ALTER TABLE integration_projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_projects_tenant_policy ON integration_projects
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for performance
CREATE INDEX idx_integration_projects_tenant_id ON integration_projects(tenant_id);
CREATE INDEX idx_integration_projects_integration_id ON integration_projects(integration_id);
CREATE INDEX idx_integration_projects_external_id ON integration_projects(external_id);
CREATE INDEX idx_integration_projects_updated_at ON integration_projects(updated_at);

-- Store synced work items (issues, tasks, tickets) from PM tools
CREATE TABLE integration_work_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES integration_projects(id) ON DELETE CASCADE,
    
    -- Work item identification
    external_id VARCHAR(255) NOT NULL, -- ID from source system
    external_key VARCHAR(100), -- Key/identifier from source system (e.g., JIRA-123)
    title VARCHAR(1000) NOT NULL,
    description TEXT,
    
    -- Work item classification
    work_item_type VARCHAR(100) NOT NULL, -- Bug, Story, Task, Epic, etc.
    status VARCHAR(100) NOT NULL,
    priority VARCHAR(50),
    
    -- Assignment and ownership
    assignee_name VARCHAR(255),
    assignee_email VARCHAR(255),
    reporter_name VARCHAR(255),
    reporter_email VARCHAR(255),
    
    -- Categorization
    labels TEXT[], -- Array of labels/tags
    components TEXT[], -- Array of components
    epic_key VARCHAR(100), -- Parent epic if applicable
    
    -- Progress tracking
    story_points INTEGER,
    time_estimate INTEGER, -- in minutes
    time_spent INTEGER, -- in minutes
    
    -- PM33 AI analysis
    ai_summary TEXT, -- AI-generated work item summary
    strategic_impact_score DECIMAL(3,2), -- 0.00 to 1.00
    complexity_score DECIMAL(3,2), -- 0.00 to 1.00
    urgency_score DECIMAL(3,2), -- 0.00 to 1.00
    strategic_context JSONB DEFAULT '{}', -- Strategic intelligence insights
    
    -- Timestamps
    source_created_at TIMESTAMP WITH TIME ZONE,
    source_updated_at TIMESTAMP WITH TIME ZONE,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_id, external_id)
);

-- Enable RLS for integration_work_items
ALTER TABLE integration_work_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_work_items_tenant_policy ON integration_work_items
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for performance and querying
CREATE INDEX idx_integration_work_items_tenant_id ON integration_work_items(tenant_id);
CREATE INDEX idx_integration_work_items_integration_id ON integration_work_items(integration_id);
CREATE INDEX idx_integration_work_items_project_id ON integration_work_items(project_id);
CREATE INDEX idx_integration_work_items_external_key ON integration_work_items(external_key);
CREATE INDEX idx_integration_work_items_status ON integration_work_items(status);
CREATE INDEX idx_integration_work_items_assignee ON integration_work_items(assignee_email);
CREATE INDEX idx_integration_work_items_updated_at ON integration_work_items(updated_at);
CREATE INDEX idx_integration_work_items_strategic_impact ON integration_work_items(strategic_impact_score);

-- Store user information from PM tools
CREATE TABLE integration_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- User identification
    external_id VARCHAR(255) NOT NULL, -- ID from source system
    email VARCHAR(255),
    display_name VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    
    -- User details
    avatar_url TEXT,
    timezone VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    
    -- PM33 analysis
    activity_score DECIMAL(3,2), -- 0.00 to 1.00 based on work activity
    collaboration_score DECIMAL(3,2), -- Based on cross-team work
    
    -- Sync tracking
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_id, external_id)
);

-- Enable RLS for integration_users
ALTER TABLE integration_users ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_users_tenant_policy ON integration_users
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_integration_users_tenant_id ON integration_users(tenant_id);
CREATE INDEX idx_integration_users_integration_id ON integration_users(integration_id);
CREATE INDEX idx_integration_users_email ON integration_users(email);
CREATE INDEX idx_integration_users_display_name ON integration_users(display_name);

-- =============================================
-- INTEGRATION SYNC STATUS AND HEALTH
-- =============================================

-- Track sync operations and their results
CREATE TABLE integration_sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Sync operation details
    sync_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'manual'
    sync_status VARCHAR(20) NOT NULL, -- 'running', 'completed', 'failed'
    
    -- Sync metrics
    records_synced INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    api_calls_made INTEGER DEFAULT 0,
    
    -- Error tracking
    error_messages JSONB DEFAULT '[]',
    warning_messages JSONB DEFAULT '[]',
    
    -- Performance metrics
    sync_duration_seconds DECIMAL(10,3),
    data_size_mb DECIMAL(10,3),
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_sync_status CHECK (sync_status IN ('running', 'completed', 'failed', 'cancelled'))
);

-- Enable RLS for integration_sync_logs
ALTER TABLE integration_sync_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_sync_logs_tenant_policy ON integration_sync_logs
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for performance monitoring
CREATE INDEX idx_integration_sync_logs_tenant_id ON integration_sync_logs(tenant_id);
CREATE INDEX idx_integration_sync_logs_integration_id ON integration_sync_logs(integration_id);
CREATE INDEX idx_integration_sync_logs_status ON integration_sync_logs(sync_status);
CREATE INDEX idx_integration_sync_logs_started_at ON integration_sync_logs(started_at);

-- =============================================
-- FIELD MAPPING AND TRANSFORMATION RULES
-- =============================================

-- Store field mapping configurations with AI suggestions
CREATE TABLE integration_field_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Mapping definition
    source_field VARCHAR(255) NOT NULL,
    target_field VARCHAR(255) NOT NULL,
    transformation_rule JSONB DEFAULT '{}', -- Transformation logic
    
    -- AI-powered mapping
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    is_ai_suggested BOOLEAN DEFAULT false,
    is_user_approved BOOLEAN DEFAULT false,
    is_required BOOLEAN DEFAULT false,
    
    -- Validation and testing
    validation_rules JSONB DEFAULT '{}',
    test_results JSONB DEFAULT '{}',
    success_rate DECIMAL(3,2) DEFAULT 1.00,
    
    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_id, source_field, target_field)
);

-- Enable RLS for integration_field_mappings
ALTER TABLE integration_field_mappings ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_field_mappings_tenant_policy ON integration_field_mappings
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_integration_field_mappings_tenant_id ON integration_field_mappings(tenant_id);
CREATE INDEX idx_integration_field_mappings_integration_id ON integration_field_mappings(integration_id);
CREATE INDEX idx_integration_field_mappings_confidence ON integration_field_mappings(confidence_score);

-- =============================================
-- STRATEGIC INTELLIGENCE INTEGRATION
-- =============================================

-- Link integration data to strategic contexts for AI analysis
CREATE TABLE integration_strategic_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Source integration data
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    work_item_id UUID REFERENCES integration_work_items(id) ON DELETE CASCADE,
    project_id UUID REFERENCES integration_projects(id) ON DELETE CASCADE,
    
    -- Strategic context
    strategic_conversation_id UUID REFERENCES strategic_conversations(id) ON DELETE CASCADE,
    company_context_id UUID REFERENCES company_contexts(id) ON DELETE CASCADE,
    
    -- AI analysis results
    relevance_score DECIMAL(3,2) NOT NULL, -- How relevant to strategic context
    impact_analysis JSONB DEFAULT '{}', -- AI analysis of strategic impact
    recommendations JSONB DEFAULT '[]', -- AI-generated recommendations
    
    -- Processing status
    analysis_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_analysis_status CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Enable RLS for integration_strategic_links
ALTER TABLE integration_strategic_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_strategic_links_tenant_policy ON integration_strategic_links
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for strategic analysis
CREATE INDEX idx_integration_strategic_links_tenant_id ON integration_strategic_links(tenant_id);
CREATE INDEX idx_integration_strategic_links_work_item_id ON integration_strategic_links(work_item_id);
CREATE INDEX idx_integration_strategic_links_relevance ON integration_strategic_links(relevance_score);
CREATE INDEX idx_integration_strategic_links_analysis_status ON integration_strategic_links(analysis_status);

-- =============================================
-- VIEWS FOR REPORTING AND ANALYTICS
-- =============================================

-- Comprehensive view of integration health and performance
CREATE VIEW integration_health_dashboard AS
SELECT 
    ti.id as integration_id,
    ti.tenant_id,
    ti.integration_type,
    ti.integration_name,
    ti.status,
    ti.last_sync_at,
    
    -- Project counts
    COALESCE(project_stats.project_count, 0) as project_count,
    
    -- Work item counts and metrics
    COALESCE(work_item_stats.work_item_count, 0) as work_item_count,
    COALESCE(work_item_stats.active_items, 0) as active_work_items,
    COALESCE(work_item_stats.avg_strategic_impact, 0) as avg_strategic_impact,
    
    -- Sync performance
    COALESCE(sync_stats.recent_sync_count, 0) as recent_syncs,
    COALESCE(sync_stats.avg_sync_duration, 0) as avg_sync_duration_seconds,
    COALESCE(sync_stats.success_rate, 1.0) as sync_success_rate,
    
    -- User engagement
    COALESCE(user_stats.active_user_count, 0) as active_users
    
FROM tenant_integrations ti

LEFT JOIN (
    SELECT 
        integration_id,
        COUNT(*) as project_count
    FROM integration_projects 
    WHERE status = 'active'
    GROUP BY integration_id
) project_stats ON ti.id = project_stats.integration_id

LEFT JOIN (
    SELECT 
        integration_id,
        COUNT(*) as work_item_count,
        SUM(CASE WHEN status NOT IN ('Done', 'Closed', 'Resolved') THEN 1 ELSE 0 END) as active_items,
        AVG(strategic_impact_score) as avg_strategic_impact
    FROM integration_work_items
    GROUP BY integration_id
) work_item_stats ON ti.id = work_item_stats.integration_id

LEFT JOIN (
    SELECT 
        integration_id,
        COUNT(*) as recent_sync_count,
        AVG(sync_duration_seconds) as avg_sync_duration,
        AVG(CASE WHEN sync_status = 'completed' THEN 1.0 ELSE 0.0 END) as success_rate
    FROM integration_sync_logs
    WHERE started_at >= NOW() - INTERVAL '7 days'
    GROUP BY integration_id
) sync_stats ON ti.id = sync_stats.integration_id

LEFT JOIN (
    SELECT 
        integration_id,
        COUNT(*) as active_user_count
    FROM integration_users
    WHERE is_active = true
    GROUP BY integration_id
) user_stats ON ti.id = user_stats.integration_id;

-- Comments for documentation
COMMENT ON TABLE integration_projects IS 'Synced projects/workspaces from PM tools with tenant isolation';
COMMENT ON TABLE integration_work_items IS 'Synced work items (issues, tasks) from PM tools with AI analysis';
COMMENT ON TABLE integration_users IS 'User information from PM tools with activity scoring';
COMMENT ON TABLE integration_sync_logs IS 'Sync operation tracking and performance monitoring';
COMMENT ON TABLE integration_field_mappings IS 'AI-powered field mapping configurations';
COMMENT ON TABLE integration_strategic_links IS 'Links between integration data and strategic contexts';
COMMENT ON VIEW integration_health_dashboard IS 'Comprehensive integration health and performance metrics';