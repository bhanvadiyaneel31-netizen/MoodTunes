from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.music.schemas import RecommendRequest, RecommendResponse, TrackResponse, SearchRequest
from app.music.service import recommend_tracks, search_tracks

router = APIRouter(prefix="/music", tags=["Music & Recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(data: RecommendRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await recommend_tracks(db=db, emotion_scores=data.emotion_scores, limit=data.limit,
                                  exclude_ids=data.exclude_track_ids or [], blend=data.blend_moods)


@router.post("/search", response_model=list[TrackResponse])
async def search(data: SearchRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await search_tracks(db=db, query=data.query, genre=data.genre, mood=data.mood, limit=data.limit)


@router.get("/genres", response_model=list[str])
async def list_genres():
    return ["acoustic","afrobeat","ambient","alternative","chillhop","classical","dance","dark-ambient",
            "disco","drum-and-bass","easy-listening","electronic","experimental","folk","funk","grunge",
            "hardcore","house","indie","indie-pop","industrial","jazz","jazz-fusion","lo-fi","metal",
            "neo-soul","noise-rock","pop","post-punk","post-rock","punk","r-and-b","rock","soundtrack",
            "synth-pop","trip-hop"]
