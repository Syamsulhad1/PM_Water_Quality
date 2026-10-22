from app.db import Base, engine, SessionLocal
from app.models import Station, Threshold, User, Device
from app.config import settings
from app.security import hash_password, hash_key
def seed():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try:
        if not db.query(Station).first():
            for name,lat,lng in [("Sungai Pilot A",-5.3971,105.2668),("Sungai Pilot B",-5.4100,105.2500)]:
                s=Station(nama=name,lat=lat,lng=lng,aktif=True); db.add(s); db.flush()
                db.add(Threshold(id_titik=s.id_titik))
                db.add(Device(id_titik=s.id_titik,api_key_hash=hash_key(settings.node_api_key)))
        for username,password,role in [(settings.seed_admin_username,settings.seed_admin_password,"admin"),(settings.seed_petugas_username,settings.seed_petugas_password,"petugas")]:
            if not db.query(User).filter_by(username=username).first():
                db.add(User(username=username,password_hash=hash_password(password),role=role,aktif=True))
        db.commit()
    finally: db.close()
if __name__=="__main__": seed()
