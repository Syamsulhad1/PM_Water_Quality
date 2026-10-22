import json, threading
import paho.mqtt.client as mqtt
from app.config import settings
from app.db import SessionLocal
from app.schemas import ReadingIn
from app.services.ingest import ingest_one
_client=None
def start_mqtt():
    global _client
    def on_connect(client,userdata,flags,reason_code,properties=None):
        client.subscribe("sungai/+/data",qos=1)
    def on_message(client,userdata,msg):
        # Payload wajib menyertakan id_titik agar identitas tidak hanya bergantung pada topik.
        try:
            data=json.loads(msg.payload.decode())
            parts=msg.topic.split("/")
            data["id_titik"]=int(parts[1])
            payload=ReadingIn(id_titik=data["id_titik"],suhu=data["suhu"],ph=data["ph"],kekeruhan=data["kekeruhan"],timestamp=data["timestamp"])
            db=SessionLocal()
            try:
                import asyncio
                asyncio.run(ingest_one(db,payload,None))
            finally: db.close()
        except Exception as exc: print(f"[MQTT] payload ditolak: {exc}")
    _client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    _client.on_connect=on_connect; _client.on_message=on_message
    _client.connect(settings.mqtt_host,settings.mqtt_port,60); _client.loop_start()
def stop_mqtt():
    if _client: _client.loop_stop(); _client.disconnect()
