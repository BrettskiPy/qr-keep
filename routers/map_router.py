from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from services.map_service import generate_scan_map, get_all_map_data_by_qrcode
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models.map_model import TimeBoundParams


router = APIRouter(prefix="/map")


@router.post("/generate_html/{qr_id}")
async def generate_qrcode_scan_map(
    qr_id: int, time_params: TimeBoundParams = Depends(), db: Session = Depends(get_db)
):
    location_data = get_all_map_data_by_qrcode(
        db=db,
        qr_id=qr_id,
        start_time=time_params.start_time,
        end_time=time_params.end_time,
    )

    if not location_data:
        raise HTTPException(
            status_code=404,
            detail=f"No location data found for QR code ID: {qr_id} within the specified time range.",
        )

    map_file = generate_scan_map(location_data=location_data, qr_id=qr_id)

    # Return the in-memory HTML file as a downloadable response
    return StreamingResponse(
        map_file,
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename=map_qrcode_{qr_id}_scans.html"
        },
    )
