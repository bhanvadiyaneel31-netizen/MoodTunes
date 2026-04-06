"""
Music endpoints using iTunes API — search, mood-based, and trending.
All responses include 30-second preview URLs for browser playback.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.music.deezer import search_tracks, get_mood_tracks, get_chart_tracks, MusicTrack

router = APIRouter(prefix="/deezer", tags=["Music (iTunes)"])


class TrackResponse(BaseModel):
    id: int
    title: str
    artist: str
    album: str
    cover_url: str
    cover_url_big: str
    preview_url: str
    duration: int
    link: str


class MoodRequest(BaseModel):
    mood: str
    limit: int = 20


class MoodRecommendRequest(BaseModel):
    emotion_scores: dict[str, float]
    limit: int = 20


def to_response(t: MusicTrack) -> TrackResponse:
    return TrackResponse(
        id=t.id, title=t.title, artist=t.artist, album=t.album,
        cover_url=t.cover_url, cover_url_big=t.cover_url_big,
        preview_url=t.preview_url, duration=t.duration, link=t.link,
    )


@router.get("/search", response_model=list[TrackResponse])
async def music_search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(get_current_user),
):
    """Search for tracks. Returns results with 30-sec preview URLs."""
    tracks = await search_tracks(q, limit)
    return [to_response(t) for t in tracks]


@router.post("/mood", response_model=list[TrackResponse])
async def music_by_mood(
    data: MoodRequest,
    user: User = Depends(get_current_user),
):
    """Get tracks matching a specific mood."""
    tracks = await get_mood_tracks(data.mood, data.limit)
    return [to_response(t) for t in tracks]


@router.post("/recommend", response_model=list[TrackResponse])
async def music_recommend(
    data: MoodRecommendRequest,
    user: User = Depends(get_current_user),
):
    """Get track recommendations based on emotion scores from the detector."""
    if not data.emotion_scores or all(v == 0 for v in data.emotion_scores.values()):
        mood = "neutral"
    else:
        mood = max(data.emotion_scores, key=data.emotion_scores.get)

    tracks = await get_mood_tracks(mood, data.limit)
    return [to_response(t) for t in tracks]


@router.get("/chart", response_model=list[TrackResponse])
async def music_chart(
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(get_current_user),
):
    """Get trending/popular tracks."""
    tracks = await get_chart_tracks(limit)
    return [to_response(t) for t in tracks]