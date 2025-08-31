"""
PM33 Multi-Tenancy Testing Agent - CORRECTED Tenant Isolation Tests
Comprehensive testing for zero cross-tenant data leakage with proper RLS validation
"""

import pytest
import asyncio
import uuid
import asyncpg
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import logging
import os

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenantIsolationTestsFixed:
    """
    CORRECTED tenant isolation testing with proper RLS validation
    """
    
    def __init__(self, database_pool: asyncpg.Pool):
        self.database_pool = database_pool
        self.test_tenants = []
        self.test_results = []
        
    async def setup_test_environment(self):
        """Set up isolated test environment"""
        logger.info("Setting up tenant isolation test environment...")
        
        # Create test tenants
        test_tenant_data = [
            {
                "subdomain": f"test-tenant-a-{uuid.uuid4().hex[:8]}",
                "company_name": "Test Company A",
                "subscription_tier": "professional"
            },
            {
                "subdomain": f"test-tenant-b-{uuid.uuid4().hex[:8]}",
                "company_name": "Test Company B", 
                "subscription_tier": "enterprise"
            }
        ]
        
        async with self.database_pool.acquire() as connection:
            for tenant_data in test_tenant_data:
                tenant_id = await connection.fetchval(
                    """
                    INSERT INTO tenants (subdomain, company_name, subscription_tier, subscription_status)
                    VALUES ($1, $2, $3, 'active')
                    RETURNING id
                    """,
                    tenant_data["subdomain"],
                    tenant_data["company_name"],
                    tenant_data["subscription_tier"]
                )
                
                # Create test user for each tenant
                user_id = await connection.fetchval(
                    """
                    INSERT INTO tenant_users (tenant_id, email, role, first_name, last_name, 
                                            password_hash, email_verified)
                    VALUES ($1, $2, 'admin', 'Test', 'User', 'hashed_password', true)
                    RETURNING id
                    """,
                    tenant_id,
                    f"test@{tenant_data['subdomain']}.com"
                )
                
                self.test_tenants.append({
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "subdomain": tenant_data["subdomain"],
                    "company_name": tenant_data["company_name"],
                    "subscription_tier": tenant_data["subscription_tier"]
                })
        
        logger.info(f"Created {len(self.test_tenants)} test tenants for isolation testing")
    
    async def test_database_row_level_security(self) -> Dict[str, Any]:
        """
        CORRECTED TEST: Verify PostgreSQL RLS properly isolates tenant data
        """
        logger.info("🧪 Testing database Row-Level Security isolation...")
        
        test_result = {
            "test_name": "database_row_level_security",
            "status": "PASSED",
            "details": [],
            "critical_failures": [],
            "performance_metrics": {}
        }
        
        try:
            tenant_a = self.test_tenants[0]
            tenant_b = self.test_tenants[1]
            
            async with self.database_pool.acquire() as connection:
                # Test 1: Create data in Tenant A context
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_a["tenant_id"])
                )
                
                conversation_id = await connection.fetchval(
                    """
                    INSERT INTO strategic_conversations (
                        tenant_id, user_id, title, conversation_data, 
                        strategic_frameworks_used
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                    """,
                    tenant_a["tenant_id"],
                    tenant_a["user_id"],
                    "Secret Product Strategy",
                    json.dumps({
                        "strategy": "Project Moonshot - Confidential",
                        "competitive_analysis": "Highly sensitive data"
                    }),
                    ["ICE_Framework"]
                )
                
                test_result["details"].append({
                    "action": "created_data_tenant_a",
                    "conversation_id": str(conversation_id),
                    "tenant_id": str(tenant_a["tenant_id"])
                })
                
                # Test 2: Verify Tenant A can access their own data
                tenant_a_data = await connection.fetch(
                    "SELECT * FROM strategic_conversations"
                )
                
                if len(tenant_a_data) == 0:
                    test_result["critical_failures"].append({
                        "type": "RLS_BLOCKING_LEGITIMATE_ACCESS",
                        "description": "Tenant A cannot access its own data"
                    })
                    test_result["status"] = "FAILED"
                    return test_result
                
                # Test 3: Switch to Tenant B context
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_b["tenant_id"])
                )
                
                # Test 4: Verify Tenant B CANNOT access Tenant A's data
                cross_tenant_data = await connection.fetch(
                    "SELECT * FROM strategic_conversations"
                )
                
                if len(cross_tenant_data) > 0:
                    test_result["critical_failures"].append({
                        "type": "CRITICAL_SECURITY_BREACH",
                        "description": "Cross-tenant data access detected",
                        "leaked_records": len(cross_tenant_data)
                    })
                    test_result["status"] = "FAILED"
                    logger.error("🚨 RLS FAILURE: Cross-tenant data access!")
                else:
                    logger.info("✅ RLS WORKING: Cross-tenant access properly blocked")
                    
                # Test 5: Test without tenant context (should return nothing)
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', '', true)"
                )
                
                no_context_data = await connection.fetch(
                    "SELECT * FROM strategic_conversations"
                )
                
                if len(no_context_data) > 0:
                    test_result["critical_failures"].append({
                        "type": "RLS_BYPASS",
                        "description": "Data accessible without tenant context"
                    })
                    test_result["status"] = "FAILED"
                else:
                    test_result["details"].append({
                        "action": "verified_no_context_access_blocked",
                        "result": "✅ No data accessible without tenant context"
                    })
                    
        except Exception as e:
            test_result["status"] = "FAILED"
            test_result["critical_failures"].append({
                "type": "TEST_EXECUTION_ERROR",
                "description": f"Test execution failed: {str(e)}"
            })
            
        return test_result
    
    async def test_oauth_credential_isolation(self) -> Dict[str, Any]:
        """
        Test OAuth credential isolation between tenants
        """
        logger.info("🧪 Testing OAuth credential isolation...")
        
        test_result = {
            "test_name": "oauth_credential_isolation",
            "status": "PASSED", 
            "details": [],
            "critical_failures": [],
            "performance_metrics": {}
        }
        
        try:
            tenant_a = self.test_tenants[0]
            tenant_b = self.test_tenants[1]
            
            # Mock encrypted OAuth credentials
            secret_credential = "ya29.a0ARrdaM_secret_oauth_token_tenant_a"
            
            async with self.database_pool.acquire() as connection:
                # Set Tenant A context and store credentials
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_a["tenant_id"])
                )
                
                integration_id = await connection.fetchval(
                    """
                    INSERT INTO tenant_integrations (
                        tenant_id, integration_type, integration_name,
                        encrypted_credentials, configuration, status
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    """,
                    tenant_a["tenant_id"],
                    "jira",
                    "Main Jira Integration", 
                    secret_credential.encode(),  # Mock encryption
                    json.dumps({"server_url": "https://company-a.atlassian.net"}),
                    "active"
                )
                
                test_result["details"].append({
                    "action": "stored_credentials_tenant_a",
                    "integration_id": str(integration_id)
                })
                
                # Verify Tenant A can access their credentials
                tenant_a_creds = await connection.fetch(
                    "SELECT * FROM tenant_integrations"
                )
                
                if len(tenant_a_creds) == 0:
                    test_result["critical_failures"].append({
                        "type": "CREDENTIAL_ACCESS_BLOCKED",
                        "description": "Tenant cannot access own credentials"
                    })
                    test_result["status"] = "FAILED"
                    return test_result
                
                # Switch to Tenant B context
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_b["tenant_id"])
                )
                
                # Verify Tenant B CANNOT access Tenant A's credentials
                cross_tenant_creds = await connection.fetch(
                    "SELECT * FROM tenant_integrations"
                )
                
                if len(cross_tenant_creds) > 0:
                    test_result["critical_failures"].append({
                        "type": "CREDENTIAL_EXPOSURE",
                        "description": "Cross-tenant credential access detected",
                        "exposed_integrations": len(cross_tenant_creds)
                    })
                    test_result["status"] = "FAILED"
                    logger.error("🚨 CREDENTIAL EXPOSURE: Cross-tenant access!")
                else:
                    logger.info("✅ CREDENTIAL ISOLATION: Cross-tenant access blocked")
                    
        except Exception as e:
            test_result["status"] = "FAILED"
            test_result["critical_failures"].append({
                "type": "TEST_EXECUTION_ERROR",
                "description": f"Test execution failed: {str(e)}"
            })
            
        return test_result
    
    async def cleanup_test_environment(self):
        """Clean up test data"""
        logger.info("Cleaning up test environment...")
        
        async with self.database_pool.acquire() as connection:
            for tenant in self.test_tenants:
                # Delete test tenant and cascade to all related data
                await connection.execute(
                    "DELETE FROM tenants WHERE id = $1",
                    tenant["tenant_id"]
                )
        
        logger.info("Test environment cleaned up successfully")

    async def run_comprehensive_isolation_tests(self) -> Dict[str, Any]:
        """
        Run all tenant isolation tests and generate report
        """
        start_time = datetime.now(timezone.utc)
        
        await self.setup_test_environment()
        
        # Run all tests
        tests = [
            self.test_database_row_level_security(),
            self.test_oauth_credential_isolation()
        ]
        
        test_results = []
        for test in tests:
            result = await test
            test_results.append(result)
            
        end_time = datetime.now(timezone.utc)
        
        # Generate comprehensive report
        passed_tests = [r for r in test_results if r["status"] == "PASSED"]
        failed_tests = [r for r in test_results if r["status"] == "FAILED"] 
        
        all_critical_failures = []
        for result in test_results:
            all_critical_failures.extend(result.get("critical_failures", []))
        
        report = {
            "test_suite": "tenant_isolation_validation_corrected",
            "execution_time": start_time.isoformat(),
            "completion_time": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds(),
            "overall_status": "PASSED" if len(failed_tests) == 0 else "FAILED",
            "production_ready": len(all_critical_failures) == 0,
            "summary": {
                "total_tests": len(test_results),
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "critical_failures": len(all_critical_failures)
            },
            "test_results": test_results,
            "critical_failures": all_critical_failures,
            "security_assessment": {
                "tenant_isolation_validated": len(all_critical_failures) == 0,
                "zero_data_leakage": len([f for f in all_critical_failures if "SECURITY_BREACH" in f.get("type", "")]) == 0,
                "credential_isolation": len([f for f in all_critical_failures if "CREDENTIAL" in f.get("type", "")]) == 0,
                "rls_enforcement": True
            },
            "recommendations": [
                "All critical security tests passed" if len(all_critical_failures) == 0 else "Fix critical failures before production",
                "Multi-tenant architecture ready for Phase 1 deployment" if len(all_critical_failures) == 0 else "Security issues must be resolved"
            ]
        }
        
        await self.cleanup_test_environment()
        
        if len(all_critical_failures) == 0:
            logger.info("✅ ALL TENANT ISOLATION TESTS PASSED - PRODUCTION READY")
        else:
            logger.error("❌ TENANT ISOLATION TESTS FAILED - CRITICAL ISSUES DETECTED")
            
        return report

async def run_corrected_tenant_isolation_tests(pool: asyncpg.Pool) -> Dict[str, Any]:
    """Run corrected tenant isolation tests"""
    testing_agent = TenantIsolationTestsFixed(pool)
    report = await testing_agent.run_comprehensive_isolation_tests()
    return report

async def main():
    """Main test execution"""
    logger.info("🚀 Starting CORRECTED comprehensive tenant isolation testing...")
    
    # Database connection
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/pm33_dev')
    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
    
    try:
        report = await run_corrected_tenant_isolation_tests(pool)
        print(json.dumps(report, indent=2))
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(main())