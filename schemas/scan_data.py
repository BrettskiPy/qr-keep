from pydantic import BaseModel


class ScanDataCreate(BaseModel):
    qr_id: str
    ip_address: str
    user_agent: str


class ScanDataResponse(ScanDataCreate):
    id: int

    class Config:
        from_attributes = True
