from sqlalchemy import Column, Integer, String, LargeBinary, Float
from sqlalchemy.orm import relationship
from database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    img_bytes = Column(LargeBinary, nullable=False)
    version = Column(Integer, nullable=False)
    box_size = Column(Integer, nullable=False)
    border = Column(Integer, nullable=False)
    fill_color = Column(String, nullable=False)
    back_color = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    scan_data = relationship(
        "ScanData", back_populates="qr_code", cascade="all, delete-orphan"
    )
