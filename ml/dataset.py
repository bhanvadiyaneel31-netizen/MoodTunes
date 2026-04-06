import os
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms
from PIL import Image

EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
LABEL_TO_IDX = {l: i for i, l in enumerate(EMOTION_LABELS)}


class FER2013Dataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        for label_name in EMOTION_LABELS:
            label_dir = self.root_dir / label_name
            if not label_dir.exists(): continue
            idx = LABEL_TO_IDX[label_name]
            for p in sorted(label_dir.glob("*")):
                if p.suffix.lower() in (".png", ".jpg", ".jpeg"):
                    self.samples.append((str(p), idx))
        print(f"Loaded {len(self.samples)} images from {root_dir}")

    def __len__(self): return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("L")
        if self.transform: img = self.transform(img)
        else: img = transforms.ToTensor()(img)
        return img, label

    def get_class_weights(self):
        counts = np.zeros(len(EMOTION_LABELS))
        for _, l in self.samples: counts[l] += 1
        w = 1.0 / (counts + 1e-6)
        return torch.FloatTensor(w / w.sum() * len(EMOTION_LABELS))

    def get_sampler(self):
        cw = self.get_class_weights()
        sw = [cw[l] for _, l in self.samples]
        return WeightedRandomSampler(sw, len(self.samples), replacement=True)


def get_train_transform(sz=48):
    return transforms.Compose([
        transforms.Resize((sz, sz)), transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10), transforms.RandomAffine(0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.RandomAutocontrast(p=0.3), transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]), transforms.RandomErasing(p=0.2, scale=(0.02, 0.15)),
    ])


def get_test_transform(sz=48):
    return transforms.Compose([transforms.Resize((sz, sz)), transforms.ToTensor(), transforms.Normalize([0.5], [0.5])])


def create_dataloaders(data_dir="data/fer2013", batch_size=64, num_workers=4, input_size=48):
    train_ds = FER2013Dataset(os.path.join(data_dir, "train"), get_train_transform(input_size))
    test_ds = FER2013Dataset(os.path.join(data_dir, "test"), get_test_transform(input_size))
    train_loader = DataLoader(train_ds, batch_size=batch_size, sampler=train_ds.get_sampler(), num_workers=num_workers, pin_memory=True, drop_last=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
    return train_loader, test_loader
