# inspect_probs.py

import torch

from backend.ai_engine.models import VideoEvidenceAI
from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform,
)

dataset = KaggleDeepfakeDataset(
    "backend/kaggle_data/train",
    transform=vit_transform
)

model = VideoEvidenceAI()

model.load_state_dict(
    torch.load(
        "models_weights/vit_evidence_checkpoint.pth",
        map_location="cpu"
    )
)

model.eval()

for idx in [0, 100, 1000, 5000, 9584, 12000]:
    image, label = dataset[idx]

    with torch.no_grad():
        logits = model(image.unsqueeze(0))
        probs = torch.softmax(logits, dim=1)

    print(
        f"Sample {idx} "
        f"Label={label} "
        f"Prob0={probs[0][0].item():.4f} "
        f"Prob1={probs[0][1].item():.4f}"
    )