import qrcode
import uuid
from io import BytesIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.qrcode import QRCode
from models.metadata import Metadata
from schemas.qrcode import QRCodeCreate
from schemas.metadata import MetadataCreate


def create_qrcode(db: Session, qr_data: QRCodeCreate):
    qr_id = str(uuid.uuid4())
    # Append qr_id as a query parameter to the original data (URL)
    if "?" in qr_data.data:
        url_with_id = f"{qr_data.data}&qr_id={qr_id}"
    else:
        url_with_id = f"{qr_data.data}?qr_id={qr_id}"
    # Generate QR code with the modified URL
    qr = qrcode.QRCode(
        version=qr_data.version,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=qr_data.box_size,
        border=qr_data.border,
    )
    qr.add_data(url_with_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_data.fill_color, back_color=qr_data.back_color)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    db_qrcode = QRCode(qr_id=qr_id, data=qr_data.data, img_bytes=img_bytes)
    db.add(db_qrcode)
    db.commit()
    db.refresh(db_qrcode)
    return db_qrcode


def get_qrcode_by_qr_id(db: Session, qr_id: str):
    return db.query(QRCode).filter(QRCode.qr_id == qr_id).first()


def save_metadata(db: Session, metadata: MetadataCreate):
    db_qrcode = get_qrcode_by_qr_id(db, metadata.qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    db_metadata = Metadata(
        qr_code_id=db_qrcode.id,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata
