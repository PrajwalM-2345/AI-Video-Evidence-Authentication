# compare_logits.py

import torch

from backend.ai_engine.models import VideoEvidenceAI
from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform
)

dataset = KaggleDeepfakeDataset(
    "backend/kaggle_data/train",
    transform=vit_transform
)

img, label = dataset[0]

trained = VideoEvidenceAI()
trained.load_state_dict(
    torch.load(
        "models_weights/vit_evidence_checkpoint.pth",
        map_location="cpu"
    )
)

fresh = VideoEvidenceAI()

trained.eval()
fresh.eval()

with torch.no_grad():
    out1 = trained(img.unsqueeze(0))
    out2 = fresh(img.unsqueeze(0))

print("TRAINED")
print(out1)

print("\nFRESH")
print(out2)