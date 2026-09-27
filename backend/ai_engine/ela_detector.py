"""
ELA (Error Level Analysis) detector for manual edits and splicing.

Method:
  - Re-save the image at a known JPEG quality
  - Compute pixel-wise error between original and re-saved
  - In an unedited image, error is uniform across the image
  - In an edited image, the edited regions show different error levels
    (because they were saved at a different quality or compressed twice)

References:
  Krawetz (2007), "A Picture's Worth: Digital Image Analysis and Forensics"
  Farid (2009), "Image Forgery Detection"
"""

import numpy as np
import cv2


def _ela_map(image_path, quality=90):
    original = cv2.imread(image_path)
    if original is None:
        return None, None
    ok, buf = cv2.imencode(".jpg", original, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        return None, None
    recompressed = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    diff = cv2.absdiff(original, recompressed)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    return original, gray


def detect_image_ela(image_path, quality=90, block=32):
    original, ela = _ela_map(image_path, quality)
    if original is None:
        return {"available": False, "reason": "Cannot read image",
                "verdict": "Original", "fake_probability": 0.0}

    h, w = ela.shape
    # Block-wise mean ELA
    block_means = []
    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            patch = ela[y:y + block, x:x + block]
            block_means.append(float(patch.mean()))

    if not block_means:
        return {"available": False, "reason": "Image too small",
                "verdict": "Original", "fake_probability": 0.0}

    arr = np.array(block_means)
    median_v = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median_v))) + 1e-6

    # In an unedited image, all blocks have similar ELA.
    # In an edited image, some blocks are wildly different.
    outlier_ratio = float(np.mean(np.abs(arr - median_v) > 4 * mad))

    score = 0.0
    if outlier_ratio > 0.10:
        score += 0.4
    if outlier_ratio > 0.25:
        score += 0.4
    score = min(1.0, score)

    verdict = "Synthetic" if score >= 0.5 else "Original"

    # Region localization: return bounding boxes of outlier blocks
    regions = []
    idx = 0
    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            if idx < len(arr) and abs(arr[idx] - median_v) > 4 * mad:
                regions.append({"x": int(x), "y": int(y),
                                "w": int(block), "h": int(block),
                                "source": "ela"})
            idx += 1

    return {
        "available": True,
        "method": "Error Level Analysis (ELA)",
        "median_ela": round(median_v, 3),
        "outlier_block_ratio": round(outlier_ratio, 4),
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "regions": regions[:15],
        "disclaimer": "ELA is heuristic. Re-compressed real images may "
                      "trigger false positives.",
    }


def detect_video_ela(video_path, max_frames=6, block=32):
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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (256, 256))
        blocks = []
        for y in range(0, 256 - block, block):
            for x in range(0, 256 - block, block):
                blocks.append(float(gray[y:y + block, x:x + block].std()))
        if not blocks:
            continue
        arr = np.array(blocks)
        med = float(np.median(arr))
        mad = float(np.median(np.abs(arr - med))) + 1e-6
        out = float(np.mean(np.abs(arr - med) > 4 * mad))
        s = 0.0
        if out > 0.10:
            s += 0.4
        if out > 0.25:
            s += 0.4
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
        "method": "Error Level Analysis (ELA) - aggregated",
        "frames_analyzed": len(scores),
        "mean_score": round(mean_score, 4),
        "flagged_ratio": round(flagged, 4),
        "fake_probability": round(mean_score, 4),
        "verdict": verdict,
        "disclaimer": "ELA heuristic only.",
    }
