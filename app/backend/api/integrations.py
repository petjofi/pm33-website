"""
PM33 Integration Management API
FastAPI endpoints for tenant integration setup, management, and monitoring
"""

import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
import json

from ..middleware.tenant_context import get_tenant_context, require_tenant_context
from ..auth.jwt_auth import get_current_user, require_permission
from ..integrations.base.oauth_manager import OAuthManager
from ..integrations.base.integration_base import IntegrationConfig
from ..integrations.jira.jira_service import JiraIntegration

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# Pydantic models
class IntegrationSetupRequest(BaseModel):
    integration_type: str
    integration_name: str

class IntegrationSetupResponse(BaseModel):
    success: bool
    authorize_url: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    integration_name: str

class IntegrationSyncRequest(BaseModel):
    integration_id: uuid.UUID
    incremental: bool = True

class IntegrationResponse(BaseModel):
    id: uuid.UUID
    integration_type: str
    integration_name: str
    status: str
    last_sync_at: Optional[datetime]
    credential_expires_at: Optional[datetime]
    needs_token_refresh: bool
    last_error: Optional[str]

# Global OAuth manager (would be injected via dependency injection in production)
oauth_manager: Optional[OAuthManager] = None
database_pool: Optional[asyncpg.Pool] = None

async def get_oauth_manager():
    """Dependency to get OAuth manager"""
    if oauth_manager is None:
        raise HTTPException(status_code=500, detail="OAuth manager not initialized")
    return oauth_manager

async def get_database_pool():
    """Dependency to get database pool"""
    if database_pool is None:
        raise HTTPException(status_code=500, detail="Database pool not initialized")
    return database_pool

@router.post("/setup", response_model=IntegrationSetupResponse)
async def setup_integration(
    request: IntegrationSetupRequest,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("integrations", "write")),
    oauth_mgr: OAuthManager = Depends(get_oauth_manager)
):
    """
    Initiate OAuth setup for a new integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Validate integration type
        supported_types = ["jira", "linear", "monday"]
        if request.integration_type not in supported_types:
            return IntegrationSetupResponse(
                success=False,
                error=f"Unsupported integration type. Supported: {', '.join(supported_types)}"
            )
        
        # Check if integration name already exists for this tenant
        pool = await get_database_pool()
        async with pool.acquire() as connection:
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            existing = await connection.fetchval(
                """
                SELECT COUNT(*) FROM tenant_integrations 
                WHERE tenant_id = $1 AND integration_name = $2
                """,
                tenant_id,
                request.integration_name
            )
            
            if existing > 0:
                return IntegrationSetupResponse(
                    success=False,
                    error=f"Integration with name '{request.integration_name}' already exists"
                )
        
        # Initiate OAuth flow
        authorize_url, state = await oauth_mgr.initiate_oauth_flow(
            tenant_id,
            request.integration_type,
            request.integration_name
        )
        
        return IntegrationSetupResponse(
            success=True,
            authorize_url=authorize_url,
            state=state
        )
        
    except Exception as e:
        logger.error(f"Integration setup error: {str(e)}")
        return IntegrationSetupResponse(
            success=False,
            error="Failed to initiate integration setup"
        )

@router.post("/oauth/callback")
async def oauth_callback(
    request: OAuthCallbackRequest,
    oauth_mgr: OAuthManager = Depends(get_oauth_manager)
):
    """
    Handle OAuth callback and complete integration setup
    """
    try:
        success, error, integration_id = await oauth_mgr.handle_oauth_callback(
            request.code,
            request.state,
            request.integration_name
        )
        
        if success:
            return {
                "success": True,
                "integration_id": integration_id,
                "message": f"Integration '{request.integration_name}' setup completed successfully"
            }
        else:
            return {"success": False, "error": error}
            
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return {"success": False, "error": "OAuth callback failed"}

@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("integrations", "read")),
    pool: asyncpg.Pool = Depends(get_database_pool)
):
    """
    List all integrations for the current tenant
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        async with pool.acquire() as connection:
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            integrations = await connection.fetch(
                """
                SELECT id, integration_type, integration_name, status,
                       last_sync_at, credential_expires_at, last_error
                FROM tenant_integrations
                WHERE tenant_id = $1
                ORDER BY created_at DESC
                """,
                tenant_id
            )
            
            result = []
            for integration in integrations:
                needs_refresh = (
                    integration["credential_expires_at"] and
                    integration["credential_expires_at"] < datetime.now(timezone.utc) + timedelta(hours=24)
                )
                
                result.append(IntegrationResponse(
                    id=integration["id"],
                    integration_type=integration["integration_type"],
                    integration_name=integration["integration_name"],
                    status=integration["status"],
                    last_sync_at=integration["last_sync_at"],
                    credential_expires_at=integration["credential_expires_at"],
                    needs_token_refresh=needs_refresh,
                    last_error=integration["last_error"]
                ))
            
            return result
            
    except Exception as e:
        logger.error(f"List integrations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list integrations")

@router.get("/{integration_id}/status")
async def get_integration_status(
    integration_id: uuid.UUID,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("integrations", "read")),
    oauth_mgr: OAuthManager = Depends(get_oauth_manager)
):
    """
    Get detailed status of a specific integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        status = await oauth_mgr.get_integration_status(tenant_id, integration_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get integration status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get integration status")

@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: uuid.UUID,
    request: IntegrationSyncRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("integrations", "write")),
    pool: asyncpg.Pool = Depends(get_database_pool)
):
    """
    Trigger manual sync for an integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Get integration config
        async with pool.acquire() as connection:
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            integration = await connection.fetchrow(
                """
                SELECT integration_type, integration_name, encrypted_credentials,
                       configuration, field_mappings, sync_settings, status, last_sync_at
                FROM tenant_integrations
                WHERE id = $1 AND tenant_id = $2
                """,
                integration_id,
                tenant_id
            )
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
            
            if integration["status"] != "active":
                raise HTTPException(status_code=400, detail="Integration is not active")
        
        # Create integration config
        config = IntegrationConfig(
            tenant_id=tenant_id,
            integration_id=integration_id,
            integration_type=integration["integration_type"],
            integration_name=integration["integration_name"],
            encrypted_credentials=integration["encrypted_credentials"],
            configuration=integration["configuration"] or {},
            field_mappings=integration["field_mappings"] or {},
            sync_settings=integration["sync_settings"] or {},
            status=integration["status"],
            last_sync_at=integration["last_sync_at"]
        )
        
        # Start sync in background
        background_tasks.add_task(
            _perform_integration_sync,
            config,
            request.incremental,
            pool
        )
        
        return {
            "success": True,
            "message": f"Sync started for integration '{integration['integration_name']}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync integration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start sync")

@router.post("/{integration_id}/test")
async def test_integration_connection(
    integration_id: uuid.UUID,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("integrations", "read")),
    pool: asyncpg.Pool = Depends(get_database_pool)
):
    """
    Test connection to an integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Get integration config
        async with pool.acquire() as connection:
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            integration = await connection.fetchrow(
                """
                SELECT integration_type, integration_name, encrypted_credentials,
                       configuration, field_mappings, sync_settings, status
                FROM tenant_integrations
                WHERE id = $1 AND tenant_id = $2
                """,
                integration_id,
                tenant_id
            )
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
        
        # Create integration config
        config = IntegrationConfig(
            tenant_id=tenant_id,
            integration_id=integration_id,
            integration_type=integration["integration_type"],
            integration_name=integration["integration_name"],
            encrypted_credentials=integration["encrypted_credentials"],
            configuration=integration["configuration"] or {},
            field_mappings=integration["field_mappings"] or {},
            sync_settings=integration["sync_settings"] or {},
            status=integration["status"]
        )
        
        # Test connection based on integration type
        if integration["integration_type"] == "jira":
            integration_service = JiraIntegration(pool, config)
            success, message = await integration_service.test_connection()
            
            return {
                "success": success,
                "message": message,
                "integration_type": "jira"
            }
        else:
            return {
                "success": False,
                "message": f"Connection test not implemented for {integration['integration_type']}",
                "integration_type": integration["integration_type"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test integration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Connection test failed")

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: uuid.UUID,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("integrations", "delete")),
    pool: asyncpg.Pool = Depends(get_database_pool)
):
    """
    Delete an integration and its data
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        async with pool.acquire() as connection:
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            # Get integration details for logging
            integration = await connection.fetchrow(
                """
                SELECT integration_type, integration_name
                FROM tenant_integrations
                WHERE id = $1 AND tenant_id = $2
                """,
                integration_id,
                tenant_id
            )
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
            
            # Delete integration (CASCADE will delete related data)
            await connection.execute(
                """
                DELETE FROM tenant_integrations
                WHERE id = $1 AND tenant_id = $2
                """,
                integration_id,
                tenant_id
            )
            
            # Log deletion
            await connection.execute(
                """
                INSERT INTO tenant_audit_logs (
                    tenant_id, user_id, event_type, event_category,
                    event_description, result
                ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                tenant_id,
                uuid.UUID(current_user["sub"]),
                "integration_deleted",
                "integrations",
                f"Deleted integration '{integration['integration_name']}' ({integration['integration_type']})",
                "success"
            )
        
        return {
            "success": True,
            "message": f"Integration '{integration['integration_name']}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete integration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete integration")

# Background task functions
async def _perform_integration_sync(
    config: IntegrationConfig,
    incremental: bool,
    pool: asyncpg.Pool
):
    """Background task to perform integration sync"""
    try:
        if config.integration_type == "jira":
            integration_service = JiraIntegration(pool, config)
            result = await integration_service.sync_data(incremental)
            logger.info(f"Jira sync completed: {result.records_synced} records synced")
        else:
            logger.error(f"Sync not implemented for {config.integration_type}")
            
    except Exception as e:
        logger.error(f"Background sync error: {str(e)}")

# Initialization function
def initialize_integration_api(db_pool: asyncpg.Pool):
    """Initialize the integration API with dependencies"""
    global oauth_manager, database_pool
    oauth_manager = OAuthManager(db_pool)
    database_pool = db_pool