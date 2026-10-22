from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Station, Reading, Threshold, Device
from app.schemas import ReadingIn
from app.security import hash_key
from app.services.analysis import turbidity_level, classify
from app.services.websocket import hub
async def ingest_one(db:Session, payload:ReadingIn, api_key:str|None=None):
    station=db.get(Station,payload.id_titik)
    if not station or not station.aktif: raise HTTPException(404,"Titik pantau tidak aktif/tidak ditemukan")
    if api_key:
        device=db.get(Device,payload.id_titik)
        # ASUMSI: jika tabel perangkat belum dibuat untuk titik, gunakan NODE_API_KEY global sebagai bootstrap.
        from app.config import settings
        import hmac
        expected=device.api_key_hash if device else hash_key(settings.node_api_key)
        if not hmac.compare_digest(hash_key(api_key),expected): raise HTTPException(401,"API key node salah")
    ts=payload.timestamp
    if ts.tzinfo is None: ts=ts.replace(tzinfo=timezone.utc)
    exists=db.scalars(select(Reading).where(Reading.id_titik==payload.id_titik,Reading.waktu_baca==ts)).first()
    if exists: return {"duplicate":True,"id_baca":exists.id_baca,"status":exists.status}
    # Check ekstrem validasi sebelum database.
    if not (-5<=payload.suhu<=70 and 0<=payload.ph<=14 and 0<=payload.kekeruhan<=100000):
        raise HTTPException(422,"Nilai sensor di luar rentang")
    level=turbidity_level(payload.kekeruhan)
    r=Reading(id_titik=payload.id_titik,waktu_baca=ts,suhu=payload.suhu,ph=payload.ph,kekeruhan=payload.kekeruhan,level_kekeruhan=level,status="Normal" if level<=3 else "Waspada")
    db.add(r); db.flush()
    db.add(db.get(Threshold,payload.id_titik) or Threshold(id_titik=payload.id_titik))
    result = classify(db,r)
    print("DEBUG HASIL ANALISIS:", result)
    db.commit()
    db.refresh(r)
    await hub.publish({"type":"reading","id_titik":r.id_titik,"waktu_baca":r.waktu_baca.isoformat(),"suhu":r.suhu,"ph":r.ph,"kekeruhan":r.kekeruhan,"level_kekeruhan":r.level_kekeruhan,"status":r.status})
    if result["alert"]: await hub.publish({"type":"alert","id_titik":r.id_titik,"status":r.status,"label":result["label"],"cross_sensor":result["cross_sensor"]})
    return {"duplicate":False,"id_baca":r.id_baca,"status":r.status,"analysis":result}
