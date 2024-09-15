from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship
from database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    qr_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    img_bytes = Column(LargeBinary, nullable=False)
    version: int = Column(Integer, nullable=False)
    box_size: int = Column(Integer, nullable=False)
    border: int = Column(Integer, nullable=False)
    fill_color: str = Column(String, nullable=False)
    back_color: str = Column(String, nullable=False)

    scan_data = relationship(
        "ScanData", back_populates="qr_code", cascade="all, delete-orphan"
    )
