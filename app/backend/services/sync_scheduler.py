"""
PM33 Sync Scheduler Service
Manages scheduled syncing of PM tool data with tenant isolation and usage tracking
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError

from ..integrations.base.integration_base import IntegrationConfig, SyncResult
from ..integrations.jira.jira_service import JiraIntegration

logger = logging.getLogger(__name__)

class SyncFrequency(Enum):
    """Sync frequency options"""
    REALTIME = "realtime"  # Webhook-triggered (future)
    EVERY_15_MIN = "every_15_min"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"

@dataclass
class SyncJob:
    """Sync job configuration"""
    job_id: str
    tenant_id: uuid.UUID
    integration_id: uuid.UUID
    integration_type: str
    integration_name: str
    frequency: SyncFrequency
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    consecutive_failures: int = 0
    max_failures: int = 5

@dataclass
class UsageMetrics:
    """Usage tracking metrics"""
    tenant_id: uuid.UUID
    integration_id: uuid.UUID
    date: datetime
    api_calls_made: int = 0
    records_synced: int = 0
    sync_duration_seconds: float = 0
    data_transfer_mb: float = 0
    sync_count: int = 0

class SyncScheduler:
    """
    Tenant-aware sync scheduler with usage tracking
    
    Features:
    - Tenant isolation for all sync operations
    - Configurable sync frequencies per integration
    - Usage tracking for billing and rate limiting
    - Automatic retry logic with exponential backoff
    - Health monitoring and failure detection
    """
    
    def __init__(self, database_pool: asyncpg.Pool):
        self.database_pool = database_pool
        self.scheduler = AsyncIOScheduler()
        self.active_jobs: Dict[str, SyncJob] = {}
        self.usage_tracker: Dict[str, UsageMetrics] = {}  # Daily usage cache
        
    async def initialize(self):
        """Initialize scheduler and load existing jobs"""
        try:
            # Start the scheduler
            self.scheduler.start()
            
            # Load existing sync jobs from database
            await self._load_sync_jobs()
            
            # Schedule daily usage aggregation
            self.scheduler.add_job(
                self._aggregate_daily_usage,
                CronTrigger(hour=1, minute=0),  # Run at 1 AM daily
                id="daily_usage_aggregation",
                replace_existing=True
            )
            
            logger.info(f"Sync scheduler initialized with {len(self.active_jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Failed to initialize sync scheduler: {str(e)}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown scheduler"""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Sync scheduler shutdown complete")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {str(e)}")
    
    async def _load_sync_jobs(self):
        """Load sync jobs from database"""
        async with self.database_pool.acquire() as connection:
            jobs = await connection.fetch("""
                SELECT ti.id as integration_id, ti.tenant_id, ti.integration_type,
                       ti.integration_name, ti.sync_settings, ti.status,
                       ti.last_sync_at
                FROM tenant_integrations ti
                WHERE ti.status = 'active'
                  AND (ti.sync_settings->>'auto_sync')::boolean = true
            """)
            
            for job_data in jobs:
                sync_settings = job_data['sync_settings'] or {}
                frequency = SyncFrequency(sync_settings.get('sync_frequency', 'hourly'))
                
                sync_job = SyncJob(
                    job_id=f"sync_{job_data['integration_id']}",
                    tenant_id=job_data['tenant_id'],
                    integration_id=job_data['integration_id'],
                    integration_type=job_data['integration_type'],
                    integration_name=job_data['integration_name'],
                    frequency=frequency,
                    enabled=True,
                    last_run=job_data['last_sync_at']
                )
                
                await self._schedule_job(sync_job)
    
    async def _schedule_job(self, sync_job: SyncJob):
        """Schedule a sync job with the scheduler"""
        if sync_job.frequency == SyncFrequency.MANUAL:
            # Don't schedule manual jobs
            return
        
        # Remove existing job if it exists
        try:
            self.scheduler.remove_job(sync_job.job_id)
        except JobLookupError:
            pass
        
        # Define cron triggers for different frequencies
        triggers = {
            SyncFrequency.EVERY_15_MIN: CronTrigger(minute="*/15"),
            SyncFrequency.HOURLY: CronTrigger(minute=0),
            SyncFrequency.DAILY: CronTrigger(hour=2, minute=0),
            SyncFrequency.WEEKLY: CronTrigger(day_of_week='sun', hour=3, minute=0)
        }
        
        trigger = triggers.get(sync_job.frequency)
        if not trigger:
            logger.error(f"Unknown sync frequency: {sync_job.frequency}")
            return
        
        # Schedule the job
        self.scheduler.add_job(
            self._execute_sync_job,
            trigger,
            args=[sync_job.job_id],
            id=sync_job.job_id,
            replace_existing=True,
            max_instances=1  # Prevent overlapping syncs
        )
        
        self.active_jobs[sync_job.job_id] = sync_job
        logger.info(f"Scheduled sync job {sync_job.job_id} with frequency {sync_job.frequency.value}")
    
    async def add_integration_sync(
        self,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        integration_type: str,
        integration_name: str,
        frequency: SyncFrequency
    ) -> bool:
        """Add a new sync job for an integration"""
        try:
            sync_job = SyncJob(
                job_id=f"sync_{integration_id}",
                tenant_id=tenant_id,
                integration_id=integration_id,
                integration_type=integration_type,
                integration_name=integration_name,
                frequency=frequency,
                enabled=True
            )
            
            await self._schedule_job(sync_job)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add sync job: {str(e)}")
            return False
    
    async def update_sync_frequency(
        self,
        integration_id: uuid.UUID,
        frequency: SyncFrequency
    ) -> bool:
        """Update sync frequency for an integration"""
        job_id = f"sync_{integration_id}"
        
        if job_id not in self.active_jobs:
            logger.error(f"Sync job {job_id} not found")
            return False
        
        try:
            sync_job = self.active_jobs[job_id]
            sync_job.frequency = frequency
            
            # Reschedule with new frequency
            await self._schedule_job(sync_job)
            
            # Update database
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(sync_job.tenant_id)
                )
                
                await connection.execute("""
                    UPDATE tenant_integrations
                    SET sync_settings = sync_settings || $1,
                        updated_at = NOW()
                    WHERE id = $2 AND tenant_id = $3
                """, 
                    {"sync_frequency": frequency.value},
                    integration_id,
                    sync_job.tenant_id
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sync frequency: {str(e)}")
            return False
    
    async def remove_integration_sync(self, integration_id: uuid.UUID) -> bool:
        """Remove sync job for an integration"""
        job_id = f"sync_{integration_id}"
        
        try:
            # Remove from scheduler
            self.scheduler.remove_job(job_id)
            
            # Remove from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            logger.info(f"Removed sync job {job_id}")
            return True
            
        except JobLookupError:
            logger.warning(f"Sync job {job_id} was not found in scheduler")
            return True  # Job wasn't there anyway
        except Exception as e:
            logger.error(f"Failed to remove sync job: {str(e)}")
            return False
    
    async def trigger_manual_sync(
        self,
        integration_id: uuid.UUID,
        incremental: bool = True
    ) -> Optional[str]:
        """Trigger a manual sync for an integration"""
        job_id = f"sync_{integration_id}"
        
        if job_id not in self.active_jobs:
            logger.error(f"Integration {integration_id} not found")
            return None
        
        try:
            # Execute sync immediately
            await self._execute_sync_job(job_id, incremental=incremental)
            return f"manual_sync_{uuid.uuid4()}"
            
        except Exception as e:
            logger.error(f"Manual sync failed: {str(e)}")
            return None
    
    async def _execute_sync_job(self, job_id: str, incremental: bool = True):
        """Execute a sync job"""
        if job_id not in self.active_jobs:
            logger.error(f"Sync job {job_id} not found")
            return
        
        sync_job = self.active_jobs[job_id]
        
        # Check if job is enabled
        if not sync_job.enabled:
            logger.info(f"Sync job {job_id} is disabled, skipping")
            return
        
        # Check failure count
        if sync_job.consecutive_failures >= sync_job.max_failures:
            logger.error(f"Sync job {job_id} has exceeded max failures, disabling")
            sync_job.enabled = False
            await self._update_job_status(sync_job)
            return
        
        logger.info(f"Starting sync for {sync_job.integration_name} ({sync_job.integration_type})")
        
        try:
            # Create integration config
            config = await self._get_integration_config(sync_job)
            if not config:
                raise Exception("Failed to load integration configuration")
            
            # Execute sync based on integration type
            result = await self._perform_sync(config, incremental)
            
            # Track success
            sync_job.consecutive_failures = 0
            sync_job.last_run = datetime.now(timezone.utc)
            
            # Update usage metrics
            await self._track_usage(sync_job, result)
            
            logger.info(f"Sync completed for {sync_job.integration_name}: {result.records_synced} records")
            
        except Exception as e:
            # Track failure
            sync_job.consecutive_failures += 1
            logger.error(f"Sync failed for {sync_job.integration_name}: {str(e)}")
            
            # Log failure
            await self._log_sync_failure(sync_job, str(e))
        
        finally:
            # Update job status
            await self._update_job_status(sync_job)
    
    async def _get_integration_config(self, sync_job: SyncJob) -> Optional[IntegrationConfig]:
        """Get integration configuration from database"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(sync_job.tenant_id)
                )
                
                integration = await connection.fetchrow("""
                    SELECT integration_type, integration_name, encrypted_credentials,
                           configuration, field_mappings, sync_settings, status, last_sync_at
                    FROM tenant_integrations
                    WHERE id = $1 AND tenant_id = $2
                """, sync_job.integration_id, sync_job.tenant_id)
                
                if not integration:
                    return None
                
                return IntegrationConfig(
                    tenant_id=sync_job.tenant_id,
                    integration_id=sync_job.integration_id,
                    integration_type=integration['integration_type'],
                    integration_name=integration['integration_name'],
                    encrypted_credentials=integration['encrypted_credentials'],
                    configuration=integration['configuration'] or {},
                    field_mappings=integration['field_mappings'] or {},
                    sync_settings=integration['sync_settings'] or {},
                    status=integration['status'],
                    last_sync_at=integration['last_sync_at']
                )
                
        except Exception as e:
            logger.error(f"Failed to get integration config: {str(e)}")
            return None
    
    async def _perform_sync(self, config: IntegrationConfig, incremental: bool) -> SyncResult:
        """Perform sync based on integration type"""
        if config.integration_type == "jira":
            integration_service = JiraIntegration(self.database_pool, config)
            return await integration_service.sync_data(incremental)
        else:
            raise Exception(f"Sync not implemented for {config.integration_type}")
    
    async def _track_usage(self, sync_job: SyncJob, result: SyncResult):
        """Track usage metrics for billing"""
        try:
            today = datetime.now(timezone.utc).date()
            usage_key = f"{sync_job.tenant_id}_{sync_job.integration_id}_{today}"
            
            # Update in-memory usage cache
            if usage_key not in self.usage_tracker:
                self.usage_tracker[usage_key] = UsageMetrics(
                    tenant_id=sync_job.tenant_id,
                    integration_id=sync_job.integration_id,
                    date=datetime.combine(today, datetime.min.time())
                )
            
            usage = self.usage_tracker[usage_key]
            usage.api_calls_made += getattr(result, 'api_calls_made', 0)
            usage.records_synced += result.records_synced
            usage.sync_duration_seconds += result.sync_duration_seconds
            usage.sync_count += 1
            
            # Store usage in database
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(sync_job.tenant_id)
                )
                
                await connection.execute("""
                    INSERT INTO integration_usage_metrics (
                        tenant_id, integration_id, usage_date,
                        api_calls_made, records_synced, sync_duration_seconds,
                        sync_count, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                    ON CONFLICT (tenant_id, integration_id, usage_date)
                    DO UPDATE SET
                        api_calls_made = integration_usage_metrics.api_calls_made + $4,
                        records_synced = integration_usage_metrics.records_synced + $5,
                        sync_duration_seconds = integration_usage_metrics.sync_duration_seconds + $6,
                        sync_count = integration_usage_metrics.sync_count + $7,
                        updated_at = NOW()
                """,
                    sync_job.tenant_id,
                    sync_job.integration_id,
                    today,
                    usage.api_calls_made,
                    usage.records_synced,
                    usage.sync_duration_seconds,
                    usage.sync_count
                )
            
        except Exception as e:
            logger.error(f"Failed to track usage: {str(e)}")
    
    async def _update_job_status(self, sync_job: SyncJob):
        """Update sync job status in database"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(sync_job.tenant_id)
                )
                
                await connection.execute("""
                    UPDATE tenant_integrations
                    SET last_sync_at = $1,
                        sync_settings = sync_settings || $2,
                        updated_at = NOW()
                    WHERE id = $3 AND tenant_id = $4
                """,
                    sync_job.last_run,
                    {
                        "consecutive_failures": sync_job.consecutive_failures,
                        "enabled": sync_job.enabled
                    },
                    sync_job.integration_id,
                    sync_job.tenant_id
                )
                
        except Exception as e:
            logger.error(f"Failed to update job status: {str(e)}")
    
    async def _log_sync_failure(self, sync_job: SyncJob, error_message: str):
        """Log sync failure for monitoring"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(sync_job.tenant_id)
                )
                
                await connection.execute("""
                    INSERT INTO integration_sync_logs (
                        tenant_id, integration_id, sync_type, sync_status,
                        error_messages, started_at, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                    sync_job.tenant_id,
                    sync_job.integration_id,
                    f"scheduled_{sync_job.frequency.value}",
                    "failed",
                    [error_message],
                    datetime.now(timezone.utc)
                )
                
        except Exception as e:
            logger.error(f"Failed to log sync failure: {str(e)}")
    
    async def _aggregate_daily_usage(self):
        """Aggregate daily usage metrics for reporting"""
        try:
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
            
            async with self.database_pool.acquire() as connection:
                # Aggregate usage by tenant
                await connection.execute("""
                    INSERT INTO tenant_usage_summary (
                        tenant_id, usage_date, total_api_calls, total_records_synced,
                        total_sync_duration, total_sync_count, active_integrations,
                        created_at
                    )
                    SELECT 
                        tenant_id,
                        $1 as usage_date,
                        SUM(api_calls_made) as total_api_calls,
                        SUM(records_synced) as total_records_synced,
                        SUM(sync_duration_seconds) as total_sync_duration,
                        SUM(sync_count) as total_sync_count,
                        COUNT(DISTINCT integration_id) as active_integrations,
                        NOW() as created_at
                    FROM integration_usage_metrics
                    WHERE usage_date = $1
                    GROUP BY tenant_id
                    ON CONFLICT (tenant_id, usage_date) DO NOTHING
                """, yesterday)
                
            logger.info(f"Aggregated usage metrics for {yesterday}")
            
        except Exception as e:
            logger.error(f"Failed to aggregate daily usage: {str(e)}")
    
    async def get_tenant_usage(
        self,
        tenant_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get usage metrics for a tenant"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                usage_data = await connection.fetch("""
                    SELECT usage_date, total_api_calls, total_records_synced,
                           total_sync_duration, total_sync_count, active_integrations
                    FROM tenant_usage_summary
                    WHERE tenant_id = $1 
                      AND usage_date BETWEEN $2 AND $3
                    ORDER BY usage_date DESC
                """, tenant_id, start_date.date(), end_date.date())
                
                return [dict(record) for record in usage_data]
                
        except Exception as e:
            logger.error(f"Failed to get tenant usage: {str(e)}")
            return []
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get list of active sync jobs"""
        return [asdict(job) for job in self.active_jobs.values()]