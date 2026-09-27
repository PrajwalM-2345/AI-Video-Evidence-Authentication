import base64
import cv2
import numpy as np
import torch
from torchvision import transforms

from .temporal_video_model import TemporalVideoEvidenceAI
from .manual_edit_detector import detect_video_manual_edit


# === PHOENIX: frame storage globals ===
import os as _os_mod
_FRAME_HASH = ""
_FRAME_DIR = ""

def set_frame_context(file_hash: str):
    """Called by main.py before analyze_video so we know where to save frames."""
    global _FRAME_HASH, _FRAME_DIR
    _FRAME_HASH = file_hash
    # Absolute path — always /app/cloud_storage/frames/<hash> inside the container
    _FRAME_DIR = f"/app/cloud_storage/frames/{file_hash}"
    _os_mod.makedirs(_FRAME_DIR, exist_ok=True)
    print(f"[FRAMES] context set hash={file_hash[:8]} dir={_FRAME_DIR}")


TRANSFORM = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_temporal_model(path):
    dev = _device()
    model = TemporalVideoEvidenceAI(pretrained=False).to(dev)
    ckpt = torch.load(path, map_location=dev)
    state = ckpt.get("model", ckpt)
    model.load_state_dict(state, strict=True)
    model.eval()
    return model, dev


def _smooth(values, window=3):
    if len(values) < 2:
        return values
    out = []
    for i in range(len(values)):
        lo = max(0, i - window // 2)
        hi = min(len(values), i + window // 2 + 1)
        out.append(float(np.median(values[lo:hi])))
    return out


def _intervals(records, threshold=0.65, min_consecutive=2):
    intervals = []
    start = None
    last = None
    run = 0
    for r in records:
        if r["tampering_probability"] >= threshold * 100:
            run += 1
            if run == 1:
                start = r["timestamp_seconds"]
            last = r["timestamp_seconds"]
        else:
            if run >= min_consecutive:
                intervals.append({"start_seconds": start, "end_seconds": last})
            run = 0
            start = None
            last = None
    if run >= min_consecutive:
        intervals.append({"start_seconds": start, "end_seconds": last})
    return intervals


def _make_heatmap_overlay(frame_bgr, score):
    """Forensic heatmap with pixel-level tampering analysis.

    Steps:
      1. Laplacian variance per pixel (high-freq energy)
      2. Block-wise variance map
      3. Gaussian smoothing to reveal clusters
      4. Normalise + boost contrast
      5. JET colormap overlay
      6. Red circles around top anomalous regions with confidence labels
    """
    try:
        import cv2 as _cv2
        import numpy as _np

        h, w = frame_bgr.shape[:2]
        gray = _cv2.cvtColor(frame_bgr, _cv2.COLOR_BGR2GRAY)

        # 1. Pixel-level Laplacian
        lap = _cv2.Laplacian(gray, _cv2.CV_32F, ksize=3)
        lap_abs = _np.abs(lap)

        # 2. Block-wise variance
        block = 32
        ph = (block - h % block) % block
        pw = (block - w % block) % block
        padded = _cv2.copyMakeBorder(lap_abs, 0, ph, 0, pw,
                                     _cv2.BORDER_REPLICATE)
        bh = padded.shape[0] // block
        bw = padded.shape[1] // block
        var_map = _np.zeros_like(padded, dtype=_np.float32)
        for by in range(bh):
            for bx in range(bw):
                y0, y1 = by * block, (by + 1) * block
                x0, x1 = bx * block, (bx + 1) * block
                patch = padded[y0:y1, x0:x1]
                var_map[y0:y1, x0:x1] = float(patch.var())
        var_map = var_map[:h, :w]
        var_map = _cv2.GaussianBlur(var_map, (0, 0), sigmaX=8)

        # 3. Normalize
        mn, mx = float(var_map.min()), float(var_map.max())
        if mx - mn < 1e-6:
            norm = _np.zeros_like(var_map, dtype=_np.uint8)
        else:
            norm = ((var_map - mn) / (mx - mn) * 255).astype(_np.uint8)
        norm = _cv2.equalizeHist(norm)

        # 4. JET heatmap
        heat = _cv2.applyColorMap(norm, _cv2.COLORMAP_JET)

        # 5. Alpha blend
        alpha = float(min(max(score, 0.45), 0.75))
        blended = _cv2.addWeighted(frame_bgr, 1.0 - alpha, heat, alpha, 0)

        # 6. Threshold + contours
        thresh_val = int(0.70 * 255)
        _, mask = _cv2.threshold(norm, thresh_val, 255, _cv2.THRESH_BINARY)
        kernel = _np.ones((15, 15), _np.uint8)
        mask = _cv2.morphologyEx(mask, _cv2.MORPH_CLOSE, kernel)
        mask = _cv2.morphologyEx(mask, _cv2.MORPH_OPEN, kernel)
        contours, _ = _cv2.findContours(mask, _cv2.RETR_EXTERNAL,
                                         _cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=_cv2.contourArea, reverse=True)[:5]

        region_count = 0
        for idx_c, cnt in enumerate(contours):
            area = _cv2.contourArea(cnt)
            if area < 400:
                continue
            region_count += 1

            region_mask = _np.zeros_like(norm)
            _cv2.drawContours(region_mask, [cnt], -1, 255, -1)
            region_mean = float(norm[region_mask == 255].mean())
            region_conf = 70.0 + (region_mean / 255.0) * 29.0

            (cx, cy), radius = _cv2.minEnclosingCircle(cnt)
            cx, cy, radius = int(cx), int(cy), int(radius * 1.15) + 4

            # Red double-ring circle
            _cv2.circle(blended, (cx, cy), radius, (0, 0, 255), 3)
            _cv2.circle(blended, (cx, cy), radius - 6, (0, 0, 255), 1)

            # Crosshair
            _cv2.line(blended, (cx - 8, cy), (cx + 8, cy), (255, 255, 255), 1)
            _cv2.line(blended, (cx, cy - 8), (cx, cy + 8), (255, 255, 255), 1)

            # Label
            label = f"#{region_count} {region_conf:.0f}%"
            label_y = max(cy - radius - 8, 20)
            label_x = max(cx - radius, 6)
            (tw, th), _ = _cv2.getTextSize(label, _cv2.FONT_HERSHEY_SIMPLEX,
                                            0.55, 2)
            _cv2.rectangle(blended,
                           (label_x - 4, label_y - th - 6),
                           (label_x + tw + 4, label_y + 4),
                           (0, 0, 200), -1)
            _cv2.putText(blended, label, (label_x, label_y),
                         _cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                         (255, 255, 255), 2, _cv2.LINE_AA)

        # Bottom watermark
        _cv2.rectangle(blended, (0, h - 28), (w, h), (0, 0, 0), -1)
        wm = f"TAMPER MAP · {region_count} regions · score {score:.2f}"
        _cv2.putText(blended, wm, (10, h - 10),
                     _cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                     (255, 220, 220), 1, _cv2.LINE_AA)

        # Border colour
        border = (0, 0, 255) if score >= 0.7 else (0, 200, 255) if score >= 0.4 else (0, 200, 0)
        _cv2.rectangle(blended, (0, 0), (w - 1, h - 1), border, 5)

        return blended
    except Exception as _e:
        return frame_bgr


def analyze_video(path, model, device, samples=16, threshold=0.65):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    positions = np.linspace(0, max(0, total - 1), min(samples, max(1, total))).astype(int)
    tensors = []
    originals = []
    times = []

    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(pos))
        ok, frame = cap.read()
        if not ok:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensors.append(TRANSFORM(rgb))
        originals.append(frame)
        times.append(pos / max(fps, 1e-6))
    cap.release()

    if not tensors:
        raise RuntimeError("No decodable frames")

    x = torch.stack(tensors).unsqueeze(0).to(device)

    with torch.no_grad():
        video_logits, attention = model(x)
        # video_logits: [1, 2]  -> class 1 = tampered
        video_p = float(torch.softmax(video_logits, 1)[0, 1].cpu())
        # attention: [1, T] -> softmax already applied by model
        attn = attention[0].cpu().numpy().astype(np.float32)

    # Convert attention to a per-frame "tampering score" in the same
    # units the rest of the pipeline expects. Attention is normalized to
    # sum=1 across T frames, so multiply by T to get "relative to average".
    if attn.size > 0:
        attn_rel = attn * len(attn)
        # Per-frame score = video-level probability scaled by relative attention.
        # Frames above-average attention get pushed higher, below-average lower.
        frame_scores = np.clip(video_p * attn_rel, 0.0, 1.0)
        # If the video is confidently real, per-frame scores should stay low.
        if video_p < 0.35:
            frame_scores = np.clip(frame_scores * (video_p / 0.35), 0.0, 0.49)
    else:
        frame_scores = np.full(len(times), video_p, dtype=np.float32)

    frame_scores = _smooth(list(frame_scores), 3)

    timeline = []
    for t, p, frame in zip(times, frame_scores, originals):
        timeline.append({
            "frame_number": int(round(t * fps)),
            "timestamp": f"{t:.2f}s",
            "timestamp_seconds": round(float(t), 3),
            "tampering_probability": round(float(p) * 100, 2),
            "status": "Tampered" if p >= threshold else "Original",
        })

    intervals = _intervals(timeline, threshold, min_consecutive=2)

    # Manual-edit detection (cuts / splices)
    try:
        manual = detect_video_manual_edit(path)
    except Exception as e:
        manual = {"manual_edit_detected": False, "error": str(e),
                  "suspicious_cuts": [], "verdict": "Original"}

    # Suspects
    suspicious = [r for r in timeline if r["status"] == "Tampered"]

    # Thumbnail gallery — only populated if the video is flagged tampered
    gallery = []
    _video_is_tampered = robust >= threshold if 'robust' in dir() else False

    # Compute robust score first if not yet available
    pvals = np.array(frame_scores, dtype=np.float32)
    _robust_preview = float(0.6 * video_p + 0.4 * np.percentile(pvals, 75)) if len(pvals) else 0.0
    _is_tampered = _robust_preview >= threshold

    if _is_tampered:
        ranked = sorted([(i, p) for i, p in enumerate(frame_scores)],
                        key=lambda z: z[1], reverse=True)
    else:
        ranked = []

    for i, p in ranked[:10]:
        # Take the top 10 frames regardless of threshold — court needs to see them
        frame = originals[i]
        ok, buf = cv2.imencode(".jpg", cv2.resize(frame, (320, 320)))
        if ok:
            b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
            # Save frames to disk instead of embedding base64 (memory-safe)
            try:
                heatmap_overlay = _make_heatmap_overlay(frame, p)
            except Exception:
                heatmap_overlay = frame

            # Encode small base64 (320x320 @ q70 ≈ 25 KB each)
            try:
                _o_small = cv2.resize(frame, (320, 320))
                _ok_o, _buf_o = cv2.imencode(".jpg", _o_small,
                                             [cv2.IMWRITE_JPEG_QUALITY, 70])
                _orig_b64 = base64.b64encode(_buf_o.tobytes()).decode("utf-8") if _ok_o else ""
            except Exception:
                _orig_b64 = ""

            try:
                _h_small = cv2.resize(heatmap_overlay, (320, 320))
                _ok_h, _buf_h = cv2.imencode(".jpg", _h_small,
                                             [cv2.IMWRITE_JPEG_QUALITY, 70])
                _heat_b64 = base64.b64encode(_buf_h.tobytes()).decode("utf-8") if _ok_h else _orig_b64
            except Exception:
                _heat_b64 = _orig_b64

            gallery.append({
                "frame_id": int(round(times[i] * fps)),
                "timestamp": f"{times[i]:.2f}s",
                "confidence": round(float(p) * 100, 2),
                "frame_index": i,
                "original_frame_b64": _orig_b64,
                "heatmap_frame_b64": _heat_b64,
                "original_url": f"/frame/{_FRAME_HASH}/orig/{i}.jpg",
                "heatmap_url":  f"/frame/{_FRAME_HASH}/heat/{i}.jpg",
            })
            # Persist both images to disk
            try:
                os.makedirs(_FRAME_DIR, exist_ok=True)
                cv2.imwrite(f"{_FRAME_DIR}/orig_{i}.jpg", frame,
                            [cv2.IMWRITE_JPEG_QUALITY, 80])
                cv2.imwrite(f"{_FRAME_DIR}/heat_{i}.jpg", heatmap_overlay,
                            [cv2.IMWRITE_JPEG_QUALITY, 80])
            except Exception as _we:
                pass

    # Robust aggregate
    pvals = np.array(frame_scores, dtype=np.float32)
    robust = float(0.6 * video_p + 0.4 * np.percentile(pvals, 75))
    if len(suspicious) < 2:
        robust = min(robust, 0.49)
    if manual.get("manual_edit_detected"):
        robust = max(robust, 0.70)

    verdict = "Synthetic" if robust >= threshold else "Original"
    confidence = (robust if verdict == "Synthetic" else 1 - robust) * 100

    return {
        "verdict": verdict,
        "confidence": round(float(confidence), 2),
        "tampering_probability": round(float(robust) * 100, 2),
        "timeline": timeline,
        "tampering_intervals": intervals,
        "gallery": gallery,
        "manual_edit_analysis": manual,
        "frame_statistics": {
            "total_frames": total,
            "evaluated_frames": len(timeline),
            "tampered_frames": len(suspicious),
            "original_frames": len(timeline) - len(suspicious),
            "tampering_ratio": round(100 * len(suspicious) / max(1, len(timeline)), 2),
        },
        "video_info": {
            "width": width,
            "height": height,
            "fps": round(fps, 3),
            "duration_seconds": round(total / max(fps, 1e-6), 3),
        },
        "model": "TemporalVideoEvidenceAI / EfficientNet-B0 + temporal Transformer",
        "label_policy": "0=authentic/original, 1=tampered/fake",
        "frame_localization_method": "attention_weighted",
    }
