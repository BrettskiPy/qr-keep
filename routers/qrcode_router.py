from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
from starlette.responses import StreamingResponse

from database import get_db
from schemas.qrcode import QRCodeCreate, QRCodeResponse, QRCodeDataResponse
from schemas.scan_data import ScanDataCreate, ScanDataResponse
from services.qrcode_service import create_qrcode, get_qrcode_by_qr_id, save_scan_data
from schemas.qrcode import QRCodeBase
from services.qrcode_service import get_all_qrcodes


router = APIRouter()


@router.post("/generate_qrcode/", response_model=QRCodeResponse)
async def generate_qrcode(qr_data: QRCodeCreate, db: Session = Depends(get_db)):
    db_qrcode = create_qrcode(db, qr_data)
    return db_qrcode


@router.get("/qrcode_image/{qr_id}")
async def get_qrcode(qr_id: str, db: Session = Depends(get_db)):
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return Response(content=db_qrcode.img_bytes, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.get("/download_qrcode_image/{qr_id}")
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


@router.get("/qrcode_data/{qr_id}", response_model=QRCodeDataResponse)
async def get_qrcode_data(qr_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the original data used to generate the QR code.
    """
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return db_qrcode
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.post("/receive_scan_data/", response_model=ScanDataResponse)
async def receive_scan_data(metadata: ScanDataCreate, db: Session = Depends(get_db)):
    """
    Endpoint for external sites to send scan data associated with a QR code.
    """
    db_metadata = save_scan_data(db, metadata)

    # Ensure that the qr_code relationship is loaded
    db.refresh(db_metadata, attribute_names=["qr_code"])

    qr_id = db_metadata.qr_code.qr_id if db_metadata.qr_code else None
    response = ScanDataResponse(
        id=db_metadata.id,
        qr_id=qr_id,
        ip_address=db_metadata.ip_address,
        user_agent=db_metadata.user_agent,
    )
    return response


@router.get("/scan_data/{qr_id}", response_model=List[ScanDataResponse])
async def get_metadata(qr_id: str, db: Session = Depends(get_db)):
    """
    Retrieve scan data associated with a specific QR code.
    """
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    scan_data = [
        ScanDataResponse(
            id=scan.id,
            qr_id=qr_id,
            ip_address=scan.ip_address,
            user_agent=scan.user_agent,
        )
        for scan in db_qrcode.scan_data
    ]

    return scan_data


@router.get("/all_qrcodes_data/", response_model=List[QRCodeBase])
async def all_qrcodes_data(db: Session = Depends(get_db)):
    """
    Retrieve all QR codes with data.
    """
    db_qrcodes = get_all_qrcodes(db)
    return db_qrcodes
