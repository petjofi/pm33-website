"""
Test RLS with proper non-superuser role
"""

import asyncio
import uuid
import asyncpg
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rls_with_app_user():
    """Test RLS with non-superuser application role"""
    
    # Get the base database URL and modify it for the app user
    base_url = os.getenv('DATABASE_URL', 'postgresql://localhost/railway')
    
    # Extract host/port/database from the base URL
    import re
    match = re.search(r'postgresql://[^@]+@([^/]+)/(.+)', base_url)
    if match:
        host_port = match.group(1)
        database = match.group(2)
        app_user_url = f"postgresql://pm33_app_user:test_password_123@{host_port}/{database}"
    else:
        logger.error("Could not parse database URL")
        return
    
    logger.info(f"Testing RLS with app user connection: {app_user_url}")
    
    # Connect as the application user (non-superuser)
    try:
        conn = await asyncpg.connect(app_user_url)
        
        # Verify we're not a superuser
        is_superuser = await conn.fetchval("SELECT current_setting('is_superuser')")
        logger.info(f"Connected as: {await conn.fetchval('SELECT current_user')}")
        logger.info(f"Is superuser: {is_superuser}")
        
        if is_superuser == 'on':
            logger.error("Still connected as superuser! RLS test will not be valid.")
            return
        
        # Test 1: Create test tenant and user (use superuser connection for setup)
        setup_conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        tenant_a_id = await setup_conn.fetchval(
            """
            INSERT INTO tenants (subdomain, company_name, subscription_tier, subscription_status)
            VALUES ($1, $2, $3, 'active')
            RETURNING id
            """,
            f"rls-test-a-{uuid.uuid4().hex[:8]}",
            "RLS Test Company A",
            "professional"
        )
        
        user_a_id = await setup_conn.fetchval(
            """
            INSERT INTO tenant_users (tenant_id, email, role, first_name, last_name, password_hash, email_verified)
            VALUES ($1, $2, 'admin', 'Test', 'User', 'hash', true)
            RETURNING id
            """,
            tenant_a_id,
            f"test-a@rlstest.com"
        )
        
        tenant_b_id = await setup_conn.fetchval(
            """
            INSERT INTO tenants (subdomain, company_name, subscription_tier, subscription_status)
            VALUES ($1, $2, $3, 'active')
            RETURNING id
            """,
            f"rls-test-b-{uuid.uuid4().hex[:8]}",
            "RLS Test Company B",
            "enterprise"
        )
        
        await setup_conn.close()
        
        logger.info(f"Created test tenants: {tenant_a_id}, {tenant_b_id}")
        
        # Test 2: Set Tenant A context and create data (as app user)
        logger.info("--- Testing Tenant A context ---")
        await conn.execute(
            "SELECT set_config('app.current_tenant_id', $1, false)",
            str(tenant_a_id)
        )
        
        current_tenant = await conn.fetchval(
            "SELECT current_setting('app.current_tenant_id', false)"
        )
        logger.info(f"Current tenant context: {current_tenant}")
        
        # Create conversation as app user
        conv_id = await conn.fetchval(
            """
            INSERT INTO strategic_conversations (
                tenant_id, user_id, title, conversation_data
            ) VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            tenant_a_id,
            user_a_id,
            "RLS Test Conversation",
            json.dumps({"secret": "tenant_a_data"})
        )
        logger.info(f"Created conversation: {conv_id}")
        
        # Verify Tenant A can see their data
        tenant_a_data = await conn.fetch(
            "SELECT id, tenant_id, title FROM strategic_conversations"
        )
        logger.info(f"Tenant A sees {len(tenant_a_data)} conversations")
        
        # Test 3: Switch to Tenant B context
        logger.info("--- Testing Tenant B context ---")
        await conn.execute(
            "SELECT set_config('app.current_tenant_id', $1, false)",
            str(tenant_b_id)
        )
        
        current_tenant = await conn.fetchval(
            "SELECT current_setting('app.current_tenant_id', false)"
        )
        logger.info(f"Current tenant context: {current_tenant}")
        
        # Try to see conversations as Tenant B
        tenant_b_data = await conn.fetch(
            "SELECT id, tenant_id, title FROM strategic_conversations"
        )
        logger.info(f"Tenant B sees {len(tenant_b_data)} conversations")
        
        if len(tenant_b_data) == 0:
            logger.info("✅ SUCCESS: RLS working - Tenant B cannot see Tenant A data")
        else:
            logger.error("❌ FAILURE: RLS not working - Tenant B can see Tenant A data")
        
        # Test 4: Clear tenant context
        logger.info("--- Testing empty context ---")
        await conn.execute(
            "SELECT set_config('app.current_tenant_id', '', false)"
        )
        
        empty_context_data = await conn.fetch(
            "SELECT id, tenant_id, title FROM strategic_conversations"
        )
        logger.info(f"Empty context sees {len(empty_context_data)} conversations")
        
        if len(empty_context_data) == 0:
            logger.info("✅ SUCCESS: RLS working - No data visible without tenant context")
        else:
            logger.error("❌ FAILURE: RLS not working - Data visible without tenant context")
        
        await conn.close()
        
        # Cleanup with superuser connection
        cleanup_conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await cleanup_conn.execute(
            "DELETE FROM tenants WHERE id IN ($1, $2)",
            tenant_a_id, tenant_b_id
        )
        await cleanup_conn.close()
        
        logger.info("RLS test completed and cleaned up")
        
    except Exception as e:
        logger.error(f"RLS test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_rls_with_app_user())