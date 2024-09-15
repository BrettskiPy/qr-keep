from pydantic import BaseModel, Field
from typing import Optional
from typing import List


class QRCodeCreate(BaseModel):
    url: str
    version: int = Field(default=1, ge=1, le=40)
    box_size: int = Field(default=10, ge=1)
    border: int = Field(default=4, ge=0)
    fill_color: str = Field(default="black")
    back_color: str = Field(default="white")
    qr_id: Optional[str] = Field(default=None)


class QRCodeBase(BaseModel):
    id: int
    qr_id: str
    url: str

    class Config:
        from_attributes = True  # For Pydantic v2


class QRCodeResponse(QRCodeBase):
    pass


class QRCodeListResponse(BaseModel):
    qrcodes: List[QRCodeBase]


class QRCodeURLResponse(QRCodeBase):
    url: str
