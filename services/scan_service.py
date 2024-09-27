from sqlalchemy.orm import Session
from fastapi import HTTPException

from .qrcode_service import get_qrcode_by_qr_id
from models.scan_model import ScanData
from schemas.scan_data import ScanDataCreate


def save_scan_data(db: Session, scan_data: ScanDataCreate, qr_id):
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    db_scan_data = ScanData(
        qr_id=db_qrcode.id,
        ip_address=scan_data.ip_address,
        user_agent=scan_data.user_agent,
        latitude=scan_data.location.latitude,
        longitude=scan_data.location.longitude,
    )
    db.add(db_scan_data)
    db.commit()
    db.refresh(db_scan_data)
    return db_scan_data
