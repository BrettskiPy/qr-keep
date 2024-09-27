from pydantic import BaseModel


class ScanDataCreate(BaseModel):
    ip_address: str
    user_agent: str


class ScanDataResponse(ScanDataCreate):
    id: int

    class Config:
        from_attributes = True
