import uuid
from pydantic import BaseModel, Field


class TrackResponse(BaseModel):
    id: uuid.UUID
    title: str
    artist: str
    album: str | None
    genre: str
    cover_url: str | None
    preview_url: str | None
    duration_ms: int
    valence: float
    energy: float
    tempo: float
    primary_mood: str
    model_config = {"from_attributes": True}


class TrackWithScore(TrackResponse):
    relevance_score: float = Field(ge=0.0, le=1.0)


class RecommendRequest(BaseModel):
    emotion_scores: dict[str, float]
    limit: int = Field(default=20, ge=1, le=50)
    exclude_track_ids: list[uuid.UUID] = Field(default_factory=list)
    blend_moods: bool = True


class RecommendResponse(BaseModel):
    mood_label: str
    target_valence: tuple[float, float]
    target_energy: tuple[float, float]
    target_tempo: tuple[float, float]
    genres: list[str]
    tracks: list[TrackWithScore]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    genre: str | None = None
    mood: str | None = None
    limit: int = Field(default=20, ge=1, le=50)
