from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.config import settings
from app.routers.api import router
from app.services.websocket import hub
from app.services.mqtt import start_mqtt, stop_mqtt
@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine) # Alembic menjadi jalur migrasi produksi.
    if settings.mqtt_enabled: start_mqtt()
    yield
    stop_mqtt()
app=FastAPI(title="API Deteksi Anomali Kualitas Air Sungai",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],allow_credentials=True,allow_methods=["GET","POST","PUT","DELETE"],allow_headers=["Authorization","Content-Type","X-API-Key"])
app.include_router(router,prefix="/api/v1")
@app.get("/health")
def health(): return {"status":"ok"}
@app.websocket("/ws/live")
async def ws_live(ws:WebSocket):
    await hub.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: hub.disconnect(ws)
