import base64
import io
from dataclasses import dataclass

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from app.config import get_settings
from ml.model import EmotionCNN, load_model

settings = get_settings()


@dataclass
class EmotionResult:
    emotion: str
    confidence: float
    scores: dict[str, float]
    face_detected: bool
    face_bbox: tuple[int, int, int, int] | None = None


class MoodDetector:
    _instance: "MoodDetector | None" = None

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model: EmotionCNN | None = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.transform = transforms.Compose([
            transforms.Resize((settings.MODEL_INPUT_SIZE, settings.MODEL_INPUT_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5]),
        ])
        self.labels = settings.EMOTION_LABELS

    @classmethod
    def get_instance(cls) -> "MoodDetector":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> None:
        try:
            self.model = load_model(settings.MODEL_PATH, self.device)
            print(f"EmotionCNN loaded on {self.device}")
        except FileNotFoundError:
            print(f"WARNING: Model weights not found at {settings.MODEL_PATH}")
            print("Run `python -m ml.train_fer` first to train the model.")
            self.model = None

    def detect_from_base64(self, b64_image: str) -> EmotionResult:
        img_bytes = base64.b64decode(b64_image)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        frame = np.array(img)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        return self._detect_from_gray(gray)

    def detect_from_frame(self, frame: np.ndarray) -> EmotionResult:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self._detect_from_gray(gray)

    def _detect_from_gray(self, gray: np.ndarray) -> EmotionResult:
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            return EmotionResult(
                emotion="neutral", confidence=0.0,
                scores={label: 0.0 for label in self.labels}, face_detected=False,
            )

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y:y+h, x:x+w]
        face_pil = Image.fromarray(face_roi)
        tensor = self.transform(face_pil).unsqueeze(0).to(self.device)

        if self.model is None:
            return EmotionResult(
                emotion="neutral", confidence=0.0,
                scores={label: 0.0 for label in self.labels},
                face_detected=True, face_bbox=(int(x), int(y), int(w), int(h)),
            )

        probs = self.model.predict_proba(tensor)[0].cpu().numpy()
        scores = {label: round(float(p), 4) for label, p in zip(self.labels, probs)}
        top_idx = int(np.argmax(probs))

        return EmotionResult(
            emotion=self.labels[top_idx],
            confidence=round(float(probs[top_idx]), 4),
            scores=scores,
            face_detected=True,
            face_bbox=(int(x), int(y), int(w), int(h)),
        )


def get_detector() -> MoodDetector:
    return MoodDetector.get_instance()
