# Phoenix AI — Next Training Run

## 1. Build the complete video manifest

```bash
python build_video_manifest.py
```

Expected sources:
- Celeb-DF-v2: Celeb-real + YouTube-real = authentic; Celeb-synthesis = tampered
- FakeAVCeleb: RealVideo-* = authentic; FakeVideo-* = tampered

The manifest is video-level. No extracted-frame dataset is used for the new model.

## 2. Train on the complete discovered video dataset

```bash
python train_video_temporal.py \
  --manifest backend/kaggle_data/video_manifest_all.jsonl \
  --frames 8 \
  --batch-size 2 \
  --epochs 8
```

The run keeps a video-disjoint validation and test split so frames from the same video cannot leak between train and evaluation.

## 3. Verify the checkpoint

```bash
ls -lh models_weights/temporal_video_evidence_best.pth
```

## 4. Start the backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The new backend uses the temporal video model for video uploads and AASIST for audio uploads.

## Label policy

```text
Video: 0 = authentic/original, 1 = tampered/fake
Audio AASIST: 0 = spoof/tampered, 1 = bonafide/authentic
```

The previous video inference code incorrectly assumed class 0 was tampered, and the previous audio inference code used AASIST class 1 as fake. Those paths have been corrected.
