from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from schemas.common import Location, TimeBoundParams


class QRCodeCreate(BaseModel):
    name: str
    url: str
    version: int = Field(default=1, ge=1, le=40)
    box_size: int = Field(default=10, ge=1)
    border: int = Field(default=4, ge=0)
    fill_color: str = Field(default="black")
    back_color: str = Field(default="white")
    location: Location = Field(
        ..., description="Location data with latitude and longitude"
    )


class QRCodeBase(BaseModel):
    id: int
    name: str
    url: str
    version: int
    box_size: int
    border: int
    fill_color: str
    back_color: str
    location: Location = Field(
        ..., description="Location data with latitude and longitude"
    )

    class Config:
        from_attributes = True


class QRCodeResponse(QRCodeBase):
    pass


class QRCodeListResponse(BaseModel):
    qrcodes: List[QRCodeBase]


class QRCodeDataResponse(QRCodeBase):
    pass
