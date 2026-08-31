import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import sys
import copy
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from ai_engine.models import VideoEvidenceAI, EfficientNetBackend, SwinTransformerBackend
from ai_engine.dataset_loader import KaggleDeepfakeDataset, train_transform, vit_transform

MODEL_PATHS = {
    "vit": "models_weights/vit_evidence_checkpoint.pth",
    "efficientnet": "models_weights/efficientnet_evidence_checkpoint.pth",
    "swin": "models_weights/swin_evidence_checkpoint.pth",
}

META_PATHS = {
    "vit": "models_weights/vit_evidence_meta.json",
    "efficientnet": "models_weights/efficientnet_evidence_meta.json",
    "swin": "models_weights/swin_evidence_meta.json",
}

def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

def build_dataloaders(data_directory, batch_size):
    base_dataset = KaggleDeepfakeDataset(data_directory, transform=None)
    if len(base_dataset) == 0:
        raise RuntimeError("Dataset empty. Check the training directory path.")

    print(f"[debug] total images found: {len(base_dataset)}")
    print(f"[debug] label distribution: label=0 -> {(len(base_dataset.labels) - sum(base_dataset.labels))}, label=1 -> {sum(base_dataset.labels)}")

    generator = torch.Generator().manual_seed(42)
    indices = torch.randperm(len(base_dataset), generator=generator).tolist()

    train_size = int(0.8 * len(base_dataset))
    train_indices = indices[:train_size]
    val_indices = indices[train_size:]

    train_dataset = KaggleDeepfakeDataset(data_directory, transform=train_transform)
    val_dataset = KaggleDeepfakeDataset(data_directory, transform=vit_transform)

    train_subset = Subset(train_dataset, train_indices)
    val_subset = Subset(val_dataset, val_indices)

    train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, val_loader

def save_metadata(model_name):
    os.makedirs("models_weights", exist_ok=True)
    meta = {
        "class_to_idx": {
            "fake": 0,
            "tampered": 0,
            "authentic": 1,
            "original": 1
        },
        "label_policy": "0=tampered/fake, 1=authentic/original"
    }
    with open(META_PATHS[model_name], "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def train_single_model(model_name, model, train_loader, val_loader, device, epochs, learning_rate, save_path):
    print(f"\n{'='*60}")
    print(f"TRAINING MODEL: {model_name.upper()}")
    print(f"{'='*60}")

    model = model.to(device)
    labels = train_loader.dataset.dataset.labels

    fake_count = labels.count(0)
    real_count = labels.count(1)

    class_weights = torch.tensor(
    [
        len(labels) / (2 * fake_count),
        len(labels) / (2 * real_count)
    ],
    dtype=torch.float32
    ).to(device)

    print(f"[debug] real={real_count} fake={fake_count}")
    print(f"[debug] class_weights={class_weights}")

    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=3)

    best_accuracy = 0.0
    best_weights = None

    for epoch in range(epochs):
        model.train()
        train_correct = 0
        train_total = 0
        epoch_start = time.time()

        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, preds = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (preds == labels).sum().item()

            if batch_idx % 50 == 0:
                print(
                    f"[{model_name}] Epoch {epoch+1}/{epochs} "
                    f"Batch {batch_idx}/{len(train_loader)} "
                    f"Loss={loss.item():.4f}"
                )

        train_accuracy = 100 * train_correct / max(train_total, 1)
        epoch_time = time.time() - epoch_start

        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (preds == labels).sum().item()

        val_accuracy = 100 * val_correct / max(val_total, 1)
        scheduler.step(val_accuracy)

        print(f"[{model_name}] Epoch [{epoch+1:02d}/{epochs}] | Train Acc: {train_accuracy:.2f}% | Val Acc: {val_accuracy:.2f}% | Time: {epoch_time:.1f}s")

        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            best_weights = copy.deepcopy(model.state_dict())
            print(f"Saved new best weights for {model_name} ({best_accuracy:.2f}%)")

    os.makedirs("models_weights", exist_ok=True)
    if best_weights is None:
        raise RuntimeError(f"No weights captured for {model_name}.")
    torch.save(best_weights, save_path)
    print(f"Saved: {save_path}")
    return best_accuracy

def train_all_models(data_directory, epochs=50, batch_size=32, learning_rate=1e-4, models_to_train=("vit", "efficientnet", "swin")):
    device = get_device()
    print(f"Using execution device: {device}")

    train_loader, val_loader = build_dataloaders(data_directory, batch_size)
    results = {}

    if "vit" in models_to_train:
        vit_model = VideoEvidenceAI()
        results["vit"] = train_single_model("vit", vit_model, train_loader, val_loader, device, epochs, learning_rate, MODEL_PATHS["vit"])
        save_metadata("vit")

    if "efficientnet" in models_to_train:
        eff_model = EfficientNetBackend()
        results["efficientnet"] = train_single_model("efficientnet", eff_model, train_loader, val_loader, device, epochs, learning_rate, MODEL_PATHS["efficientnet"])
        save_metadata("efficientnet")

    if "swin" in models_to_train:
        swin_model = SwinTransformerBackend()
        results["swin"] = train_single_model("swin", swin_model, train_loader, val_loader, device, epochs, learning_rate, MODEL_PATHS["swin"])
        save_metadata("swin")

    print(f"\n{'='*60}")
    print("TRAINING COMPLETE")
    print(f"{'='*60}")
    for name, acc in results.items():
        print(f"{name.upper():<15} Best Val Accuracy: {acc:.2f}%")

    return results

if __name__ == "__main__":
    train_all_models(
        data_directory="backend/kaggle_data/merged_train_balanced",
        epochs=15,
        batch_size=4,
        learning_rate=5e-5,
        models_to_train=("swin",)
    )