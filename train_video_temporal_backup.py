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
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms

from backend.ai_engine.temporal_video_model import TemporalVideoEvidenceAI

VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
LABELS = {"authentic": 0, "tampered": 1}


def classify_video(path: Path):
    p = str(path).replace("\\", "/").lower()
    # Celeb-DF v2
    if "/celeb-real/" in p or "/youtube-real/" in p:
        return 0
    if "/celeb-synthesis/" in p:
        return 1
    # FakeAVCeleb naming convention: FakeVideo-* vs RealVideo-*.
    if "fakevideo" in p or "/fake/" in p or "synthesis" in p or "deepfake" in p:
        return 1
    if "realvideo" in p or "/real/" in p or "original" in p or "authentic" in p:
        return 0
    return None


def discover(root: Path):
    records = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
            label = classify_video(p)
            if label is not None:
                records.append({"path": str(p.resolve()), "label": label})
    return records


def build_manifest(args):
    roots = [Path(args.celebdf), Path(args.fakeav)]
    records = []
    for root in roots:
        if root.exists():
            found = discover(root)
            print(f"{root}: {len(found)} labeled videos")
            records.extend(found)
        else:
            print(f"Skipping missing dataset: {root}")

    # Remove duplicates by absolute path.
    uniq = {r["path"]: r for r in records}
    records = list(uniq.values())

    # Video-level stratified split. No frames from the same video can leak across sets.
    rng = random.Random(args.seed)
    authentic = [r for r in records if r["label"] == 0]
    tampered = [r for r in records if r["label"] == 1]
    rng.shuffle(authentic)
    rng.shuffle(tampered)

    def split(items):
        n = len(items)
        n_test = max(1, int(n * args.test_ratio))
        n_val = max(1, int(n * args.val_ratio))
        return items[n_test + n_val:], items[n_test:n_test + n_val], items[:n_test]

    tr0, va0, te0 = split(authentic)
    tr1, va1, te1 = split(tampered)
    train = tr0 + tr1
    val = va0 + va1
    test = te0 + te1
    rng.shuffle(train); rng.shuffle(val); rng.shuffle(test)

    out = Path(args.manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for split_name, items in (("train", train), ("val", val), ("test", test)):
            for r in items:
                f.write(json.dumps({"split": split_name, **r}) + "\n")

    print(f"Manifest: {out}")
    for name, items in (("train", train), ("val", val), ("test", test)):
        print(f"{name}: total={len(items)} authentic={sum(x['label']==0 for x in items)} tampered={sum(x['label']==1 for x in items)}")
    return out


class VideoSequenceDataset(Dataset):
    def __init__(self, records, frames=8, train=False):
        self.records = records
        self.frames = frames
        self.train = train
        self.base = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((256, 256)),
            transforms.RandomResizedCrop(224, scale=(0.82, 1.0)) if train else transforms.CenterCrop(224),
            transforms.RandomHorizontalFlip(0.5) if train else transforms.Lambda(lambda x: x),
            transforms.ColorJitter(0.08, 0.08, 0.08, 0.02) if train else transforms.Lambda(lambda x: x),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    def __len__(self):
        return len(self.records)

    def _read(self, path):
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
        if total <= 0:
            cap.release()
            raise RuntimeError(f"Cannot read video: {path}")

        positions = np.linspace(0, max(0, total - 1), self.frames).astype(int)
        imgs = []
        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(pos))
            ok, frame = cap.read()
            if not ok or frame is None:
                if imgs:
                    frame = imgs[-1]
                else:
                    frame = np.zeros((224, 224, 3), dtype=np.uint8)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgs.append(frame)
        cap.release()
        return imgs, fps, total

    def __getitem__(self, idx):
        rec = self.records[idx]
        try:
            imgs, fps, total = self._read(rec["path"])
            tensor = torch.stack([self.base(x) for x in imgs])
            return tensor, torch.tensor(rec["label"], dtype=torch.long), rec["path"]
        except Exception as e:
            # Retry a different video instead of killing a long run on one corrupt file.
            if idx + 1 < len(self.records):
                return self.__getitem__((idx + 1) % len(self.records))
            raise e


def load_records(manifest, split):
    records = []
    with open(manifest) as f:
        for line in f:
            r = json.loads(line)
            if r["split"] == split:
                records.append(r)
    return records


def device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def evaluate(model, loader, criterion, dev):
    model.eval(); losses=[]; ys=[]; ps=[]
    with torch.no_grad():
        for x, y, _ in loader:
            x, y = x.to(dev), y.to(dev)
            logits, frame_logits = model(x)
            loss = criterion(logits, y)
            losses.append(loss.item())
            ys.extend(y.cpu().numpy().tolist())
            ps.extend(torch.softmax(logits, 1)[:, 1].cpu().numpy().tolist())
    pred = [int(p >= 0.5) for p in ps]
    acc = accuracy_score(ys, pred)
    auc = roc_auc_score(ys, ps) if len(set(ys)) == 2 else float("nan")
    return float(np.mean(losses)), acc, auc, ys, pred, ps


def main(args):
    if args.manifest_missing or not Path(args.manifest).exists():
        build_manifest(args)
    train_records = load_records(args.manifest, "train")
    val_records = load_records(args.manifest, "val")
    test_records = load_records(args.manifest, "test")

    dev = device(); print("Device:", dev)
    print("Video counts:", len(train_records), len(val_records), len(test_records))

    train_ds = VideoSequenceDataset(train_records, args.frames, True)
    val_ds = VideoSequenceDataset(val_records, args.frames, False)
    test_ds = VideoSequenceDataset(test_records, args.frames, False)
    # Balanced training sampler: approximately equal authentic/tampered
    # sampling while preserving the original video-level split.
    train_labels = [r["label"] for r in train_records]

    class_counts = np.bincount(train_labels, minlength=2)

    sample_weights = np.array([
        1.0 / class_counts[label]
        for label in train_labels
    ], dtype=np.float64)

    sampler = WeightedRandomSampler(
        weights=torch.as_tensor(sample_weights, dtype=torch.double),
        num_samples=len(train_records),
        replacement=True
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        sampler=sampler,
        num_workers=0
    )
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = TemporalVideoEvidenceAI(pretrained=True).to(dev)
    model.freeze_backbone()

    # Balanced loss computed from the entire training-video population.
    n0 = sum(r["label"] == 0 for r in train_records)
    n1 = sum(r["label"] == 1 for r in train_records)
    weights = torch.tensor([len(train_records)/(2*n0), len(train_records)/(2*n1)], dtype=torch.float32, device=dev)
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.05)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr, weight_decay=1e-4)
    best_auc = -1
    best_path = Path(args.output)
    best_path.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        t0=time.time(); model.train(); total=0; correct=0; losses=[]
        if epoch == args.unfreeze_epoch:
            model.unfreeze_last_backbone_blocks(2)
            optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.finetune_lr, weight_decay=1e-4)
            print("Unfroze last EfficientNet blocks for fine-tuning")
        for bi,(x,y,_) in enumerate(train_loader):
            x,y=x.to(dev),y.to(dev); optimizer.zero_grad(set_to_none=True)
            vlogits, flogits = model(x)
            loss = criterion(vlogits,y) + args.frame_loss_weight * criterion(flogits.reshape(-1,2), y[:,None].expand(-1, flogits.shape[1]).reshape(-1))
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0); optimizer.step()
            losses.append(loss.item()); correct += (vlogits.argmax(1)==y).sum().item(); total += y.numel()
            if bi % 100 == 0: print(f"epoch={epoch+1} batch={bi}/{len(train_loader)} loss={loss.item():.4f}")
        val_loss,val_acc,val_auc,_,_,_=evaluate(model,val_loader,criterion,dev)
        print(f"Epoch {epoch+1}/{args.epochs} train_loss={np.mean(losses):.4f} train_acc={100*correct/max(1,total):.2f}% val_acc={100*val_acc:.2f}% val_auc={val_auc:.4f} time={time.time()-t0:.1f}s")
        if val_auc > best_auc:
            best_auc=val_auc
            torch.save({"model":model.state_dict(),"epoch":epoch+1,"val_auc":val_auc,"label_policy":"0=authentic/original,1=tampered/fake","frames":args.frames},best_path)
            print("Saved best:",best_path)

    ckpt=torch.load(best_path,map_location=dev); model.load_state_dict(ckpt["model"])
    test_loss,test_acc,test_auc,y,pred,prob=evaluate(model,test_loader,criterion,dev)
    print("\nFINAL VIDEO-DISJOINT TEST")
    print("Accuracy:",round(100*test_acc,2),"%")
    print("ROC-AUC:",round(test_auc,5))
    print(confusion_matrix(y,pred))
    print(classification_report(y,pred,target_names=["Authentic","Tampered"]))


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--celebdf",default="backend/kaggle_data/Celeb-DF-v2")
    p.add_argument("--fakeav",default="backend/kaggle_data/FakeAVCeleb_v1.2")
    p.add_argument("--manifest",default="backend/kaggle_data/video_manifest.jsonl")
    p.add_argument("--manifest-missing",action="store_true")
    p.add_argument("--frames",type=int,default=8)
    p.add_argument("--batch-size",type=int,default=2)
    p.add_argument("--epochs",type=int,default=8)
    p.add_argument("--unfreeze-epoch",type=int,default=3)
    p.add_argument("--lr",type=float,default=2e-4)
    p.add_argument("--finetune-lr",type=float,default=2e-5)
    p.add_argument("--frame-loss-weight",type=float,default=0.25)
    p.add_argument("--val-ratio",type=float,default=0.10)
    p.add_argument("--test-ratio",type=float,default=0.10)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--output",default="models_weights/temporal_video_evidence_best.pth")
    main(p.parse_args())
