from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
from starlette.responses import StreamingResponse

from database import get_db
from schemas.qrcode import QRCodeCreate, QRCodeResponse, QRCodeURLResponse
from schemas.scan_data import ScanDataCreate, ScanDataResponse
from services.qrcode_service import create_qrcode, get_qrcode_by_qr_id, save_scan_data
from schemas.qrcode import QRCodeBase
from services.qrcode_service import get_all_qrcodes


router = APIRouter()


@router.post("/generate_qrcode/", response_model=QRCodeResponse)
async def generate_qrcode_endpoint(
    qr_data: QRCodeCreate, db: Session = Depends(get_db)
):
    db_qrcode = create_qrcode(db, qr_data)
    return db_qrcode


@router.get("/get_qrcode_image/{qr_id}")
async def get_qrcode(qr_id: str, db: Session = Depends(get_db)):
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return Response(content=db_qrcode.img_bytes, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.get("/download_qrcode_image/{qr_id}")
async def download_qrcode_endpoint(qr_id: str, db: Session = Depends(get_db)):
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return StreamingResponse(
            BytesIO(db_qrcode.img_bytes),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={qr_id}.png"},
        )
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.get("/get_qrcode_data/{qr_id}", response_model=QRCodeURLResponse)
async def get_qrcode_data(qr_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the original data used to generate the QR code.
    """
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if db_qrcode:
        return db_qrcode
    else:
        raise HTTPException(status_code=404, detail="QR code not found")


@router.post("/receive_metadata/", response_model=ScanDataResponse)
async def receive_metadata(metadata: ScanDataCreate, db: Session = Depends(get_db)):
    """
    Endpoint for external sites to send metadata associated with a QR code scan.
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


@router.get("/all_scan_data/{qr_id}", response_model=List[ScanDataResponse])
async def get_metadata(qr_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all metadata associated with a specific QR code.
    """
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    all_scan_data = [
        ScanDataResponse(
            id=scan.id,
            qr_id=qr_id,
            ip_address=scan.ip_address,
            user_agent=scan.user_agent,
        )
        for scan in db_qrcode.scan_data
    ]

    return all_scan_data


@router.get("/qrcodes/", response_model=List[QRCodeBase])
async def get_all_qrcodes_endpoint(db: Session = Depends(get_db)):
    """
    Retrieve all QR codes along with their data.
    """
    db_qrcodes = get_all_qrcodes(db)
    return db_qrcodes
