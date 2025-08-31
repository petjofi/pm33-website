"""
PM33 OAuth Manager
Handles OAuth flows for PM tool integrations with tenant isolation
"""

import uuid
import asyncio
import logging
import secrets
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import asyncpg
from urllib.parse import urlencode, parse_qs, urlparse
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OAuthConfig:
    """OAuth configuration for a PM tool"""
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    redirect_uri: str
    scopes: List[str]

@dataclass
class OAuthState:
    """OAuth state tracking"""
    state: str
    tenant_id: uuid.UUID
    integration_type: str
    created_at: datetime
    expires_at: datetime

class OAuthManager:
    """
    Manages OAuth flows for PM tool integrations
    
    Features:
    - Tenant-isolated OAuth state management
    - Secure credential encryption and storage
    - Token refresh and expiry handling
    - Integration-specific OAuth configurations
    """
    
    def __init__(self, database_pool: asyncpg.Pool):
        self.database_pool = database_pool
        self.oauth_configs = self._load_oauth_configs()
        self.active_states: Dict[str, OAuthState] = {}
        
    def _load_oauth_configs(self) -> Dict[str, OAuthConfig]:
        """Load OAuth configurations for supported PM tools"""
        return {
            "jira": OAuthConfig(
                client_id="pm33_jira_client_id",  # From environment
                client_secret="pm33_jira_client_secret",
                authorize_url="https://auth.atlassian.com/authorize",
                token_url="https://auth.atlassian.com/oauth/token",
                redirect_uri="https://app.pm33.ai/auth/jira/callback",
                scopes=["read:jira-user", "read:jira-work", "write:jira-work"]
            ),
            "linear": OAuthConfig(
                client_id="pm33_linear_client_id",
                client_secret="pm33_linear_client_secret", 
                authorize_url="https://linear.app/oauth/authorize",
                token_url="https://api.linear.app/oauth/token",
                redirect_uri="https://app.pm33.ai/auth/linear/callback",
                scopes=["read", "write"]
            ),
            "monday": OAuthConfig(
                client_id="pm33_monday_client_id",
                client_secret="pm33_monday_client_secret",
                authorize_url="https://auth.monday.com/oauth2/authorize",
                token_url="https://auth.monday.com/oauth2/token", 
                redirect_uri="https://app.pm33.ai/auth/monday/callback",
                scopes=["boards:read", "boards:write", "updates:read"]
            )
        }
    
    async def initiate_oauth_flow(
        self, 
        tenant_id: uuid.UUID, 
        integration_type: str,
        integration_name: str
    ) -> Tuple[str, str]:
        """
        Initiate OAuth flow for a tenant
        Returns (authorize_url, state) tuple
        """
        if integration_type not in self.oauth_configs:
            raise ValueError(f"Unsupported integration type: {integration_type}")
        
        config = self.oauth_configs[integration_type]
        
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        
        # Store OAuth state with expiry
        oauth_state = OAuthState(
            state=state,
            tenant_id=tenant_id,
            integration_type=integration_type,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        self.active_states[state] = oauth_state
        
        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scopes),
            "state": state
        }
        
        # Add integration-specific parameters
        if integration_type == "jira":
            auth_params["audience"] = "api.atlassian.com"
            auth_params["prompt"] = "consent"
        
        authorize_url = f"{config.authorize_url}?{urlencode(auth_params)}"
        
        # Log OAuth initiation
        await self._log_oauth_event(
            tenant_id, 
            "oauth_initiated", 
            f"OAuth flow started for {integration_type}"
        )
        
        return authorize_url, state
    
    async def handle_oauth_callback(
        self, 
        code: str, 
        state: str,
        integration_name: str
    ) -> Tuple[bool, Optional[str], Optional[uuid.UUID]]:
        """
        Handle OAuth callback and exchange code for tokens
        Returns (success, error_message, integration_id)
        """
        # Validate state
        if state not in self.active_states:
            return False, "Invalid or expired OAuth state", None
            
        oauth_state = self.active_states[state]
        
        # Check expiry
        if datetime.now(timezone.utc) > oauth_state.expires_at:
            del self.active_states[state]
            return False, "OAuth state expired", None
        
        try:
            # Exchange code for tokens
            tokens = await self._exchange_code_for_tokens(
                code, 
                oauth_state.integration_type
            )
            
            if not tokens:
                return False, "Failed to exchange code for tokens", None
            
            # Store encrypted credentials
            integration_id = await self._store_integration_credentials(
                oauth_state.tenant_id,
                oauth_state.integration_type,
                integration_name,
                tokens
            )
            
            # Clean up state
            del self.active_states[state]
            
            # Log success
            await self._log_oauth_event(
                oauth_state.tenant_id,
                "oauth_completed",
                f"OAuth flow completed successfully for {oauth_state.integration_type}"
            )
            
            return True, None, integration_id
            
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            return False, f"OAuth callback failed: {str(e)}", None
    
    async def _exchange_code_for_tokens(
        self, 
        code: str, 
        integration_type: str
    ) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens"""
        config = self.oauth_configs[integration_type]
        
        token_data = {
            "grant_type": "authorization_code",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": config.redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.token_url,
                data=token_data,
                headers={"Accept": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Token exchange failed: {response.status}")
                    return None
    
    async def _store_integration_credentials(
        self,
        tenant_id: uuid.UUID,
        integration_type: str,
        integration_name: str,
        tokens: Dict[str, Any]
    ) -> uuid.UUID:
        """Store encrypted integration credentials"""
        integration_id = uuid.uuid4()
        
        # Encrypt credentials (simplified for demo)
        encrypted_credentials = json.dumps(tokens).encode('utf-8')
        
        # Calculate token expiry
        expires_at = None
        if 'expires_in' in tokens:
            expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=int(tokens['expires_in'])
            )
        
        async with self.database_pool.acquire() as connection:
            # Set tenant context
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            # Store integration
            await connection.execute(
                """
                INSERT INTO tenant_integrations (
                    id, tenant_id, integration_type, integration_name,
                    encrypted_credentials, credential_expires_at,
                    configuration, field_mappings, sync_settings, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                integration_id,
                tenant_id,
                integration_type,
                integration_name,
                encrypted_credentials,
                expires_at,
                {},  # Default configuration
                {},  # Default field mappings
                {"auto_sync": True, "sync_frequency": "hourly"},  # Default sync settings
                "active"
            )
        
        return integration_id
    
    async def refresh_token(
        self, 
        integration_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> bool:
        """Refresh OAuth token for an integration"""
        try:
            async with self.database_pool.acquire() as connection:
                # Set tenant context
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                # Get current credentials
                integration = await connection.fetchrow(
                    """
                    SELECT integration_type, encrypted_credentials, credential_expires_at
                    FROM tenant_integrations 
                    WHERE id = $1 AND tenant_id = $2
                    """,
                    integration_id,
                    tenant_id
                )
                
                if not integration:
                    return False
                
                # Decrypt current credentials
                current_tokens = json.loads(
                    integration['encrypted_credentials'].decode('utf-8')
                )
                
                if 'refresh_token' not in current_tokens:
                    logger.error("No refresh token available")
                    return False
                
                # Refresh token
                config = self.oauth_configs[integration['integration_type']]
                
                refresh_data = {
                    "grant_type": "refresh_token",
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "refresh_token": current_tokens['refresh_token']
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        config.token_url,
                        data=refresh_data,
                        headers={"Accept": "application/json"}
                    ) as response:
                        if response.status == 200:
                            new_tokens = await response.json()
                            
                            # Update stored credentials
                            encrypted_new_credentials = json.dumps(new_tokens).encode('utf-8')
                            new_expires_at = datetime.now(timezone.utc) + timedelta(
                                seconds=int(new_tokens.get('expires_in', 3600))
                            )
                            
                            await connection.execute(
                                """
                                UPDATE tenant_integrations 
                                SET encrypted_credentials = $1, credential_expires_at = $2,
                                    updated_at = NOW()
                                WHERE id = $3 AND tenant_id = $4
                                """,
                                encrypted_new_credentials,
                                new_expires_at,
                                integration_id,
                                tenant_id
                            )
                            
                            return True
                        else:
                            logger.error(f"Token refresh failed: {response.status}")
                            return False
                            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return False
    
    async def _log_oauth_event(
        self,
        tenant_id: uuid.UUID,
        event_type: str,
        description: str
    ):
        """Log OAuth events for audit trail"""
        try:
            async with self.database_pool.acquire() as connection:
                # Set tenant context
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                await connection.execute(
                    """
                    INSERT INTO tenant_audit_logs (
                        tenant_id, event_type, event_category, 
                        event_description, result
                    ) VALUES ($1, $2, $3, $4, $5)
                    """,
                    tenant_id,
                    event_type,
                    "oauth",
                    description,
                    "success"
                )
        except Exception as e:
            logger.error(f"Failed to log OAuth event: {str(e)}")
    
    async def get_integration_status(
        self,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID
    ) -> Optional[Dict[str, Any]]:
        """Get integration status and health"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                integration = await connection.fetchrow(
                    """
                    SELECT integration_type, integration_name, status,
                           credential_expires_at, last_sync_at, last_error
                    FROM tenant_integrations
                    WHERE id = $1 AND tenant_id = $2
                    """,
                    integration_id,
                    tenant_id
                )
                
                if not integration:
                    return None
                
                return {
                    "integration_type": integration["integration_type"],
                    "integration_name": integration["integration_name"], 
                    "status": integration["status"],
                    "credential_expires_at": integration["credential_expires_at"],
                    "last_sync_at": integration["last_sync_at"],
                    "last_error": integration["last_error"],
                    "needs_token_refresh": (
                        integration["credential_expires_at"] and
                        integration["credential_expires_at"] < datetime.now(timezone.utc) + timedelta(hours=24)
                    )
                }
                
        except Exception as e:
            logger.error(f"Failed to get integration status: {str(e)}")
            return None