import torch
import torch.nn as nn
import cv2
import numpy as np
from torch.utils.data import DataLoader, random_split

from src.dataset import CULaneDataset
from src.mask_generator import generate_lane_mask
from src.model import LaneNet


# =====================
# CONFIG
# =====================
ROOT = "/Users/apple/Downloads/CULane"
BATCH_SIZE = 4
EPOCHS = 5
LR = 1e-3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# =====================
# DATA WRAPPER
# =====================
class LaneDataset(torch.utils.data.Dataset):
    def __init__(self, base_dataset):
        self.data = base_dataset

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]

        img = cv2.imread(sample["img_path"])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))

        mask = generate_lane_mask(img.shape, sample["lines"])
        mask = cv2.resize(mask, (256, 256))

        img = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        mask = torch.from_numpy(mask).unsqueeze(0).float() / 255.0

        return img, mask


# =====================
# METRICS
# =====================
def compute_iou(preds, masks):
    preds = torch.sigmoid(preds)
    preds = (preds > 0.5).float()

    inter = (preds * masks).sum()
    union = ((preds + masks) > 0).float().sum()

    return (inter / (union + 1e-6)).item()


def compute_acc(preds, masks):
    preds = torch.sigmoid(preds)
    preds = (preds > 0.5).float()

    return (preds == masks).float().mean().item()


# =====================
# VALIDATION
# =====================
def validate(model, loader, criterion):
    model.eval()

    loss_total = 0
    iou_total = 0
    acc_total = 0

    with torch.no_grad():
        for imgs, masks in loader:
            imgs = imgs.to(DEVICE)
            masks = masks.to(DEVICE)

            preds = model(imgs)
            loss = criterion(preds, masks)

            loss_total += loss.item()
            iou_total += compute_iou(preds, masks)
            acc_total += compute_acc(preds, masks)

    n = len(loader)

    return loss_total / n, iou_total / n, acc_total / n


# =====================
# TRAIN FUNCTION (IMPORTANT FIX)
# =====================
def main():
    print("Loading dataset...")

    base = CULaneDataset(ROOT)
    dataset = LaneDataset(base)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    # 🔥 FIX: num_workers = 0 (prevents macOS crash)
    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    # =====================
    # MODEL
    # =====================
    model = LaneNet().to(DEVICE)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    best_iou = 0

    # =====================
    # TRAIN LOOP
    # =====================
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0

        for i, (imgs, masks) in enumerate(train_loader):
            imgs = imgs.to(DEVICE)
            masks = masks.to(DEVICE)

            preds = model(imgs)
            loss = criterion(preds, masks)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            if i % 50 == 0:
                print(f"Epoch {epoch+1} Step {i} Loss {loss.item():.4f}")

        val_loss, val_iou, val_acc = validate(model, val_loader, criterion)

        print("\n====================")
        print(f"Epoch {epoch+1}")
        print(f"Train Loss: {train_loss/len(train_loader):.4f}")
        print(f"Val Loss:   {val_loss:.4f}")
        print(f"Val IoU:    {val_iou:.4f}")
        print(f"Val Acc:    {val_acc:.4f}")
        print("====================\n")

        if val_iou > best_iou:
            best_iou = val_iou
            torch.save(model.state_dict(), "lanenet_best.pth")
            print("🔥 Best model saved!")


# =====================
# ENTRY POINT (IMPORTANT FIX)
# =====================
if __name__ == "__main__":
    main()