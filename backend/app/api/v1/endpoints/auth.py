from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.database import get_db
from app.models.user import Token, UserCreate, UserResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    """Authenticate user and return access token"""
    try:
        # Get user from database
        response = db.table('users').select("*").eq('email', form_data.username).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user = response.data[0]
        
        # Verify password
        if not verify_password(form_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if user['status'] != 'active':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Update last login
        db.table('users').update({
            'last_login': 'now()'
        }).eq('id', user['id']).execute()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email']},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db = Depends(get_db)
):
    """Register new user (creates pending account)"""
    try:
        # Check if user already exists
        response = db.table('users').select("email").eq('email', user_data.email).execute()
        
        if response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        from app.core.security import get_password_hash
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "role": user_data.role,
            "password_hash": password_hash,
            "status": "pending"  # New users start as pending
        }
        
        response = db.table('users').insert(user_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        created_user = response.data[0]
        
        return UserResponse(
            id=created_user['id'],
            name=created_user['name'],
            email=created_user['email'],
            role=created_user['role'],
            status=created_user['status'],
            last_login=None,
            created_at=created_user['created_at'],
            updated_at=created_user['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        status=current_user.status,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat()
    )