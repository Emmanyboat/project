from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ViolationType(str, Enum):
    SPEEDING = "speeding"
    PARKING = "parking"
    RED_LIGHT = "red-light"
    STOP_SIGN = "stop-sign"
    NO_PARKING = "no-parking"

class ViolationStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"

class ViolationBase(BaseModel):
    plate_number: str
    violation_type: ViolationType
    location: str
    date_time: datetime
    status: ViolationStatus = ViolationStatus.OPEN
    description: Optional[str] = None
    fine_amount: Optional[float] = None

class ViolationCreate(ViolationBase):
    pass

class ViolationUpdate(BaseModel):
    plate_number: Optional[str] = None
    violation_type: Optional[ViolationType] = None
    location: Optional[str] = None
    date_time: Optional[datetime] = None
    status: Optional[ViolationStatus] = None
    description: Optional[str] = None
    fine_amount: Optional[float] = None

class ViolationInDB(ViolationBase):
    id: str
    created_at: datetime
    updated_at: datetime

class Violation(ViolationInDB):
    pass

class ViolationResponse(BaseModel):
    id: str
    plate_number: str
    violation_type: str
    location: str
    date_time: str
    status: str
    description: Optional[str] = None
    fine_amount: Optional[float] = None
    created_at: str
    updated_at: str