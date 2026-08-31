import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import sys
import json
import random
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

sys.path.append("backend/aasist")

from models.AASIST import Model


REAL_DIR = Path("backend/kaggle_data/audio_dataset/real")
FAKE_DIR = Path("backend/kaggle_data/audio_dataset/fake")

CHECKPOINT = "models_weights/aasist_finetuned.pth"
CONFIG_PATH = "backend/aasist/config/AASIST.conf"

SEED = 42
BATCH_SIZE = 8
TARGET_LEN = 64600


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class AudioDataset(Dataset):

    def __init__(self, files, labels):
        self.files = files
        self.labels = labels

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):

        try:
            wav, sr = sf.read(str(self.files[idx]))
        except Exception:
            wav = np.zeros(TARGET_LEN, dtype=np.float32)

        if wav.ndim > 1:
            wav = np.mean(wav, axis=1)

        if len(wav) == 0:
            wav = np.zeros(TARGET_LEN, dtype=np.float32)

        if len(wav) >= TARGET_LEN:
            wav = wav[:TARGET_LEN]
        else:
            repeat = TARGET_LEN // len(wav) + 1
            wav = np.tile(wav, repeat)[:TARGET_LEN]

        wav = torch.tensor(wav, dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.long)

        return wav, label


print("\n========================================")
print("       AASIST TEST EVALUATION")
print("========================================")

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

device = get_device()

print("Device:", device)
print("Dataset:", "backend/kaggle_data/audio_dataset")


# ============================================================
# DATASET
# ============================================================

real_files = sorted(REAL_DIR.glob("*.wav"))
fake_files = sorted(FAKE_DIR.glob("*.wav"))

files = real_files + fake_files
labels = [1] * len(real_files) + [0] * len(fake_files)

print("Total audio:", len(files))
print("Real:", len(real_files))
print("Fake:", len(fake_files))


# ============================================================
# DETERMINISTIC 80/10/10 SPLIT
# ============================================================

indices = list(range(len(files)))

rng = random.Random(SEED)
rng.shuffle(indices)

n = len(indices)

train_end = int(0.80 * n)
val_end = int(0.90 * n)

train_indices = indices[:train_end]
val_indices = indices[train_end:val_end]
test_indices = indices[val_end:]

print("\nSplit:")
print("Train:", len(train_indices))
print("Validation:", len(val_indices))
print("Test:", len(test_indices))


test_files = [files[i] for i in test_indices]
test_labels = [labels[i] for i in test_indices]

test_dataset = AudioDataset(test_files, test_labels)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# ============================================================
# MODEL
# ============================================================

print("\nLoading AASIST checkpoint...")

with open(CONFIG_PATH, "r") as f:
    cfg = json.load(f)

model = Model(cfg["model_config"])

checkpoint = torch.load(
    CHECKPOINT,
    map_location="cpu"
)

if isinstance(checkpoint, dict) and "model" in checkpoint:
    model.load_state_dict(checkpoint["model"])
else:
    model.load_state_dict(checkpoint)

model = model.to(device)
model.eval()

print("Checkpoint loaded successfully.")


# ============================================================
# EVALUATION
# ============================================================

y_true = []
y_pred = []
y_prob = []

print("\nRunning test evaluation...")

with torch.no_grad():

    for batch_idx, (audio, labels_batch) in enumerate(test_loader):

        audio = audio.to(device)

        _, logits = model(audio)

        probabilities = torch.softmax(logits, dim=1)

        predictions = torch.argmax(probabilities, dim=1)

        y_true.extend(
            labels_batch.numpy().tolist()
        )

        y_pred.extend(
            predictions.cpu().numpy().tolist()
        )

        # Label policy:
        # 0 = fake
        # 1 = real

        y_prob.extend(
            probabilities[:, 1]
            .cpu()
            .numpy()
            .tolist()
        )

        if batch_idx % 50 == 0:
            processed = min(
                (batch_idx + 1) * BATCH_SIZE,
                len(test_dataset)
            )

            print(
                f"Processed {processed}/{len(test_dataset)}"
            )


# ============================================================
# METRICS
# ============================================================

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


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("========================================")
print("       FINAL AASIST TEST RESULTS")
print("========================================")

print(f"Accuracy : {accuracy * 100:.2f}%")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall   : {recall * 100:.2f}%")
print(f"F1 Score : {f1 * 100:.2f}%")
print(f"ROC-AUC  : {auc:.4f}")

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
