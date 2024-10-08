from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
from starlette.responses import StreamingResponse

from database import get_db
from schemas.qrcode import QRCodeCreate, QRCodeResponse, QRCodeDataResponse
from services.qrcode_service import create_qrcode, get_qrcode_by_qr_id
from schemas.qrcode import QRCodeBase, Location
from services.qrcode_service import get_all_qrcodes


router = APIRouter(prefix="/qrcode")


@router.post("/generate", response_model=QRCodeResponse)
async def generate_qrcode(qr_data: QRCodeCreate, db: Session = Depends(get_db)):
    db_qrcode = create_qrcode(db, qr_data)
    return db_qrcode


@router.get("/fetch_image/{qr_id}")
async def get_qrcode_image(qr_id: str, db: Session = Depends(get_db)):
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return Response(content=db_qrcode.img_bytes, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.get("/download/{qr_id}")
async def download_qrcode(qr_id: str, db: Session = Depends(get_db)):
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return StreamingResponse(
            BytesIO(db_qrcode.img_bytes),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={qr_id}.png"},
        )
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.get("/data/{qr_id}", response_model=QRCodeDataResponse)
async def get_qrcode_data(qr_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the original data used to generate the QR code.
    """
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return QRCodeDataResponse(
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
            ),
        )
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.get("/all_data/", response_model=List[QRCodeBase])
async def all_qrcodes_data(db: Session = Depends(get_db)):
    """
    Retrieve all QR codes with data.
    """
    db_qrcodes = get_all_qrcodes(db)
    # Convert the SQLAlchemy QRCode objects to the Pydantic QRCodeBase model
    return [
        QRCodeBase(
            id=qr.id,
            name=qr.name,
            url=qr.url,
            version=qr.version,
            box_size=qr.box_size,
            border=qr.border,
            fill_color=qr.fill_color,
            back_color=qr.back_color,
            location=Location(latitude=qr.latitude, longitude=qr.longitude),
        )
        for qr in db_qrcodes
    ]
