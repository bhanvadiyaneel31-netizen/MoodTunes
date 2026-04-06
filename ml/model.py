import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch, dropout=0.25):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2), nn.Dropout2d(dropout),
        )

    def forward(self, x):
        return self.block(x)


class EmotionCNN(nn.Module):
    def __init__(self, num_classes=7, input_size=48):
        super().__init__()
        self.features = nn.Sequential(
            ConvBlock(1, 64), ConvBlock(64, 128), ConvBlock(128, 256), ConvBlock(256, 512),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(512, 256), nn.BatchNorm1d(256), nn.ReLU(inplace=True),
            nn.Dropout(0.5), nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))

    def predict_proba(self, x):
        self.eval()
        with torch.no_grad():
            return F.softmax(self.forward(x), dim=1)


def load_model(weights_path, device="cpu"):
    model = EmotionCNN()
    checkpoint = torch.load(weights_path, map_location=device, weights_only=True)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model
