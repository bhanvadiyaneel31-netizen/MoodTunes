import asyncio, random
from app.database import AsyncSessionLocal, engine, Base
from app.models.track import Track

TRACKS = [
    {"title":"Sunlight Disco","artist":"Solar Beats","genre":"disco","primary_mood":"happy","valence":0.85,"energy":0.78,"tempo":118,"danceability":0.82},
    {"title":"Morning Radiance","artist":"Ethereal Bloom","genre":"pop","primary_mood":"happy","valence":0.92,"energy":0.65,"tempo":110,"danceability":0.74},
    {"title":"Pure Serotonin","artist":"Neon Pulse","genre":"dance","primary_mood":"happy","valence":0.88,"energy":0.82,"tempo":128,"danceability":0.89},
    {"title":"Electric Smile","artist":"Voltage","genre":"synth-pop","primary_mood":"happy","valence":0.79,"energy":0.71,"tempo":122,"danceability":0.76},
    {"title":"Vibe Check","artist":"Good Times","genre":"funk","primary_mood":"happy","valence":0.83,"energy":0.75,"tempo":115,"danceability":0.85},
    {"title":"Golden Hour","artist":"Sunset Drive","genre":"indie-pop","primary_mood":"happy","valence":0.76,"energy":0.58,"tempo":108,"danceability":0.68},
    {"title":"Starlight Horizon","artist":"Neon Echoes","genre":"pop","primary_mood":"happy","valence":0.81,"energy":0.67,"tempo":112,"danceability":0.72},
    {"title":"Rainy Day Vibes","artist":"Grey Skies","genre":"acoustic","primary_mood":"sad","valence":0.15,"energy":0.22,"tempo":72,"danceability":0.28},
    {"title":"Midnight Echoes","artist":"Solitude","genre":"indie","primary_mood":"sad","valence":0.21,"energy":0.30,"tempo":85,"danceability":0.32},
    {"title":"Fading Light","artist":"Hollow Moon","genre":"folk","primary_mood":"sad","valence":0.12,"energy":0.18,"tempo":68,"danceability":0.22},
    {"title":"Empty Rooms","artist":"Cold Frames","genre":"ambient","primary_mood":"sad","valence":0.08,"energy":0.15,"tempo":60,"danceability":0.12},
    {"title":"Silent Roads","artist":"Winter Archive","genre":"lo-fi","primary_mood":"sad","valence":0.25,"energy":0.28,"tempo":82,"danceability":0.35},
    {"title":"Primal Surge","artist":"Iron Wake","genre":"metal","primary_mood":"angry","valence":0.32,"energy":0.95,"tempo":165,"danceability":0.42},
    {"title":"Shattered Glass","artist":"Broken Circuit","genre":"rock","primary_mood":"angry","valence":0.28,"energy":0.88,"tempo":150,"danceability":0.48},
    {"title":"Rage Protocol","artist":"System Crash","genre":"industrial","primary_mood":"angry","valence":0.22,"energy":0.92,"tempo":160,"danceability":0.38},
    {"title":"Burning Edge","artist":"Voltage Spike","genre":"punk","primary_mood":"angry","valence":0.35,"energy":0.85,"tempo":172,"danceability":0.52},
    {"title":"Neural Flow","artist":"Lofi Dreamer","genre":"lo-fi","primary_mood":"calm","valence":0.45,"energy":0.32,"tempo":85,"danceability":0.48},
    {"title":"Neon Serenity","artist":"Lofi Dreamer","genre":"chillhop","primary_mood":"calm","valence":0.50,"energy":0.35,"tempo":88,"danceability":0.52},
    {"title":"Lunar Echoes","artist":"Deep Space","genre":"ambient","primary_mood":"neutral","valence":0.40,"energy":0.20,"tempo":70,"danceability":0.25},
    {"title":"Midnight Chill","artist":"Blue Hour","genre":"jazz","primary_mood":"calm","valence":0.48,"energy":0.38,"tempo":92,"danceability":0.45},
    {"title":"Focus Mode","artist":"Code Runner","genre":"lo-fi","primary_mood":"calm","valence":0.52,"energy":0.40,"tempo":90,"danceability":0.50},
    {"title":"Ocean Drift","artist":"Tidal Mind","genre":"neo-soul","primary_mood":"calm","valence":0.48,"energy":0.35,"tempo":84,"danceability":0.55},
    {"title":"Electric Drive","artist":"Synthwave 84","genre":"electronic","primary_mood":"energetic","valence":0.72,"energy":0.88,"tempo":140,"danceability":0.82},
    {"title":"Cyberpunk Runner","artist":"Neon Grid","genre":"synth-pop","primary_mood":"energetic","valence":0.65,"energy":0.85,"tempo":135,"danceability":0.78},
    {"title":"Power Surge","artist":"Volt","genre":"house","primary_mood":"energetic","valence":0.68,"energy":0.80,"tempo":128,"danceability":0.85},
    {"title":"Shadow Protocol","artist":"Dark Matter","genre":"dark-ambient","primary_mood":"fear","valence":0.15,"energy":0.45,"tempo":95,"danceability":0.22},
    {"title":"Whispers","artist":"Ghost Signal","genre":"trip-hop","primary_mood":"fear","valence":0.22,"energy":0.52,"tempo":105,"danceability":0.35},
    {"title":"Summer Waves","artist":"Beach Day","genre":"afrobeat","primary_mood":"happy","valence":0.82,"energy":0.72,"tempo":108,"danceability":0.88},
    {"title":"Classic Jazz Essentials","artist":"Blue Note","genre":"jazz","primary_mood":"calm","valence":0.55,"energy":0.40,"tempo":100,"danceability":0.55},
    {"title":"Supernova","artist":"Cosmic Ray","genre":"dance","primary_mood":"energetic","valence":0.75,"energy":0.90,"tempo":138,"danceability":0.88},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        count = await session.execute(select(func.count(Track.id)))
        if count.scalar() > 0:
            print("Already seeded."); return
        for d in TRACKS:
            session.add(Track(**d, duration_ms=random.randint(180000, 320000)))
        await session.commit()
        print(f"Seeded {len(TRACKS)} tracks.")


if __name__ == "__main__":
    asyncio.run(seed())
