from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TimeBoundParams(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class Location(BaseModel):
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
