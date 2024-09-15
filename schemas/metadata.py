from pydantic import BaseModel


class MetadataCreate(BaseModel):
    qr_id: str
    ip_address: str
    user_agent: str


class MetadataResponse(MetadataCreate):
    id: int

    class Config:
        from_attributes = True
