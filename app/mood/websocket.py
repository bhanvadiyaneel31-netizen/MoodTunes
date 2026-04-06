import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.mood.detector import MoodDetector

ws_router = APIRouter()


@ws_router.websocket("/ws/mood")
async def mood_websocket(websocket: WebSocket):
    await websocket.accept()
    detector = MoodDetector.get_instance()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            if "image" not in payload:
                await websocket.send_json({"error": "Missing image field"})
                continue

            result = detector.detect_from_base64(payload["image"])
            await websocket.send_json({
                "emotion": result.emotion,
                "confidence": result.confidence,
                "scores": result.scores,
                "face_detected": result.face_detected,
                "face_bbox": list(result.face_bbox) if result.face_bbox else None,
            })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
