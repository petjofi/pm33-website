"""
PM33 Multi-Tenancy Context Middleware
FastAPI middleware for automatic tenant isolation and security
"""

import uuid
import logging
from typing import Optional, Callable, Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.base import BaseHTTPMiddleware
import asyncpg
import jwt
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Automatic tenant context isolation middleware for PM33 multi-tenancy
    
    Features:
    - Subdomain-based tenant identification
    - Header-based tenant context (API access)
    - Automatic PostgreSQL session variable setting for RLS
    - JWT token validation with tenant claims
    - Security logging and audit trails
    """
    
    def __init__(
        self,
        app: FastAPI,
        database_pool: asyncpg.Pool,
        jwt_secret_key: str,
        excluded_paths: list = None
    ):
        super().__init__(app)
        self.database_pool = database_pool
        self.jwt_secret_key = jwt_secret_key
        self.excluded_paths = excluded_paths or [
            "/health", 
            "/docs", 
            "/openapi.json",
            "/favicon.ico"
        ]
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch function with tenant isolation"""
        
        # Skip tenant context for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
            
        try:
            # Extract tenant context from request
            tenant_context = await self.extract_tenant_context(request)
            
            if not tenant_context:
                logger.warning(f"No tenant context found for request: {request.url}")
                raise HTTPException(
                    status_code=400, 
                    detail="Tenant context required. Please provide tenant via subdomain or X-Tenant-ID header."
                )
            
            # Validate tenant exists and is active
            tenant_info = await self.validate_tenant(tenant_context["tenant_id"])
            if not tenant_info:
                logger.error(f"Invalid tenant ID: {tenant_context['tenant_id']}")
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or inactive tenant"
                )
            
            # Set tenant context in request state
            request.state.tenant_id = tenant_context["tenant_id"]
            request.state.tenant_subdomain = tenant_context.get("subdomain")
            request.state.tenant_info = tenant_info
            
            # Set PostgreSQL session variable for RLS
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_context["tenant_id"])
                )
                
                # Log tenant access for audit
                await self.log_tenant_access(
                    connection,
                    tenant_context["tenant_id"],
                    request
                )
            
            logger.info(f"Tenant context set: {tenant_context['tenant_id']}")
            
            # Process request with tenant context
            response = await call_next(request)
            
            # Add tenant context to response headers (for debugging)
            response.headers["X-Tenant-Context"] = str(tenant_context["tenant_id"])
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Tenant context middleware error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error in tenant context processing"
            )
    
    async def extract_tenant_context(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Extract tenant context from request
        Priority: X-Tenant-ID header > Subdomain > Path-based
        """
        
        # Priority 1: X-Tenant-ID header for API access
        if tenant_header := request.headers.get("X-Tenant-ID"):
            try:
                tenant_id = uuid.UUID(tenant_header)
                return {
                    "tenant_id": tenant_id,
                    "source": "header"
                }
            except ValueError:
                logger.error(f"Invalid tenant UUID in header: {tenant_header}")
                return None
        
        # Priority 2: Subdomain extraction
        host = request.headers.get("host", "")
        if "." in host and not host.startswith("localhost"):
            subdomain = host.split(".")[0]
            
            # Skip common subdomains
            if subdomain not in ["www", "api", "app"]:
                tenant_info = await self.get_tenant_by_subdomain(subdomain)
                if tenant_info:
                    return {
                        "tenant_id": tenant_info["id"],
                        "subdomain": subdomain,
                        "source": "subdomain"
                    }
        
        # Priority 3: JWT token tenant claims
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            tenant_claims = await self.extract_tenant_from_jwt(token)
            if tenant_claims:
                return tenant_claims
        
        # Priority 4: Path-based tenant context (fallback)
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) > 1 and path_parts[0] == "tenant":
            try:
                tenant_id = uuid.UUID(path_parts[1])
                return {
                    "tenant_id": tenant_id,
                    "source": "path"
                }
            except (ValueError, IndexError):
                pass
        
        return None
    
    async def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Dict[str, Any]]:
        """Retrieve tenant information by subdomain"""
        try:
            async with self.database_pool.acquire() as connection:
                result = await connection.fetchrow(
                    """
                    SELECT id, company_name, subscription_tier, subscription_status
                    FROM tenants 
                    WHERE subdomain = $1 AND subscription_status = 'active'
                    """,
                    subdomain
                )
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching tenant by subdomain {subdomain}: {str(e)}")
            return None
    
    async def extract_tenant_from_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract tenant context from JWT token claims"""
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret_key, 
                algorithms=["HS256"]
            )
            
            tenant_id = payload.get("tenant_id")
            if tenant_id:
                return {
                    "tenant_id": uuid.UUID(tenant_id),
                    "user_id": payload.get("sub"),
                    "source": "jwt"
                }
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting tenant from JWT: {str(e)}")
        
        return None
    
    async def validate_tenant(self, tenant_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Validate tenant exists and is active"""
        try:
            async with self.database_pool.acquire() as connection:
                result = await connection.fetchrow(
                    """
                    SELECT id, company_name, subscription_tier, subscription_status,
                           created_at, settings
                    FROM tenants 
                    WHERE id = $1 AND subscription_status IN ('active', 'trial')
                    """,
                    tenant_id
                )
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error validating tenant {tenant_id}: {str(e)}")
            return None
    
    async def log_tenant_access(
        self, 
        connection: asyncpg.Connection, 
        tenant_id: uuid.UUID, 
        request: Request
    ):
        """Log tenant access for audit trail"""
        try:
            await connection.execute(
                """
                INSERT INTO tenant_audit_logs (
                    tenant_id, event_type, event_category, event_description,
                    ip_address, user_agent, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                tenant_id,
                "tenant_access",
                "security",
                f"Tenant access via {request.method} {request.url.path}",
                request.client.host if request.client else None,
                request.headers.get("user-agent"),
                {
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query) if request.url.query else None
                }
            )
        except Exception as e:
            logger.error(f"Error logging tenant access: {str(e)}")


class TenantSecurityMiddleware(BaseHTTPMiddleware):
    """
    Additional security middleware for tenant isolation validation
    """
    
    def __init__(self, app: FastAPI, database_pool: asyncpg.Pool):
        super().__init__(app)
        self.database_pool = database_pool
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate tenant security and prevent cross-tenant access"""
        
        # Skip for non-authenticated endpoints
        if not hasattr(request.state, 'tenant_id'):
            return await call_next(request)
        
        try:
            # Validate tenant context is properly set
            tenant_id = request.state.tenant_id
            
            async with self.database_pool.acquire() as connection:
                # Verify PostgreSQL session variable is set correctly
                current_tenant = await connection.fetchval(
                    "SELECT current_setting('app.current_tenant_id', true)"
                )
                
                if not current_tenant or uuid.UUID(current_tenant) != tenant_id:
                    logger.error(f"Tenant context mismatch: request={tenant_id}, session={current_tenant}")
                    raise HTTPException(
                        status_code=500,
                        detail="Tenant context security validation failed"
                    )
            
            # Process request with validated tenant context
            response = await call_next(request)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Tenant security validation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Tenant security validation failed"
            )


# Utility functions for tenant context management

def get_current_tenant_id(request: Request) -> Optional[uuid.UUID]:
    """Get current tenant ID from request state"""
    return getattr(request.state, 'tenant_id', None)

def get_current_tenant_info(request: Request) -> Optional[Dict[str, Any]]:
    """Get current tenant information from request state"""
    return getattr(request.state, 'tenant_info', None)

def require_tenant_context(request: Request) -> uuid.UUID:
    """Require tenant context and return tenant ID"""
    tenant_id = get_current_tenant_id(request)
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant context required for this operation"
        )
    return tenant_id

# Dependency for FastAPI route handlers
async def get_tenant_context(request: Request) -> Dict[str, Any]:
    """FastAPI dependency to inject tenant context"""
    tenant_id = get_current_tenant_id(request)
    tenant_info = get_current_tenant_info(request)
    
    if not tenant_id or not tenant_info:
        raise HTTPException(
            status_code=403,
            detail="Valid tenant context required"
        )
    
    return {
        "tenant_id": tenant_id,
        "tenant_info": tenant_info,
        "subdomain": getattr(request.state, 'tenant_subdomain', None)
    }


# Database connection helper with tenant context
class TenantAwareDatabase:
    """Database helper that automatically sets tenant context for RLS"""
    
    def __init__(self, database_pool: asyncpg.Pool):
        self.database_pool = database_pool
    
    async def execute_with_tenant_context(
        self, 
        tenant_id: uuid.UUID, 
        query: str, 
        *args
    ):
        """Execute query with tenant context set"""
        async with self.database_pool.acquire() as connection:
            # Set tenant context
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id)
            )
            
            # Execute query with RLS applied
            return await connection.execute(query, *args)
    
    async def fetch_with_tenant_context(
        self, 
        tenant_id: uuid.UUID, 
        query: str, 
        *args
    ):
        """Fetch data with tenant context set"""
        async with self.database_pool.acquire() as connection:
            # Set tenant context
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id)
            )
            
            # Fetch data with RLS applied
            return await connection.fetch(query, *args)