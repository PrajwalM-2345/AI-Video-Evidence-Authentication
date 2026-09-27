import numpy as np
import cv2


def image_ela(image_path, quality=90):
    original = cv2.imread(image_path)
    if original is None:
        return 0.0, []
    cv2.imwrite("/tmp/_ela.jpg", original, [cv2.IMWRITE_JPEG_QUALITY, quality])
    recompressed = cv2.imread("/tmp/_ela.jpg")
    diff = cv2.absdiff(original, recompressed)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    mean_score = float(gray.mean())
    thresh = max(20, mean_score * 3)
    _, mask = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 400:
            regions.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h),
                            "source": "ela"})
    return mean_score, regions[:10]


def image_copy_move(image_path, min_dist=20, max_dist=300):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []
    orb = cv2.ORB_create(1000)
    kp, des = orb.detectAndCompute(img, None)
    if des is None or len(kp) < 12:
        return []
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    try:
        matches = bf.knnMatch(des, des, k=3)
    except Exception:
        return []
    regions = []
    for group in matches:
        if len(group) < 3:
            continue
        m1, m2, _ = group
        if m1.queryIdx == m2.trainIdx:
            continue
        if m1.distance < 30 and m2.distance > m1.distance * 1.6:
            p1 = kp[m1.queryIdx].pt
            p2 = kp[m2.trainIdx].pt
            d = float(np.hypot(p1[0] - p2[0], p1[1] - p2[1]))
            if min_dist < d < max_dist:
                x, y = int(p1[0]), int(p1[1])
                regions.append({"x": x - 20, "y": y - 20, "w": 40, "h": 40,
                                "source": "copy_move"})
    return regions[:10]


def detect_image_manual_edit(image_path, threshold=8.0):
    ela_mean, ela_regions = image_ela(image_path)
    copy_regions = image_copy_move(image_path)
    all_regions = ela_regions + copy_regions
    flagged = (ela_mean > threshold) or (len(copy_regions) > 0)
    return {
        "manual_edit_detected": flagged,
        "ela_mean_score": round(ela_mean, 3),
        "copy_move_count": len(copy_regions),
        "suspicious_regions": all_regions,
        "verdict": "Synthetic" if flagged else "Original",
    }


def detect_video_manual_edit(video_path, threshold_factor=3.0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"manual_edit_detected": False, "reason": "Cannot open video",
                "verdict": "Original", "suspicious_cuts": []}
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # CAP: never scan more than 60 frames regardless of video length
    MAX_SCAN = 30
    if total_frames > 0:
        step = max(1, total_frames // MAX_SCAN)
    else:
        step = 1
    prev = None
    idx = 0
    diffs = []
    times = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        # Skip frames to stay under MAX_SCAN
        if idx % step != 0:
            idx += 1
            continue
        g = cv2.cvtColor(cv2.resize(frame, (160, 90)), cv2.COLOR_BGR2GRAY)
        if prev is not None:
            d = float(np.mean(cv2.absdiff(g, prev)))
            diffs.append(d)
            times.append(idx / max(fps, 1e-6))
        prev = g
        idx += 1
    cap.release()
    if not diffs:
        return {"manual_edit_detected": False, "suspicious_cuts": [],
                "verdict": "Original", "total_frames": idx}
    arr = np.array(diffs)
    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med))) + 1e-6
    thresh = med + threshold_factor * mad
    cuts = []
    for i, d in enumerate(diffs):
        if d > thresh and d > 15.0:
            cuts.append({"frame_number": i + 1,
                         "timestamp_seconds": round(times[i], 3),
                         "frame_difference": round(d, 3)})
    flagged = len(cuts) > 2
    return {
        "manual_edit_detected": flagged,
        "total_frames": idx,
        "median_frame_diff": round(med, 3),
        "threshold_used": round(thresh, 3),
        "suspicious_cuts": cuts[:25],
        "verdict": "Synthetic" if flagged else "Original",
    }


def detect_audio_manual_edit(audio, sr, threshold_factor=4.0):
    import librosa
    if audio is None or len(audio) < sr:
        return {"manual_edit_detected": False, "suspicious_splices": [],
                "verdict": "Original"}
    S = np.abs(librosa.stft(audio, n_fft=1024, hop_length=512))
    if S.shape[1] < 2:
        return {"manual_edit_detected": False, "suspicious_splices": [],
                "verdict": "Original"}
    flux = np.sqrt(np.sum(np.diff(S, axis=1) ** 2, axis=0))
    med = float(np.median(flux))
    mad = float(np.median(np.abs(flux - med))) + 1e-6
    thresh = med + threshold_factor * mad
    hop_time = 512 / sr
    splices = []
    for i, f in enumerate(flux):
        if f > thresh:
            splices.append({"timestamp_seconds": round(i * hop_time, 3),
                            "spectral_flux": round(float(f), 3)})
    flagged = len(splices) > 3
    return {
        "manual_edit_detected": flagged,
        "median_flux": round(med, 4),
        "threshold_used": round(thresh, 4),
        "suspicious_splices": splices[:25],
        "verdict": "Synthetic" if flagged else "Original",
    }
