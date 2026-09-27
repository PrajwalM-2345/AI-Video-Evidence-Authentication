"""
PRNU / Noise Consistency Detector.

Every camera sensor leaves a unique noise pattern (PRNU) in every photo
or video frame. Edited, spliced, or re-encoded content breaks this
consistency. This detector measures within-frame noise consistency and
between-frame consistency.

Signals:
  - within_frame_noise_variance: high variance in noise = spliced regions
  - between_frame_consistency:   high inconsistency = re-encoded/spliced
  - verdict:                     "Synthetic" if signals indicate tampering

Reference: Fridrich (2009), "Digital Image Forensics"
"""

import numpy as np
import cv2


def _extract_noise(gray):
    """Extract noise residual using a simple high-pass filter."""
    # Median filter to approximate the smooth content
    smooth = cv2.medianBlur(gray, 3)
    noise = gray.astype(np.float32) - smooth.astype(np.float32)
    return noise


def analyze_image_prnu(image_path):
    """Analyze PRNU consistency for a single image."""
    img = cv2.imread(image_path)
    if img is None:
        return {"available": False, "reason": "Cannot read image",
                "verdict": "Original", "fake_probability": 0.0}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Split into 16x16 blocks
    h, w = gray.shape
    block = 32
    variances = []

    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            patch = gray[y:y + block, x:x + block]
            noise = _extract_noise(patch)
            variances.append(float(noise.std()))

    if not variances:
        return {"available": False, "reason": "Image too small",
                "verdict": "Original", "fake_probability": 0.0}

    arr = np.array(variances)
    median_var = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median_var))) + 1e-6

    # In a genuine (unmodified) photo, noise is roughly uniform.
    # In a spliced photo, some blocks have very different noise.
    outlier_ratio = float(np.mean(np.abs(arr - median_var) > 4 * mad))

    score = 0.0
    if outlier_ratio > 0.15:
        score += 0.5
    if outlier_ratio > 0.30:
        score += 0.3
    score = min(1.0, score)

    verdict = "Synthetic" if score >= 0.5 else "Original"

    return {
        "available": True,
        "method": "Within-image PRNU noise consistency",
        "median_noise_variance": round(median_var, 4),
        "outlier_block_ratio": round(outlier_ratio, 4),
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "disclaimer": "Noise heuristic only. Low-res or heavily-compressed "
                      "images can trigger false positives.",
    }


def analyze_video_prnu(video_path, max_frames=8):
    """Analyze PRNU consistency across sampled frames."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"available": False, "reason": "Cannot open video",
                "verdict": "Original", "fake_probability": 0.0}

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return {"available": False, "reason": "Invalid video",
                "verdict": "Original", "fake_probability": 0.0}

    n = min(max_frames, total)
    positions = np.linspace(0, total - 1, n).astype(int)
    frame_vars = []

    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(pos))
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (256, 256))
        noise = _extract_noise(gray)
        frame_vars.append(float(noise.std()))
    cap.release()

    if len(frame_vars) < 3:
        return {"available": False, "reason": "Too few frames",
                "verdict": "Original", "fake_probability": 0.0}

    arr = np.array(frame_vars)
    median_v = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median_v))) + 1e-6
    inconsistency = float(np.mean(np.abs(arr - median_v) > 4 * mad))

    score = min(1.0, inconsistency * 2.5)
    verdict = "Synthetic" if score >= 0.5 else "Original"

    return {
        "available": True,
        "method": "Cross-frame PRNU consistency",
        "frames_analyzed": len(frame_vars),
        "median_noise_std": round(median_v, 4),
        "frame_inconsistency_ratio": round(inconsistency, 4),
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "disclaimer": "Noise heuristic only. Real videos with scene "
                      "transitions can trigger false positives.",
    }
