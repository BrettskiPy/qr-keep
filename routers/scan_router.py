from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.scan_data import ScanDataCreate, ScanDataResponse, Location
from schemas.qrcode import TimeBoundParams
from services.qrcode_service import get_qrcode_by_qr_id
from services.scan_service import save_scan_data
from models import ScanData


router = APIRouter(prefix="/scan")


@router.post("/{qr_id}", response_model=ScanDataResponse)
async def create_scan_data(
    qr_id: str, scan_data: ScanDataCreate, db: Session = Depends(get_db)
):
    """
    Create scan data for a QR code.
    """
    db_scan_data = save_scan_data(db, scan_data, qr_id)

    # Ensure that the qr_code relationship is loaded
    db.refresh(db_scan_data, attribute_names=["qr_code"])

    response = ScanDataResponse(
        id=db_scan_data.id,
        ip_address=db_scan_data.ip_address,
        user_agent=db_scan_data.user_agent,
        location=Location(
            latitude=db_scan_data.latitude, longitude=db_scan_data.longitude
        ),
        created=db_scan_data.created,
    )
    return response


@router.get("/{qr_id}", response_model=List[ScanDataResponse])
async def get_scan_data_from_qrcode(qr_id: str, db: Session = Depends(get_db)):
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
            location=Location(latitude=scan.latitude, longitude=scan.longitude),
            created=scan.created,
        )
        for scan in db_qrcode.scan_data
    ]

    return scan_data


@router.get("/count/{qr_id}")
async def scan_count_in_timeframe(
    qr_id: str, db: Session = Depends(get_db), time_params: TimeBoundParams = Depends()
):
    """
    Checks QR Code scan count within an optional timeframe.
    """
    # Fetch the QR code by ID
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    # Get scan data and filter by optional timeframe
    scan_data_query = db.query(ScanData).filter(ScanData.qr_id == db_qrcode.id)

    if time_params.start_time:
        scan_data_query = scan_data_query.filter(
            ScanData.created >= time_params.start_time
        )
    if time_params.end_time:
        scan_data_query = scan_data_query.filter(
            ScanData.created <= time_params.end_time
        )

    # Get the count of scans directly
    scan_count = scan_data_query.count()

    # Return the count and whether any scans were found (boolean)
    return {
        "scan_count": scan_count,
    }


@router.delete("/{qr_id}")
async def delete_all_scanned_data_from_qrcode(
    qr_id: str, db: Session = Depends(get_db)
):
    """
    Delete all scanned data from a QR code.
    """
    db_qrcode = get_qrcode_by_qr_id(db, qr_id)
    if not db_qrcode:
        raise HTTPException(status_code=404, detail="QR code not found")

    deleted_rows = (
        db.query(ScanData)
        .filter(ScanData.qr_id == qr_id)
        .delete(synchronize_session=False)
    )
    db.commit()

    if deleted_rows == 0:
        raise HTTPException(
            status_code=404, detail=f"No scan data found for the QR code id: {qr_id}"
        )

    return {
        "message": f"Successfully deleted {deleted_rows} scan data entries for the QR code id: {qr_id}"
    }
