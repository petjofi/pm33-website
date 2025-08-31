"""
PM33 Multi-Tenant JWT Authentication System
Secure JWT authentication with tenant claims and RBAC
"""

import uuid
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import asyncpg
import logging
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

class TokenData(BaseModel):
    """JWT token payload data"""
    sub: str  # user_id
    tenant_id: str
    tenant_subdomain: str
    role: str
    permissions: Dict[str, Any]
    subscription_tier: str
    features: List[str]
    exp: int
    iat: int

class UserCredentials(BaseModel):
    """User login credentials"""
    email: EmailStr
    password: str
    tenant_subdomain: Optional[str] = None

class UserRegistration(BaseModel):
    """User registration data"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    tenant_subdomain: str
    role: str = "member"

class JWTAuthManager:
    """
    JWT Authentication Manager with multi-tenant support
    
    Features:
    - Tenant-aware authentication
    - Role-based access control (RBAC)
    - JWT token generation with tenant claims
    - Password hashing and verification
    - Session management
    """
    
    def __init__(
        self, 
        database_pool: asyncpg.Pool,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.database_pool = database_pool
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        # Subscription tier features mapping
        self.tier_features = {
            "professional": [
                "basic_strategic_intelligence",
                "basic_integrations",
                "core_frameworks"
            ],
            "enterprise": [
                "advanced_strategic_intelligence",
                "unlimited_integrations", 
                "advanced_frameworks",
                "competitive_intelligence",
                "team_collaboration"
            ],
            "strategic": [
                "custom_ai_training",
                "advanced_analytics",
                "white_glove_support",
                "api_access",
                "custom_frameworks"
            ]
        }
        
        # Role permissions mapping
        self.role_permissions = {
            "admin": {
                "user_management": ["read", "write", "delete"],
                "billing": ["read", "write"],
                "integrations": ["read", "write", "delete"],
                "strategic_intelligence": ["read", "write"],
                "settings": ["read", "write"]
            },
            "member": {
                "strategic_intelligence": ["read", "write"],
                "integrations": ["read"],
                "settings": ["read"]
            },
            "read_only": {
                "strategic_intelligence": ["read"],
                "integrations": ["read"]
            }
        }
    
    async def authenticate_user(
        self, 
        credentials: UserCredentials
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with tenant context
        Returns user info with tenant context if successful
        """
        try:
            async with self.database_pool.acquire() as connection:
                # Find user by email and tenant
                query = """
                    SELECT u.id, u.tenant_id, u.email, u.role, u.password_hash,
                           u.first_name, u.last_name, u.permissions,
                           t.subdomain, t.company_name, t.subscription_tier,
                           t.subscription_status, t.settings
                    FROM tenant_users u
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.email = $1 
                    AND ($2::text IS NULL OR t.subdomain = $2)
                    AND t.subscription_status IN ('active', 'trial')
                """
                
                user_record = await connection.fetchrow(
                    query, 
                    credentials.email,
                    credentials.tenant_subdomain
                )
                
                if not user_record:
                    logger.warning(f"User not found: {credentials.email}")
                    return None
                
                # Verify password
                if not self.verify_password(credentials.password, user_record['password_hash']):
                    logger.warning(f"Invalid password for user: {credentials.email}")
                    return None
                
                # Update last login
                await connection.execute(
                    "UPDATE tenant_users SET last_login_at = NOW() WHERE id = $1",
                    user_record['id']
                )
                
                # Log successful authentication
                await connection.execute(
                    """
                    INSERT INTO tenant_audit_logs (
                        tenant_id, user_id, event_type, event_category,
                        event_description, result
                    ) VALUES ($1, $2, 'user_login', 'security', 'User login successful', 'success')
                    """,
                    user_record['tenant_id'],
                    user_record['id']
                )
                
                return dict(user_record)
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    async def create_access_token(
        self, 
        user_data: Dict[str, Any]
    ) -> str:
        """Create JWT access token with tenant claims"""
        
        # Calculate expiration
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        
        # Get user permissions
        user_permissions = user_data.get('permissions', {})
        role_permissions = self.role_permissions.get(user_data['role'], {})
        
        # Merge user-specific and role-based permissions
        combined_permissions = {**role_permissions, **user_permissions}
        
        # Get subscription tier features
        tier_features = self.tier_features.get(
            user_data['subscription_tier'], 
            self.tier_features['professional']
        )
        
        # Build JWT payload with tenant claims
        payload = {
            # Standard claims
            "sub": str(user_data['id']),  # Subject (user ID)
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": "pm33-auth-service",
            
            # Tenant claims
            "tenant_id": str(user_data['tenant_id']),
            "tenant_subdomain": user_data['subdomain'],
            
            # User claims
            "email": user_data['email'],
            "role": user_data['role'],
            "permissions": combined_permissions,
            
            # Subscription claims
            "subscription_tier": user_data['subscription_tier'],
            "subscription_status": user_data['subscription_status'],
            "features": tier_features,
            
            # User profile
            "first_name": user_data['first_name'],
            "last_name": user_data['last_name']
        }
        
        # Encode JWT token
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify token hasn't expired
            if datetime.fromtimestamp(payload['exp'], timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token has expired")
                return None
            
            # Verify user still exists and is active
            user_valid = await self.verify_user_active(
                uuid.UUID(payload['sub']),
                uuid.UUID(payload['tenant_id'])
            )
            
            if not user_valid:
                logger.warning(f"User no longer active: {payload['sub']}")
                return None
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None
    
    async def verify_user_active(
        self, 
        user_id: uuid.UUID, 
        tenant_id: uuid.UUID
    ) -> bool:
        """Verify user is still active in tenant"""
        try:
            async with self.database_pool.acquire() as connection:
                result = await connection.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM tenant_users u
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.id = $1 
                    AND u.tenant_id = $2
                    AND t.subscription_status IN ('active', 'trial')
                    """,
                    user_id,
                    tenant_id
                )
                return result > 0
        except Exception as e:
            logger.error(f"Error verifying user active status: {str(e)}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    async def register_user(
        self, 
        registration: UserRegistration
    ) -> Optional[Dict[str, Any]]:
        """Register new user in tenant"""
        try:
            async with self.database_pool.acquire() as connection:
                # Check if tenant exists
                tenant = await connection.fetchrow(
                    "SELECT id, subscription_tier FROM tenants WHERE subdomain = $1",
                    registration.tenant_subdomain
                )
                
                if not tenant:
                    raise HTTPException(
                        status_code=404,
                        detail="Tenant not found"
                    )
                
                # Check if user already exists
                existing_user = await connection.fetchval(
                    "SELECT COUNT(*) FROM tenant_users WHERE tenant_id = $1 AND email = $2",
                    tenant['id'],
                    registration.email
                )
                
                if existing_user > 0:
                    raise HTTPException(
                        status_code=409,
                        detail="User already exists in this tenant"
                    )
                
                # Hash password
                password_hash = self.hash_password(registration.password)
                
                # Create user
                user_id = await connection.fetchval(
                    """
                    INSERT INTO tenant_users (
                        tenant_id, email, role, first_name, last_name, 
                        password_hash, email_verified
                    ) VALUES ($1, $2, $3, $4, $5, $6, false)
                    RETURNING id
                    """,
                    tenant['id'],
                    registration.email,
                    registration.role,
                    registration.first_name,
                    registration.last_name,
                    password_hash
                )
                
                # Log user creation
                await connection.execute(
                    """
                    INSERT INTO tenant_audit_logs (
                        tenant_id, user_id, event_type, event_category,
                        event_description, result
                    ) VALUES ($1, $2, 'user_created', 'security', 'New user registration', 'success')
                    """,
                    tenant['id'],
                    user_id
                )
                
                return {
                    "user_id": user_id,
                    "tenant_id": tenant['id'],
                    "email": registration.email,
                    "role": registration.role
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User registration error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Registration failed"
            )
    
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        try:
            # Verify refresh token
            payload = await self.verify_token(refresh_token)
            if not payload:
                return None
            
            # Get fresh user data
            async with self.database_pool.acquire() as connection:
                user_data = await connection.fetchrow(
                    """
                    SELECT u.id, u.tenant_id, u.email, u.role, u.permissions,
                           u.first_name, u.last_name,
                           t.subdomain, t.company_name, t.subscription_tier,
                           t.subscription_status
                    FROM tenant_users u
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.id = $1 AND u.tenant_id = $2
                    """,
                    uuid.UUID(payload['sub']),
                    uuid.UUID(payload['tenant_id'])
                )
                
                if not user_data:
                    return None
                
                # Generate new access token
                return await self.create_access_token(dict(user_data))
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return None
    
    async def revoke_token(
        self, 
        user_id: uuid.UUID, 
        tenant_id: uuid.UUID
    ) -> bool:
        """Revoke user tokens (logout)"""
        try:
            async with self.database_pool.acquire() as connection:
                # Clear session token
                await connection.execute(
                    """
                    UPDATE tenant_users 
                    SET session_token = NULL, session_expires_at = NULL
                    WHERE id = $1 AND tenant_id = $2
                    """,
                    user_id,
                    tenant_id
                )
                
                # Log logout
                await connection.execute(
                    """
                    INSERT INTO tenant_audit_logs (
                        tenant_id, user_id, event_type, event_category,
                        event_description, result
                    ) VALUES ($1, $2, 'user_logout', 'security', 'User logout', 'success')
                    """,
                    tenant_id,
                    user_id
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            return False


# FastAPI dependencies for authentication

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_manager: JWTAuthManager = Depends()
) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    
    token_data = await auth_manager.verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data

async def require_role(required_role: str):
    """FastAPI dependency to require specific role"""
    def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user['role'] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    return role_checker

async def require_permission(resource: str, action: str):
    """FastAPI dependency to require specific permission"""
    def permission_checker(current_user: Dict = Depends(get_current_user)):
        user_permissions = current_user.get('permissions', {})
        resource_permissions = user_permissions.get(resource, [])
        
        if action not in resource_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {resource}.{action}"
            )
        return current_user
    return permission_checker