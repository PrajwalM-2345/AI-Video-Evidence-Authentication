"""
Celeb-DF-v2 Frame Extraction
-----------------------------
Extracts face-cropped frames from Celeb-DF-v2 videos and merges them into
the existing backend/kaggle_data/train/authentic and .../fake folders
alongside your current 2,041 images from real-and-fake-face-detection.

Sampling is deliberately imbalanced PER VIDEO to correct for Celeb-DF-v2's
~6.3:1 fake:real video-count skew:
    - Real videos (Celeb-real, YouTube-real): more frames per video
    - Fake videos (Celeb-synthesis): fewer frames per video
This keeps the final image-level class balance reasonable.

Run from project root:
    python3 extract_celebdf_frames.py

Adjust FRAMES_PER_REAL_VIDEO / FRAMES_PER_FAKE_VIDEO below if you want more
or less data -- more frames = longer runtime, more training data.
"""

import os
import sys
import cv2
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from ai_engine.face_analysis import ForensicFaceAnalyzer

# --- Config ---
CELEBDF_ROOT = "backend/kaggle_data/Celeb-DF-v2"
OUTPUT_AUTHENTIC = "backend/kaggle_data/train/authentic"
OUTPUT_FAKE = "backend/kaggle_data/train/fake"

FRAMES_PER_REAL_VIDEO = 8   # Celeb-real, YouTube-real
FRAMES_PER_FAKE_VIDEO = 2   # Celeb-synthesis

MIN_CROP_SIZE = 128  # matches the check already used in run_forensic_pipeline

SOURCE_FOLDERS = [
    ("Celeb-real", OUTPUT_AUTHENTIC, FRAMES_PER_REAL_VIDEO, "real"),
    ("YouTube-real", OUTPUT_AUTHENTIC, FRAMES_PER_REAL_VIDEO, "real"),
    ("Celeb-synthesis", OUTPUT_FAKE, FRAMES_PER_FAKE_VIDEO, "fake"),
]


def extract_frames_from_video(video_path, num_frames, face_analyzer):
    """Samples num_frames evenly-spaced frames from a video, face-crops each.
    Returns a list of cropped BGR numpy arrays (may be shorter than num_frames
    if some samples fail face detection or are unreadable)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []

    # Evenly spaced sample indices across the video
    if total_frames <= num_frames:
        sample_indices = list(range(total_frames))
    else:
        step = total_frames / num_frames
        sample_indices = [int(i * step) for i in range(num_frames)]

    crops = []
    sample_set = set(sample_indices)
    current_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        if current_idx in sample_set:
            face_crop, _ = face_analyzer.extract_and_align_face(frame)
            if (
                face_crop is not None
                and face_crop.size > 0
                and face_crop.shape[0] >= MIN_CROP_SIZE
                and face_crop.shape[1] >= MIN_CROP_SIZE
            ):
                crops.append(face_crop)
            # If face detection fails, we simply skip this frame rather than
            # falling back to a full-frame crop -- for training data we want
            # clean face crops, not background noise that could teach the
            # model spurious correlations.

        current_idx += 1
        if current_idx > max(sample_indices):
            break

    cap.release()
    return crops


def process_folder(folder_name, output_dir, frames_per_video, label_tag, face_analyzer):
    source_dir = os.path.join(CELEBDF_ROOT, folder_name)
    if not os.path.isdir(source_dir):
        print(f"  WARNING: {source_dir} not found, skipping.")
        return 0

    os.makedirs(output_dir, exist_ok=True)

    video_files = sorted([
        f for f in os.listdir(source_dir)
        if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    ])

    print(f"\n{'='*60}")
    print(f"  Processing {folder_name}: {len(video_files)} videos -> {output_dir}")
    print(f"  Sampling {frames_per_video} frames/video")
    print(f"{'='*60}")

    total_saved = 0
    start_time = time.time()

    for i, video_file in enumerate(video_files):
        video_path = os.path.join(source_dir, video_file)
        crops = extract_frames_from_video(video_path, frames_per_video, face_analyzer)

        base_name = os.path.splitext(video_file)[0]
        for crop_idx, crop in enumerate(crops):
            out_filename = f"celebdf_{label_tag}_{base_name}_{crop_idx:02d}.jpg"
            out_path = os.path.join(output_dir, out_filename)
            cv2.imwrite(out_path, crop)
            total_saved += 1

        if (i + 1) % 50 == 0 or (i + 1) == len(video_files):
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (len(video_files) - (i + 1)) / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(video_files)}] videos processed, "
                  f"{total_saved} frames saved so far, "
                  f"~{eta:.0f}s remaining")

    elapsed_total = time.time() - start_time
    print(f"  Done: {total_saved} frames saved from {folder_name} in {elapsed_total:.1f}s")
    return total_saved


def main():
    print("Loading face analyzer...")
    face_analyzer = ForensicFaceAnalyzer()

    grand_total = 0
    for folder_name, output_dir, frames_per_video, label_tag in SOURCE_FOLDERS:
        saved = process_folder(folder_name, output_dir, frames_per_video, label_tag, face_analyzer)
        grand_total += saved

    print(f"\n{'='*60}")
    print(f"  EXTRACTION COMPLETE: {grand_total} new frames added")
    print(f"{'='*60}")

    # Report final combined counts
    auth_count = len([f for f in os.listdir(OUTPUT_AUTHENTIC) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    fake_count = len([f for f in os.listdir(OUTPUT_FAKE) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    print(f"  Total authentic/ images now: {auth_count}")
    print(f"  Total fake/ images now: {fake_count}")
    print(f"  Class ratio: {auth_count / max(fake_count, 1):.2f} (1.0 = perfectly balanced)")


if __name__ == "__main__":
    main()