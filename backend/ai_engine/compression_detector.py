"""
Compression-history detector.

Detects double-JPEG compression, re-encoding, and bitrate anomalies.
Signals manual edit, WhatsApp re-compression, YouTube re-upload, etc.

Method:
  - Recompress the input image at quality Q
  - Compare compression error to original
  - Analyze block-DCT coefficient histograms for periodicity
    (a hallmark of double compression)

Reference: Farid (2009), "Exposing Digital Forgeries from JPEG Ghosts"
"""

import numpy as np
import cv2


def _jpeg_ghost_score(img_bgr):
    """Compute JPEG ghost map — strong ghosts indicate re-compression."""
    qualities = [60, 70, 80, 90, 95]
    scores = []
    for q in qualities:
        ok, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, q])
        if not ok:
            continue
        recompressed = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        diff = cv2.absdiff(img_bgr, recompressed).astype(np.float32)
        scores.append(float(diff.mean()))
    if not scores:
        return 0.0
    return float(np.std(scores))


def _dct_periodicity(gray):
    """Detect periodic DCT coefficient histograms (double-JPEG signature)."""
    gray_f = gray.astype(np.float32)
    # Block DCT — compute DC coefficient per 8x8 block
    h, w = gray_f.shape
    h8 = (h // 8) * 8
    w8 = (w // 8) * 8
    if h8 < 16 or w8 < 16:
        return 0.0
    dcs = []
    for y in range(0, h8, 8):
        for x in range(0, w8, 8):
            block = gray_f[y:y + 8, x:x + 8]
            dct = cv2.dct(block)
            dcs.append(dct[0, 0])
    if len(dcs) < 10:
        return 0.0
    dcs = np.array(dcs)
    hist, _ = np.histogram(dcs, bins=64)
    hist = hist.astype(np.float32)
    hist = hist / (hist.sum() + 1e-9)
    # Periodicity: autocorrelation of the histogram
    ac = np.correlate(hist, hist, mode="full")[len(hist) - 1:]
    ac = ac / (ac[0] + 1e-9)
    # Peaks in the autocorrelation indicate periodicity
    peak_score = float(np.max(ac[3:20])) if len(ac) > 20 else 0.0
    return peak_score


def detect_image_compression(image_path):
    """Analyze compression history of an image."""
    img = cv2.imread(image_path)
    if img is None:
        return {"available": False, "reason": "Cannot read image",
                "verdict": "Original", "fake_probability": 0.0}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ghost = _jpeg_ghost_score(img)
    periodicity = _dct_periodicity(gray)

    score = 0.0
    if ghost > 1.5:
        score += 0.4
    if periodicity > 0.35:
        score += 0.4
    score = min(1.0, score)

    verdict = "Synthetic" if score >= 0.5 else "Original"

    return {
        "available": True,
        "method": "JPEG ghost + DCT coefficient periodicity",
        "jpeg_ghost_score": round(ghost, 4),
        "dct_periodicity": round(periodicity, 4),
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "disclaimer": "Compression heuristic only. High-quality "
                      "compressions may pass undetected.",
    }


def detect_video_compression(video_path, max_frames=6):
    """Analyze compression consistency across frames."""
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
    ghosts = []
    periodicities = []

    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(pos))
        ok, frame = cap.read()
        if not ok:
            continue
        frame_small = cv2.resize(frame, (256, 256))
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        ghosts.append(_jpeg_ghost_score(frame_small))
        periodicities.append(_dct_periodicity(gray))
    cap.release()

    if not ghosts:
        return {"available": False, "reason": "No decodable frames",
                "verdict": "Original", "fake_probability": 0.0}

    ghost_mean = float(np.mean(ghosts))
    period_mean = float(np.mean(periodicities))

    score = 0.0
    if ghost_mean > 1.5:
        score += 0.4
    if period_mean > 0.35:
        score += 0.4
    score = min(1.0, score)

    verdict = "Synthetic" if score >= 0.5 else "Original"

    return {
        "available": True,
        "method": "JPEG ghost + DCT periodicity (aggregated)",
        "frames_analyzed": len(ghosts),
        "mean_ghost_score": round(ghost_mean, 4),
        "mean_periodicity": round(period_mean, 4),
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "disclaimer": "Compression heuristic only.",
    }
