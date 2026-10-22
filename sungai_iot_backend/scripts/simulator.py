import argparse, json, time, random
from datetime import datetime, timezone, timedelta
import httpx
import paho.mqtt.publish as publish
def main():
    p=argparse.ArgumentParser(); p.add_argument("--mode",choices=["normal","persistent","sediment","brief","replay"],default="normal"); p.add_argument("--transport",choices=["http","mqtt"],default="http"); p.add_argument("--station",type=int,default=1); p.add_argument("--count",type=int,default=8); p.add_argument("--url",default="http://localhost:8000/api/v1/readings"); p.add_argument("--api-key",default="demo-node-key-change-me"); p.add_argument("--broker",default="localhost"); a=p.parse_args()
    base=datetime.now(timezone.utc); batch=[]
    for i in range(a.count):
        ntu,ph,temp=3.0,7.2,27.0
        if a.mode=="persistent" and i>=a.count-4: ntu,ph,temp=17,5.8,30
        elif a.mode=="sediment" and i>=a.count-4: ntu=19
        elif a.mode=="brief" and i in (2,3): ntu,ph=18,5.5
        elif a.mode=="replay" and i>=a.count-4: ntu,ph=18,5.5
        item={"id_titik":a.station,"suhu":temp+random.uniform(-.2,.2),"ph":ph+random.uniform(-.05,.05),"kekeruhan":ntu+random.uniform(-.3,.3),"timestamp":(base+timedelta(minutes=15*i)).isoformat()}
        batch.append(item)
    if a.transport=="http":
        with httpx.Client(timeout=10) as c:
            for item in batch:
                r=c.post(a.url,json=item,headers={"X-API-Key":a.api_key}); print(r.status_code,r.text)
                if a.mode!="replay": time.sleep(.1)
            if a.mode=="replay":
                r=c.post(a.url,json=batch[-4:],headers={"X-API-Key":a.api_key}); print("REPLAY",r.status_code,r.text)
    else:
        for item in batch:
            publish.single(f"sungai/{a.station}/data",json.dumps({k:v for k,v in item.items() if k!="id_titik"}),hostname=a.broker)
            time.sleep(.1)
if __name__=="__main__": main()
