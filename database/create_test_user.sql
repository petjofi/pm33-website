-- Create non-superuser role for proper RLS testing

-- Create test role if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pm33_app_user') THEN
        CREATE ROLE pm33_app_user WITH LOGIN PASSWORD 'test_password_123';
    END IF;
END
$$;

-- Grant necessary permissions to the test role
GRANT CONNECT ON DATABASE pm33_dev TO pm33_app_user;
GRANT USAGE ON SCHEMA public TO pm33_app_user;

-- Grant table permissions (but not bypass RLS)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pm33_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pm33_app_user;

-- Grant function execution permissions  
GRANT EXECUTE ON FUNCTION set_tenant_context(UUID) TO pm33_app_user;
GRANT EXECUTE ON FUNCTION get_current_tenant_id() TO pm33_app_user;
GRANT EXECUTE ON FUNCTION validate_tenant_access(UUID, TEXT) TO pm33_app_user;

-- Verify the role is NOT a superuser and does NOT bypass RLS
SELECT 
    rolname,
    rolsuper,
    rolbypassrls,
    rolcanlogin
FROM pg_roles 
WHERE rolname = 'pm33_app_user';

-- Show connection string for testing
SELECT 'postgresql://pm33_app_user:test_password_123@' || 
       split_part(current_setting('listen_addresses'), ',', 1) || 
       '/' || current_database() as test_connection_string;