-- PM33 Multi-Tenancy RLS Policy Fixes
-- Fix RLS policies to properly handle null/empty tenant contexts

-- Drop existing policies
DROP POLICY IF EXISTS strategic_conversations_isolation_policy ON strategic_conversations;
DROP POLICY IF EXISTS tenant_users_isolation_policy ON tenant_users;
DROP POLICY IF EXISTS tenant_integrations_isolation_policy ON tenant_integrations;
DROP POLICY IF EXISTS tenant_usage_logs_isolation_policy ON tenant_usage_logs;
DROP POLICY IF EXISTS tenant_audit_logs_isolation_policy ON tenant_audit_logs;
DROP POLICY IF EXISTS company_contexts_isolation_policy ON company_contexts;

-- Create RESTRICTIVE policies that properly handle null contexts
-- CRITICAL: These policies block ALL access unless proper tenant context is set

CREATE POLICY strategic_conversations_isolation_policy ON strategic_conversations
    AS RESTRICTIVE
    FOR ALL
    TO public
    USING (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    )
    WITH CHECK (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    );

CREATE POLICY tenant_users_isolation_policy ON tenant_users
    AS RESTRICTIVE
    FOR ALL
    TO public
    USING (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    )
    WITH CHECK (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    );

CREATE POLICY tenant_integrations_isolation_policy ON tenant_integrations
    AS RESTRICTIVE
    FOR ALL
    TO public
    USING (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    )
    WITH CHECK (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    );

CREATE POLICY tenant_usage_logs_isolation_policy ON tenant_usage_logs
    AS RESTRICTIVE
    FOR ALL
    TO public
    USING (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    )
    WITH CHECK (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    );

CREATE POLICY tenant_audit_logs_isolation_policy ON tenant_audit_logs
    AS RESTRICTIVE
    FOR ALL
    TO public
    USING (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    )
    WITH CHECK (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    );

CREATE POLICY company_contexts_isolation_policy ON company_contexts
    AS RESTRICTIVE
    FOR ALL
    TO public
    USING (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    )
    WITH CHECK (
        CASE 
            WHEN current_setting('app.current_tenant_id', true) = '' THEN false
            WHEN current_setting('app.current_tenant_id', true) IS NULL THEN false
            ELSE tenant_id = current_setting('app.current_tenant_id', true)::uuid
        END
    );

-- Verify all policies are applied
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    CASE WHEN cmd = 'ALL' THEN 'ALL_OPERATIONS' ELSE cmd END as operations,
    CASE WHEN permissive = 'PERMISSIVE' THEN 'PERMISSIVE' ELSE 'RESTRICTIVE' END as policy_type
FROM pg_policies 
WHERE tablename LIKE '%tenant%' OR tablename IN ('strategic_conversations', 'company_contexts')
ORDER BY tablename, policyname;