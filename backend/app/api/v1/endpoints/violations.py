from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, date
from app.core.database import get_db
from app.models.violation import ViolationResponse, ViolationCreate, ViolationUpdate, ViolationType, ViolationStatus
from app.api.deps import get_current_active_user, require_operator

router = APIRouter()

@router.get("/", response_model=List[ViolationResponse])
async def get_violations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plate_number: Optional[str] = None,
    violation_type: Optional[ViolationType] = None,
    status: Optional[ViolationStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get all violations with filtering and pagination"""
    try:
        query = db.table('violations').select("*")
        
        # Apply filters
        if plate_number:
            query = query.ilike('plate_number', f'%{plate_number}%')
        if violation_type:
            query = query.eq('violation_type', violation_type)
        if status:
            query = query.eq('status', status)
        if date_from:
            query = query.gte('date_time', date_from.isoformat())
        if date_to:
            query = query.lte('date_time', date_to.isoformat())
        if search:
            query = query.or_(f'plate_number.ilike.%{search}%,location.ilike.%{search}%,description.ilike.%{search}%')
        
        # Apply pagination and ordering
        response = query.order('date_time', desc=True).range(skip, skip + limit - 1).execute()
        
        violations = []
        for violation_data in response.data:
            violations.append(ViolationResponse(
                id=violation_data['id'],
                plate_number=violation_data['plate_number'],
                violation_type=violation_data['violation_type'],
                location=violation_data['location'],
                date_time=violation_data['date_time'],
                status=violation_data['status'],
                description=violation_data.get('description'),
                fine_amount=violation_data.get('fine_amount'),
                created_at=violation_data['created_at'],
                updated_at=violation_data['updated_at']
            ))
        
        return violations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch violations"
        )

@router.get("/{violation_id}", response_model=ViolationResponse)
async def get_violation(
    violation_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get violation by ID"""
    try:
        response = db.table('violations').select("*").eq('id', violation_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        violation_data = response.data[0]
        return ViolationResponse(
            id=violation_data['id'],
            plate_number=violation_data['plate_number'],
            violation_type=violation_data['violation_type'],
            location=violation_data['location'],
            date_time=violation_data['date_time'],
            status=violation_data['status'],
            description=violation_data.get('description'),
            fine_amount=violation_data.get('fine_amount'),
            created_at=violation_data['created_at'],
            updated_at=violation_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch violation"
        )

@router.post("/", response_model=ViolationResponse)
async def create_violation(
    violation_data: ViolationCreate,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Create new violation record"""
    try:
        # Create violation
        violation_dict = violation_data.dict()
        response = db.table('violations').insert(violation_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create violation"
            )
        
        created_violation = response.data[0]
        return ViolationResponse(
            id=created_violation['id'],
            plate_number=created_violation['plate_number'],
            violation_type=created_violation['violation_type'],
            location=created_violation['location'],
            date_time=created_violation['date_time'],
            status=created_violation['status'],
            description=created_violation.get('description'),
            fine_amount=created_violation.get('fine_amount'),
            created_at=created_violation['created_at'],
            updated_at=created_violation['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create violation"
        )

@router.put("/{violation_id}", response_model=ViolationResponse)
async def update_violation(
    violation_id: str,
    violation_update: ViolationUpdate,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Update violation record"""
    try:
        # Check if violation exists
        response = db.table('violations').select("*").eq('id', violation_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in violation_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update violation
        response = db.table('violations').update(update_data).eq('id', violation_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update violation"
            )
        
        updated_violation = response.data[0]
        return ViolationResponse(
            id=updated_violation['id'],
            plate_number=updated_violation['plate_number'],
            violation_type=updated_violation['violation_type'],
            location=updated_violation['location'],
            date_time=updated_violation['date_time'],
            status=updated_violation['status'],
            description=updated_violation.get('description'),
            fine_amount=updated_violation.get('fine_amount'),
            created_at=updated_violation['created_at'],
            updated_at=updated_violation['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update violation"
        )

@router.post("/{violation_id}/resolve", response_model=ViolationResponse)
async def resolve_violation(
    violation_id: str,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Mark violation as resolved"""
    try:
        response = db.table('violations').update({
            'status': 'resolved'
        }).eq('id', violation_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        resolved_violation = response.data[0]
        return ViolationResponse(
            id=resolved_violation['id'],
            plate_number=resolved_violation['plate_number'],
            violation_type=resolved_violation['violation_type'],
            location=resolved_violation['location'],
            date_time=resolved_violation['date_time'],
            status=resolved_violation['status'],
            description=resolved_violation.get('description'),
            fine_amount=resolved_violation.get('fine_amount'),
            created_at=resolved_violation['created_at'],
            updated_at=resolved_violation['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve violation"
        )

@router.delete("/{violation_id}")
async def delete_violation(
    violation_id: str,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Delete violation record"""
    try:
        response = db.table('violations').delete().eq('id', violation_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        return {"message": "Violation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete violation"
        )