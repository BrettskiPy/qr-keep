from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship
from database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    qr_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    img_bytes = Column(LargeBinary, nullable=False)

    scan_data = relationship(
        "ScanData", back_populates="qr_code", cascade="all, delete-orphan"
    )
