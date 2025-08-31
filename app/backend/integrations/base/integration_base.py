"""
PM33 Integration Engine - Base Integration Class
Provides foundation for all PM tool integrations with tenant isolation
"""

import uuid
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import asyncpg
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuration for a tenant's integration"""
    tenant_id: uuid.UUID
    integration_id: uuid.UUID
    integration_type: str
    integration_name: str
    encrypted_credentials: bytes
    configuration: Dict[str, Any]
    field_mappings: Dict[str, Any]
    sync_settings: Dict[str, Any]
    status: str
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None

@dataclass
class SyncResult:
    """Result of a sync operation"""
    success: bool
    records_synced: int
    records_updated: int
    records_created: int
    errors: List[str]
    sync_duration_seconds: float
    last_sync_at: datetime
    next_sync_at: Optional[datetime] = None

@dataclass
class FieldMapping:
    """Field mapping between PM tool and PM33"""
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    confidence: float = 1.0
    is_required: bool = False
    default_value: Any = None

class BaseIntegration(ABC):
    """
    Abstract base class for all PM tool integrations
    
    Provides:
    - Tenant-aware database operations
    - OAuth credential management
    - Sync scheduling and status tracking
    - Field mapping with AI assistance
    - Error handling and logging
    """
    
    def __init__(self, database_pool: asyncpg.Pool, config: IntegrationConfig):
        self.database_pool = database_pool
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the PM tool using stored credentials"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test connection to PM tool and return status"""
        pass
    
    @abstractmethod
    async def sync_data(self, incremental: bool = True) -> SyncResult:
        """Sync data from PM tool to PM33"""
        pass
    
    @abstractmethod
    async def get_available_fields(self) -> List[Dict[str, Any]]:
        """Get available fields from PM tool for mapping"""
        pass
    
    @abstractmethod
    def get_default_field_mappings(self) -> List[FieldMapping]:
        """Get default field mappings for this PM tool"""
        pass
    
    async def set_tenant_context(self, connection: asyncpg.Connection):
        """Set PostgreSQL tenant context for RLS"""
        await connection.execute(
            "SELECT set_config('app.current_tenant_id', $1, false)",
            str(self.config.tenant_id)
        )
    
    async def update_sync_status(self, result: SyncResult):
        """Update integration sync status in database"""
        try:
            async with self.database_pool.acquire() as connection:
                await self.set_tenant_context(connection)
                
                # Update integration status
                await connection.execute(
                    """
                    UPDATE tenant_integrations 
                    SET status = $1, last_sync_at = $2, last_error = $3, updated_at = NOW()
                    WHERE id = $4 AND tenant_id = $5
                    """,
                    "active" if result.success else "error",
                    result.last_sync_at,
                    json.dumps(result.errors) if result.errors else None,
                    self.config.integration_id,
                    self.config.tenant_id
                )
                
                # Log sync result
                await connection.execute(
                    """
                    INSERT INTO tenant_audit_logs (
                        tenant_id, event_type, event_category, event_description,
                        metadata, result
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    self.config.tenant_id,
                    "integration_sync",
                    "data_sync",
                    f"{self.config.integration_type} data sync",
                    {
                        "integration_id": str(self.config.integration_id),
                        "records_synced": result.records_synced,
                        "sync_duration": result.sync_duration_seconds,
                        "errors_count": len(result.errors)
                    },
                    "success" if result.success else "error"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to update sync status: {str(e)}")
    
    async def log_usage(self, operation: str, api_calls: int = 1, tokens_used: int = 0):
        """Log usage for billing purposes"""
        try:
            async with self.database_pool.acquire() as connection:
                await self.set_tenant_context(connection)
                
                await connection.execute(
                    """
                    INSERT INTO tenant_usage_logs (
                        tenant_id, metric_type, metric_value, endpoint,
                        tokens_used, estimated_cost, billing_period
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    self.config.tenant_id,
                    "integration_sync",
                    api_calls,
                    f"{self.config.integration_type}_{operation}",
                    tokens_used,
                    api_calls * 0.001,  # $0.001 per API call estimate
                    datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                )
                
        except Exception as e:
            self.logger.error(f"Failed to log usage: {str(e)}")
    
    async def store_synced_data(self, data_type: str, records: List[Dict[str, Any]]) -> int:
        """Store synced data in PM33 database with tenant isolation"""
        try:
            async with self.database_pool.acquire() as connection:
                await self.set_tenant_context(connection)
                
                # Store in strategic_conversations as structured data
                stored_count = 0
                for record in records:
                    await connection.execute(
                        """
                        INSERT INTO strategic_conversations (
                            tenant_id, user_id, title, conversation_data,
                            strategic_frameworks_used, company_context_id
                        ) VALUES ($1, 
                                 (SELECT id FROM tenant_users WHERE tenant_id = $1 LIMIT 1),
                                 $2, $3, $4, 
                                 (SELECT id FROM company_contexts WHERE tenant_id = $1 LIMIT 1))
                        """,
                        self.config.tenant_id,
                        f"{self.config.integration_type}_{data_type}: {record.get('title', 'Untitled')}",
                        {
                            "integration_type": self.config.integration_type,
                            "data_type": data_type,
                            "source_data": record,
                            "synced_at": datetime.now(timezone.utc).isoformat()
                        },
                        [f"{self.config.integration_type}_sync"]
                    )
                    stored_count += 1
                
                return stored_count
                
        except Exception as e:
            self.logger.error(f"Failed to store synced data: {str(e)}")
            return 0
    
    def decrypt_credentials(self) -> Dict[str, str]:
        """Decrypt stored OAuth credentials (simplified for demo)"""
        try:
            # In production, use proper encryption with tenant-specific keys
            credentials_str = self.config.encrypted_credentials.decode('utf-8')
            return json.loads(credentials_str)
        except Exception as e:
            self.logger.error(f"Failed to decrypt credentials: {str(e)}")
            return {}
    
    async def validate_field_mappings(self) -> List[str]:
        """Validate field mappings and return any issues"""
        issues = []
        available_fields = await self.get_available_fields()
        available_field_names = [field['name'] for field in available_fields]
        
        for source_field, target_field in self.config.field_mappings.items():
            if source_field not in available_field_names:
                issues.append(f"Source field '{source_field}' not available in {self.config.integration_type}")
        
        return issues
    
    async def suggest_field_mappings(self) -> List[FieldMapping]:
        """Use AI to suggest optimal field mappings"""
        # This would integrate with Claude/OpenAI for intelligent mapping
        # For now, return default mappings
        return self.get_default_field_mappings()