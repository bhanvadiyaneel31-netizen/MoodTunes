"""
iTunes/Apple Music API Integration — Free music search with 30-second previews.

No API key required. Works globally including India.

Endpoint: https://itunes.apple.com/search
Each track includes a 30-second AAC preview URL that plays in the browser.
"""

import httpx
from dataclasses import dataclass

ITUNES_API = "https://itunes.apple.com"

# Mood → iTunes search queries
MOOD_SEARCH_QUERIES: dict[str, list[str]] = {
    "happy": [
        "Bollywood happy songs", "Badshah party songs", "AP Dhillon hits",
        "Pharrell Williams Happy", "upbeat Hindi songs", "Arijit Singh happy",
        "Bruno Mars uptown funk", "Dua Lipa dance", "Punjabi party hits",
        "Ed Sheeran shape of you", "Bollywood dance hits",
    ],
    "sad": [
        "Arijit Singh sad songs", "Bollywood sad songs", "Adele someone like you",
        "Channa Mereya", "Lewis Capaldi", "sad Hindi songs",
        "Billie Eilish sad", "Tujhe Kitna Chahne Lage", "Sam Smith ballads",
        "Atif Aslam sad songs", "heartbreak Bollywood",
    ],
    "angry": [
        "Eminem rap god", "hard rock hits", "Imagine Dragons",
        "Bollywood action songs", "Linkin Park", "KR$NA rap",
        "AC DC thunderstruck", "Raftaar songs", "Metallica",
        "aggressive workout music", "Twenty One Pilots",
    ],
    "fear": [
        "dark soundtrack music", "Hans Zimmer inception", "suspense Bollywood",
        "thriller movie soundtrack", "horror movie music",
        "Interstellar soundtrack", "eerie instrumental", "dark ambient",
    ],
    "surprise": [
        "electronic dance hits", "Daft Punk", "The Weeknd blinding lights",
        "Bollywood remix songs", "Calvin Harris", "Nucleya bass",
        "Marshmello songs", "DJ Snake", "Martin Garrix",
    ],
    "disgust": [
        "grunge rock nirvana", "alternative rock", "Radiohead",
        "Bollywood angry songs", "frustrated Hindi songs",
        "Eminem not afraid", "Three Days Grace", "Breaking Benjamin",
        "dark Bollywood songs", "intense rap Hindi", "Emiway Bantai",
    ],
    "neutral": [
        "lofi Hindi songs", "Bollywood unplugged", "Prateek Kuhad",
        "The Beatles hits", "Coldplay popular songs", "Anuv Jain songs",
        "soft rock classics", "Arijit Singh unplugged", "Ed Sheeran perfect",
        "chill Bollywood", "Taylor Swift popular",
    ],
    "calm": [
        "Arijit Singh romantic", "peaceful Hindi songs", "Norah Jones",
        "Bollywood romantic songs", "Lata Mangeshkar classics",
        "soft acoustic guitar", "Kishore Kumar songs", "spa relaxing music",
        "AR Rahman soft songs", "John Legend all of me",
    ],
    "energetic": [
        "Bollywood workout songs", "Honey Singh party", "Badshah DJ wale",
        "Shakira hips dont lie", "BTS dynamite", "Zumba dance music",
        "Bollywood gym motivation", "Pitbull party hits", "Diljit Dosanjh",
        "high energy EDM", "Sia cheap thrills",
    ],
}


@dataclass
class MusicTrack:
    id: int
    title: str
    artist: str
    album: str
    cover_url: str
    cover_url_big: str
    preview_url: str
    duration: int
    link: str


def _parse_itunes_track(item: dict) -> MusicTrack | None:
    """Parse an iTunes API result into a MusicTrack."""
    preview = item.get("previewUrl", "")
    if not preview:
        return None

    # Get high-res artwork (replace 100x100 with 300x300)
    art100 = item.get("artworkUrl100", "")
    art300 = art100.replace("100x100bb", "300x300bb") if art100 else ""

    return MusicTrack(
        id=item.get("trackId", 0),
        title=item.get("trackName", "Unknown"),
        artist=item.get("artistName", "Unknown"),
        album=item.get("collectionName", ""),
        cover_url=art100,
        cover_url_big=art300,
        preview_url=preview,
        duration=int(item.get("trackTimeMillis", 0)) // 1000,
        link=item.get("trackViewUrl", ""),
    )


async def search_tracks(query: str, limit: int = 20) -> list[MusicTrack]:
    """Search iTunes for tracks matching a query."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                f"{ITUNES_API}/search",
                params={"term": query, "media": "music", "limit": limit, "entity": "song", "country": "IN"}
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

    tracks = []
    for item in data.get("results", []):
        track = _parse_itunes_track(item)
        if track:
            tracks.append(track)
    return tracks


async def get_mood_tracks(mood: str, limit: int = 20) -> list[MusicTrack]:
    """Get tracks matching a mood by searching iTunes with mood-related queries."""
    queries = MOOD_SEARCH_QUERIES.get(mood.lower(), MOOD_SEARCH_QUERIES["neutral"])
    all_tracks: list[MusicTrack] = []
    seen_ids: set[int] = set()

    per_query = max(5, limit // len(queries) + 2)

    async with httpx.AsyncClient(timeout=10) as client:
        for query in queries:
            try:
                resp = await client.get(
                    f"{ITUNES_API}/search",
                    params={"term": query, "media": "music", "limit": per_query, "entity": "song", "country": "IN"}
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                continue

            for item in data.get("results", []):
                track = _parse_itunes_track(item)
                if track and track.id not in seen_ids:
                    seen_ids.add(track.id)
                    all_tracks.append(track)

            if len(all_tracks) >= limit:
                break

    return all_tracks[:limit]


async def get_chart_tracks(limit: int = 20) -> list[MusicTrack]:
    """Get popular/trending tracks from iTunes."""
    # Mix of Bollywood, Hollywood, and trending queries
    queries = [
        "Bollywood hits 2025 Hindi", "trending Hindi songs 2025",
        "Arijit Singh latest Hindi", "AP Dhillon Hindi songs",
        "Diljit Dosanjh Hindi hits", "Badshah new songs Hindi",
        "Shreya Ghoshal latest Hindi", "Jubin Nautiyal Hindi songs",
        "latest Bollywood movie songs Hindi", "Punjabi hits 2025 Hindi",
        "Bollywood romantic songs Hindi", "Atif Aslam Hindi songs",
    ]
    all_tracks: list[MusicTrack] = []
    seen_ids: set[int] = set()

    per_query = max(5, limit // len(queries) + 2)

    async with httpx.AsyncClient(timeout=10) as client:
        for query in queries:
            try:
                resp = await client.get(
                    f"{ITUNES_API}/search",
                    params={"term": query, "media": "music", "limit": per_query, "entity": "song", "country": "IN"}
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                continue

            for item in data.get("results", []):
                track = _parse_itunes_track(item)
                if track and track.id not in seen_ids:
                    seen_ids.add(track.id)
                    all_tracks.append(track)

            if len(all_tracks) >= limit:
                break

    return all_tracks[:limit]