import qrcode
from io import BytesIO
from sqlalchemy.orm import Session

from models.qrcode import QRCode
from schemas.qrcode import QRCodeCreate


def create_qrcode(db: Session, qr_data: QRCodeCreate):
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
    return db.query(QRCode).filter(QRCode.id == qr_id).first()


def get_all_qrcodes(db: Session):
    return db.query(QRCode).all()
