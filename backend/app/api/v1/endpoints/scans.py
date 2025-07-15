from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, date
from app.core.database import get_db
from app.models.scan import ScanResponse, ScanCreate, ScanUpdate
from app.api.deps import get_current_active_user, require_operator

router = APIRouter()

@router.get("/", response_model=List[ScanResponse])
async def get_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plate_number: Optional[str] = None,
    location: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    camera_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get all scans with filtering and pagination"""
    try:
        query = db.table('scans').select("*")
        
        # Apply filters
        if plate_number:
            query = query.ilike('plate_number', f'%{plate_number}%')
        if location:
            query = query.ilike('location', f'%{location}%')
        if camera_id:
            query = query.eq('camera_id', camera_id)
        if date_from:
            query = query.gte('scan_time', date_from.isoformat())
        if date_to:
            query = query.lte('scan_time', date_to.isoformat())
        if search:
            query = query.or_(f'plate_number.ilike.%{search}%,location.ilike.%{search}%,camera_id.ilike.%{search}%')
        
        # Apply pagination and ordering
        response = query.order('scan_time', desc=True).range(skip, skip + limit - 1).execute()
        
        scans = []
        for scan_data in response.data:
            scans.append(ScanResponse(
                id=scan_data['id'],
                plate_number=scan_data['plate_number'],
                location=scan_data['location'],
                scan_time=scan_data['scan_time'],
                confidence_score=scan_data.get('confidence_score'),
                image_url=scan_data.get('image_url'),
                camera_id=scan_data.get('camera_id'),
                created_at=scan_data['created_at']
            ))
        
        return scans
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scans"
        )

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get scan by ID"""
    try:
        response = db.table('scans').select("*").eq('id', scan_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        scan_data = response.data[0]
        return ScanResponse(
            id=scan_data['id'],
            plate_number=scan_data['plate_number'],
            location=scan_data['location'],
            scan_time=scan_data['scan_time'],
            confidence_score=scan_data.get('confidence_score'),
            image_url=scan_data.get('image_url'),
            camera_id=scan_data.get('camera_id'),
            created_at=scan_data['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scan"
        )

@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan_data: ScanCreate,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Create new scan record"""
    try:
        # Create scan
        scan_dict = scan_data.dict()
        response = db.table('scans').insert(scan_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create scan"
            )
        
        created_scan = response.data[0]
        return ScanResponse(
            id=created_scan['id'],
            plate_number=created_scan['plate_number'],
            location=created_scan['location'],
            scan_time=created_scan['scan_time'],
            confidence_score=created_scan.get('confidence_score'),
            image_url=created_scan.get('image_url'),
            camera_id=created_scan.get('camera_id'),
            created_at=created_scan['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan"
        )

@router.get("/stats/daily")
async def get_daily_scan_stats(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get daily scan statistics"""
    try:
        query = db.table('scans').select("scan_time", count="exact")
        
        if date_from:
            query = query.gte('scan_time', date_from.isoformat())
        if date_to:
            query = query.lte('scan_time', date_to.isoformat())
        
        response = query.execute()
        
        return {
            "total_scans": response.count,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scan statistics"
        )

@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: str,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Delete scan record"""
    try:
        response = db.table('scans').delete().eq('id', scan_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        return {"message": "Scan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scan"
        )