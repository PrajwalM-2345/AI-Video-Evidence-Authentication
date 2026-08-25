import torch
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score
)

from backend.ai_engine.models import (
    VideoEvidenceAI,
    ForensicEnsembleEngine
)

from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform
)

print("Loading dataset...")

dataset = KaggleDeepfakeDataset(
    "backend/kaggle_data/train",
    transform=vit_transform
)

train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

_, val_dataset = random_split(
    dataset,
    [train_size, val_size],
    generator=torch.Generator().manual_seed(42)
)

loader = DataLoader(
    val_dataset,
    batch_size=64,
    shuffle=False
)

print("Loading ensemble...")

vit_model = VideoEvidenceAI()

vit_model.load_state_dict(
    torch.load(
        "models_weights/vit_evidence_checkpoint.pth",
        map_location="cpu"
    ),
    strict=False
)

ensemble = ForensicEnsembleEngine(
    vit_model,
    eff_weights_path="models_weights/efficientnet_evidence_checkpoint.pth",
    swin_weights_path="models_weights/swin_evidence_checkpoint.pth"
)

ensemble.eval()

print("Starting evaluation...")

y_true = []
y_pred = []
y_prob = []

with torch.no_grad():
    for idx, (images, labels) in enumerate(loader):

        if idx % 20 == 0:
            print(f"Processed batch {idx}/{len(loader)}")

        probs = ensemble(images)

        positive_probs = probs[:, 1]

        preds = probs.argmax(dim=1)

        y_true.extend(labels.numpy())
        y_pred.extend(preds.numpy())
        y_prob.extend(positive_probs.numpy())

print("\nCONFUSION MATRIX")
print(confusion_matrix(y_true, y_pred))

print("\nCLASSIFICATION REPORT")
print(classification_report(y_true, y_pred))

print("\nACCURACY")
print(accuracy_score(y_true, y_pred))

print("\nROC-AUC")
print(roc_auc_score(y_true, y_prob))