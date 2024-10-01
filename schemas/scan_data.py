from pydantic import BaseModel, Field
from datetime import datetime
from schemas.common import Location


class ScanDataCreate(BaseModel):
    ip_address: str
    user_agent: str
    location: Location = Field(
        ..., description="Location data with latitude and longitude"
    )


class ScanDataResponse(BaseModel):
    id: int
    ip_address: str
    user_agent: str
    location: Location = Field(
        ..., description="Location data with latitude and longitude"
    )
    created: datetime

    class Config:
        from_attributes = True
