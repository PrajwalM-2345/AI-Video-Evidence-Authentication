import argparse
import json
import os
import random
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn

from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

from torch.utils.data import (
    Dataset,
    DataLoader,
    WeightedRandomSampler,
)

from torchvision import transforms

from backend.ai_engine.temporal_video_model import (
    TemporalVideoEvidenceAI,
)


VIDEO_EXTS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
}

LABELS = {
    "authentic": 0,
    "tampered": 1,
}


# ============================================================
# REPRODUCIBILITY
# ============================================================

def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ============================================================
# VIDEO LABELING
# ============================================================

def classify_video(path: Path):

    p = str(path).replace("\\", "/").lower()

    # Celeb-DF
    if "/celeb-real/" in p:
        return 0

    if "/youtube-real/" in p:
        return 0

    if "/celeb-synthesis/" in p:
        return 1

    # FakeAVCeleb
    if "fakevideo" in p:
        return 1

    if "realvideo" in p:
        return 0

    return None


def discover(root: Path):

    records = []

    for p in root.rglob("*"):

        if not p.is_file():
            continue

        if p.suffix.lower() not in VIDEO_EXTS:
            continue

        label = classify_video(p)

        if label is not None:

            records.append(
                {
                    "path": str(p.resolve()),
                    "label": label,
                }
            )

    return records


# ============================================================
# MANIFEST
# ============================================================

def load_records(manifest, split):

    records = []

    with open(manifest) as f:

        for line in f:

            r = json.loads(line)

            if r.get("split") == split:
                records.append(r)

    return records


# ============================================================
# DATASET
# ============================================================

class VideoSequenceDataset(Dataset):

    def __init__(
        self,
        records,
        frames=4,
        train=False,
    ):

        self.records = records
        self.frames = frames
        self.train = train

        if train:

            self.transform = transforms.Compose(
                [
                    transforms.ToPILImage(),
                    transforms.Resize((256, 256)),
                    transforms.RandomResizedCrop(
                        224,
                        scale=(0.90, 1.0),
                    ),
                    transforms.RandomHorizontalFlip(
                        p=0.5
                    ),
                    transforms.ColorJitter(
                        brightness=0.05,
                        contrast=0.05,
                        saturation=0.05,
                        hue=0.01,
                    ),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        [0.485, 0.456, 0.406],
                        [0.229, 0.224, 0.225],
                    ),
                ]
            )

        else:

            self.transform = transforms.Compose(
                [
                    transforms.ToPILImage(),
                    transforms.Resize((256, 256)),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        [0.485, 0.456, 0.406],
                        [0.229, 0.224, 0.225],
                    ),
                ]
            )

    def __len__(self):
        return len(self.records)

    def read_video(self, path):

        cap = cv2.VideoCapture(path)

        if not cap.isOpened():
            raise RuntimeError(
                f"Cannot open video: {path}"
            )

        total = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        if total <= 0:
            cap.release()

            raise RuntimeError(
                f"Invalid video: {path}"
            )

        positions = np.linspace(
            0,
            total - 1,
            self.frames,
        ).astype(int)

        frames = []

        last_frame = None

        for position in positions:

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(position),
            )

            ok, frame = cap.read()

            if not ok or frame is None:

                if last_frame is None:

                    frame = np.zeros(
                        (224, 224, 3),
                        dtype=np.uint8,
                    )

                else:

                    frame = last_frame

            else:

                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

            last_frame = frame
            frames.append(frame)

        cap.release()

        return frames

    def __getitem__(self, idx):

        record = self.records[idx]

        try:

            frames = self.read_video(
                record["path"]
            )

            tensor = torch.stack(
                [
                    self.transform(frame)
                    for frame in frames
                ]
            )

            label = torch.tensor(
                record["label"],
                dtype=torch.long,
            )

            return (
                tensor,
                label,
                record["path"],
            )

        except Exception as e:

            print(
                f"Warning: {e}"
            )

            # Return a valid fallback instead of
            # recursively selecting another label.
            tensor = torch.zeros(
                self.frames,
                3,
                224,
                224,
                dtype=torch.float32,
            )

            label = torch.tensor(
                record["label"],
                dtype=torch.long,
            )

            return (
                tensor,
                label,
                record["path"],
            )


# ============================================================
# DEVICE
# ============================================================

def get_device():

    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    model,
    loader,
    criterion,
    device,
):

    model.eval()

    losses = []
    ys = []
    probabilities = []

    with torch.no_grad():

        for x, y, _ in loader:

            x = x.to(device)
            y = y.to(device)

            logits, attention = model(x)

            loss = criterion(
                logits,
                y,
            )

            losses.append(
                loss.item()
            )

            prob = torch.softmax(
                logits,
                dim=1,
            )[:, 1]

            ys.extend(
                y.cpu().numpy().tolist()
            )

            probabilities.extend(
                prob.cpu().numpy().tolist()
            )

    predictions = [
        int(p >= 0.5)
        for p in probabilities
    ]

    accuracy = accuracy_score(
        ys,
        predictions,
    )

    auc = roc_auc_score(
        ys,
        probabilities,
    )

    return (
        float(np.mean(losses)),
        float(accuracy),
        float(auc),
        ys,
        predictions,
        probabilities,
    )


# ============================================================
# TRAINING
# ============================================================

def main(args):

    seed_everything(args.seed)

    device = get_device()

    print()
    print("=" * 60)
    print("PHOENIX TEMPORAL VIDEO V3")
    print("=" * 60)
    print("Device:", device)

    manifest = Path(args.manifest)

    if not manifest.exists():

        raise FileNotFoundError(
            f"Manifest not found:\n{manifest}"
        )

    train_records = load_records(
        manifest,
        "train",
    )

    val_records = load_records(
        manifest,
        "val",
    )

    test_records = load_records(
        manifest,
        "test",
    )

    print()
    print("DATASET")

    for name, records in [
        ("TRAIN", train_records),
        ("VAL", val_records),
        ("TEST", test_records),
    ]:

        n0 = sum(
            r["label"] == 0
            for r in records
        )

        n1 = sum(
            r["label"] == 1
            for r in records
        )

        print(
            f"{name}: "
            f"{len(records)} "
            f"(authentic={n0}, tampered={n1})"
        )

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    train_ds = VideoSequenceDataset(
        train_records,
        args.frames,
        train=True,
    )

    val_ds = VideoSequenceDataset(
        val_records,
        args.frames,
        train=False,
    )

    test_ds = VideoSequenceDataset(
        test_records,
        args.frames,
        train=False,
    )

    # --------------------------------------------------------
    # BALANCED SAMPLING
    # --------------------------------------------------------

    labels = np.array(
        [
            r["label"]
            for r in train_records
        ]
    )

    class_counts = np.bincount(
        labels,
        minlength=2,
    )

    sample_weights = np.array(
        [
            1.0 / class_counts[label]
            for label in labels
        ],
        dtype=np.float64,
    )

    sampler = WeightedRandomSampler(
        weights=torch.as_tensor(
            sample_weights,
            dtype=torch.double,
        ),
        num_samples=len(train_records),
        replacement=True,
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        sampler=sampler,
        num_workers=0,
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    test_loader = DataLoader(
        test_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model = TemporalVideoEvidenceAI(
        pretrained=True,
        feature_dim=256,
        nhead=4,
        layers=2,
        dropout=0.20,
    ).to(device)

    # Start with the backbone frozen.
    model.freeze_backbone()

    # --------------------------------------------------------
    # LOSS
    # --------------------------------------------------------

    # Balanced dataset + balanced sampler.
    # No auxiliary frame loss.
    criterion = nn.CrossEntropyLoss(
        label_smoothing=0.02
    )

    # --------------------------------------------------------
    # OPTIMIZER
    # --------------------------------------------------------

    head_params = []

    for name, param in model.named_parameters():

        if not param.requires_grad:
            continue

        head_params.append(param)

    optimizer = torch.optim.AdamW(
        head_params,
        lr=args.lr,
        weight_decay=1e-4,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=args.epochs,
        eta_min=args.lr * 0.1,
    )

    # --------------------------------------------------------
    # CHECKPOINT
    # --------------------------------------------------------

    best_auc = -1.0

    output = Path(args.output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("MODEL")
    print(
        "Total parameters:",
        sum(
            p.numel()
            for p in model.parameters()
        ),
    )

    print(
        "Trainable parameters:",
        sum(
            p.numel()
            for p in model.parameters()
            if p.requires_grad
        ),
    )

    print()
    print("=" * 60)
    print("START TRAINING")
    print("=" * 60)

    # --------------------------------------------------------
    # EPOCHS
    # --------------------------------------------------------

    for epoch in range(args.epochs):

        epoch_start = time.time()

        # Unfreeze late EfficientNet blocks after
        # the temporal head has learned a useful representation.
        if epoch == args.unfreeze_epoch:

            model.unfreeze_last_backbone_blocks(
                args.unfreeze_blocks
            )

            optimizer = torch.optim.AdamW(
                [
                    {
                        "params": [
                            p
                            for p in model.parameters()
                            if p.requires_grad
                        ],
                        "lr": args.finetune_lr,
                    }
                ],
                weight_decay=1e-4,
            )

            print()
            print(
                "Unfroze last",
                args.unfreeze_blocks,
                "EfficientNet blocks",
            )

        model.train()

        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (x, y, _) in enumerate(
            train_loader
        ):

            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad(
                set_to_none=True
            )

            logits, attention = model(x)

            loss = criterion(
                logits,
                y,
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=2.0,
            )

            optimizer.step()

            running_loss += loss.item()

            correct += (
                logits.argmax(1) == y
            ).sum().item()

            total += y.numel()

            if (
                batch_idx == 0
                or batch_idx % args.print_every == 0
            ):

                print(
                    f"epoch={epoch+1}/{args.epochs} "
                    f"batch={batch_idx}/{len(train_loader)} "
                    f"loss={loss.item():.4f}"
                )

        scheduler.step()

        train_loss = (
            running_loss
            / len(train_loader)
        )

        train_acc = (
            correct
            / max(1, total)
        )

        val_loss, val_acc, val_auc, _, _, _ = evaluate(
            model,
            val_loader,
            criterion,
            device,
        )

        elapsed = (
            time.time()
            - epoch_start
        )

        print()
        print(
            f"Epoch {epoch+1}/{args.epochs}"
        )

        print(
            f"Train Loss : {train_loss:.4f}"
        )

        print(
            f"Train Acc  : {100*train_acc:.2f}%"
        )

        print(
            f"Val Loss   : {val_loss:.4f}"
        )

        print(
            f"Val Acc    : {100*val_acc:.2f}%"
        )

        print(
            f"Val AUC    : {val_auc:.5f}"
        )

        print(
            f"Time       : {elapsed:.1f}s"
        )

        # ----------------------------------------------------
        # BEST CHECKPOINT
        # ----------------------------------------------------

        if val_auc > best_auc:

            best_auc = val_auc

            torch.save(
                {
                    "model": model.state_dict(),
                    "epoch": epoch + 1,
                    "val_auc": val_auc,
                    "frames": args.frames,
                    "label_policy":
                        "0=authentic/original,"
                        "1=tampered/fake",
                },
                output,
            )

            print(
                "✓ Saved best:",
                output,
            )

    # ========================================================
    # FINAL TEST
    # ========================================================

    print()
    print("=" * 60)
    print("LOADING BEST CHECKPOINT")
    print("=" * 60)

    checkpoint = torch.load(
        output,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model"]
    )

    test_loss, test_acc, test_auc, y, pred, prob = evaluate(
        model,
        test_loader,
        criterion,
        device,
    )

    print()
    print("=" * 60)
    print("FINAL VIDEO-DISJOINT TEST")
    print("=" * 60)

    print(
        "Best validation ROC-AUC:",
        round(
            checkpoint["val_auc"],
            5,
        ),
    )

    print(
        "Accuracy:",
        round(
            100 * test_acc,
            2,
        ),
        "%",
    )

    print(
        "ROC-AUC:",
        round(
            test_auc,
            5,
        ),
    )

    print()
    print("CONFUSION MATRIX")

    print(
        confusion_matrix(
            y,
            pred,
        )
    )

    print()
    print("CLASSIFICATION REPORT")

    print(
        classification_report(
            y,
            pred,
            target_names=[
                "Authentic",
                "Tampered",
            ],
            digits=4,
        )
    )

    print()
    print(
        "Checkpoint:",
        output,
    )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        default=
        "backend/kaggle_data/video_manifest_balanced.jsonl",
    )

    parser.add_argument(
        "--frames",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--unfreeze-epoch",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--unfreeze-blocks",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=3e-4,
    )

    parser.add_argument(
        "--finetune-lr",
        type=float,
        default=2e-5,
    )

    parser.add_argument(
        "--print-every",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--output",
        default=
        "models_weights/temporal_video_evidence_v3_best.pth",
    )

    args = parser.parse_args()

    main(args)
