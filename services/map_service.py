import folium
from io import BytesIO
from sqlalchemy.orm import Session
from models.scan_model import ScanData
from typing import Optional
from datetime import datetime


def get_all_map_data_by_qrcode(
    db: Session,
    qr_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    query = db.query(ScanData).filter(ScanData.qr_id == qr_id)

    if start_time:
        query = query.filter(ScanData.timestamp >= start_time)
    if end_time:
        query = query.filter(ScanData.timestamp <= end_time)

    return query.all()


def generate_scan_map(location_data, qr_id: int):

    if not location_data:
        raise ValueError(f"No location data found for QR code ID {qr_id}")

    # Use the first location to center the map
    initial_location = [location_data[0].latitude, location_data[0].longitude]
    map_object = folium.Map(location=initial_location, zoom_start=5)

    # Add markers for each location in the location_data list
    for location in location_data:
        folium.Marker([location.latitude, location.longitude]).add_to(map_object)

    file_obj = BytesIO()
    map_object.save(file_obj, close_file=False)
    file_obj.seek(0)

    return file_obj
