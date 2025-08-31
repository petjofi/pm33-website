-- PM33 Multi-Tenancy Database Schema
-- PostgreSQL schema with Row-Level Security for enterprise B2B SaaS
-- Version: 1.0 - Phase 1 Week 1 Implementation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- CORE TENANT MANAGEMENT TABLES
-- =============================================

-- Primary tenant registration and configuration
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subdomain VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'professional',
    subscription_status VARCHAR(20) NOT NULL DEFAULT 'trial',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}',
    
    -- Subscription and billing
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    billing_email VARCHAR(255),
    
    -- Enterprise features
    custom_domain VARCHAR(255),
    sso_enabled BOOLEAN DEFAULT FALSE,
    data_residency VARCHAR(50) DEFAULT 'us-east-1',
    
    -- Security and compliance
    encryption_key_id UUID,
    audit_retention_days INTEGER DEFAULT 365,
    
    CONSTRAINT valid_subdomain CHECK (subdomain ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'),
    CONSTRAINT valid_subscription_tier CHECK (subscription_tier IN ('professional', 'enterprise', 'strategic')),
    CONSTRAINT valid_subscription_status CHECK (subscription_status IN ('trial', 'active', 'canceled', 'suspended'))
);

-- Create index for performance
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX idx_tenants_subscription_tier ON tenants(subscription_tier);

-- Tenant user management and roles
CREATE TABLE tenant_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    
    -- Authentication
    password_hash VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Session management
    session_token VARCHAR(255),
    session_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Access control
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, email),
    CONSTRAINT valid_role CHECK (role IN ('admin', 'member', 'read_only'))
);

-- Enable Row-Level Security for tenant_users
ALTER TABLE tenant_users ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY tenant_users_isolation_policy ON tenant_users
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create indexes for performance
CREATE INDEX idx_tenant_users_tenant_id ON tenant_users(tenant_id);
CREATE INDEX idx_tenant_users_email ON tenant_users(email);
CREATE INDEX idx_tenant_users_session_token ON tenant_users(session_token);

-- =============================================
-- STRATEGIC INTELLIGENCE DATA TABLES
-- =============================================

-- Strategic conversations and context
CREATE TABLE strategic_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    
    -- Conversation content
    title VARCHAR(500),
    conversation_data JSONB NOT NULL,
    strategic_frameworks_used TEXT[],
    confidence_scores JSONB,
    
    -- Context and intelligence
    company_context_id UUID,
    competitive_context_id UUID,
    market_context_id UUID,
    
    -- Workflow integration
    jira_tasks_generated JSONB DEFAULT '[]',
    strategic_outcomes JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row-Level Security for strategic_conversations
ALTER TABLE strategic_conversations ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY strategic_conversations_isolation_policy ON strategic_conversations
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create indexes for performance
CREATE INDEX idx_strategic_conversations_tenant_id ON strategic_conversations(tenant_id);
CREATE INDEX idx_strategic_conversations_user_id ON strategic_conversations(user_id);
CREATE INDEX idx_strategic_conversations_created_at ON strategic_conversations(created_at);

-- Company context per tenant
CREATE TABLE company_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Company intelligence
    company_name VARCHAR(255),
    industry VARCHAR(100),
    stage VARCHAR(50),
    team_size INTEGER,
    revenue_stage VARCHAR(50),
    
    -- Strategic context
    mission_statement TEXT,
    strategic_objectives JSONB,
    current_okrs JSONB,
    competitive_landscape JSONB,
    
    -- Document intelligence
    extracted_documents JSONB DEFAULT '[]',
    website_analysis JSONB DEFAULT '{}',
    
    -- AI context embeddings (reference to Pinecone)
    embedding_namespace VARCHAR(100),
    context_summary TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row-Level Security for company_contexts
ALTER TABLE company_contexts ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY company_contexts_isolation_policy ON company_contexts
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create index for performance
CREATE INDEX idx_company_contexts_tenant_id ON company_contexts(tenant_id);

-- =============================================
-- INTEGRATION CREDENTIALS STORAGE
-- =============================================

-- Secure OAuth and API credential storage per tenant
CREATE TABLE tenant_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Integration details
    integration_type VARCHAR(50) NOT NULL, -- 'jira', 'linear', 'slack', etc.
    integration_name VARCHAR(255) NOT NULL,
    
    -- OAuth credentials (encrypted)
    encrypted_credentials BYTEA NOT NULL,
    credential_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Integration configuration
    configuration JSONB DEFAULT '{}',
    field_mappings JSONB DEFAULT '{}',
    sync_settings JSONB DEFAULT '{}',
    
    -- Status and health
    status VARCHAR(20) DEFAULT 'active',
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, integration_type, integration_name),
    CONSTRAINT valid_integration_type CHECK (integration_type IN ('jira', 'linear', 'monday', 'asana', 'slack', 'teams', 'mixpanel', 'amplitude')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'error', 'disabled'))
);

-- Enable Row-Level Security for tenant_integrations
ALTER TABLE tenant_integrations ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY tenant_integrations_isolation_policy ON tenant_integrations
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create indexes for performance
CREATE INDEX idx_tenant_integrations_tenant_id ON tenant_integrations(tenant_id);
CREATE INDEX idx_tenant_integrations_type ON tenant_integrations(integration_type);

-- =============================================
-- BILLING AND USAGE TRACKING
-- =============================================

-- Usage tracking for billing and analytics
CREATE TABLE tenant_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID,
    
    -- Usage metrics
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metric_type VARCHAR(50) NOT NULL, -- 'api_call', 'ai_usage', 'storage', etc.
    metric_value INTEGER DEFAULT 1,
    
    -- Usage context
    endpoint VARCHAR(255),
    ai_engine VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0,
    
    -- Billing context
    billable BOOLEAN DEFAULT TRUE,
    billing_period DATE DEFAULT DATE_TRUNC('month', NOW()),
    
    CONSTRAINT valid_metric_type CHECK (metric_type IN ('api_call', 'ai_usage', 'storage', 'integration_sync'))
);

-- Enable Row-Level Security for tenant_usage_logs
ALTER TABLE tenant_usage_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY tenant_usage_logs_isolation_policy ON tenant_usage_logs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create indexes for performance and billing queries
CREATE INDEX idx_tenant_usage_logs_tenant_id ON tenant_usage_logs(tenant_id);
CREATE INDEX idx_tenant_usage_logs_billing_period ON tenant_usage_logs(billing_period);
CREATE INDEX idx_tenant_usage_logs_timestamp ON tenant_usage_logs(timestamp);

-- =============================================
-- AUDIT LOGGING FOR COMPLIANCE
-- =============================================

-- Comprehensive audit trail per tenant
CREATE TABLE tenant_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID,
    
    -- Audit event details
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(50) NOT NULL, -- 'security', 'compliance', 'data_access', etc.
    event_description TEXT,
    
    -- Event context
    resource_type VARCHAR(50),
    resource_id UUID,
    action VARCHAR(50),
    result VARCHAR(20) DEFAULT 'success',
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}',
    severity INTEGER DEFAULT 5, -- 1-10 scale
    
    CONSTRAINT valid_result CHECK (result IN ('success', 'failure', 'error')),
    CONSTRAINT valid_severity CHECK (severity BETWEEN 1 AND 10)
);

-- Enable Row-Level Security for tenant_audit_logs
ALTER TABLE tenant_audit_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY tenant_audit_logs_isolation_policy ON tenant_audit_logs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create indexes for performance and compliance queries
CREATE INDEX idx_tenant_audit_logs_tenant_id ON tenant_audit_logs(tenant_id);
CREATE INDEX idx_tenant_audit_logs_timestamp ON tenant_audit_logs(timestamp);
CREATE INDEX idx_tenant_audit_logs_event_type ON tenant_audit_logs(event_type);
CREATE INDEX idx_tenant_audit_logs_severity ON tenant_audit_logs(severity);

-- =============================================
-- FUNCTIONS FOR TENANT CONTEXT MANAGEMENT
-- =============================================

-- Function to set tenant context for RLS
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', tenant_uuid::text, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current tenant context
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_tenant_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate tenant access
CREATE OR REPLACE FUNCTION validate_tenant_access(tenant_uuid UUID, user_email TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_exists BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM tenant_users 
        WHERE tenant_id = tenant_uuid 
        AND email = user_email
    ) INTO user_exists;
    
    RETURN user_exists;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- TESTING DATA FOR DEVELOPMENT
-- =============================================

-- Insert test tenant for development (will be removed in production)
INSERT INTO tenants (
    id,
    subdomain,
    company_name,
    subscription_tier,
    subscription_status,
    billing_email
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test-tenant',
    'Test Company',
    'professional',
    'trial',
    'test@example.com'
) ON CONFLICT (subdomain) DO NOTHING;

-- Insert test user for development
INSERT INTO tenant_users (
    tenant_id,
    email,
    role,
    first_name,
    last_name,
    email_verified
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test@example.com',
    'admin',
    'Test',
    'User',
    true
) ON CONFLICT (tenant_id, email) DO NOTHING;

-- =============================================
-- SCHEMA VALIDATION AND COMMENTS
-- =============================================

COMMENT ON TABLE tenants IS 'Core tenant registration and configuration with enterprise features';
COMMENT ON TABLE tenant_users IS 'User management within tenants with RBAC and session handling';
COMMENT ON TABLE strategic_conversations IS 'Strategic intelligence conversations with AI context isolation';
COMMENT ON TABLE company_contexts IS 'Company-specific intelligence and strategic context per tenant';
COMMENT ON TABLE tenant_integrations IS 'Secure OAuth credential storage and integration management';
COMMENT ON TABLE tenant_usage_logs IS 'Usage tracking for billing and analytics with tenant isolation';
COMMENT ON TABLE tenant_audit_logs IS 'Comprehensive audit trail for compliance and security monitoring';

-- Ensure all tables have RLS enabled (safety check)
DO $$ 
DECLARE 
    tbl_name TEXT;
BEGIN
    FOR tbl_name IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'tenant_%' OR table_name IN ('strategic_conversations', 'company_contexts')
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl_name);
    END LOOP;
END $$;