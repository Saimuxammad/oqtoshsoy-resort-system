from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..websocket.manager import manager
from ..utils.dependencies import get_current_user_ws
import json

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        token: str = Query(...),
        db: Session = Depends(get_db)
):
    try:
        # Verify user from token
        user = await get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=4001, reason="Unauthorized")
            return

        await manager.connect(websocket, user.id)

        # Send initial connection success
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user.id
        })

        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle ping/pong for connection keepalive
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id)

    except Exception as e:
        await websocket.close(code=4000, reason=str(e))