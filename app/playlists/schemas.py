import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.music.schemas import TrackResponse


class PlaylistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    mood_tag: str | None = None
    track_ids: list[uuid.UUID] = Field(default_factory=list)


class PlaylistUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    mood_tag: str | None = None


class PlaylistTrackAdd(BaseModel):
    track_id: uuid.UUID
    position: int | None = None


class PlaylistTrackReorder(BaseModel):
    track_id: uuid.UUID
    new_position: int = Field(ge=0)


class PlaylistTrackItem(BaseModel):
    position: int
    added_at: datetime
    track: TrackResponse
    model_config = {"from_attributes": True}


class PlaylistResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    cover_url: str | None
    mood_tag: str | None
    is_auto_generated: bool
    track_count: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PlaylistDetailResponse(PlaylistResponse):
    tracks: list[PlaylistTrackItem] = []
