from fastapi import FastAPI
from database import engine, Base
from routers import qrcode_router, scan_router, map_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(qrcode_router.router, tags=["QR Code"])
app.include_router(scan_router.router, tags=["Scan"])
app.include_router(map_router.router, tags=["Map"])
