from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}  # user_id → socket

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)

    async def send(self, user_id: str, data: dict):
        ws = self.active.get(user_id)
        if ws:
            await ws.send_json(data)

    async def broadcast(self, data: dict):
        for ws in list(self.active.values()):
            await ws.send_json(data)


manager = ConnectionManager()
