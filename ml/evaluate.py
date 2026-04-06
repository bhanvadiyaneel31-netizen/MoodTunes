import argparse
import numpy as np, torch
from ml.model import load_model
from ml.dataset import create_dataloaders, EMOTION_LABELS


def evaluate(weights_path, data_dir="data/fer2013"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_model(weights_path, device)
    _, test_loader = create_dataloaders(data_dir=data_dir, batch_size=64)

    preds, labels = [], []
    with torch.no_grad():
        for imgs, lbl in test_loader:
            out = model(imgs.to(device))
            preds.extend(out.max(1)[1].cpu().numpy())
            labels.extend(lbl.numpy())

    preds, labels = np.array(preds), np.array(labels)
    print(f"\nAccuracy: {(preds == labels).mean():.2%}")

    for i, name in enumerate(EMOTION_LABELS):
        tp = ((preds == i) & (labels == i)).sum()
        fp = ((preds == i) & (labels != i)).sum()
        fn = ((preds != i) & (labels == i)).sum()
        prec = tp/(tp+fp) if tp+fp else 0
        rec = tp/(tp+fn) if tp+fn else 0
        f1 = 2*prec*rec/(prec+rec) if prec+rec else 0
        print(f"  {name:<10} P={prec:.3f} R={rec:.3f} F1={f1:.3f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default="ml/weights/emotion_cnn.pth")
    args = p.parse_args()
    evaluate(args.weights)
