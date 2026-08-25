import torch
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)

from backend.ai_engine.models import VideoEvidenceAI
from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform
)

dataset = KaggleDeepfakeDataset(
    "backend/kaggle_data/train",
    transform=vit_transform
)
print("Loading dataset...")
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

model = VideoEvidenceAI()
print("Loading model weights...")
model.load_state_dict(
    torch.load(
        "models_weights/vit_evidence_checkpoint.pth",
        map_location="cpu"
    )
)

model.eval()

y_true = []
y_pred = []
y_prob = []
print("Starting evaluation...")
with torch.no_grad():
    for idx, (images, labels) in enumerate(loader):

        if idx % 20 == 0:
            print(f"Processed batch {idx}/{len(loader)}")

        outputs = model(images)

        probs = torch.softmax(outputs, dim=1)[:, 1]
        preds = outputs.argmax(dim=1)

        y_true.extend(labels.numpy())
        y_pred.extend(preds.numpy())
        y_prob.extend(probs.numpy())

print("\nCONFUSION MATRIX")
print(confusion_matrix(y_true, y_pred))

print("\nCLASSIFICATION REPORT")
print(classification_report(y_true, y_pred))

print("\nACCURACY")
print(accuracy_score(y_true, y_pred))

print("\nROC-AUC")
print(roc_auc_score(y_true, y_prob))