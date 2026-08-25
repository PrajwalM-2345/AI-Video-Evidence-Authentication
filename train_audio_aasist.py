import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
# Avoid CPU oversubscription hangs on some platforms (safe no-op if unused)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import sys
import json
import time
import signal
import argparse
from pathlib import Path

import numpy as np
import soundfile as sf

import torch
import torch.nn as nn
import torch.optim as optim

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

sys.path.append("backend/aasist")

from models.AASIST import Model


# ============================================================
# PATHS
# ============================================================

REAL_DIR = Path("backend/kaggle_data/audio_dataset/real")
FAKE_DIR = Path("backend/kaggle_data/audio_dataset/fake")

CONFIG_PATH = "backend/aasist/config/AASIST.conf"

PRETRAINED_MODEL = "backend/aasist/models/weights/AASIST.pth"

SAVE_MODEL = "models_weights/aasist_finetuned.pth"

SAVE_META = "models_weights/aasist_finetuned_meta.json"


# ============================================================
# TRAIN CONFIG
# ============================================================

EPOCHS = 15
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
MAX_TRAIN_SECONDS_PER_EPOCH = None  # set an int to hard-cap epoch time; None = unlimited


# ============================================================
# DEVICE
# ============================================================

def get_device():
    """
    NOTE: MPS is often the actual cause of a 'hang' — some ops silently
    fall back to CPU or stall on certain Mac configs with large batches
    or specific conv kernel shapes. If training seems frozen (no CPU
    spin, no error) for more than ~2 minutes on the *first* batch,
    rerun with --device cpu to isolate whether MPS is the culprit.
    """
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


# ============================================================
# DATASET
# ============================================================

class AudioDataset(Dataset):

    def __init__(self, files, labels):
        self.files = files
        self.labels = labels
        self.cut = 64600

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        try:
            wav, sr = sf.read(str(self.files[idx]))
        except Exception as e:
            # A single corrupt/unreadable file must not hang or crash
            # the whole run — return silence and let training continue.
            print(f"⚠ Could not read {self.files[idx]}: {e} — using silence")
            wav = np.zeros(self.cut, dtype=np.float32)
            sr = 16000

        if wav.ndim > 1:
            wav = np.mean(wav, axis=1)

        if len(wav) == 0:
            wav = np.zeros(self.cut, dtype=np.float32)

        if len(wav) >= self.cut:
            wav = wav[:self.cut]
        else:
            repeat = self.cut // len(wav) + 1
            wav = np.tile(wav, repeat)[:self.cut]

        wav = torch.tensor(wav, dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.long)

        return wav, label


# ============================================================
# DATALOADER
# ============================================================

def build_dataloaders(batch_size=BATCH_SIZE, num_workers=0, limit=None):

    if not REAL_DIR.exists() or not FAKE_DIR.exists():
        raise FileNotFoundError(
            f"Dataset directories missing.\n"
            f"  REAL_DIR: {REAL_DIR} (exists={REAL_DIR.exists()})\n"
            f"  FAKE_DIR: {FAKE_DIR} (exists={FAKE_DIR.exists()})\n"
            f"Fix the paths before running — this is a common silent-hang cause "
            f"if glob() returns nothing and later steps wait on empty tensors."
        )

    real_files = sorted(REAL_DIR.glob("*.wav"))
    fake_files = sorted(FAKE_DIR.glob("*.wav"))

    if limit:
        real_files = real_files[:limit]
        fake_files = fake_files[:limit]

    if len(real_files) == 0 or len(fake_files) == 0:
        raise ValueError(
            f"One or both classes are empty (real={len(real_files)}, "
            f"fake={len(fake_files)}). Check your dataset paths and file extensions."
        )

    files = real_files + fake_files
    labels = [1] * len(real_files) + [0] * len(fake_files)

    print("=" * 60)
    print("AUDIO DATASET SUMMARY")
    print("=" * 60)
    print("Real Files :", len(real_files))
    print("Fake Files :", len(fake_files))
    print("Total Files:", len(files))
    print("=" * 60)

    train_files, val_files, train_labels, val_labels = train_test_split(
        files, labels,
        test_size=0.20,
        random_state=42,
        stratify=labels
    )

    train_dataset = AudioDataset(train_files, train_labels)
    val_dataset = AudioDataset(val_files, val_labels)

    # num_workers=0 runs data loading on the main process/thread.
    # On macOS this is usually the *safe* choice (multiprocessing +
    # MPS + fork can deadlock). Keep 0 unless you've confirmed >0
    # works on your platform. persistent_workers/pin_memory are only
    # meaningful when num_workers > 0, so they're conditionally set.
    loader_kwargs = dict(
        batch_size=batch_size,
        num_workers=num_workers,
    )
    if num_workers > 0:
        loader_kwargs["persistent_workers"] = True
        loader_kwargs["prefetch_factor"] = 2

    train_loader = DataLoader(train_dataset, shuffle=True, **loader_kwargs)
    val_loader = DataLoader(val_dataset, shuffle=False, **loader_kwargs)

    print("Training batches  :", len(train_loader))
    print("Validation batches:", len(val_loader))

    return train_loader, val_loader


# ============================================================
# SAVE LABEL METADATA
# ============================================================

def save_metadata():
    os.makedirs("models_weights", exist_ok=True)
    meta = {
        "class_to_idx": {
            "fake": 0,
            "tampered": 0,
            "real": 1,
            "authentic": 1
        },
        "label_policy": "0=fake, 1=real"
    }
    with open(SAVE_META, "w") as f:
        json.dump(meta, f, indent=2)


# ============================================================
# LOAD MODEL
# ============================================================

def build_model(device):
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    if not os.path.exists(PRETRAINED_MODEL):
        raise FileNotFoundError(f"Pretrained weights not found: {PRETRAINED_MODEL}")

    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)

    model = Model(cfg["model_config"]).to(device)

    print("\nLoading pretrained AASIST weights...")

    state = torch.load(PRETRAINED_MODEL, map_location=device)
    model.load_state_dict(state)

    print("✓ Pretrained weights loaded")

    return model


# ============================================================
# TRAIN SETUP
# ============================================================

def build_training_objects(model):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=5e-6)
    return criterion, optimizer, scheduler


# ============================================================
# CHECKPOINT HELPERS
# ============================================================

def save_checkpoint(model, optimizer, scheduler, epoch, best_acc):
    os.makedirs("models_weights", exist_ok=True)
    tmp_path = SAVE_MODEL + ".tmp"
    torch.save(
        {
            "epoch": epoch,
            "best_acc": best_acc,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict()
        },
        tmp_path
    )
    # Atomic replace — prevents a corrupt checkpoint if the process
    # is killed mid-write (a common cause of the *next* run hanging
    # while loading a half-written .pth file).
    os.replace(tmp_path, SAVE_MODEL)


def load_checkpoint(model, optimizer, scheduler, device):
    if not os.path.exists(SAVE_MODEL):
        return 0, 0.0

    print("\nResuming from checkpoint...")
    try:
        checkpoint = torch.load(SAVE_MODEL, map_location=device)
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        scheduler.load_state_dict(checkpoint["scheduler"])
        epoch = checkpoint["epoch"]
        best_acc = checkpoint["best_acc"]
        print(f"✓ Resumed from epoch {epoch} (Best Val Acc={best_acc:.2f}%)")
        return epoch, best_acc
    except Exception as e:
        print(f"⚠ Could not load checkpoint ({e}) — starting fresh")
        return 0, 0.0


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(model, loader, criterion, optimizer, device, epoch):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    epoch_start = time.time()
    n_batches = len(loader)

    for batch_idx, (audio, labels) in enumerate(loader):
        batch_start = time.time()

        audio = audio.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        _, outputs = model(audio)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        predictions = outputs.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

        batch_time = time.time() - batch_start

        # Print EVERY batch's timing at least once so a stall is visible
        # immediately instead of silently waiting up to 50 batches.
        if batch_idx == 0 or batch_idx % 10 == 0:
            print(
                f"[Epoch {epoch+1}/{EPOCHS}] "
                f"Batch {batch_idx}/{n_batches} "
                f"Loss={loss.item():.4f} "
                f"({batch_time:.2f}s/batch)"
            )

        if MAX_TRAIN_SECONDS_PER_EPOCH and (time.time() - epoch_start) > MAX_TRAIN_SECONDS_PER_EPOCH:
            print(f"⚠ Epoch time cap reached ({MAX_TRAIN_SECONDS_PER_EPOCH}s) — ending epoch early")
            break

    avg_loss = running_loss / max(1, batch_idx + 1)
    train_acc = 100.0 * correct / max(1, total)
    elapsed = time.time() - epoch_start

    return avg_loss, train_acc, elapsed


# ============================================================
# VALIDATION
# ============================================================

def validate(model, loader, criterion, device):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for audio, labels in loader:
            audio = audio.to(device)
            labels = labels.to(device)

            _, outputs = model(audio)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    avg_loss = running_loss / len(loader)
    accuracy = 100.0 * correct / total

    return avg_loss, accuracy


# ============================================================
# TRAINING PIPELINE
# ============================================================

def train_audio(args):
    device = torch.device(args.device) if args.device else get_device()
    print(f"\nUsing device: {device}")

    global EPOCHS
    if args.epochs:
        EPOCHS = args.epochs

    train_loader, val_loader = build_dataloaders(
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        limit=args.limit
    )

    model = build_model(device)
    criterion, optimizer, scheduler = build_training_objects(model)

    start_epoch, best_acc = load_checkpoint(model, optimizer, scheduler, device)

    print("\n" + "=" * 60)
    print("STARTING AASIST TRAINING")
    print("=" * 60)

    for epoch in range(start_epoch, EPOCHS):

        train_loss, train_acc, elapsed = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )

        val_loss, val_acc = validate(model, val_loader, criterion, device)

        scheduler.step()

        print(
            f"\nEpoch [{epoch+1}/{EPOCHS}]"
            f"\nTrain Loss : {train_loss:.4f}"
            f"\nTrain Acc  : {train_acc:.2f}%"
            f"\nVal Loss   : {val_loss:.4f}"
            f"\nVal Acc    : {val_acc:.2f}%"
            f"\nTime       : {elapsed:.1f}s"
        )

        if val_acc > best_acc:
            best_acc = val_acc
            save_checkpoint(model, optimizer, scheduler, epoch + 1, best_acc)
            print(f"\n★ Saved Best Model ({best_acc:.2f}%)")

    save_metadata()

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Best Validation Accuracy : {best_acc:.2f}%")
    print(f"Checkpoint Saved         : {SAVE_MODEL}")
    print(f"Metadata Saved           : {SAVE_META}")


# ============================================================
# MAIN
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(description="AASIST fine-tuning")
    p.add_argument("--device", type=str, default=None,
                    help="Force device: cpu | mps | cuda. Default: auto-detect. "
                         "Use --device cpu first to rule out an MPS hang.")
    p.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--num-workers", type=int, default=0,
                    help="DataLoader workers. Keep 0 on macOS unless tested.")
    p.add_argument("--limit", type=int, default=None,
                    help="Cap files per class — use a small number (e.g. 20) "
                         "for a fast smoke test to confirm the pipeline runs "
                         "end-to-end before committing to a full run.")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    def handle_sigint(sig, frame):
        print("\n\n⚠ Interrupted by user (Ctrl+C) — exiting cleanly.")
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        train_audio(args)
    except KeyboardInterrupt:
        print("\n⚠ Training interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        raise