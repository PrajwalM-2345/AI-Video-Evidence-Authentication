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

for i in range(10):
    image, label = dataset[i]

    with torch.no_grad():
        pred = model(image.unsqueeze(0)).argmax(1).item()

    print(
        f"Sample {i} | Label={label} | Prediction={pred}"
    )