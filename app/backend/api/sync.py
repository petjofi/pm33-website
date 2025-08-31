"""
PM33 Sync Management API
FastAPI endpoints for managing sync schedules and monitoring sync operations
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from enum import Enum

from ..middleware.tenant_context import get_tenant_context, require_tenant_context
from ..auth.jwt_auth import get_current_user, require_permission
from ..services.sync_scheduler import SyncScheduler, SyncFrequency

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sync", tags=["sync"])

# Pydantic models
class SyncFrequencyEnum(str, Enum):
    REALTIME = "realtime"
    EVERY_15_MIN = "every_15_min"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"

class UpdateSyncConfigRequest(BaseModel):
    frequency: SyncFrequencyEnum
    enabled: bool = True

class ManualSyncRequest(BaseModel):
    integration_id: uuid.UUID
    incremental: bool = True
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")

class SyncJobResponse(BaseModel):
    job_id: str
    tenant_id: uuid.UUID
    integration_id: uuid.UUID
    integration_name: str
    integration_type: str
    frequency: str
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    consecutive_failures: int
    health_status: str

class UsageMetricsResponse(BaseModel):
    date: datetime
    api_calls_made: int
    records_synced: int
    sync_count: int
    sync_duration_seconds: float
    success_rate: float
    estimated_cost_usd: float

class SyncStatsResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    healthy_jobs: int
    failed_jobs: int
    syncs_today: int
    records_synced_today: int
    avg_success_rate: float

# Global sync scheduler (would be injected via dependency injection in production)
sync_scheduler: Optional[SyncScheduler] = None

async def get_sync_scheduler():
    """Dependency to get sync scheduler"""
    if sync_scheduler is None:
        raise HTTPException(status_code=500, detail="Sync scheduler not initialized")
    return sync_scheduler

@router.get("/status", response_model=SyncStatsResponse)
async def get_sync_status(
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "read")),
    scheduler: SyncScheduler = Depends(get_sync_scheduler)
):
    """
    Get overall sync status and statistics for the tenant
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Get active jobs for this tenant
        all_jobs = scheduler.get_active_jobs()
        tenant_jobs = [job for job in all_jobs if job["tenant_id"] == str(tenant_id)]
        
        # Calculate statistics
        total_jobs = len(tenant_jobs)
        active_jobs = len([job for job in tenant_jobs if job["enabled"]])
        healthy_jobs = len([job for job in tenant_jobs if job["consecutive_failures"] == 0])
        failed_jobs = len([job for job in tenant_jobs if job["consecutive_failures"] > 0])
        
        # Get today's usage metrics
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        usage_data = await scheduler.get_tenant_usage(tenant_id, today, tomorrow)
        
        syncs_today = sum(day.get("total_sync_count", 0) for day in usage_data)
        records_synced_today = sum(day.get("total_records_synced", 0) for day in usage_data)
        
        # Calculate average success rate
        success_rates = [job.get("success_rate", 1.0) for job in usage_data if job.get("success_rate") is not None]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 1.0
        
        return SyncStatsResponse(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            healthy_jobs=healthy_jobs,
            failed_jobs=failed_jobs,
            syncs_today=syncs_today,
            records_synced_today=records_synced_today,
            avg_success_rate=avg_success_rate
        )
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@router.get("/jobs", response_model=List[SyncJobResponse])
async def list_sync_jobs(
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "read")),
    scheduler: SyncScheduler = Depends(get_sync_scheduler)
):
    """
    List all sync jobs for the current tenant
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Get active jobs for this tenant
        all_jobs = scheduler.get_active_jobs()
        tenant_jobs = [job for job in all_jobs if job["tenant_id"] == str(tenant_id)]
        
        result = []
        for job in tenant_jobs:
            health_status = "healthy"
            if job["consecutive_failures"] > 0:
                if job["consecutive_failures"] >= job.get("max_failures", 5):
                    health_status = "disabled"
                elif job["consecutive_failures"] >= 3:
                    health_status = "critical"
                else:
                    health_status = "warning"
            
            result.append(SyncJobResponse(
                job_id=job["job_id"],
                tenant_id=uuid.UUID(job["tenant_id"]),
                integration_id=uuid.UUID(job["integration_id"]),
                integration_name=job["integration_name"],
                integration_type=job["integration_type"],
                frequency=job["frequency"],
                enabled=job["enabled"],
                last_run=job.get("last_run"),
                next_run=job.get("next_run"),
                consecutive_failures=job["consecutive_failures"],
                health_status=health_status
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing sync jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list sync jobs")

@router.put("/{integration_id}/config")
async def update_sync_config(
    integration_id: uuid.UUID,
    request: UpdateSyncConfigRequest,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "write")),
    scheduler: SyncScheduler = Depends(get_sync_scheduler)
):
    """
    Update sync configuration for an integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Convert enum to SyncFrequency
        frequency = SyncFrequency(request.frequency.value)
        
        # Update sync frequency
        success = await scheduler.update_sync_frequency(integration_id, frequency)
        
        if not success:
            raise HTTPException(status_code=404, detail="Integration or sync job not found")
        
        return {
            "success": True,
            "message": f"Sync configuration updated for integration {integration_id}",
            "frequency": request.frequency.value,
            "enabled": request.enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sync config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update sync configuration")

@router.post("/manual")
async def trigger_manual_sync(
    request: ManualSyncRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "write")),
    scheduler: SyncScheduler = Depends(get_sync_scheduler)
):
    """
    Trigger a manual sync for an integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Start manual sync in background
        sync_id = await scheduler.trigger_manual_sync(
            request.integration_id,
            request.incremental
        )
        
        if not sync_id:
            raise HTTPException(status_code=404, detail="Integration not found or sync failed to start")
        
        return {
            "success": True,
            "sync_id": sync_id,
            "message": f"Manual sync started for integration {request.integration_id}",
            "incremental": request.incremental,
            "priority": request.priority
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger manual sync")

@router.get("/usage")
async def get_usage_metrics(
    start_date: datetime = Query(..., description="Start date for usage metrics"),
    end_date: datetime = Query(..., description="End date for usage metrics"),
    integration_id: Optional[uuid.UUID] = Query(None, description="Filter by specific integration"),
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "read")),
    scheduler: SyncScheduler = Depends(get_sync_scheduler)
):
    """
    Get usage metrics for the tenant within a date range
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # Validate date range
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")
        
        if (end_date - start_date).days > 90:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 90 days")
        
        # Get usage data
        usage_data = await scheduler.get_tenant_usage(tenant_id, start_date, end_date)
        
        # Calculate estimated costs (simplified pricing model)
        cost_per_api_call = 0.001  # $0.001 per API call
        
        result = []
        for day_data in usage_data:
            estimated_cost = day_data.get("total_api_calls", 0) * cost_per_api_call
            
            result.append(UsageMetricsResponse(
                date=day_data["usage_date"],
                api_calls_made=day_data.get("total_api_calls", 0),
                records_synced=day_data.get("total_records_synced", 0),
                sync_count=day_data.get("total_sync_count", 0),
                sync_duration_seconds=day_data.get("total_sync_duration", 0),
                success_rate=day_data.get("overall_success_rate", 1.0),
                estimated_cost_usd=estimated_cost
            ))
        
        return {
            "usage_metrics": result,
            "summary": {
                "total_days": len(result),
                "total_api_calls": sum(m.api_calls_made for m in result),
                "total_records_synced": sum(m.records_synced for m in result),
                "total_syncs": sum(m.sync_count for m in result),
                "avg_success_rate": sum(m.success_rate for m in result) / len(result) if result else 1.0,
                "total_estimated_cost": sum(m.estimated_cost_usd for m in result)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting usage metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get usage metrics")

@router.get("/{integration_id}/history")
async def get_sync_history(
    integration_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=1000, description="Number of sync records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "read"))
):
    """
    Get sync history for a specific integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        # This would query the integration_sync_logs table
        # For now, return mock data
        
        # In production, implement actual database query:
        # async with database_pool.acquire() as connection:
        #     await connection.execute(
        #         "SELECT set_config('app.current_tenant_id', $1, false)",
        #         str(tenant_id)
        #     )
        #     
        #     sync_logs = await connection.fetch("""
        #         SELECT * FROM integration_sync_logs
        #         WHERE integration_id = $1
        #         ORDER BY started_at DESC
        #         LIMIT $2 OFFSET $3
        #     """, integration_id, limit, offset)
        
        mock_history = [
            {
                "id": f"sync_{i}",
                "sync_type": "incremental" if i % 2 == 0 else "full",
                "sync_status": "completed" if i % 3 != 0 else "failed",
                "records_synced": 100 - i * 10,
                "records_created": 5,
                "records_updated": 95 - i * 10,
                "started_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "completed_at": (datetime.now() - timedelta(hours=i) + timedelta(minutes=5)).isoformat(),
                "sync_duration_seconds": 300 + i * 10,
                "error_messages": [] if i % 3 != 0 else ["Sample error message"]
            }
            for i in range(offset, min(offset + limit, 20))
        ]
        
        return {
            "sync_history": mock_history,
            "pagination": {
                "total": 20,  # Mock total
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < 20
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting sync history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sync history")

@router.delete("/{integration_id}/sync-job")
async def delete_sync_job(
    integration_id: uuid.UUID,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context),
    current_user: Dict[str, Any] = Depends(require_permission("sync", "delete")),
    scheduler: SyncScheduler = Depends(get_sync_scheduler)
):
    """
    Delete sync job for an integration
    """
    try:
        tenant_id = tenant_context["tenant_id"]
        
        success = await scheduler.remove_integration_sync(integration_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Sync job not found")
        
        return {
            "success": True,
            "message": f"Sync job deleted for integration {integration_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sync job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete sync job")

# Initialization function
def initialize_sync_api(scheduler: SyncScheduler):
    """Initialize the sync API with the sync scheduler"""
    global sync_scheduler
    sync_scheduler = scheduler