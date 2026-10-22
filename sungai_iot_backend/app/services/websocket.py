from fastapi import WebSocket
class Hub:
    def __init__(self): self.clients=set()
    async def connect(self, ws:WebSocket):
        await ws.accept(); self.clients.add(ws)
    def disconnect(self,ws): self.clients.discard(ws)
    async def publish(self,data):
        dead=[]
        for ws in list(self.clients):
            try: await ws.send_json(data)
            except Exception: dead.append(ws)
        for ws in dead: self.disconnect(ws)
hub=Hub()
