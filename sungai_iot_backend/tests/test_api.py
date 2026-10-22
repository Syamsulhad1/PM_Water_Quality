from datetime import datetime, timezone, timedelta
def login(client,username="admin",password="Admin123!Change"):
    r=client.post("/api/v1/auth/login",json={"username":username,"password":password}); assert r.status_code==200; return r.json()["access_token"]
def payload(ts,ntu=3,ph=7.2,temp=27):
    return {"id_titik":1,"suhu":temp,"ph":ph,"kekeruhan":ntu,"timestamp":ts.isoformat()}
def test_TC01_classification_and_public_status(client):
    r=client.post("/api/v1/readings",headers={"X-API-Key":"demo-node-key-change-me"},json=payload(datetime.now(timezone.utc),ntu=6))
    assert r.status_code==200
    assert client.get("/api/v1/status").status_code==200
def test_IT02_idempotent_replay(client):
    p=payload(datetime.now(timezone.utc))
    h={"X-API-Key":"demo-node-key-change-me"}
    assert client.post("/api/v1/readings",headers=h,json=p).status_code==200
    result=client.post("/api/v1/readings",headers=h,json=p).json()["results"][0]
    assert result["duplicate"] is True
def test_SEC01_petugas_forbidden_admin_route(client):
    token=login(client,"petugas","Petugas123!Change")
    r=client.get("/api/v1/users",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==403
def test_AI02_extreme_rejected(client):
    r=client.post("/api/v1/readings",headers={"X-API-Key":"demo-node-key-change-me"},json=payload(datetime.now(timezone.utc),ntu=-5))
    assert r.status_code==422
def test_IT01_reading_visible(client):
    h={"X-API-Key":"demo-node-key-change-me"}; p=payload(datetime.now(timezone.utc))
    client.post("/api/v1/readings",headers=h,json=p)
    assert client.get("/api/v1/readings/latest?id_titik=1").status_code==200
def test_TC07_pdf(client):
    token=login(client); h={"Authorization":f"Bearer {token}","X-API-Key":"demo-node-key-change-me"}
    client.post("/api/v1/readings",headers={"X-API-Key":"demo-node-key-change-me"},json=payload(datetime.now(timezone.utc),ntu=16,ph=5.5))
    from app.db import SessionLocal
    from app.models import Analysis
    db=SessionLocal()
    try:
        a=db.query(Analysis).first()
        if not a:
            a=Analysis(id_titik=1,tingkat_risiko="Sedang",aturan_crosssensor="",keterangan="uji"); db.add(a); db.commit(); db.refresh(a)
        r=client.post("/api/v1/reports/anomaly",params={"id_hasil":a.id_hasil},headers=h)
        assert r.status_code==200 and r.headers["content-type"]=="application/pdf"
    finally: db.close()
