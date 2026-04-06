import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.playlists.schemas import PlaylistCreate, PlaylistUpdate, PlaylistResponse, PlaylistDetailResponse, PlaylistTrackAdd, PlaylistTrackItem
from app.playlists import service

router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.get("/", response_model=list[PlaylistResponse])
async def list_playlists(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_user_playlists(db, user.id)


@router.post("/", response_model=PlaylistResponse, status_code=201)
async def create_playlist(data: PlaylistCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.create_playlist(db, user.id, data)


@router.get("/{playlist_id}", response_model=PlaylistDetailResponse)
async def get_playlist(playlist_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    playlist = await service.get_playlist_by_id(db, playlist_id, user.id)
    track_items = [PlaylistTrackItem(position=pt.position, added_at=pt.added_at, track=pt.track)
                   for pt in sorted(playlist.tracks, key=lambda t: t.position)]
    return PlaylistDetailResponse(
        id=playlist.id, name=playlist.name, description=playlist.description,
        cover_url=playlist.cover_url, mood_tag=playlist.mood_tag,
        is_auto_generated=playlist.is_auto_generated, track_count=playlist.track_count,
        created_at=playlist.created_at, updated_at=playlist.updated_at, tracks=track_items,
    )


@router.patch("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(playlist_id: uuid.UUID, data: PlaylistUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.update_playlist(db, playlist_id, user.id, data)


@router.delete("/{playlist_id}", status_code=204)
async def delete_playlist(playlist_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await service.delete_playlist(db, playlist_id, user.id)


@router.post("/{playlist_id}/tracks", status_code=201)
async def add_track(playlist_id: uuid.UUID, data: PlaylistTrackAdd, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await service.add_track_to_playlist(db, playlist_id, user.id, data.track_id, data.position)
    return {"status": "added"}


@router.delete("/{playlist_id}/tracks/{track_id}", status_code=204)
async def remove_track(playlist_id: uuid.UUID, track_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await service.remove_track_from_playlist(db, playlist_id, user.id, track_id)
