def normalize_verdict(raw: str) -> str:
    if not raw:
        return "Original"
    v = str(raw).lower()
    # Preserve explicit forensic-review state
    if "expert review" in v or "review required" in v or "uncertain" in v:
        return "Requires Expert Review"
    synth = ("synthetic", "tamper", "fake", "deepfake", "manipulat",
             "edit", "forg", "spoof", "anomal", "detected")
    orig = ("original", "authentic", "bonafide", "genuine", "match", "real")
    if any(m in v for m in synth):
        return "Synthetic"
    if any(m in v for m in orig):
        return "Original"
    return "Original"


def normalize_confidence(raw) -> float:
    try:
        c = float(raw)
        if c <= 1.0:
            c *= 100.0
        return round(max(0.0, min(100.0, c)), 2)
    except Exception:
        return 0.0
