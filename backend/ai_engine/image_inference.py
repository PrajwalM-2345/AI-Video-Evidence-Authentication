import os
import cv2
import torch
from PIL import Image

from .dataset_loader import vit_transform
from .face_analysis import ForensicFaceAnalyzer
from .manual_edit_detector import detect_image_manual_edit
from .verdict_normalizer import normalize_verdict, normalize_confidence

_face_analyzer = None


def _get_face_analyzer():
    global _face_analyzer
    if _face_analyzer is None:
        _face_analyzer = ForensicFaceAnalyzer()
    return _face_analyzer


def _tensor_from_path(path, device):
    img = Image.open(path).convert("RGB")
    return vit_transform(img).unsqueeze(0).to(device)


def _fake_prob(model, tensor):
    with torch.no_grad():
        p = model(tensor)
    if p.dim() == 2:
        return float(p[0, 0].cpu())
    return float(p[0].cpu())


def analyze_image(image_path, ensemble_model, device, threshold=0.65):
    result = {
        "media_type": "image",
        "model": "ForensicEnsembleEngine (ViT+EffNet+Swin)",
        "threshold_used": threshold,
    }

    whole_fake = 0.0
    if ensemble_model is not None:
        try:
            t = _tensor_from_path(image_path, device)
            whole_fake = _fake_prob(ensemble_model, t)
        except Exception as e:
            result["ensemble_error"] = str(e)

    result["whole_image"] = {
        "fake_probability": round(whole_fake, 4),
        "fake_probability_percent": round(whole_fake * 100, 2),
        "verdict": "Synthetic" if whole_fake >= threshold else "Original",
    }

    faces = []
    try:
        if ensemble_model is not None:
            img_bgr = cv2.imread(image_path)
            if img_bgr is not None:
                crop, lms = _get_face_analyzer().extract_and_align_face(img_bgr)
                if crop is not None and crop.size > 0:
                    tmp = "/tmp/_face.jpg"
                    cv2.imwrite(tmp, crop)
                    fp = _fake_prob(ensemble_model, _tensor_from_path(tmp, device))
                    faces.append({
                        "face_index": 0,
                        "fake_probability": round(fp, 4),
                        "fake_probability_percent": round(fp * 100, 2),
                        "verdict": "Synthetic" if fp >= threshold else "Original",
                        "landmarks_detected": (len(lms) // 3) if lms else 0,
                    })
    except Exception as e:
        result["face_error"] = str(e)

    result["face_level"] = faces if faces else "no_face_detected"

    try:
        result["manual_edit_analysis"] = detect_image_manual_edit(image_path)
    except Exception as e:
        result["manual_edit_analysis"] = {"error": str(e), "verdict": "Original",
                                          "suspicious_regions": []}

    signals = []
    if whole_fake >= threshold:
        signals.append("ensemble")
    if any(f["fake_probability"] >= threshold for f in faces):
        signals.append("face")

    # Manual-edit heuristic is ADVISORY ONLY.
    # It contributes to the verdict ONLY when the ensemble/face is already
    # at least mildly suspicious (>= 0.35), to avoid false positives from
    # ELA / ORB noise on clean JPEGs.
    manual_flag = bool(result["manual_edit_analysis"].get("manual_edit_detected"))
    ensemble_mildly_suspicious = whole_fake >= 0.35
    face_mildly_suspicious = any(f["fake_probability"] >= 0.35 for f in faces)

    if manual_flag and (ensemble_mildly_suspicious or face_mildly_suspicious):
        signals.append("manual_edit")
    elif manual_flag:
        result["manual_edit_analysis"]["manual_edit_note"] = (
            "Manual-edit heuristic flagged but ensemble is confident Original; "
            "reported as advisory only."
        )

    final_verdict = "Synthetic" if signals else "Original"

    vals = [whole_fake * 100]
    vals += [f["fake_probability"] * 100 for f in faces]
    if "manual_edit" in signals:
        vals.append(max(whole_fake * 100, 55.0))
    conf = max(vals) if signals else (100.0 - whole_fake * 100)

    result["verdict"] = normalize_verdict(final_verdict)
    result["confidence"] = normalize_confidence(conf)
    result["signals_triggered"] = signals
    result["tampering_regions"] = result["manual_edit_analysis"].get("suspicious_regions", [])
    result["tampering_intervals"] = []
    return result
