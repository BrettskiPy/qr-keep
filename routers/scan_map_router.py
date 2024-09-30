from fastapi import APIRouter, Depends
from database import get_db
from services.map_service import (
    create_pin_map,
    fetch_scan_location_data,
    fetch_qrcode_location_data,
    generate_map_response,
)

from sqlalchemy.orm import Session
from models.map_model import TimeBoundParams
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/map")


@router.get("/pin/{qr_id}")
async def generate_pin_map(
    qr_id: int, time_params: TimeBoundParams = Depends(), db: Session = Depends(get_db)
):
    """
    Creates a pin map of scanned QR codes.
    """
    qrcode_locations = fetch_qrcode_location_data(
        db=db, qr_id=qr_id, time_params=time_params
    )
    scan_locations = fetch_scan_location_data(
        db=db, qr_id=qr_id, time_params=time_params
    )
    map_file = create_pin_map(qrcodes=qrcode_locations, scans=scan_locations)
    return generate_map_response(map_file, qr_id)
