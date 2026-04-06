import argparse, time
from pathlib import Path
import torch, torch.nn as nn, torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from ml.model import EmotionCNN
from ml.dataset import create_dataloaders, EMOTION_LABELS


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    loss_sum, correct, total = 0., 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        out = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        loss_sum += loss.item() * imgs.size(0)
        correct += out.max(1)[1].eq(labels).sum().item()
        total += labels.size(0)
    return loss_sum / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    loss_sum, correct, total = 0., 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        out = model(imgs)
        loss = criterion(out, labels)
        loss_sum += loss.item() * imgs.size(0)
        correct += out.max(1)[1].eq(labels).sum().item()
        total += labels.size(0)
    return loss_sum / total, correct / total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default="data/fer2013")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch_size", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--save_dir", default="ml/weights")
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    train_loader, test_loader = create_dataloaders(args.data_dir, args.batch_size)
    model = EmotionCNN().to(device)
    print(f"Params: {sum(p.numel() for p in model.parameters()):,}")

    cw = train_loader.dataset.get_class_weights().to(device)
    criterion = nn.CrossEntropyLoss(weight=cw, label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    best_acc = 0.
    save_path = Path(args.save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        tl, ta = train_one_epoch(model, train_loader, criterion, optimizer, device)
        vl, va = evaluate(model, test_loader, criterion, device)
        scheduler.step()
        print(f"Epoch {epoch:>3} | Train {ta:.2%} | Test {va:.2%} | {time.time()-t0:.1f}s")

        if va > best_acc:
            best_acc = va
            torch.save({"epoch": epoch, "model_state_dict": model.state_dict(), "test_accuracy": va}, save_path / "emotion_cnn.pth")
            print(f"  -> Saved (acc: {best_acc:.2%})")

    print(f"\nBest: {best_acc:.2%}")


if __name__ == "__main__":
    main()
