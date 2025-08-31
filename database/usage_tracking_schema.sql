-- PM33 Usage Tracking Schema
-- Extended schema for tracking integration usage metrics and billing

-- =============================================
-- INTEGRATION USAGE TRACKING TABLES
-- =============================================

-- Track daily usage metrics per integration for billing
CREATE TABLE integration_usage_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Usage period
    usage_date DATE NOT NULL,
    
    -- API usage metrics
    api_calls_made INTEGER DEFAULT 0,
    data_transfer_mb DECIMAL(10,3) DEFAULT 0,
    rate_limit_hits INTEGER DEFAULT 0,
    
    -- Sync metrics
    records_synced INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    sync_count INTEGER DEFAULT 0,
    sync_duration_seconds DECIMAL(10,3) DEFAULT 0,
    
    -- Performance metrics
    avg_response_time_ms DECIMAL(8,2) DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 1.0, -- 0.0000 to 1.0000
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate daily records
    UNIQUE(tenant_id, integration_id, usage_date)
);

-- Enable RLS for integration_usage_metrics
ALTER TABLE integration_usage_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_usage_metrics_tenant_policy ON integration_usage_metrics
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes for performance
CREATE INDEX idx_integration_usage_metrics_tenant_id ON integration_usage_metrics(tenant_id);
CREATE INDEX idx_integration_usage_metrics_integration_id ON integration_usage_metrics(integration_id);
CREATE INDEX idx_integration_usage_metrics_date ON integration_usage_metrics(usage_date);
CREATE INDEX idx_integration_usage_metrics_api_calls ON integration_usage_metrics(api_calls_made);

-- Track aggregated usage by tenant for billing and reporting
CREATE TABLE tenant_usage_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Usage period
    usage_date DATE NOT NULL,
    
    -- Aggregated metrics across all integrations
    total_api_calls INTEGER DEFAULT 0,
    total_data_transfer_mb DECIMAL(10,3) DEFAULT 0,
    total_records_synced INTEGER DEFAULT 0,
    total_sync_count INTEGER DEFAULT 0,
    total_sync_duration DECIMAL(10,3) DEFAULT 0,
    active_integrations INTEGER DEFAULT 0,
    
    -- Billing metrics
    estimated_cost_usd DECIMAL(10,2) DEFAULT 0,
    billing_tier VARCHAR(50) DEFAULT 'free',
    
    -- Quality metrics
    overall_success_rate DECIMAL(5,4) DEFAULT 1.0,
    avg_response_time_ms DECIMAL(8,2) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, usage_date)
);

-- Enable RLS for tenant_usage_summary
ALTER TABLE tenant_usage_summary ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_usage_summary_tenant_policy ON tenant_usage_summary
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_tenant_usage_summary_tenant_id ON tenant_usage_summary(tenant_id);
CREATE INDEX idx_tenant_usage_summary_date ON tenant_usage_summary(usage_date);
CREATE INDEX idx_tenant_usage_summary_billing_tier ON tenant_usage_summary(billing_tier);

-- =============================================
-- SYNC SCHEDULER CONFIGURATION TABLES
-- =============================================

-- Store sync job configurations and schedules
CREATE TABLE sync_job_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Job configuration
    job_name VARCHAR(255) NOT NULL,
    sync_frequency VARCHAR(50) NOT NULL, -- 'realtime', 'every_15_min', 'hourly', 'daily', 'weekly', 'manual'
    is_enabled BOOLEAN DEFAULT true,
    
    -- Schedule details
    cron_expression VARCHAR(100), -- For custom schedules
    timezone VARCHAR(100) DEFAULT 'UTC',
    
    -- Sync configuration
    sync_type VARCHAR(50) DEFAULT 'incremental', -- 'full', 'incremental'
    batch_size INTEGER DEFAULT 100,
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 300,
    
    -- Health monitoring
    consecutive_failures INTEGER DEFAULT 0,
    max_failures_before_disable INTEGER DEFAULT 5,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    
    -- Notifications
    notify_on_failure BOOLEAN DEFAULT true,
    notify_on_success BOOLEAN DEFAULT false,
    notification_emails TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_id),
    CONSTRAINT valid_sync_frequency CHECK (sync_frequency IN ('realtime', 'every_15_min', 'hourly', 'daily', 'weekly', 'manual'))
);

-- Enable RLS for sync_job_configs
ALTER TABLE sync_job_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY sync_job_configs_tenant_policy ON sync_job_configs
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_sync_job_configs_tenant_id ON sync_job_configs(tenant_id);
CREATE INDEX idx_sync_job_configs_integration_id ON sync_job_configs(integration_id);
CREATE INDEX idx_sync_job_configs_enabled ON sync_job_configs(is_enabled);
CREATE INDEX idx_sync_job_configs_next_run ON sync_job_configs(next_run_at);

-- =============================================
-- BILLING AND RATE LIMITING TABLES
-- =============================================

-- Define usage tiers and limits for billing
CREATE TABLE usage_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Tier configuration
    tier_name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    monthly_price_usd DECIMAL(10,2) NOT NULL,
    
    -- Usage limits
    max_api_calls_per_day INTEGER,
    max_integrations INTEGER,
    max_data_transfer_mb INTEGER,
    max_sync_frequency VARCHAR(50) DEFAULT 'hourly',
    
    -- Features
    features JSONB DEFAULT '[]',
    support_level VARCHAR(50) DEFAULT 'community',
    sla_uptime_percent DECIMAL(5,2) DEFAULT 99.0,
    
    -- Billing
    billing_cycle VARCHAR(50) DEFAULT 'monthly',
    overage_cost_per_api_call DECIMAL(10,6) DEFAULT 0.001,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default tiers
INSERT INTO usage_tiers (tier_name, display_name, description, monthly_price_usd, max_api_calls_per_day, max_integrations, max_data_transfer_mb, max_sync_frequency, features) VALUES
('free', 'Free Tier', 'Perfect for individual PMs and small teams', 0.00, 1000, 2, 100, 'daily', '["Basic sync", "Email support"]'),
('pro', 'Pro Tier', 'For growing teams and active PM operations', 47.00, 10000, 10, 1000, 'hourly', '["Advanced sync", "Field mapping AI", "Priority support", "Webhooks"]'),
('enterprise', 'Enterprise Tier', 'For large organizations with complex needs', 197.00, 100000, 50, 10000, 'every_15_min', '["Real-time sync", "Custom integrations", "SSO", "24/7 support", "SLA guarantee"]');

-- Track tenant billing information
CREATE TABLE tenant_billing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Current subscription
    current_tier VARCHAR(100) NOT NULL REFERENCES usage_tiers(tier_name),
    subscription_start_date DATE NOT NULL,
    subscription_end_date DATE,
    
    -- Billing details
    billing_email VARCHAR(255),
    billing_address JSONB DEFAULT '{}',
    payment_method_id VARCHAR(255), -- Stripe payment method ID
    stripe_customer_id VARCHAR(255),
    
    -- Usage tracking
    current_month_api_calls INTEGER DEFAULT 0,
    current_month_data_transfer_mb DECIMAL(10,3) DEFAULT 0,
    last_billing_date DATE,
    next_billing_date DATE,
    
    -- Status
    subscription_status VARCHAR(50) DEFAULT 'active', -- 'active', 'past_due', 'canceled', 'paused'
    is_trial BOOLEAN DEFAULT false,
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id)
);

-- Enable RLS for tenant_billing
ALTER TABLE tenant_billing ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_billing_tenant_policy ON tenant_billing
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_tenant_billing_tenant_id ON tenant_billing(tenant_id);
CREATE INDEX idx_tenant_billing_tier ON tenant_billing(current_tier);
CREATE INDEX idx_tenant_billing_status ON tenant_billing(subscription_status);
CREATE INDEX idx_tenant_billing_next_billing ON tenant_billing(next_billing_date);

-- =============================================
-- RATE LIMITING AND MONITORING TABLES
-- =============================================

-- Track API rate limiting per tenant and integration
CREATE TABLE rate_limit_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Rate limiting window
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_seconds INTEGER NOT NULL, -- 3600 for hourly, 86400 for daily
    
    -- Request tracking
    requests_made INTEGER DEFAULT 0,
    requests_allowed INTEGER NOT NULL,
    requests_denied INTEGER DEFAULT 0,
    
    -- Status
    is_rate_limited BOOLEAN DEFAULT false,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_id, window_start, window_duration_seconds)
);

-- Enable RLS for rate_limit_tracking
ALTER TABLE rate_limit_tracking ENABLE ROW LEVEL SECURITY;
CREATE POLICY rate_limit_tracking_tenant_policy ON rate_limit_tracking
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_rate_limit_tracking_tenant_id ON rate_limit_tracking(tenant_id);
CREATE INDEX idx_rate_limit_tracking_integration_id ON rate_limit_tracking(integration_id);
CREATE INDEX idx_rate_limit_tracking_window ON rate_limit_tracking(window_start);
CREATE INDEX idx_rate_limit_tracking_reset ON rate_limit_tracking(rate_limit_reset_at);

-- =============================================
-- MONITORING AND ALERTS TABLES
-- =============================================

-- Store integration health alerts and notifications
CREATE TABLE integration_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    integration_id UUID REFERENCES tenant_integrations(id) ON DELETE CASCADE,
    
    -- Alert details
    alert_type VARCHAR(100) NOT NULL, -- 'sync_failure', 'rate_limit', 'quota_exceeded', 'auth_expired', 'performance_degraded'
    severity VARCHAR(50) NOT NULL, -- 'info', 'warning', 'error', 'critical'
    title VARCHAR(500) NOT NULL,
    message TEXT,
    
    -- Alert data
    alert_data JSONB DEFAULT '{}',
    threshold_value DECIMAL(10,3),
    current_value DECIMAL(10,3),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved', 'suppressed'
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Notification tracking
    notification_sent BOOLEAN DEFAULT false,
    notification_sent_at TIMESTAMP WITH TIME ZONE,
    notification_channels TEXT[], -- ['email', 'slack', 'webhook']
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_alert_type CHECK (alert_type IN ('sync_failure', 'rate_limit', 'quota_exceeded', 'auth_expired', 'performance_degraded')),
    CONSTRAINT valid_severity CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'acknowledged', 'resolved', 'suppressed'))
);

-- Enable RLS for integration_alerts
ALTER TABLE integration_alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY integration_alerts_tenant_policy ON integration_alerts
    FOR ALL TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Create indexes
CREATE INDEX idx_integration_alerts_tenant_id ON integration_alerts(tenant_id);
CREATE INDEX idx_integration_alerts_integration_id ON integration_alerts(integration_id);
CREATE INDEX idx_integration_alerts_type ON integration_alerts(alert_type);
CREATE INDEX idx_integration_alerts_severity ON integration_alerts(severity);
CREATE INDEX idx_integration_alerts_status ON integration_alerts(status);
CREATE INDEX idx_integration_alerts_created_at ON integration_alerts(created_at);

-- =============================================
-- VIEWS FOR REPORTING AND MONITORING
-- =============================================

-- Comprehensive usage dashboard view
CREATE VIEW tenant_usage_dashboard AS
SELECT 
    t.id as tenant_id,
    t.name as tenant_name,
    tb.current_tier,
    tb.subscription_status,
    
    -- Current usage
    COALESCE(tus.total_api_calls, 0) as daily_api_calls,
    COALESCE(tus.total_records_synced, 0) as daily_records_synced,
    COALESCE(tus.active_integrations, 0) as active_integrations,
    COALESCE(tus.overall_success_rate, 1.0) as success_rate,
    
    -- Usage limits from tier
    ut.max_api_calls_per_day,
    ut.max_integrations,
    ut.max_data_transfer_mb,
    
    -- Usage percentages
    CASE 
        WHEN ut.max_api_calls_per_day > 0 
        THEN COALESCE(tus.total_api_calls, 0) * 100.0 / ut.max_api_calls_per_day
        ELSE 0
    END as api_usage_percent,
    
    CASE 
        WHEN ut.max_integrations > 0 
        THEN COALESCE(tus.active_integrations, 0) * 100.0 / ut.max_integrations
        ELSE 0
    END as integration_usage_percent,
    
    -- Billing information
    tb.next_billing_date,
    ut.monthly_price_usd,
    tb.is_trial,
    tb.trial_ends_at

FROM tenants t
LEFT JOIN tenant_billing tb ON t.id = tb.tenant_id
LEFT JOIN usage_tiers ut ON tb.current_tier = ut.tier_name
LEFT JOIN tenant_usage_summary tus ON t.id = tus.tenant_id 
    AND tus.usage_date = CURRENT_DATE
WHERE t.is_active = true;

-- Integration performance monitoring view
CREATE VIEW integration_performance_dashboard AS
SELECT 
    ti.id as integration_id,
    ti.tenant_id,
    ti.integration_type,
    ti.integration_name,
    ti.status,
    
    -- Recent usage metrics
    ium.usage_date,
    ium.api_calls_made,
    ium.records_synced,
    ium.sync_count,
    ium.success_rate,
    ium.avg_response_time_ms,
    
    -- Health indicators
    CASE 
        WHEN ium.success_rate >= 0.95 THEN 'excellent'
        WHEN ium.success_rate >= 0.85 THEN 'good'
        WHEN ium.success_rate >= 0.70 THEN 'fair'
        ELSE 'poor'
    END as health_status,
    
    -- Sync job configuration
    sjc.sync_frequency,
    sjc.is_enabled as sync_enabled,
    sjc.consecutive_failures,
    sjc.last_success_at,
    sjc.last_failure_at,
    sjc.next_run_at,
    
    -- Active alerts
    (SELECT COUNT(*) FROM integration_alerts ia 
     WHERE ia.integration_id = ti.id AND ia.status = 'active'
    ) as active_alerts

FROM tenant_integrations ti
LEFT JOIN integration_usage_metrics ium ON ti.id = ium.integration_id 
    AND ium.usage_date = CURRENT_DATE
LEFT JOIN sync_job_configs sjc ON ti.id = sjc.integration_id
WHERE ti.status = 'active';

-- Comments for documentation
COMMENT ON TABLE integration_usage_metrics IS 'Daily usage metrics per integration for billing and monitoring';
COMMENT ON TABLE tenant_usage_summary IS 'Aggregated daily usage summary per tenant for billing';
COMMENT ON TABLE sync_job_configs IS 'Sync job configurations and scheduling settings';
COMMENT ON TABLE usage_tiers IS 'Available subscription tiers with limits and pricing';
COMMENT ON TABLE tenant_billing IS 'Tenant subscription and billing information';
COMMENT ON TABLE rate_limit_tracking IS 'API rate limiting tracking per tenant and integration';
COMMENT ON TABLE integration_alerts IS 'Integration health alerts and notifications';
COMMENT ON VIEW tenant_usage_dashboard IS 'Comprehensive tenant usage and billing dashboard';
COMMENT ON VIEW integration_performance_dashboard IS 'Integration performance and health monitoring';