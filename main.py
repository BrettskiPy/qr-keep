from fastapi import FastAPI
from database import engine, Base
from routers import qrcode_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(qrcode_router.router)
