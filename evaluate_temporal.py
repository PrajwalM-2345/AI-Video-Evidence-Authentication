import json
from pathlib import Path

import cv2
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from backend.ai_engine.temporal_video_model import TemporalVideoEvidenceAI


MANIFEST = "backend/kaggle_data/video_manifest_balanced_split.jsonl"
CHECKPOINT = "backend/models_weights/temporal_balanced_16f.pth"

FRAMES = 16
BATCH_SIZE = 2


class VideoSequenceDataset(Dataset):

    def __init__(self, records):
        self.records = records

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            ),
        ])

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):

        record = self.records[idx]
        path = record["path"]
        label = record["label"]

        cap = cv2.VideoCapture(path)

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total <= 0:
            cap.release()
            raise RuntimeError(f"Cannot read video: {path}")

        positions = np.linspace(
            0,
            max(0, total - 1),
            FRAMES
        ).astype(int)

        frames = []

        for pos in positions:

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(pos)
            )

            ok, frame = cap.read()

            if not ok or frame is None:

                if frames:
                    frame = frames[-1]

                else:
                    frame = np.zeros(
                        (224, 224, 3),
                        dtype=np.uint8
                    )

            else:

                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

            frames.append(frame)

        cap.release()

        tensor = torch.stack([
            self.transform(frame)
            for frame in frames
        ])

        return (
            tensor,
            torch.tensor(label, dtype=torch.long)
        )


def get_device():

    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def load_test_records():

    records = []

    with open(MANIFEST, "r") as f:

        for line in f:

            r = json.loads(line)

            if r["split"] == "test":
                records.append(r)

    return records


def main():

    device = get_device()

    print("\n========================================")
    print("TEMPORAL MODEL TEST EVALUATION")
    print("========================================")

    print("Device:", device)

    records = load_test_records()

    authentic = sum(
        r["label"] == 0
        for r in records
    )

    tampered = sum(
        r["label"] == 1
        for r in records
    )

    print("Test videos:", len(records))
    print("Authentic:", authentic)
    print("Tampered:", tampered)

    dataset = VideoSequenceDataset(records)

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    print("\nLoading model...")

    model = TemporalVideoEvidenceAI(
        pretrained=False
    ).to(device)

    checkpoint = torch.load(
        CHECKPOINT,
        map_location=device
    )

    model.load_state_dict(
        checkpoint["model"]
    )

    model.eval()

    print("Checkpoint epoch:",
          checkpoint.get("epoch"))

    print("Validation AUC:",
          checkpoint.get("val_auc"))

    y_true = []
    y_pred = []
    y_prob = []

    print("\nRunning test evaluation...")

    with torch.no_grad():

        for batch_idx, (x, y) in enumerate(loader):

            x = x.to(device)
            y = y.to(device)

            logits, frame_logits = model(x)

            probabilities = torch.softmax(
                logits,
                dim=1
            )[:, 1]

            predictions = (
                probabilities >= 0.5
            ).long()

            y_true.extend(
                y.cpu().numpy().tolist()
            )

            y_pred.extend(
                predictions.cpu().numpy().tolist()
            )

            y_prob.extend(
                probabilities.cpu().numpy().tolist()
            )

            if batch_idx % 50 == 0:

                print(
                    f"Processed "
                    f"{batch_idx}/{len(loader)}"
                )

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

    print("\n")
    print("========================================")
    print("FINAL TEMPORAL TEST RESULTS")
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
                "Authentic",
                "Tampered"
            ],
            digits=4,
            zero_division=0
        )
    )

    print("========================================")


if __name__ == "__main__":
    main()
