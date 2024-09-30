import qrcode
from io import BytesIO
from sqlalchemy.orm import Session

from models.qrcode_model import QRCode
from schemas.qrcode import QRCodeCreate, Location, QRCodeResponse


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
        name=qr_data.name,
        img_bytes=img_bytes,
        version=qr_data.version,
        box_size=qr_data.box_size,
        border=qr_data.border,
        fill_color=qr_data.fill_color,
        back_color=qr_data.back_color,
        latitude=qr_data.location.latitude,
        longitude=qr_data.location.longitude,
    )
    db.add(db_qrcode)
    db.commit()
    db.refresh(db_qrcode)
    
    return QRCodeResponse(
        id=db_qrcode.id,
        name=db_qrcode.name,
        url=db_qrcode.url,
        version=db_qrcode.version,
        box_size=db_qrcode.box_size,
        border=db_qrcode.border,
        fill_color=db_qrcode.fill_color,
        back_color=db_qrcode.back_color,
        location=Location(
            latitude=db_qrcode.latitude, longitude=db_qrcode.longitude
        )
    )


def get_qrcode_by_qr_id(db: Session, qr_id: str):
    return db.query(QRCode).filter(QRCode.id == qr_id).first()


def get_all_qrcodes(db: Session):
    return db.query(QRCode).all()
