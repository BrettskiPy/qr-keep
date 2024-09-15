from pydantic import BaseModel, Field


class QRCodeCreate(BaseModel):
    data: str
    version: int = Field(default=1, ge=1, le=40)
    box_size: int = Field(default=10, ge=1)
    border: int = Field(default=4, ge=0)
    fill_color: str = Field(default="black")
    back_color: str = Field(default="white")


class QRCodeBase(BaseModel):
    qr_id: str

    class Config:
        from_attributes = True  # For Pydantic v2


class QRCodeResponse(QRCodeBase):
    pass  # No additional fields needed


class QRCodeDataResponse(QRCodeBase):
    data: str
