from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from wss.manager import manager

ws_router = APIRouter(tags=["WebSocket"])


@ws_router.websocket("/ws/{user_id}")
async def ecg_stream(websocket: WebSocket, user_id: str):
    """
    Bidirectional ECG stream for a user session.

    Client → Server messages (JSON):
      {"type": "ecg_sample", "v_mV": int, "t_us": int}
      {"type": "ping"}

    Server → Client messages (JSON):
      {"type": "ecg_sample", "v_mV": int, "t_us": int}
      {"type": "pong"}
      {"type": "error", "detail": str}
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ecg_sample":
                # Echo back — in the future route to doctor's socket
                await manager.send(user_id, {
                    "type": "ecg_sample",
                    "v_mV": data.get("v_mV", 0),
                    "t_us": data.get("t_us", 0),
                })
            elif msg_type == "ping":
                await manager.send(user_id, {"type": "pong"})
            else:
                await manager.send(user_id, {"type": "error", "detail": "Unknown message type"})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
