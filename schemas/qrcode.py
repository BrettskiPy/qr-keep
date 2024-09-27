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


class QRCodeBase(BaseModel):
    id: int
    url: str
    version: int
    box_size: int
    border: int
    fill_color: str
    back_color: str

    class Config:
        from_attributes = True


class QRCodeResponse(QRCodeBase):
    pass


class QRCodeListResponse(BaseModel):
    qrcodes: List[QRCodeBase]


class QRCodeDataResponse(QRCodeBase):
    pass
