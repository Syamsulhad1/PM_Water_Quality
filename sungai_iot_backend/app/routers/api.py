from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Station, Reading, Analysis, Threshold, User, Notification
from app.schemas import ReadingIn, StationIn, ThresholdIn, UserIn, LoginIn, ReadingOut
from app.security import current_user, roles, hash_password, verify_password, create_token, hash_key
from app.config import settings
from app.services.ingest import ingest_one
from app.services.report import make_report
router=APIRouter()
@router.post("/auth/login")
def login(data:LoginIn,db:Session=Depends(get_db)):
    u=db.scalars(select(User).where(User.username==data.username)).first()
    if not u or not u.aktif or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Username/password salah")
    return {"access_token":create_token(u),"token_type":"bearer"}
@router.get("/auth/me")
def me(u=Depends(current_user)): return {"id":u.id,"username":u.username,"role":u.role}
@router.get("/stations")
def stations(db:Session=Depends(get_db)): return db.scalars(select(Station).where(Station.aktif==True)).all()
@router.get("/status")
def status(db:Session=Depends(get_db)):
    out=[]
    for s in db.scalars(select(Station).where(Station.aktif==True)):
        r=db.scalars(select(Reading).where(Reading.id_titik==s.id_titik).order_by(desc(Reading.waktu_baca)).limit(1)).first()
        out.append({"station":s.nama,"id_titik":s.id_titik,"status":r.status if r else "Belum ada data","latest":r})
    return out
@router.get("/readings/latest")
def latest(id_titik:int|None=None,db:Session=Depends(get_db)):
    q=select(Reading).order_by(desc(Reading.waktu_baca))
    if id_titik: q=q.where(Reading.id_titik==id_titik)
    return db.scalars(q.limit(100)).all()
@router.get("/readings")
def readings(id_titik:int, from_time:datetime|None=Query(None,alias="from"), to:datetime|None=None, aggregation:str|None=None, limit:int=Query(500,ge=1,le=5000),db:Session=Depends(get_db)):
    q=select(Reading).where(Reading.id_titik==id_titik)
    if from_time: q=q.where(Reading.waktu_baca>=from_time)
    if to: q=q.where(Reading.waktu_baca<=to)
    return db.scalars(q.order_by(desc(Reading.waktu_baca)).limit(limit)).all()
@router.get("/analysis")
def analysis(id_titik:int|None=None,db:Session=Depends(get_db)):
    q=select(Analysis).order_by(desc(Analysis.waktu_analisis))
    if id_titik: q=q.where(Analysis.id_titik==id_titik)
    return db.scalars(q.limit(200)).all()
@router.get("/alerts")
def alerts(db:Session=Depends(get_db)): return db.scalars(select(Analysis).where(Analysis.tingkat_risiko=="Tinggi").order_by(desc(Analysis.waktu_analisis)).limit(100)).all()
@router.post("/readings")
async def post_readings(payload:ReadingIn|list[ReadingIn],x_api_key:str|None=Header(None),db:Session=Depends(get_db)):
    if not x_api_key: raise HTTPException(401,"Header X-API-Key diperlukan")
    items=payload if isinstance(payload,list) else [payload]
    results=[]
    for item in items: results.append(await ingest_one(db,item,x_api_key))
    return {"count":len(results),"results":results}
@router.post("/stations")
def create_station(data:StationIn,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    s=Station(**data.model_dump()); db.add(s); db.flush(); db.add(Threshold(id_titik=s.id_titik)); db.commit(); db.refresh(s); return s
@router.put("/stations/{station_id}")
def update_station(station_id:int,data:StationIn,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    s=db.get(Station,station_id)
    if not s: raise HTTPException(404,"Titik tidak ditemukan")
    for k,v in data.model_dump().items(): setattr(s,k,v)
    db.commit(); return s
@router.delete("/stations/{station_id}")
def delete_station(station_id:int,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    s=db.get(Station,station_id)
    if not s: raise HTTPException(404,"Titik tidak ditemukan")
    s.aktif=False; db.commit(); return {"ok":True}
@router.get("/config/thresholds/{station_id}")
def get_threshold(station_id:int,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    t=db.get(Threshold,station_id)
    if not t: raise HTTPException(404,"Konfigurasi tidak ditemukan")
    return t
@router.put("/config/thresholds/{station_id}")
def put_threshold(station_id:int,data:ThresholdIn,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    if not db.get(Station,station_id): raise HTTPException(404,"Titik tidak ditemukan")
    t=db.get(Threshold,station_id)
    if not t: t=Threshold(id_titik=station_id); db.add(t)
    for k,v in data.model_dump().items(): setattr(t,k,v)
    if t.ph_min>=t.ph_max: raise HTTPException(422,"ph_min harus lebih kecil dari ph_max")
    db.commit(); db.refresh(t); return t
@router.get("/users")
def users(db:Session=Depends(get_db),u=Depends(roles("admin"))): return db.scalars(select(User)).all()
@router.post("/users")
def create_user(data:UserIn,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    if data.role not in ("admin","petugas"): raise HTTPException(422,"Role tidak valid")
    user=User(username=data.username,password_hash=hash_password(data.password),role=data.role,telegram_chat_id=data.telegram_chat_id,aktif=data.aktif)
    db.add(user); db.commit(); db.refresh(user); return {"id":user.id,"username":user.username,"role":user.role}
@router.delete("/users/{user_id}")
def delete_user(user_id:int,db:Session=Depends(get_db),u=Depends(roles("admin"))):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,"Pengguna tidak ditemukan")
    user.aktif=False; db.commit(); return {"ok":True}
@router.get("/notifications")
def notifications(db:Session=Depends(get_db),u=Depends(roles("admin","petugas"))): return db.scalars(select(Notification).order_by(desc(Notification.waktu_kirim)).limit(500)).all()
@router.post("/reports/anomaly")
def report(id_hasil:int,db:Session=Depends(get_db),u=Depends(roles("admin","petugas"))):
    data=make_report(db,id_hasil)
    return StreamingResponse(iter([data]),media_type="application/pdf",headers={"Content-Disposition":f"attachment; filename=laporan-anomali-{id_hasil}.pdf"})
