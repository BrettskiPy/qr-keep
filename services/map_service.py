import folium
from io import BytesIO
from sqlalchemy.orm import Session
from models.scan_model import ScanData
from models.qrcode_model import QRCode
from folium.plugins import MarkerCluster
from typing import Optional
from datetime import datetime
from models.map_model import TimeBoundParams
from fastapi.responses import StreamingResponse


def fetch_qrcode_location_data(db: Session, qr_id: int, time_params: TimeBoundParams):
    qrcode_location_data = get_qrcode_map_data_by_qrcode(
        db=db,
        qr_id=qr_id,
        start_time=time_params.start_time,
        end_time=time_params.end_time,
    )

    return qrcode_location_data


def fetch_scan_location_data(db: Session, qr_id: int, time_params: TimeBoundParams):
    scan_location_data = get_scan_map_data_by_qrcode(
        db=db,
        qr_id=qr_id,
        start_time=time_params.start_time,
        end_time=time_params.end_time,
    )

    return scan_location_data


def generate_map_response(map_file, qr_id: int):
    return StreamingResponse(
        map_file,
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename=map_qrcode_{qr_id}_scans.html"
        },
    )


def get_scan_map_data_by_qrcode(
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


def get_qrcode_map_data_by_qrcode(
    db: Session,
    qr_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    query = db.query(QRCode).filter(QRCode.id == qr_id)

    if start_time:
        query = query.filter(ScanData.timestamp >= start_time)
    if end_time:
        query = query.filter(ScanData.timestamp <= end_time)

    return query.all()


def initialize_location(qrcodes: list[QRCode], scans: list[ScanData]):
    # Prioritize initial location based on qrcodes, then scans, then default to [0, 0]
    if qrcodes:
        initial_location = [qrcodes[0].latitude, qrcodes[0].longitude]
    elif scans:
        initial_location = [scans[0].latitude, scans[0].longitude]
    else:
        initial_location = [0, 0]

    return initial_location


def save_map_to_file(map_object: folium.Map) -> BytesIO:
    file_obj = BytesIO()
    map_object.save(file_obj, close_file=False)
    file_obj.seek(0)
    return file_obj


def add_marker_with_popup(map_object, latitude, longitude, popup_content):
    popup = folium.Popup(popup_content, max_width=250)
    folium.Marker([latitude, longitude], popup=popup).add_to(map_object)


def generate_popup_content(data):
    """
    Generates popup content for either a QRCode or ScanData object
    """
    if isinstance(data, QRCode):
        return f"""
        <b>Name:</b> {data.name}<br>
        <b>URL:</b> {data.url}<br>
        <b>Version:</b> {data.version}<br>
        <b>Location:</b> {data.latitude}, {data.longitude}<br>
        """
    elif isinstance(data, ScanData):
        return f"""
        <b>IP Address:</b> {data.ip_address}<br>
        <b>User Agent:</b> {data.user_agent}<br>
        <b>Location:</b> {data.latitude}, {data.longitude}<br>
        <b>Scan Time:</b> {data.created}<br>
        """
    return ""


def create_pin_map(qrcodes: list[QRCode], scans: list[ScanData]) -> BytesIO:
    initial_location = initialize_location(qrcodes=qrcodes, scans=scans)
    map_object = folium.Map(location=initial_location, zoom_start=3)

    for qrcode in qrcodes:
        popup_html = generate_popup_content(qrcode)
        popup = folium.Popup(popup_html, max_width=250)
        folium.Marker([qrcode.latitude, qrcode.longitude], popup=popup).add_to(
            map_object
        )

    for scan in scans:
        popup_html = generate_popup_content(scan)
        popup = folium.Popup(popup_html, max_width=250)
        folium.Marker([scan.latitude, scan.longitude], popup=popup).add_to(map_object)

    return save_map_to_file(map_object)
