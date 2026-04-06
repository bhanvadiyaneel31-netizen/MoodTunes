# MoodTunes

AI-powered emotion-based music recommendation platform.

## Quick Start

```bash
# 1. Setup environment
cp .env.example .env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Start databases
docker-compose up -d db redis

# 3. Seed tracks
python -m scripts.seed_tracks

# 4. Run API
uvicorn app.main:app --reload

# 5. Open docs
# http://localhost:8000/docs
```

## Train the Emotion Model

1. Download FER-2013 from [Kaggle](https://www.kaggle.com/datasets/msambare/fer2013)
2. Place in `data/fer2013/train/` and `data/fer2013/test/`
3. Run: `python -m ml.train_fer --epochs 50`

## API Endpoints

- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Get JWT tokens
- `POST /api/v1/mood/detect` — Detect emotion from webcam frame
- `WS /ws/mood` — Real-time WebSocket mood detection
- `POST /api/v1/music/recommend` — Get mood-based recommendations
- `GET /api/v1/playlists/` — CRUD playlists
