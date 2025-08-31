"""
Debug RLS session variable behavior
"""

import asyncio
import uuid
import asyncpg
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_session_variables():
    """Debug session variable behavior"""
    
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/pm33_dev')
    
    # Test with direct connection (no pooling)
    connection = await asyncpg.connect(database_url)
    
    try:
        tenant_id = str(uuid.uuid4())
        print(f"Test tenant ID: {tenant_id}")
        
        # Test setting and getting session variable
        print("\n--- Test session variable setting ---")
        
        # Set the variable
        result = await connection.execute(
            "SELECT set_config('app.current_tenant_id', $1, true)",
            tenant_id
        )
        print(f"set_config result: {result}")
        
        # Get the variable back
        current_setting = await connection.fetchval(
            "SELECT current_setting('app.current_tenant_id', true)"
        )
        print(f"current_setting returned: '{current_setting}'")
        print(f"Type: {type(current_setting)}")
        print(f"Length: {len(current_setting) if current_setting else 'None'}")
        
        # Test if it's equal
        print(f"Equal to original? {current_setting == tenant_id}")
        
        # Test without the 'true' parameter
        result2 = await connection.execute(
            "SELECT set_config('app.current_tenant_id', $1, false)",
            tenant_id
        )
        print(f"set_config (transaction=false) result: {result2}")
        
        current_setting2 = await connection.fetchval(
            "SELECT current_setting('app.current_tenant_id', false)"
        )
        print(f"current_setting (missing_ok=false) returned: '{current_setting2}'")
        
        # Test the UUID cast
        try:
            uuid_result = await connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', false)::uuid"
            )
            print(f"UUID cast result: {uuid_result}")
        except Exception as e:
            print(f"UUID cast failed: {e}")
        
        # Test RLS condition manually
        rls_condition = await connection.fetchval(
            """
            SELECT CASE 
                WHEN current_setting('app.current_tenant_id', true) = '' THEN 'EMPTY'
                WHEN current_setting('app.current_tenant_id', true) IS NULL THEN 'NULL'
                ELSE 'HAS_VALUE'
            END
            """
        )
        print(f"RLS condition evaluates to: {rls_condition}")
        
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(debug_session_variables())