"""
Debug RLS Test - Find out exactly what's happening
"""

import asyncio
import uuid
import asyncpg
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_rls():
    """Debug RLS behavior step by step"""
    
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/pm33_dev')
    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=2)
    
    try:
        # Create test tenants
        async with pool.acquire() as connection:
            tenant_a_id = await connection.fetchval(
                """
                INSERT INTO tenants (subdomain, company_name, subscription_tier, subscription_status)
                VALUES ($1, $2, $3, 'active')
                RETURNING id
                """,
                f"debug-tenant-a-{uuid.uuid4().hex[:8]}",
                "Debug Company A", 
                "professional"
            )
            
            tenant_b_id = await connection.fetchval(
                """
                INSERT INTO tenants (subdomain, company_name, subscription_tier, subscription_status)
                VALUES ($1, $2, $3, 'active')
                RETURNING id
                """,
                f"debug-tenant-b-{uuid.uuid4().hex[:8]}",
                "Debug Company B",
                "enterprise"
            )
            
            user_a_id = await connection.fetchval(
                """
                INSERT INTO tenant_users (tenant_id, email, role, first_name, last_name, password_hash, email_verified)
                VALUES ($1, $2, 'admin', 'Test', 'User', 'hashed', true)
                RETURNING id
                """,
                tenant_a_id,
                f"test-a@debug.com"
            )
            
            user_b_id = await connection.fetchval(
                """
                INSERT INTO tenant_users (tenant_id, email, role, first_name, last_name, password_hash, email_verified)  
                VALUES ($1, $2, 'admin', 'Test', 'User', 'hashed', true)
                RETURNING id
                """,
                tenant_b_id,
                f"test-b@debug.com"
            )
            
            print(f"Created Tenant A: {tenant_a_id}")
            print(f"Created Tenant B: {tenant_b_id}")
            print(f"Created User A: {user_a_id}")
            print(f"Created User B: {user_b_id}")
            
            # Test 1: Set Tenant A context and create data
            print("\n--- Test 1: Set Tenant A context ---")
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_a_id)
            )
            
            current_setting = await connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', true)"
            )
            print(f"Current tenant setting: {current_setting}")
            
            # Create conversation in Tenant A
            conv_id = await connection.fetchval(
                """
                INSERT INTO strategic_conversations (
                    tenant_id, user_id, title, conversation_data
                ) VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                tenant_a_id,
                user_a_id,
                "Debug Conversation A",
                json.dumps({"test": "data"})
            )
            print(f"Created conversation: {conv_id}")
            
            # Verify Tenant A can see their data
            tenant_a_conversations = await connection.fetch(
                "SELECT id, tenant_id, title FROM strategic_conversations"
            )
            print(f"Tenant A sees {len(tenant_a_conversations)} conversations:")
            for conv in tenant_a_conversations:
                print(f"  - {conv['id']}: {conv['title']} (tenant: {conv['tenant_id']})")
            
            # Test 2: Switch to Tenant B context
            print("\n--- Test 2: Switch to Tenant B context ---")
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_b_id)
            )
            
            current_setting = await connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', true)"
            )
            print(f"Current tenant setting: {current_setting}")
            
            # Try to see conversations as Tenant B
            tenant_b_conversations = await connection.fetch(
                "SELECT id, tenant_id, title FROM strategic_conversations"
            )
            print(f"Tenant B sees {len(tenant_b_conversations)} conversations:")
            for conv in tenant_b_conversations:
                print(f"  - {conv['id']}: {conv['title']} (tenant: {conv['tenant_id']})")
            
            # Test 3: Clear tenant context
            print("\n--- Test 3: Clear tenant context ---")
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', '', true)"
            )
            
            current_setting = await connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', true)"
            )
            print(f"Current tenant setting: '{current_setting}'")
            
            # Try to see conversations with no context
            no_context_conversations = await connection.fetch(
                "SELECT id, tenant_id, title FROM strategic_conversations"
            )
            print(f"No context sees {len(no_context_conversations)} conversations:")
            for conv in no_context_conversations:
                print(f"  - {conv['id']}: {conv['title']} (tenant: {conv['tenant_id']})")
            
            # Test 4: Check RLS policy status
            print("\n--- Test 4: RLS Policy Status ---")
            rls_info = await connection.fetch(
                """
                SELECT 
                    t.tablename,
                    t.rowsecurity,
                    p.policyname,
                    p.permissive,
                    p.cmd
                FROM pg_tables t
                LEFT JOIN pg_policies p ON t.tablename = p.tablename
                WHERE t.tablename = 'strategic_conversations'
                """
            )
            for info in rls_info:
                print(f"Table: {info['tablename']}, RLS: {info['rowsecurity']}, Policy: {info['policyname']}, Type: {info['permissive']}")
            
            # Cleanup
            await connection.execute("DELETE FROM tenants WHERE id IN ($1, $2)", tenant_a_id, tenant_b_id)
            print("\nCleanup completed")
            
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(debug_rls())