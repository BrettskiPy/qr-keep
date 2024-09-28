from fastapi import APIRouter, Depends
from database import get_db
from services.map_service import (
    generate_pin_map,
    generate_heat_map,
    generate_cluster_map,
    fetch_location_data,
    generate_map_response,
)

from sqlalchemy.orm import Session
from models.map_model import TimeBoundParams
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/scan_map")


@router.get("/pin/{qr_id}")
async def generate_scan_pin_map(
    qr_id: int, time_params: TimeBoundParams = Depends(), db: Session = Depends(get_db)
):
    """
    Creates a pin map of scanned QR codes.
    """
    location_data = fetch_location_data(db=db, qr_id=qr_id, time_params=time_params)
    map_file = generate_pin_map(location_data=location_data, qr_id=qr_id)
    return generate_map_response(map_file, qr_id)


@router.get("/heat/{qr_id}")
async def generate_scan_heat_map(
    qr_id: int, time_params: TimeBoundParams = Depends(), db: Session = Depends(get_db)
):
    """
    Creates a heat map of scanned QR codes.
    """
    location_data = fetch_location_data(db=db, qr_id=qr_id, time_params=time_params)
    map_file = generate_heat_map(location_data=location_data, qr_id=qr_id)
    return generate_map_response(map_file, qr_id)


@router.get("/cluster/{qr_id}")
async def generate_scan_cluster_map(
    qr_id: int, time_params: TimeBoundParams = Depends(), db: Session = Depends(get_db)
):
    """
    Creates a cluster map of scanned QR codes.
    """
    location_data = fetch_location_data(db=db, qr_id=qr_id, time_params=time_params)
    map_file = generate_cluster_map(location_data=location_data, qr_id=qr_id)
    return generate_map_response(map_file, qr_id)
