import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.playlist import Playlist, PlaylistTrack
from app.models.track import Track
from app.playlists.schemas import PlaylistCreate, PlaylistUpdate


async def get_user_playlists(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(select(Playlist).where(Playlist.user_id == user_id).order_by(Playlist.updated_at.desc()))
    return result.scalars().all()


async def get_playlist_by_id(db: AsyncSession, playlist_id: uuid.UUID, user_id: uuid.UUID):
    result = await db.execute(select(Playlist).where(Playlist.id == playlist_id, Playlist.user_id == user_id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Playlist not found")
    return playlist


async def create_playlist(db: AsyncSession, user_id: uuid.UUID, data: PlaylistCreate):
    playlist = Playlist(user_id=user_id, name=data.name, description=data.description, mood_tag=data.mood_tag)
    db.add(playlist)
    await db.flush()

    if data.track_ids:
        for pos, tid in enumerate(data.track_ids):
            track = await db.execute(select(Track).where(Track.id == tid))
            if track.scalar_one_or_none():
                db.add(PlaylistTrack(playlist_id=playlist.id, track_id=tid, position=pos))
        playlist.track_count = len(data.track_ids)

    await db.flush()
    await db.refresh(playlist)
    return playlist


async def update_playlist(db: AsyncSession, playlist_id: uuid.UUID, user_id: uuid.UUID, data: PlaylistUpdate):
    playlist = await get_playlist_by_id(db, playlist_id, user_id)
    if data.name is not None: playlist.name = data.name
    if data.description is not None: playlist.description = data.description
    if data.mood_tag is not None: playlist.mood_tag = data.mood_tag
    await db.flush()
    await db.refresh(playlist)
    return playlist


async def delete_playlist(db: AsyncSession, playlist_id: uuid.UUID, user_id: uuid.UUID):
    playlist = await get_playlist_by_id(db, playlist_id, user_id)
    await db.delete(playlist)
    await db.flush()


async def add_track_to_playlist(db: AsyncSession, playlist_id: uuid.UUID, user_id: uuid.UUID, track_id: uuid.UUID, position=None):
    playlist = await get_playlist_by_id(db, playlist_id, user_id)

    track_result = await db.execute(select(Track).where(Track.id == track_id))
    if not track_result.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Track not found")

    existing = await db.execute(select(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist_id, PlaylistTrack.track_id == track_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Track already in playlist")

    if position is None:
        max_pos = await db.execute(select(func.max(PlaylistTrack.position)).where(PlaylistTrack.playlist_id == playlist_id))
        position = (max_pos.scalar() or -1) + 1

    db.add(PlaylistTrack(playlist_id=playlist_id, track_id=track_id, position=position))
    playlist.track_count += 1
    await db.flush()


async def remove_track_from_playlist(db: AsyncSession, playlist_id: uuid.UUID, user_id: uuid.UUID, track_id: uuid.UUID):
    playlist = await get_playlist_by_id(db, playlist_id, user_id)
    result = await db.execute(select(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist_id, PlaylistTrack.track_id == track_id))
    pt = result.scalar_one_or_none()
    if not pt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Track not in playlist")

    removed_pos = pt.position
    await db.delete(pt)

    after = await db.execute(select(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist_id, PlaylistTrack.position > removed_pos).order_by(PlaylistTrack.position))
    for t in after.scalars().all():
        t.position -= 1

    playlist.track_count = max(0, playlist.track_count - 1)
    await db.flush()
