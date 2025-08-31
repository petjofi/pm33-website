-- PM33 Multi-Tenancy RLS Policy - SIMPLE APPROACH
-- Replace complex RESTRICTIVE policies with simple PERMISSIVE ones

-- Drop all existing policies
DROP POLICY IF EXISTS strategic_conversations_isolation_policy ON strategic_conversations;
DROP POLICY IF EXISTS tenant_users_isolation_policy ON tenant_users; 
DROP POLICY IF EXISTS tenant_integrations_isolation_policy ON tenant_integrations;
DROP POLICY IF EXISTS tenant_usage_logs_isolation_policy ON tenant_usage_logs;
DROP POLICY IF EXISTS tenant_audit_logs_isolation_policy ON tenant_audit_logs;
DROP POLICY IF EXISTS company_contexts_isolation_policy ON company_contexts;

-- Create simple PERMISSIVE policies that only allow access when tenant context matches exactly
CREATE POLICY strategic_conversations_tenant_policy ON strategic_conversations
    FOR ALL
    TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

CREATE POLICY tenant_users_tenant_policy ON tenant_users
    FOR ALL
    TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

CREATE POLICY tenant_integrations_tenant_policy ON tenant_integrations
    FOR ALL
    TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

CREATE POLICY tenant_usage_logs_tenant_policy ON tenant_usage_logs
    FOR ALL
    TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

CREATE POLICY tenant_audit_logs_tenant_policy ON tenant_audit_logs
    FOR ALL
    TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

CREATE POLICY company_contexts_tenant_policy ON company_contexts
    FOR ALL
    TO public
    USING (tenant_id::text = current_setting('app.current_tenant_id', false));

-- Verify policies are in place
SELECT 
    schemaname, tablename, policyname, permissive, cmd
FROM pg_policies 
WHERE tablename LIKE '%tenant%' OR tablename IN ('strategic_conversations', 'company_contexts')
ORDER BY tablename, policyname;