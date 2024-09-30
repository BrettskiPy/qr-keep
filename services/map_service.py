import folium
from io import BytesIO
from sqlalchemy.orm import Session
from models.scan_model import ScanData
from typing import Optional
from datetime import datetime
from folium.plugins import HeatMap, MarkerCluster
from models.map_model import TimeBoundParams
from fastapi.responses import StreamingResponse


def fetch_location_data(db: Session, qr_id: int, time_params: TimeBoundParams):
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


def create_map(scans: list[ScanData], zoom_start: int = 5):
    if not scans:
        raise ValueError("No scan location data found.")

    initial_location = [scans[0].latitude, scans[0].longitude]
    return folium.Map(location=initial_location, zoom_start=zoom_start)


def save_map_to_file(map_object: folium.Map) -> BytesIO:
    file_obj = BytesIO()
    map_object.save(file_obj, close_file=False)
    file_obj.seek(0)
    return file_obj


def generate_pin_map(scans: list[ScanData]) -> BytesIO:
    map_object = create_map(scans)

    for scan in scans:
        popup_html = f"""
        <b>IP Address:</b> {scan.ip_address}<br>
        <b>User Agent:</b> {scan.user_agent}<br>
        <b>Timestamp:</b> {scan.created}<br>
        <b>Latitude:</b> {scan.latitude}<br>
        <b>Longitude:</b> {scan.longitude}
        """
        popup = folium.Popup(popup_html, max_width=250)
        folium.Marker([scan.latitude, scan.longitude], popup=popup).add_to(map_object)

    return save_map_to_file(map_object)


def generate_heat_map(scans: list[ScanData]) -> BytesIO:
    map_object = create_map(scans)

    heatmap_data = [[scan.latitude, scan.longitude] for scan in scans]
    HeatMap(heatmap_data).add_to(map_object)

    return save_map_to_file(map_object)


def generate_cluster_map(scans: list[ScanData]) -> BytesIO:
    map_object = create_map(scans)

    marker_cluster = MarkerCluster().add_to(map_object)
    for scan in scans:
        folium.Marker(
            [scan.latitude, scan.longitude],
            popup=f"IP: {scan.ip_address}, Timestamp: {scan.created}",
        ).add_to(marker_cluster)

    return save_map_to_file(map_object)
