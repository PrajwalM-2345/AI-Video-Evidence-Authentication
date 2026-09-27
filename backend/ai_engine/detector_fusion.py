"""
Detector Fusion Module.

Combines 6 independent detectors:
  1. v4 neural model           (face-swap deepfake specialist)
  2. Frequency detector        (AI-generated specialist)
  3. PRNU detector             (sensor noise / edit specialist)
  4. Compression detector      (re-encode specialist)
  5. ELA detector              (manual edit / splice specialist)
  6. Chroma detector           (social media re-encode specialist)

Fusion logic (v4-veto):
  - If v4 says Original with confidence >= 0.70 -> verdict Original
    (heuristics act as advisory only)
  - If v4 says Synthetic with confidence >= 0.70 -> verdict Synthetic
  - If v4 is uncertain (0.30 <= conf < 0.70) -> majority vote of all detectors
  - Confidence always based on number of agreeing detectors
  - Frame/region intervals merged from all detectors that flagged

The output always includes:
  - verdict: "Original" | "Synthetic" | "Requires Expert Review"
  - confidence: 0-100
  - per_detector: dict of individual results
  - signals_triggered: list of detector names that flagged Synthetic
  - reviewer_flag: True when uncertain or heuristic-only
"""

from __future__ import annotations


V4_VETO_HIGH = 0.80        # v4 must be >=80% confident to auto-decide
V4_VETO_ORIGINAL = 0.60    # v4 >=60% confident Original => accept
V4_VETO_LOW = 0.30


def _get_v4_confidence(v4_result):
    """Extract v4 verdict and its confidence as a 0-1 float."""
    if not v4_result or not v4_result.get("available", True):
        return "unknown", 0.0
    verdict = v4_result.get("verdict", "Original")
    conf = v4_result.get("confidence", 0.0)
    try:
        conf = float(conf)
        if conf > 1.0:
            conf = conf / 100.0
    except Exception:
        conf = 0.0
    return verdict, conf


def _collect_heuristic_flags(heuristic_results):
    """Return (list_of_flagged_names, average_probability)."""
    names = []
    probs = []
    for name, r in heuristic_results.items():
        if r is None:
            continue
        if not r.get("available", True):
            continue
        probs.append(float(r.get("fake_probability", 0.0)))
        if r.get("verdict") == "Synthetic":
            names.append(name)
    avg = sum(probs) / len(probs) if probs else 0.0
    return names, avg


def _merge_regions(heuristic_results):
    """Collect all suspicious regions from image heuristics."""
    merged = []
    for name, r in heuristic_results.items():
        if r is None:
            continue
        for reg in r.get("regions", []):
            reg_copy = dict(reg)
            reg_copy["detector"] = name
            merged.append(reg_copy)
    return merged


def _merge_intervals(video_result, heuristic_results):
    """Collect intervals from video model and heuristics."""
    merged = []
    if video_result and isinstance(video_result, dict):
        for iv in video_result.get("tampering_intervals", []) or []:
            merged.append({
                "start_seconds": iv.get("start_seconds"),
                "end_seconds": iv.get("end_seconds"),
                "source": "v4_model",
            })
    return merged


def fuse(
    media_type,
    v4_result=None,
    frequency_result=None,
    prnu_result=None,
    compression_result=None,
    ela_result=None,
    chroma_result=None,
):
    """
    media_type: "video" | "image" | "audio"
    v4_result:  output from video/image ensemble (or None for audio)
    All other results: dicts from dynamic detectors
    """
    heuristic_results = {
        "frequency": frequency_result,
        "prnu": prnu_result,
        "compression": compression_result,
        "ela": ela_result,
        "chroma": chroma_result,
    }

    v4_verdict, v4_conf = _get_v4_confidence(v4_result)
    flagged_names, heur_avg = _collect_heuristic_flags(heuristic_results)

    signals = []
    reviewer_flag = False

    # Case 1: v4 says Original with reasonable confidence
    if v4_verdict == "Original" and v4_conf >= V4_VETO_ORIGINAL:
        final = "Original"
        confidence = round(v4_conf * 100, 2)
        if flagged_names:
            reviewer_flag = True
            signals.append("heuristics_disagree_with_v4")
        signals.append("v4_confident_original")

    # Case 2: v4 says Synthetic AND heuristics support it OR v4 is very confident
    elif v4_verdict == "Synthetic" and v4_conf >= V4_VETO_HIGH:
        final = "Synthetic"
        confidence = round(v4_conf * 100, 2)
        signals.append("v4_confident_synthetic")
        for n in flagged_names:
            signals.append(f"{n}_agrees")

    # Case 2b: v4 says Synthetic with moderate confidence AND heuristics agree
    elif v4_verdict == "Synthetic" and v4_conf >= 0.60 and len(flagged_names) >= 2:
        final = "Synthetic"
        confidence = round(v4_conf * 100, 2)
        signals.append("v4_moderate_synthetic_with_support")
        for n in flagged_names:
            signals.append(f"{n}_agrees")

    # Case 2c: v4 says Synthetic with moderate confidence but heuristics disagree
    # -> fall back to majority vote across all detectors
    elif v4_verdict == "Synthetic" and v4_conf >= 0.60:
        synth_votes = len(flagged_names) + 1   # +1 for v4
        orig_votes = 5 - len(flagged_names)
        if synth_votes > orig_votes:
            final = "Synthetic"
            confidence = round(v4_conf * 100, 2)
            signals.append("majority_synthetic")
        else:
            final = "Original"
            confidence = round((1.0 - v4_conf) * 100, 2)
            signals.append("majority_original_overrides_v4")
        for n in flagged_names:
            signals.append(f"{n}_agrees")
        if synth_votes <= orig_votes:
            signals.append("v4_moderate_synthetic_heuristics_disagree")

    # Case 3: v4 uncertain OR v4 unavailable
    else:
        # Fall back to heuristics
        if len(flagged_names) >= 3:
            final = "Synthetic"
            confidence = round(heur_avg * 100, 2)
            signals = flagged_names[:]
        elif len(flagged_names) == 2 and heur_avg >= 0.6:
            final = "Synthetic"
            confidence = round(heur_avg * 100, 2)
            signals = flagged_names[:]
        elif len(flagged_names) == 0:
            final = "Original"
            confidence = round((1.0 - heur_avg) * 100, 2)
            signals.append("all_detectors_original")
        else:
            # Fall back to majority vote: never emit "Requires Review"
            synth_votes = len(flagged_names)
            orig_votes = 5 - synth_votes
            if synth_votes > orig_votes:
                final = "Synthetic"
                confidence = round(heur_avg * 100, 2)
            else:
                final = "Original"
                confidence = round((1.0 - heur_avg) * 100, 2)
            signals = flagged_names[:]
            signals.append("majority_fallback")

        if v4_verdict != "unknown":
            signals.append(f"v4_uncertain({v4_verdict})")

    # Region / interval merging
    regions = _merge_regions(heuristic_results)
    intervals = _merge_intervals(v4_result, heuristic_results)

    return {
        "verdict": final,
        "confidence": confidence,
        "signals_triggered": signals,
        "reviewer_flag": reviewer_flag,
        "per_detector": {
            "v4_model": v4_result,
            "frequency": frequency_result,
            "prnu": prnu_result,
            "compression": compression_result,
            "ela": ela_result,
            "chroma": chroma_result,
        },
        "tampering_regions": regions,
        "tampering_intervals": intervals,
        "fusion_note": (
            "v4 neural model holds veto power when confidence >= 70%. "
            "Heuristic detectors support the verdict on non-face-swap domains."
        ),
    }
