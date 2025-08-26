"""Authentication routes for PM33 Intelligence Operations."""

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from authlib.integrations.starlette_client import OAuth
from services.user_service import UserService
from services.stripe_service import StripeService
from utils.auth import create_access_token, get_current_user
from utils.database import get_db
from utils.config import settings
from utils.logging import logger

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# OAuth configuration
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


class UserRegistration(BaseModel):
    """User registration schema."""
    email: EmailStr
    username: str
    password: str
    first_name: str = None
    last_name: str = None
    company: str = None


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str
    user: dict


class UserProfile(BaseModel):
    """User profile schema."""
    first_name: str = None
    last_name: str = None
    company: str = None


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str


@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    try:
        # Create user account
        user = await UserService.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            company=user_data.company
        )
        
        # Create Stripe customer
        try:
            stripe_customer = StripeService.create_customer(
                email=user.email,
                name=user.full_name,
                metadata={"user_id": str(user.id)}
            )
            
            # Update user with Stripe customer ID
            await UserService.set_stripe_customer_id(
                db, user.id, stripe_customer.id
            )
            
        except Exception as e:
            logger.warning(f"Failed to create Stripe customer for user {user.id}: {str(e)}")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token."""
    user = await UserService.authenticate_user(
        db, form_data.username, form_data.password  # username field contains email
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user.to_dict()
    )


@router.post("/login-email", response_model=Token)
async def login_user_email(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password."""
    user = await UserService.authenticate_user(
        db, login_data.email, login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user.to_dict()
    )


@router.get("/me")
async def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user.to_dict()


@router.put("/me")
async def update_user_profile(
    profile_data: UserProfile,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile."""
    updated_user = await UserService.update_user_profile(
        db=db,
        user_id=current_user.id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        company=profile_data.company
    )
    
    return updated_user.to_dict()


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    success = await UserService.change_password(
        db=db,
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout_user():
    """Logout user (client should discard token)."""
    return {"message": "Logged out successfully"}


@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth login."""
    redirect_uri = f"{str(request.base_url).rstrip('/')}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback and create/authenticate user."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
        
        email = user_info.get('email')
        name = user_info.get('name', '')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = await UserService.get_user_by_email(db, email)
        
        if not user:
            # Create new user account
            user = await UserService.create_oauth_user(
                db=db,
                email=email,
                username=email,  # Use email as username for OAuth users
                first_name=first_name,
                last_name=last_name,
                provider='google',
                provider_id=user_info.get('sub')
            )
            
            # Create Stripe customer for new user
            try:
                stripe_customer = StripeService.create_customer(
                    email=user.email,
                    name=user.full_name,
                    metadata={"user_id": str(user.id)}
                )
                
                await UserService.set_stripe_customer_id(
                    db, user.id, stripe_customer.id
                )
                
            except Exception as e:
                logger.warning(f"Failed to create Stripe customer for OAuth user {user.id}: {str(e)}")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token (in production, use secure httpOnly cookies)
        frontend_url = settings.frontend_url or "http://localhost:3000"
        redirect_url = f"{frontend_url}/dashboard?token={access_token}"
        
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        frontend_url = settings.frontend_url or "http://localhost:3000"
        error_url = f"{frontend_url}/auth/error?error=oauth_failed"
        return RedirectResponse(url=error_url)