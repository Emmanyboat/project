from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.core.database import get_db
from app.models.vehicle import VehicleResponse, VehicleCreate, VehicleUpdate, VehicleStatus, VehicleType
from app.api.deps import get_current_active_user, require_operator

router = APIRouter()

@router.get("/", response_model=List[VehicleResponse])
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plate_number: Optional[str] = None,
    make: Optional[str] = None,
    vehicle_type: Optional[VehicleType] = None,
    status: Optional[VehicleStatus] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get all vehicles with filtering and pagination"""
    try:
        query = db.table('vehicles').select("*")
        
        # Apply filters
        if plate_number:
            query = query.ilike('plate_number', f'%{plate_number}%')
        if make:
            query = query.eq('make', make)
        if vehicle_type:
            query = query.eq('vehicle_type', vehicle_type)
        if status:
            query = query.eq('status', status)
        if search:
            query = query.or_(f'plate_number.ilike.%{search}%,make.ilike.%{search}%,model.ilike.%{search}%,owner_name.ilike.%{search}%')
        
        # Apply pagination
        response = query.range(skip, skip + limit - 1).execute()
        
        vehicles = []
        for vehicle_data in response.data:
            vehicles.append(VehicleResponse(
                id=vehicle_data['id'],
                plate_number=vehicle_data['plate_number'],
                make=vehicle_data['make'],
                model=vehicle_data['model'],
                year=vehicle_data['year'],
                color=vehicle_data['color'],
                vehicle_type=vehicle_data['vehicle_type'],
                engine_number=vehicle_data['engine_number'],
                chassis_number=vehicle_data['chassis_number'],
                owner_name=vehicle_data['owner_name'],
                owner_phone=vehicle_data['owner_phone'],
                owner_email=vehicle_data['owner_email'],
                owner_address=vehicle_data['owner_address'],
                registration_date=vehicle_data['registration_date'],
                expiry_date=vehicle_data['expiry_date'],
                status=vehicle_data['status'],
                created_at=vehicle_data['created_at'],
                updated_at=vehicle_data['updated_at']
            ))
        
        return vehicles
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vehicles"
        )

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get vehicle by ID"""
    try:
        response = db.table('vehicles').select("*").eq('id', vehicle_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        vehicle_data = response.data[0]
        return VehicleResponse(
            id=vehicle_data['id'],
            plate_number=vehicle_data['plate_number'],
            make=vehicle_data['make'],
            model=vehicle_data['model'],
            year=vehicle_data['year'],
            color=vehicle_data['color'],
            vehicle_type=vehicle_data['vehicle_type'],
            engine_number=vehicle_data['engine_number'],
            chassis_number=vehicle_data['chassis_number'],
            owner_name=vehicle_data['owner_name'],
            owner_phone=vehicle_data['owner_phone'],
            owner_email=vehicle_data['owner_email'],
            owner_address=vehicle_data['owner_address'],
            registration_date=vehicle_data['registration_date'],
            expiry_date=vehicle_data['expiry_date'],
            status=vehicle_data['status'],
            created_at=vehicle_data['created_at'],
            updated_at=vehicle_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vehicle"
        )

@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Create new vehicle registration"""
    try:
        # Check if plate number already exists
        response = db.table('vehicles').select("plate_number").eq('plate_number', vehicle_data.plate_number).execute()
        
        if response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this plate number already exists"
            )
        
        # Create vehicle
        vehicle_dict = vehicle_data.dict()
        response = db.table('vehicles').insert(vehicle_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create vehicle"
            )
        
        created_vehicle = response.data[0]
        return VehicleResponse(
            id=created_vehicle['id'],
            plate_number=created_vehicle['plate_number'],
            make=created_vehicle['make'],
            model=created_vehicle['model'],
            year=created_vehicle['year'],
            color=created_vehicle['color'],
            vehicle_type=created_vehicle['vehicle_type'],
            engine_number=created_vehicle['engine_number'],
            chassis_number=created_vehicle['chassis_number'],
            owner_name=created_vehicle['owner_name'],
            owner_phone=created_vehicle['owner_phone'],
            owner_email=created_vehicle['owner_email'],
            owner_address=created_vehicle['owner_address'],
            registration_date=created_vehicle['registration_date'],
            expiry_date=created_vehicle['expiry_date'],
            status=created_vehicle['status'],
            created_at=created_vehicle['created_at'],
            updated_at=created_vehicle['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vehicle"
        )

@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Update vehicle registration"""
    try:
        # Check if vehicle exists
        response = db.table('vehicles').select("*").eq('id', vehicle_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in vehicle_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update vehicle
        response = db.table('vehicles').update(update_data).eq('id', vehicle_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update vehicle"
            )
        
        updated_vehicle = response.data[0]
        return VehicleResponse(
            id=updated_vehicle['id'],
            plate_number=updated_vehicle['plate_number'],
            make=updated_vehicle['make'],
            model=updated_vehicle['model'],
            year=updated_vehicle['year'],
            color=updated_vehicle['color'],
            vehicle_type=updated_vehicle['vehicle_type'],
            engine_number=updated_vehicle['engine_number'],
            chassis_number=updated_vehicle['chassis_number'],
            owner_name=updated_vehicle['owner_name'],
            owner_phone=updated_vehicle['owner_phone'],
            owner_email=updated_vehicle['owner_email'],
            owner_address=updated_vehicle['owner_address'],
            registration_date=updated_vehicle['registration_date'],
            expiry_date=updated_vehicle['expiry_date'],
            status=updated_vehicle['status'],
            created_at=updated_vehicle['created_at'],
            updated_at=updated_vehicle['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update vehicle"
        )

@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: str,
    current_user = Depends(require_operator),
    db = Depends(get_db)
):
    """Delete vehicle registration"""
    try:
        response = db.table('vehicles').delete().eq('id', vehicle_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        return {"message": "Vehicle deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete vehicle"
        )