from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.core.database import get_db
from app.models.user import UserResponse, UserUpdate, UserRole, UserStatus
from app.api.deps import get_current_active_user, require_admin

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get all users with filtering and pagination"""
    try:
        query = db.table('users').select("*")
        
        # Apply filters
        if role:
            query = query.eq('role', role)
        if status:
            query = query.eq('status', status)
        if search:
            query = query.or_(f'name.ilike.%{search}%,email.ilike.%{search}%')
        
        # Apply pagination
        response = query.range(skip, skip + limit - 1).execute()
        
        users = []
        for user_data in response.data:
            users.append(UserResponse(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                status=user_data['status'],
                last_login=user_data.get('last_login'),
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at']
            ))
        
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )

@router.get("/pending", response_model=List[UserResponse])
async def get_pending_users(
    current_user = Depends(require_admin),
    db = Depends(get_db)
):
    """Get all pending user approvals"""
    try:
        response = db.table('users').select("*").eq('status', 'pending').execute()
        
        users = []
        for user_data in response.data:
            users.append(UserResponse(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                status=user_data['status'],
                last_login=user_data.get('last_login'),
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at']
            ))
        
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending users"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get user by ID"""
    try:
        response = db.table('users').select("*").eq('id', user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = response.data[0]
        return UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            role=user_data['role'],
            status=user_data['status'],
            last_login=user_data.get('last_login'),
            created_at=user_data['created_at'],
            updated_at=user_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user = Depends(require_admin),
    db = Depends(get_db)
):
    """Update user (admin only)"""
    try:
        # Check if user exists
        response = db.table('users').select("*").eq('id', user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = {}
        if user_update.name is not None:
            update_data['name'] = user_update.name
        if user_update.email is not None:
            update_data['email'] = user_update.email
        if user_update.role is not None:
            update_data['role'] = user_update.role
        if user_update.status is not None:
            update_data['status'] = user_update.status
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update user
        response = db.table('users').update(update_data).eq('id', user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        updated_user = response.data[0]
        return UserResponse(
            id=updated_user['id'],
            name=updated_user['name'],
            email=updated_user['email'],
            role=updated_user['role'],
            status=updated_user['status'],
            last_login=updated_user.get('last_login'),
            created_at=updated_user['created_at'],
            updated_at=updated_user['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.post("/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: str,
    current_user = Depends(require_admin),
    db = Depends(get_db)
):
    """Approve pending user"""
    try:
        response = db.table('users').update({
            'status': 'active'
        }).eq('id', user_id).eq('status', 'pending').execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pending user not found"
            )
        
        approved_user = response.data[0]
        return UserResponse(
            id=approved_user['id'],
            name=approved_user['name'],
            email=approved_user['email'],
            role=approved_user['role'],
            status=approved_user['status'],
            last_login=approved_user.get('last_login'),
            created_at=approved_user['created_at'],
            updated_at=approved_user['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve user"
        )

@router.post("/{user_id}/reject")
async def reject_user(
    user_id: str,
    current_user = Depends(require_admin),
    db = Depends(get_db)
):
    """Reject and delete pending user"""
    try:
        response = db.table('users').delete().eq('id', user_id).eq('status', 'pending').execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pending user not found"
            )
        
        return {"message": "User rejected and removed"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject user"
        )