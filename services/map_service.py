import folium
from io import BytesIO
from sqlalchemy.orm import Session
from models.scan_model import ScanData
from typing import Optional
from datetime import datetime
from folium.plugins import HeatMap, MarkerCluster
from models.map_model import TimeBoundParams
from fastapi import HTTPException
from fastapi.responses import StreamingResponse


def fetch_location_data(db: Session, qr_id: int, time_params: TimeBoundParams):
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

    return location_data


def generate_map_response(map_file, qr_id: int):
    return StreamingResponse(
        map_file,
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename=map_qrcode_{qr_id}_scans.html"
        },
    )


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


def generate_pin_map(location_data, qr_id: int):
    if not location_data:
        raise ValueError(f"No location data found for QR code ID {qr_id}")

    # Use the first location to center the map
    initial_location = [location_data[0].latitude, location_data[0].longitude]
    map_object = folium.Map(location=initial_location, zoom_start=5)

    # Add markers for each location in the location_data list with popups showing metadata
    for location in location_data:
        popup_html = f"""
        <b>IP Address:</b> {location.ip_address}<br>
        <b>User Agent:</b> {location.user_agent}<br>
        <b>Timestamp:</b> {location.timestamp}<br>
        <b>Latitude:</b> {location.latitude}<br>
        <b>Longitude:</b> {location.longitude}
        """
        popup = folium.Popup(popup_html, max_width=250)

        # Add the marker with the popup
        folium.Marker([location.latitude, location.longitude], popup=popup).add_to(
            map_object
        )

    # Save the map to an in-memory file object
    file_obj = BytesIO()
    map_object.save(file_obj, close_file=False)
    file_obj.seek(0)

    return file_obj


def generate_heat_map(location_data, qr_id: int):
    if not location_data:
        raise ValueError(f"No location data found for QR code ID {qr_id}")

    # Use the first location to center the map
    initial_location = [location_data[0].latitude, location_data[0].longitude]
    map_object = folium.Map(location=initial_location, zoom_start=5)

    # Prepare the list of coordinates for the heatmap
    heatmap_data = [
        [location.latitude, location.longitude] for location in location_data
    ]

    # Add the heatmap layer
    HeatMap(heatmap_data).add_to(map_object)

    # Save the map to an in-memory file object
    file_obj = BytesIO()
    map_object.save(file_obj, close_file=False)
    file_obj.seek(0)

    return file_obj


def generate_cluster_map(location_data, qr_id: int):
    if not location_data:
        raise ValueError(f"No location data found for QR code ID {qr_id}")

    initial_location = [location_data[0].latitude, location_data[0].longitude]
    map_object = folium.Map(location=initial_location, zoom_start=5)

    # Create a cluster object
    marker_cluster = MarkerCluster().add_to(map_object)

    # Add markers to the cluster
    for location in location_data:
        folium.Marker(
            [location.latitude, location.longitude],
            popup=f"IP: {location.ip_address}, Timestamp: {location.timestamp}",
        ).add_to(marker_cluster)

    file_obj = BytesIO()
    map_object.save(file_obj, close_file=False)
    file_obj.seek(0)

    return file_obj
