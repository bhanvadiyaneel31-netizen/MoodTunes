import uuid
from sqlalchemy import String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    artist: Mapped[str] = mapped_column(String(200), nullable=False)
    album: Mapped[str | None] = mapped_column(String(200))
    genre: Mapped[str] = mapped_column(String(50), index=True)
    cover_url: Mapped[str | None] = mapped_column(String(500))
    preview_url: Mapped[str | None] = mapped_column(String(500))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    valence: Mapped[float] = mapped_column(Float, default=0.5)
    energy: Mapped[float] = mapped_column(Float, default=0.5)
    danceability: Mapped[float] = mapped_column(Float, default=0.5)
    tempo: Mapped[float] = mapped_column(Float, default=120.0)
    primary_mood: Mapped[str] = mapped_column(String(20), index=True)
