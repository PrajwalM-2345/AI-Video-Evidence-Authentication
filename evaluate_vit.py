# evaluate_vit.py

import torch
from torch.utils.data import DataLoader, random_split, Subset

from backend.ai_engine.models import VideoEvidenceAI
from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform,
)

print("🚀 Loading dataset...")

dataset = KaggleDeepfakeDataset(
    "backend/kaggle_data/train",
    transform=vit_transform
)

print(f"✅ Total images found: {len(dataset)}")

train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

generator = torch.Generator().manual_seed(42)

_, val_dataset = random_split(
    dataset,
    [train_size, val_size],
    generator=generator
)

print(f"✅ Validation images: {len(val_dataset)}")

# Faster test first (500 images)
val_dataset = Subset(
    val_dataset,
    range(min(500, len(val_dataset)))
)

print(f"✅ Evaluating subset size: {len(val_dataset)}")

loader = DataLoader(
    val_dataset,
    batch_size=32,
    shuffle=False,
    num_workers=0
)

print("🚀 Loading ViT model...")

model = VideoEvidenceAI()

model.load_state_dict(
    torch.load(
        "models_weights/vit_evidence_checkpoint.pth",
        map_location="cpu"
    )
)

model.eval()

print("✅ Model loaded")
print("🚀 Starting evaluation...\n")

correct = 0
total = 0

with torch.no_grad():
    for batch_idx, (images, labels) in enumerate(loader):

        outputs = model(images)
        preds = outputs.argmax(dim=1)

        correct += (preds == labels).sum().item()
        total += labels.size(0)

        if batch_idx % 5 == 0:
            acc = 100 * correct / max(total, 1)
            print(
                f"Batch {batch_idx}/{len(loader)} | "
                f"Running Accuracy: {acc:.2f}%"
            )

final_acc = 100 * correct / total

print("\n" + "=" * 60)
print(f"🏆 FINAL ACCURACY: {final_acc:.2f}%")
print("=" * 60)