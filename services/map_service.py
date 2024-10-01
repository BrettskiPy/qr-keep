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
import base64
from io import BytesIO


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
    popup = folium.Popup(popup_content, max_width=300)
    folium.Marker([latitude, longitude], popup=popup).add_to(map_object)


def generate_popup_content(data):
    """
    Generates popup content for either a QRCode or ScanData object,
    with a consistent minimum width for both.
    """
    style = "min-width: 150px; max-width: 400px;"

    if isinstance(data, QRCode):
        # Convert the QR code image bytes to a base64 image string
        base64_image = qr_code_image_to_base64(data.img_bytes)

        return f"""
        <div style="{style}">
            <b>Name:</b> {data.name}<br>
            <b>URL:</b> {data.url}<br>
            <b>Version:</b> {data.version}<br>
            <b>Location:</b> {data.latitude}, {data.longitude}<br>
            <br>
            <div style="text-align: center;">
                <img src="{base64_image}" alt="QR Code" style="width:100px;" 
                onclick="this.style.width='300px'; this.style.height='300px';" />
            </div>
        </div>
        """
    elif isinstance(data, ScanData):
        return f"""
        <div style="{style}">
            <b>IP Address:</b> {data.ip_address}<br>
            <b>User Agent:</b> {data.user_agent}<br>
            <b>Location:</b> {data.latitude}, {data.longitude}<br>
            <b>Scan Time:</b> {data.created}<br>
        </div>
        """
    return ""


def qr_code_image_to_base64(img_bytes):
    """
    Converts QR code image bytes to a base64-encoded string that can be used in an HTML img tag.
    """
    encoded = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def add_marker_with_qr_icon(map_object, latitude, longitude, popup_content, img_bytes):
    # Convert the QR code image bytes to a base64 image string
    base64_image = qr_code_image_to_base64(img_bytes)

    # Create a custom icon with the base64 image
    icon = folium.CustomIcon(
        icon_image=base64_image,
        icon_size=(24, 24),  # Adjust the size of the icon as needed
    )

    # Add the marker to the map with the custom icon and popup content
    popup = folium.Popup(popup_content, max_width=300)
    folium.Marker([latitude, longitude], icon=icon, popup=popup).add_to(map_object)


def standard_map(qrcodes: list[QRCode], scans: list[ScanData]) -> BytesIO:
    initial_location = initialize_location(qrcodes=qrcodes, scans=scans)
    map_object = folium.Map(location=initial_location, zoom_start=3)

    for qrcode in qrcodes:
        popup_html = generate_popup_content(qrcode)
        add_marker_with_qr_icon(
            map_object=map_object,
            latitude=qrcode.latitude,
            longitude=qrcode.longitude,
            popup_content=popup_html,
            img_bytes=qrcode.img_bytes,
        )

    # Create a MarkerCluster for the scan locations
    scan_cluster = MarkerCluster().add_to(map_object)

    # Add ScanData markers to the cluster
    for scan in scans:
        popup_html = generate_popup_content(scan)
        folium.Marker([scan.latitude, scan.longitude], popup=popup_html).add_to(
            scan_cluster
        )

    # Save map to a file and return as BytesIO
    return save_map_to_file(map_object)
