import qrcode
import uuid
from io import BytesIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.qrcode import QRCode
from models.scan_data import ScanData
from schemas.qrcode import QRCodeCreate
from schemas.scan_data import ScanDataCreate


def create_qrcode(db: Session, qr_data: QRCodeCreate):
    qr_id = qr_data.qr_id if qr_data.qr_id else str(uuid.uuid4())

    qr = qrcode.QRCode(
        version=qr_data.version,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=qr_data.box_size,
        border=qr_data.border,
    )
    qr.add_data(qr_data.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_data.fill_color, back_color=qr_data.back_color)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    db_qrcode = QRCode(
        qr_id=qr_id,
        url=qr_data.url,
        img_bytes=img_bytes,
        version=qr_data.version,
        box_size=qr_data.box_size,
        border=qr_data.border,
        fill_color=qr_data.fill_color,
        back_color=qr_data.back_color,
    )
    db.add(db_qrcode)
    db.commit()
    db.refresh(db_qrcode)
    return db_qrcode


def get_qrcode_by_qr_id(db: Session, qr_id: str):
    return db.query(QRCode).filter(QRCode.qr_id == qr_id).first()


def save_scan_data(db: Session, scan_data: ScanDataCreate):
    db_qrcode = get_qrcode_by_qr_id(db, scan_data.qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    db_scan_data = ScanData(
        qr_code_id=db_qrcode.id,
        ip_address=scan_data.ip_address,
        user_agent=scan_data.user_agent,
    )
    db.add(db_scan_data)
    db.commit()
    db.refresh(db_scan_data)
    return db_scan_data


def get_all_qrcodes(db: Session):
    return db.query(QRCode).all()
