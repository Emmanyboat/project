from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScanBase(BaseModel):
    plate_number: str
    location: str
    scan_time: datetime
    confidence_score: Optional[float] = None
    image_url: Optional[str] = None
    camera_id: Optional[str] = None

class ScanCreate(ScanBase):
    pass

class ScanUpdate(BaseModel):
    plate_number: Optional[str] = None
    location: Optional[str] = None
    scan_time: Optional[datetime] = None
    confidence_score: Optional[float] = None
    image_url: Optional[str] = None
    camera_id: Optional[str] = None

class ScanInDB(ScanBase):
    id: str
    created_at: datetime

class Scan(ScanInDB):
    pass

class ScanResponse(BaseModel):
    id: str
    plate_number: str
    location: str
    scan_time: str
    confidence_score: Optional[float] = None
    image_url: Optional[str] = None
    camera_id: Optional[str] = None
    created_at: str