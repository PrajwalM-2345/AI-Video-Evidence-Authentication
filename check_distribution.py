from collections import Counter
import torch

from backend.ai_engine.models import VideoEvidenceAI
from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform,
)

print("Loading dataset...")

dataset = KaggleDeepfakeDataset(
    "backend/kaggle_data/train",
    transform=vit_transform
)

print("Loading model...")

model = VideoEvidenceAI()
model.load_state_dict(
    torch.load(
        "models_weights/vit_evidence_checkpoint.pth",
        map_location="cpu"
    )
)
model.eval()

pred_counter = Counter()
label_counter = Counter()

print("Starting analysis...")

with torch.no_grad():
    for i in range(100):  # only 100 samples for now
        image, label = dataset[i]

        pred = model(image.unsqueeze(0)).argmax(1).item()

        pred_counter[pred] += 1
        label_counter[label] += 1

        print(
            f"Sample {i} | Label={label} | Pred={pred}"
        )

print("\nLabels:", label_counter)
print("Predictions:", pred_counter)