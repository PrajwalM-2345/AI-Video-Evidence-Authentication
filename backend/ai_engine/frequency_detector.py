"""
Frequency-domain detector for AI-generated (GAN / Diffusion) media.

Method:
  - Convert frame(s) to grayscale
  - Compute 2D FFT
  - Analyze radial power spectrum
  - AI-generated content has characteristic high-frequency energy deficit
    (due to upsampling artifacts in the generator) and periodic peaks
    (from GAN upsampling layers).

Signals:
  - high_freq_ratio:  ratio of high-frequency energy to total
  - spectral_peaks:   count of abnormally strong peaks in spectrum
  - verdict:          "Synthetic" if signals indicate AI generation

Reference:
  Frank et al. (2020), "Leveraging Frequency Analysis for Deep Fake
  Image Recognition"
  Durall et al. (2020), "Watch your Up-Convolution: CNN Based
  Generative Architectures are Still Not Able to Reproduce Spectral
  Distributions"

This is a heuristic. False positives possible on heavily-compressed
or upscaled real content.
"""

import numpy as np
import cv2


def _radial_spectrum(gray):
    """Compute 2D FFT and radial average spectrum."""
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)

    h, w = magnitude.shape
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2).astype(np.int32)

    r_max = int(min(cy, cx))
    spectrum = np.zeros(r_max, dtype=np.float32)
    for radius in range(r_max):
        mask = (r == radius)
        if mask.any():
            spectrum[radius] = magnitude[mask].mean()
    return spectrum


def analyze_frame_frequency(frame_bgr):
    """Return per-frame frequency analysis."""
    if frame_bgr is None:
        return None
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256))

    # Hann window to reduce edge artifacts
    win = np.outer(np.hanning(256), np.hanning(256)).astype(np.float32)
    gray_w = gray.astype(np.float32) * win

    spectrum = _radial_spectrum(gray_w)
    if spectrum.sum() <= 0:
        return {"high_freq_ratio": 0.0, "spectral_peak_count": 0,
                "mean_high_freq": 0.0}

    total = spectrum.sum()
    # High frequencies: outer half of radii
    half = len(spectrum) // 2
    high_freq = spectrum[half:].sum()
    high_freq_ratio = float(high_freq / total)

    # Spectral peaks: local maxima significantly above local mean
    peaks = 0
    if len(spectrum) > 20:
        # Log spectrum for stability
        log_s = np.log(spectrum + 1e-9)
        # Smooth
        kernel = np.ones(5) / 5.0
        smooth = np.convolve(log_s, kernel, mode="same")
        for i in range(5, len(smooth) - 5):
            window = smooth[max(0, i - 5):min(len(smooth), i + 6)]
            if smooth[i] == window.max() and smooth[i] > window.mean() + 0.8:
                peaks += 1

    return {
        "high_freq_ratio": round(high_freq_ratio, 4),
        "spectral_peak_count": int(peaks),
        "mean_high_freq": round(float(spectrum[half:].mean()), 2),
    }


def detect_ai_generated_image(image_path, threshold_hf=0.35, threshold_peaks=3):
    """Return analysis dict for a single image."""
    img = cv2.imread(image_path)
    if img is None:
        return {"available": False, "reason": "Cannot read image",
                "verdict": "Original", "fake_probability": 0.0}

    per_frame = analyze_frame_frequency(img)
    if per_frame is None:
        return {"available": False, "reason": "Analysis failed",
                "verdict": "Original", "fake_probability": 0.0}

    hf = per_frame["high_freq_ratio"]
    peaks = per_frame["spectral_peak_count"]

    # Heuristic scoring: AI-generated media often has BOTH low high-freq
    # energy AND periodic peaks from upsampling
    score = 0.0
    if hf < threshold_hf:
        score += 0.5
    if peaks >= threshold_peaks:
        score += 0.5

    verdict = "Synthetic" if score >= 0.5 else "Original"

    return {
        "available": True,
        "method": "Radial FFT spectrum analysis",
        "high_freq_ratio": hf,
        "spectral_peak_count": peaks,
        "fake_probability": round(score, 4),
        "verdict": verdict,
        "disclaimer": "Frequency heuristic only. Do not rely on alone.",
    }


def detect_ai_generated_video(video_path, max_frames=8):
    """Sample frames from video and aggregate frequency signals."""
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
        fa = analyze_frame_frequency(frame)
        if fa is None:
            continue
        hf = fa["high_freq_ratio"]
        peaks = fa["spectral_peak_count"]
        s = 0.0
        if hf < 0.35:
            s += 0.5
        if peaks >= 3:
            s += 0.5
        scores.append(s)
    cap.release()

    if not scores:
        return {"available": False, "reason": "No decodable frames",
                "verdict": "Original", "fake_probability": 0.0}

    mean_score = float(np.mean(scores))
    flagged_ratio = float(sum(1 for s in scores if s >= 0.5) / len(scores))

    # Aggregate: if more than half of frames look AI-generated, flag video
    verdict = "Synthetic" if flagged_ratio >= 0.5 else "Original"

    return {
        "available": True,
        "method": "Radial FFT spectrum analysis (aggregated)",
        "frames_analyzed": len(scores),
        "mean_score": round(mean_score, 4),
        "flagged_ratio": round(flagged_ratio, 4),
        "fake_probability": round(mean_score, 4),
        "verdict": verdict,
        "disclaimer": "Frequency heuristic only. Do not rely on alone.",
    }
