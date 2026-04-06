from dataclasses import dataclass


@dataclass
class MusicProfile:
    valence_range: tuple[float, float]
    energy_range: tuple[float, float]
    tempo_range: tuple[float, float]
    genres: list[str]
    mood_label: str


MOOD_PROFILES: dict[str, MusicProfile] = {
    "happy": MusicProfile((0.6, 1.0), (0.5, 0.9), (100, 140), ["pop", "dance", "funk", "disco", "indie-pop", "afrobeat"], "Euphoric"),
    "sad": MusicProfile((0.0, 0.35), (0.1, 0.4), (60, 100), ["acoustic", "indie", "ambient", "classical", "folk", "lo-fi"], "Melancholic"),
    "angry": MusicProfile((0.2, 0.5), (0.7, 1.0), (120, 180), ["rock", "metal", "punk", "industrial", "drum-and-bass"], "Intense"),
    "fear": MusicProfile((0.1, 0.4), (0.3, 0.7), (80, 130), ["ambient", "dark-ambient", "soundtrack", "post-rock", "trip-hop"], "Tense"),
    "surprise": MusicProfile((0.5, 0.9), (0.5, 0.8), (100, 150), ["electronic", "experimental", "synth-pop", "house", "jazz-fusion"], "Electric"),
    "disgust": MusicProfile((0.1, 0.4), (0.4, 0.7), (90, 130), ["grunge", "alternative", "post-punk", "noise-rock"], "Abrasive"),
    "neutral": MusicProfile((0.3, 0.6), (0.3, 0.6), (80, 120), ["lo-fi", "chillhop", "jazz", "r-and-b", "neo-soul"], "Balanced"),
}


def get_music_profile(emotion_scores: dict[str, float], blend: bool = True) -> MusicProfile:
    sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
    dominant_emotion, dominant_score = sorted_emotions[0]
    dominant_profile = MOOD_PROFILES[dominant_emotion]

    if not blend or len(sorted_emotions) < 2 or dominant_score > 0.85:
        return dominant_profile

    secondary_emotion, secondary_score = sorted_emotions[1]
    secondary_profile = MOOD_PROFILES[secondary_emotion]

    total = dominant_score + secondary_score
    w1, w2 = dominant_score / total, secondary_score / total

    def blend_range(r1, r2):
        return (round(r1[0]*w1 + r2[0]*w2, 3), round(r1[1]*w1 + r2[1]*w2, 3))

    merged_genres = list(dominant_profile.genres)
    for g in secondary_profile.genres:
        if g not in merged_genres:
            merged_genres.append(g)

    return MusicProfile(
        valence_range=blend_range(dominant_profile.valence_range, secondary_profile.valence_range),
        energy_range=blend_range(dominant_profile.energy_range, secondary_profile.energy_range),
        tempo_range=blend_range(dominant_profile.tempo_range, secondary_profile.tempo_range),
        genres=merged_genres[:8],
        mood_label=f"{dominant_profile.mood_label} + {secondary_profile.mood_label}",
    )
