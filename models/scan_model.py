from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class ScanData(Base):
    __tablename__ = "scan_data"

    id = Column(Integer, primary_key=True, index=True)
    qr_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Add a timestamp column

    qr_code = relationship("QRCode", back_populates="scan_data", lazy="joined")
