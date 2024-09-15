from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ScanData(Base):
    __tablename__ = "scan_data"

    id = Column(Integer, primary_key=True, index=True)
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)

    qr_code = relationship("QRCode", back_populates="scan_data", lazy="joined")
