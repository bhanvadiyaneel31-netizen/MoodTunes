import math
import uuid
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.track import Track
from app.music.mood_mapper import get_music_profile, MusicProfile
from app.music.schemas import TrackWithScore, RecommendResponse


def _cosine_similarity(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    ma = math.sqrt(sum(x*x for x in a))
    mb = math.sqrt(sum(x*x for x in b))
    return dot / (ma * mb) if ma and mb else 0.0


def _mid(r):
    return (r[0] + r[1]) / 2


def _score_track(track: Track, profile: MusicProfile) -> float:
    target = [_mid(profile.valence_range), _mid(profile.energy_range), (_mid(profile.tempo_range)-60)/120]
    actual = [track.valence, track.energy, (track.tempo-60)/120]
    sim = max(0.0, _cosine_similarity(target, actual))

    genre_bonus = 1.0 if track.genre and track.genre.lower() in [g.lower() for g in profile.genres] else 0.0
    mood_map = {"euphoric": "happy", "melancholic": "sad", "intense": "angry", "tense": "fear", "electric": "energetic", "balanced": "neutral"}
    mood_bonus = 0.0
    if track.primary_mood:
        for lbl, expected in mood_map.items():
            if lbl in profile.mood_label.lower() and track.primary_mood.lower() == expected:
                mood_bonus = 1.0
                break

    return round(min(1.0, sim*0.5 + genre_bonus*0.25 + mood_bonus*0.25), 4)


async def recommend_tracks(db: AsyncSession, emotion_scores: dict[str, float],
                           limit: int = 20, exclude_ids=None, blend: bool = True) -> RecommendResponse:
    profile = get_music_profile(emotion_scores, blend=blend)
    tol = 0.2

    query = select(Track).where(
        Track.valence.between(max(0, profile.valence_range[0]-tol), min(1, profile.valence_range[1]+tol)),
        Track.energy.between(max(0, profile.energy_range[0]-tol), min(1, profile.energy_range[1]+tol)),
        Track.tempo.between(max(40, profile.tempo_range[0]-20), min(220, profile.tempo_range[1]+20)),
    )
    if exclude_ids:
        query = query.where(Track.id.notin_(exclude_ids))
    query = query.limit(limit * 3)

    result = await db.execute(query)
    candidates = result.scalars().all()

    scored = sorted([(t, _score_track(t, profile)) for t in candidates], key=lambda x: x[1], reverse=True)[:limit]

    return RecommendResponse(
        mood_label=profile.mood_label, target_valence=profile.valence_range,
        target_energy=profile.energy_range, target_tempo=profile.tempo_range,
        genres=profile.genres,
        tracks=[TrackWithScore(id=t.id, title=t.title, artist=t.artist, album=t.album, genre=t.genre,
                cover_url=t.cover_url, preview_url=t.preview_url, duration_ms=t.duration_ms,
                valence=t.valence, energy=t.energy, tempo=t.tempo, primary_mood=t.primary_mood,
                relevance_score=s) for t, s in scored],
    )


async def search_tracks(db: AsyncSession, query: str, genre=None, mood=None, limit=20):
    stmt = select(Track)
    term = f"%{query.lower()}%"
    stmt = stmt.where(or_(func.lower(Track.title).like(term), func.lower(Track.artist).like(term)))
    if genre:
        stmt = stmt.where(func.lower(Track.genre) == genre.lower())
    if mood:
        stmt = stmt.where(func.lower(Track.primary_mood) == mood.lower())
    result = await db.execute(stmt.limit(limit))
    return result.scalars().all()
