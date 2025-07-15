from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from enum import Enum

class VehicleStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

class VehicleType(str, Enum):
    SEDAN = "Sedan"
    SUV = "SUV"
    TRUCK = "Truck"
    HATCHBACK = "Hatchback"
    COUPE = "Coupe"
    CONVERTIBLE = "Convertible"
    MOTORCYCLE = "Motorcycle"

class VehicleBase(BaseModel):
    plate_number: str
    make: str
    model: str
    year: int
    color: str
    vehicle_type: VehicleType
    engine_number: str
    chassis_number: str
    owner_name: str
    owner_phone: str
    owner_email: EmailStr
    owner_address: str
    registration_date: date
    expiry_date: date
    status: VehicleStatus = VehicleStatus.ACTIVE

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    plate_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    owner_address: Optional[str] = None
    registration_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[VehicleStatus] = None

class VehicleInDB(VehicleBase):
    id: str
    created_at: datetime
    updated_at: datetime

class Vehicle(VehicleInDB):
    pass

class VehicleResponse(BaseModel):
    id: str
    plate_number: str
    make: str
    model: str
    year: int
    color: str
    vehicle_type: str
    engine_number: str
    chassis_number: str
    owner_name: str
    owner_phone: str
    owner_email: str
    owner_address: str
    registration_date: str
    expiry_date: str
    status: str
    created_at: str
    updated_at: str