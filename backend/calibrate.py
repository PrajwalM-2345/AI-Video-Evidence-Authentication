"""
Phoenix Calibration Diagnostic
--------------------------------
Run this BEFORE touching thresholds in run_forensic_pipeline.
It answers two questions definitively:
  1. Is FAKE_CLASS_INDEX = 1 correct, or is it inverted?
  2. What SENSITIVITY_THRESHOLD actually separates your real/fake videos?

Usage:
    python calibrate.py --real ./sample_videos/real --fake ./sample_videos/fake

Folder structure expected:
    sample_videos/real/*.mp4   (known authentic videos)
    sample_videos/fake/*.mp4   (known tampered/deepfake videos)

You need at least 3-5 videos in each folder. Even 3 is enough to catch
an inverted class index -- it will be obvious (100% wrong every time).
"""

import argparse
import os
import sys
import cv2
import torch
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.models import VideoEvidenceAI
from ai_engine.dataset_loader import vit_transform
from ai_engine.face_analysis import ForensicFaceAnalyzer


def load_model():
    model = VideoEvidenceAI()
    weights_path = "models_weights/vit_evidence_checkpoint.pth"
    if os.path.exists(weights_path):
        try:
            model.load_state_dict(torch.load(weights_path, map_location="cpu"), strict=True)
        except Exception as e:
            print(f"Strict load failed ({e}), trying non-strict...")
            model.load_state_dict(torch.load(weights_path, map_location="cpu"), strict=False)
    else:
        print(f"WARNING: weights not found at {weights_path}. Using randomly initialized model -- results will be meaningless.")
    model.eval()
    return model


def sample_frame_probs(video_path, model, face_analyzer, max_samples=15):
    """Runs inference on evenly-spaced frames of a video. Returns list of raw [p0, p1] probability pairs."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  -> Could not open {video_path}, skipping.")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []

    interval = max(1, total_frames // max_samples)
    probs_list = []

    for frame_idx in range(total_frames):
        ret, frame = cap.read()
        if not ret or frame is None:
            break
        if frame_idx % interval != 0:
            continue

        face_crop, _ = face_analyzer.extract_and_align_face(frame)
        use_crop = (
            face_crop is not None
            and face_crop.size > 0
            and face_crop.shape[0] >= 128
            and face_crop.shape[1] >= 128
        )

        if use_crop:
            eval_image = face_crop
        else:
            h, w, _ = frame.shape
            min_dim = min(h, w)
            sy, sx = (h - min_dim) // 2, (w - min_dim) // 2
            eval_image = frame[sy:sy + min_dim, sx:sx + min_dim]

        pil_img = Image.fromarray(cv2.cvtColor(eval_image, cv2.COLOR_BGR2RGB)).resize((224, 224))
        input_tensor = vit_transform(pil_img).unsqueeze(0)

        with torch.no_grad():
            raw_outputs = model(input_tensor)
            probs = torch.softmax(raw_outputs, dim=1).flatten().tolist()

        probs_list.append(probs)

    cap.release()
    return probs_list


def analyze_folder(folder, label, model, face_analyzer):
    print(f"\n{'='*60}")
    print(f"  ANALYZING '{label}' FOLDER: {folder}")
    print(f"{'='*60}")

    if not os.path.isdir(folder):
        print(f"  Folder does not exist. Skipping.")
        return []

    video_files = [f for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if not video_files:
        print(f"  No video files found in {folder}.")
        return []

    all_index0 = []
    all_index1 = []

    for vf in video_files:
        path = os.path.join(folder, vf)
        probs = sample_frame_probs(path, model, face_analyzer)
        if not probs:
            continue

        avg_p0 = np.mean([p[0] for p in probs])
        avg_p1 = np.mean([p[1] for p in probs])
        max_p1 = np.max([p[1] for p in probs])

        all_index0.extend([p[0] for p in probs])
        all_index1.extend([p[1] for p in probs])

        print(f"  {vf:40s}  avg[0]={avg_p0*100:5.1f}%  avg[1]={avg_p1*100:5.1f}%  max[1]={max_p1*100:5.1f}%  (n={len(probs)} frames)")

    return all_index0, all_index1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", required=True, help="Folder of known-authentic videos")
    parser.add_argument("--fake", required=True, help="Folder of known-tampered videos")
    args = parser.parse_args()

    print("Loading model and face analyzer...")
    model = load_model()
    face_analyzer = ForensicFaceAnalyzer()

    real_i0, real_i1 = analyze_folder(args.real, "REAL / AUTHENTIC", model, face_analyzer)
    fake_i0, fake_i1 = analyze_folder(args.fake, "FAKE / TAMPERED", model, face_analyzer)

    print(f"\n{'='*60}")
    print("  VERDICT")
    print(f"{'='*60}")

    if not real_i1 or not fake_i1:
        print("  Not enough data collected. Add more videos to both folders and re-run.")
        return

    real_mean_i1 = np.mean(real_i1)
    fake_mean_i1 = np.mean(fake_i1)

    print(f"\n  Mean P(index=1) on REAL videos: {real_mean_i1*100:.2f}%")
    print(f"  Mean P(index=1) on FAKE videos: {fake_mean_i1*100:.2f}%")

    if fake_mean_i1 > real_mean_i1:
        print("\n  --> CORRECT ORIENTATION: index 1 rises for fakes, as FAKE_CLASS_INDEX=1 assumes.")
        print("      Your class index is fine. The bug is elsewhere (edge-variance override, threshold).")
        gap_direction = "index 1 = fake"
    else:
        print("\n  --> INVERTED: index 1 is actually HIGHER for real videos.")
        print("      Your FAKE_CLASS_INDEX should be 0, not 1. This alone likely explains")
        print("      your flipped verdicts. Fix this first before touching anything else.")
        gap_direction = "index 0 = fake"

    # Suggest a threshold using the midpoint between the two class means,
    # oriented correctly based on what we just found.
    correct_fake_probs = fake_i1 if fake_mean_i1 > real_mean_i1 else fake_i0
    correct_real_probs = real_i1 if fake_mean_i1 > real_mean_i1 else real_i0

    suggested_threshold = (np.mean(correct_fake_probs) + np.mean(correct_real_probs)) / 2

    print(f"\n  Based on {gap_direction}:")
    print(f"    Mean fake-class prob on FAKE videos: {np.mean(correct_fake_probs)*100:.2f}%")
    print(f"    Mean fake-class prob on REAL videos: {np.mean(correct_real_probs)*100:.2f}%")
    print(f"    Suggested SENSITIVITY_THRESHOLD: {suggested_threshold:.3f}")
    print(f"\n  (Current hardcoded value in your code: 0.65)")

    separation = np.mean(correct_fake_probs) - np.mean(correct_real_probs)
    if separation < 0.15:
        print(f"\n  WARNING: separation between classes is only {separation*100:.1f} percentage points.")
        print("  This means the model itself is not confidently distinguishing real from fake")
        print("  on your test videos -- no threshold will fix that. You likely need more/better")
        print("  training data, or your face crop / preprocessing doesn't match training conditions.")


if __name__ == "__main__":
    main()