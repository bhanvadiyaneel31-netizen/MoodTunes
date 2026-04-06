import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.mood_log import MoodLog
from app.mood.detector import MoodDetector, get_detector, EmotionResult

router = APIRouter(prefix="/mood", tags=["Mood Detection"])


class DetectRequest(BaseModel):
    image: str
    session_id: str | None = None


class DetectResponse(BaseModel):
    emotion: str
    confidence: float
    scores: dict[str, float]
    face_detected: bool
    face_bbox: list[int] | None = None


class MoodHistoryItem(BaseModel):
    emotion: str
    confidence: float
    scores: dict[str, float]
    created_at: datetime
    model_config = {"from_attributes": True}


class MoodStats(BaseModel):
    dominant_mood: str
    total_detections: int
    mood_distribution: dict[str, float]
    avg_confidence: float


@router.post("/detect", response_model=DetectResponse)
async def detect_mood(
    data: DetectRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    detector: MoodDetector = Depends(get_detector),
):
    result: EmotionResult = detector.detect_from_base64(data.image)

    if result.face_detected and result.confidence > 0.3:
        log = MoodLog(
            user_id=user.id, emotion=result.emotion,
            confidence=result.confidence, emotion_scores=result.scores,
            source="webcam", session_id=data.session_id,
        )
        db.add(log)

    return DetectResponse(
        emotion=result.emotion, confidence=result.confidence,
        scores=result.scores, face_detected=result.face_detected,
        face_bbox=list(result.face_bbox) if result.face_bbox else None,
    )


@router.get("/history", response_model=list[MoodHistoryItem])
async def get_mood_history(
    minutes: int = Query(30, ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    result = await db.execute(
        select(MoodLog).where(MoodLog.user_id == user.id, MoodLog.created_at >= cutoff)
        .order_by(MoodLog.created_at.desc()).limit(200)
    )
    return result.scalars().all()


@router.get("/stats", response_model=MoodStats)
async def get_mood_stats(
    minutes: int = Query(30, ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    result = await db.execute(
        select(MoodLog).where(MoodLog.user_id == user.id, MoodLog.created_at >= cutoff)
    )
    logs = result.scalars().all()

    if not logs:
        return MoodStats(dominant_mood="neutral", total_detections=0, mood_distribution={}, avg_confidence=0.0)

    mood_counts: dict[str, int] = {}
    total_conf = 0.0
    for log in logs:
        mood_counts[log.emotion] = mood_counts.get(log.emotion, 0) + 1
        total_conf += log.confidence

    total = len(logs)
    return MoodStats(
        dominant_mood=max(mood_counts, key=mood_counts.get),
        total_detections=total,
        mood_distribution={m: round(c / total, 4) for m, c in mood_counts.items()},
        avg_confidence=round(total_conf / total, 4),
    )
