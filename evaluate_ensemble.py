import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import random
import torch
import numpy as np

from torch.utils.data import DataLoader, Subset
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from backend.ai_engine.models import (
    VideoEvidenceAI,
    ForensicEnsembleEngine,
)

from backend.ai_engine.dataset_loader import (
    KaggleDeepfakeDataset,
    vit_transform,
)


DATASET = "backend/kaggle_data/merged_train_balanced"

VIT_CHECKPOINT = "models_weights/vit_evidence_checkpoint.pth"
EFFICIENTNET_CHECKPOINT = "models_weights/efficientnet_evidence_checkpoint.pth"
SWIN_CHECKPOINT = "models_weights/swin_evidence_checkpoint.pth"

SEED = 42
BATCH_SIZE = 4


def get_device():

    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


print("\n========================================")
print("       FAIR ENSEMBLE TEST EVALUATION")
print("========================================")


random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

device = get_device()

print("Device:", device)
print("Dataset:", DATASET)


# =========================================================
# DATASET
# =========================================================

dataset = KaggleDeepfakeDataset(
    DATASET,
    transform=vit_transform
)

print("Total images:", len(dataset))

labels = np.array(dataset.labels)

print("Authentic:", int(np.sum(labels == 1)))
print("Fake:", int(np.sum(labels == 0)))


# =========================================================
# SAME 80/10/10 SPLIT AS INDIVIDUAL MODELS
# =========================================================

indices = list(range(len(dataset)))

rng = random.Random(SEED)
rng.shuffle(indices)

n = len(indices)

train_end = int(0.80 * n)
val_end = int(0.90 * n)

train_indices = indices[:train_end]
val_indices = indices[train_end:val_end]
test_indices = indices[val_end:]


test_dataset = Subset(
    dataset,
    test_indices
)


print("\nSplit:")
print("Train:", len(train_indices))
print("Validation:", len(val_indices))
print("Test:", len(test_indices))


# =========================================================
# TEST LOADER
# =========================================================

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# =========================================================
# LOAD ViT
# =========================================================

print("\nLoading ViT...")

vit_model = VideoEvidenceAI()

vit_checkpoint = torch.load(
    VIT_CHECKPOINT,
    map_location="cpu"
)

if isinstance(vit_checkpoint, dict) and "model" in vit_checkpoint:
    vit_model.load_state_dict(
        vit_checkpoint["model"],
        strict=False
    )
else:
    vit_model.load_state_dict(
        vit_checkpoint,
        strict=False
    )

vit_model = vit_model.to(device)


# =========================================================
# LOAD ENSEMBLE
# =========================================================

print("Loading EfficientNet + Swin...")

ensemble = ForensicEnsembleEngine(
    vit_model,
    eff_weights_path=EFFICIENTNET_CHECKPOINT,
    swin_weights_path=SWIN_CHECKPOINT
)

ensemble = ensemble.to(device)
ensemble.eval()


print("\nAll three models loaded.")
print("Running FAIR test evaluation...")


# =========================================================
# EVALUATION
# =========================================================

y_true = []
y_pred = []
y_prob = []


with torch.no_grad():

    for batch_idx, (images, labels_batch) in enumerate(test_loader):

        images = images.to(device)

        probs = ensemble(images)

        predictions = torch.argmax(
            probs,
            dim=1
        )

        positive_probs = probs[:, 1]

        y_true.extend(
            labels_batch.numpy().tolist()
        )

        y_pred.extend(
            predictions.cpu().numpy().tolist()
        )

        y_prob.extend(
            positive_probs.cpu().numpy().tolist()
        )

        if batch_idx % 50 == 0:

            processed = min(
                (batch_idx + 1) * BATCH_SIZE,
                len(test_dataset)
            )

            print(
                f"Processed {processed}/{len(test_dataset)}"
            )


# =========================================================
# METRICS
# =========================================================

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)

auc = roc_auc_score(
    y_true,
    y_prob
)

cm = confusion_matrix(
    y_true,
    y_pred
)


# =========================================================
# FINAL RESULTS
# =========================================================

print("\n")
print("========================================")
print("       FINAL ENSEMBLE TEST RESULTS")
print("========================================")

print(
    f"Accuracy : {accuracy * 100:.2f}%"
)

print(
    f"Precision: {precision * 100:.2f}%"
)

print(
    f"Recall   : {recall * 100:.2f}%"
)

print(
    f"F1 Score : {f1 * 100:.2f}%"
)

print(
    f"ROC-AUC  : {auc:.4f}"
)


print("\nConfusion Matrix:")
print(cm)


print("\nClassification Report:")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "Fake/Tampered",
            "Authentic/Original"
        ],
        digits=4
    )
)


print("========================================")