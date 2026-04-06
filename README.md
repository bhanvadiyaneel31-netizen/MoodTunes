# 🎵 MoodTunes — AI Emotion-Based Music Platform

An AI-powered music recommendation platform that detects your facial emotions in real-time via webcam and plays mood-matched Hindi/Bollywood music.

## 🌐 Live Demo

- **Frontend:** [https://bhanvadiyaneel31-netizen.github.io/MoodTunes/](https://bhanvadiyaneel31-netizen.github.io/MoodTunes/index.html)
- **Backend API:** [https://moodtunes-api-j6t3.onrender.com](https://moodtunes-api-j6t3.onrender.com/health)
- **API Docs:** [https://moodtunes-api-j6t3.onrender.com/docs](https://moodtunes-api-j6t3.onrender.com/docs)

> ⚠️ First load takes ~50 seconds (Render free tier cold start). After that it's fast.

## ✨ Features

- 🎭 **Real-time Emotion Detection** — CNN model trained on FER-2013 (28,000+ images, 65-67% accuracy)
- 🎵 **Mood-Based Music** — Hindi/Bollywood songs matched to 7 emotions (happy, sad, angry, fear, surprise, disgust, neutral)
- 🔊 **30-Second Previews** — Powered by iTunes API, play directly in browser
- 📋 **Playlist CRUD** — Create, edit, delete playlists, add/remove tracks
- 🔐 **JWT Authentication** — Secure register/login with token refresh
- 📡 **WebSocket** — Live webcam feed at 1 FPS for real-time detection
- 🎧 **Music Player** — Now Playing bar with play/pause/next/prev controls
- 🔍 **Search** — Search any song by name or artist
- 📈 **Trending** — Current popular Hindi & Bollywood tracks

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML, CSS, JavaScript (Vanilla) |
| **Backend** | Python, FastAPI, Uvicorn |
| **Database** | PostgreSQL, SQLAlchemy (async) |
| **ML Model** | PyTorch CNN (EmotionCNN, 4.8M params) |
| **Computer Vision** | OpenCV (Haar Cascade face detection) |
| **Music API** | iTunes Search API (free, no key needed) |
| **Auth** | JWT (python-jose), bcrypt |
| **Real-time** | WebSocket |
| **Hosting** | GitHub Pages (frontend), Render (backend) |

## 🧠 How It Works

1. **Webcam** captures your face via browser
2. **OpenCV** detects and crops the face region
3. **EmotionCNN** (trained on FER-2013) classifies into 7 emotions
4. **Mood Mapper** converts emotion → music search queries
5. **iTunes API** returns matching Hindi/Bollywood songs with previews
6. **Audio Player** plays 30-second previews in the browser

## 📂 Project Structure

