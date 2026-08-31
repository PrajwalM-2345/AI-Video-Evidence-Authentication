# inspect_more.py

import torch
from backend.ai_engine.models import VideoEvidenceAI
from backend.ai_engine.dataset_loader import KaggleDeepfakeDataset, vit_transform

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

for idx in [0, 100, 1000, 5000, 9584, 12000, 14000]:
    img, label = dataset[idx]

    with torch.no_grad():
        out = model(img.unsqueeze(0))
        probs = torch.softmax(out, dim=1)[0]

    pred = probs.argmax().item()

    print(
        f"Idx={idx} "
        f"Label={label} "
        f"Pred={pred} "
        f"P(fake)={probs[0]:.4f} "
        f"P(auth)={probs[1]:.4f}"
    )