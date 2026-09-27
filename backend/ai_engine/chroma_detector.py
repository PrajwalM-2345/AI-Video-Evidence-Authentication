"""
Chroma subsampling consistency detector.

Detects re-encoding artifacts typical of WhatsApp, YouTube, Instagram,
and other social media pipelines.

Method:
  - Convert frame to YCrCb
  - Analyze chroma plane resolutions and energy distribution
  - Real camera footage preserves full chroma consistency
  - Re-encoded media shows 4:2:0 subsampling artifacts, chroma smearing,
    or inconsistent chroma energy across the frame

Reference:
  Bianchi & Piva (2012), "Detection of Non-Aligned Double JPEG
  Compression"
"""

import numpy as np
import cv2


def _chroma_stats(image_bgr):
    ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)

    # Chroma energy vs luma energy
    y_energy = float(np.mean(np.abs(y.astype(np.float32) - 128)))
    cr_energy = float(np.mean(np.abs(cr.astype(np.float32) - 128)))
    cb_energy = float(np.mean(np.abs(cb.astype(np.float32) - 128)))

    if y_energy < 1e-6:
        return None

    chroma_luma_ratio = (cr_energy + cb_energy) / (2 * y_energy)

    # Chroma smoothness: re-encoded media has smoother chroma
    cr_smooth = float(cv2.Laplacian(cr, cv2.CV_64F).var())
    cb_smooth = float(cv2.Laplacian(cb, cv2.CV_64F).var())
    chroma_roughness = (cr_smooth + cb_smooth) / 2

    # High-frequency chroma check
    cr_high = float(np.mean(cv2.Sobel(cr, cv2.CV_64F, 1, 0) ** 2))
    cb_high = float(np.mean(cv2.Sobel(cb, cv2.CV_64F, 0, 1) ** 2))

    return {
        "chroma_luma_ratio": chroma_luma_ratio,
        "chroma_roughness": chroma_roughness,
        "chroma_high_freq": (cr_high + cb_high) / 2,
    }


def detect_image_chroma(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return {"available": False, "reason": "Cannot read image",
                "verdict": "Original", "fake_probability": 0.0}

    stats = _chroma_stats(img)
    if stats is None:
        return {"available": False, "reason": "Analysis failed",
                "verdict": "Original", "fake_probability": 0.0}

    score = 0.0
    # Re-encoded images typically have LOW chroma-luma ratio
    # (chroma has been smoothed)
    if stats["chroma_luma_ratio"] < 0.15:
        score += 0.4
    # Very low chroma roughness also indicates re-encoding
    if stats["chroma_roughness"] < 5.0:
        score += 0.3
    # Very low high-freq chroma energy indicates smoothing
    if stats["chroma_high_freq"] < 30.0:
        score += 0.2
    score = min(1.0, score)

    verdict = "Synthetic" if score >= 0.5 else "Original"

    return {
        "available": True,
        "method": "Chroma subsampling consistency",
        "chroma_luma_ratio": round(stats["chroma_luma_ratio"], 4),
        "chroma_roughness": round(stats["chroma_roughness"], 4),
        "chroma_high_freq": round(stats["chroma_high_freq"], 4),
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "disclaimer": "Chroma heuristic only. Genuine low-chroma content "
                      "(e.g., grayscale scenes) may trigger false positives.",
    }


def detect_video_chroma(video_path, max_frames=6):
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
    scores = []

    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(pos))
        ok, frame = cap.read()
        if not ok:
            continue
        frame = cv2.resize(frame, (256, 256))
        stats = _chroma_stats(frame)
        if stats is None:
            continue
        s = 0.0
        if stats["chroma_luma_ratio"] < 0.15:
            s += 0.4
        if stats["chroma_roughness"] < 5.0:
            s += 0.3
        if stats["chroma_high_freq"] < 30.0:
            s += 0.2
        scores.append(min(1.0, s))
    cap.release()

    if not scores:
        return {"available": False, "reason": "No decodable frames",
                "verdict": "Original", "fake_probability": 0.0}

    mean_score = float(np.mean(scores))
    flagged = float(sum(1 for s in scores if s >= 0.5) / len(scores))
    verdict = "Synthetic" if flagged >= 0.5 else "Original"

    return {
        "available": True,
        "method": "Chroma subsampling consistency (aggregated)",
        "frames_analyzed": len(scores),
        "mean_score": round(mean_score, 4),
        "flagged_ratio": round(flagged, 4),
        "fake_probability": round(mean_score, 4),
        "verdict": verdict,
        "disclaimer": "Chroma heuristic only.",
    }
