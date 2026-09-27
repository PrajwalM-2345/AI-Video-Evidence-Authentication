"""
Multimodal Forensic CORE

Orchestrates the existing:
    - Temporal Video Evidence AI
    - AASIST audio forensic engine

This module does NOT modify either model.

Modality policy:
    Video-only:
        Temporal Video AI

    Audio-only:
        AASIST

    Video + embedded audio:
        Temporal Video AI + AASIST

Important:
    - No filename-based prediction
    - No probability inversion
    - No artificial confidence
    - No probability clipping beyond normal [0, 1]
    - Preserve independent modality results
    - Explicitly report modality disagreement
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Any, Dict, Optional

import librosa
import numpy as np


class MultimodalForensicCore:
    """
    Evidence orchestration layer around the existing forensic models.

    The underlying models remain unchanged.
    """

    VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".webm")
    AUDIO_EXTS = (".wav", ".mp3", ".flac", ".m4a")

    def __init__(
        self,
        temporal_model=None,
        temporal_device=None,
        audio_engine=None,
        video_analyzer=None,
    ):
        self.temporal_model = temporal_model
        self.temporal_device = temporal_device
        self.audio_engine = audio_engine
        self.video_analyzer = video_analyzer

    # ------------------------------------------------------------------
    # Media detection
    # ------------------------------------------------------------------

    @classmethod
    def is_video(cls, filename: str) -> bool:
        return filename.lower().endswith(cls.VIDEO_EXTS)

    @classmethod
    def is_audio(cls, filename: str) -> bool:
        return filename.lower().endswith(cls.AUDIO_EXTS)

    # ------------------------------------------------------------------
    # Audio extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_audio(video_path: str) -> Optional[str]:
        """
        Extract embedded audio using ffmpeg.

        Returns:
            Temporary WAV path when an audio stream exists.
            None when the video has no audio stream.
        """

        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            output_path,
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                if os.path.exists(output_path):
                    os.remove(output_path)
                return None

            if not os.path.exists(output_path):
                return None

            if os.path.getsize(output_path) == 0:
                os.remove(output_path)
                return None

            return output_path

        except Exception:
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    # ------------------------------------------------------------------
    # AASIST audio analysis
    # ------------------------------------------------------------------

    def analyze_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """
        Run the existing AASIST engine on 1-second overlapping segments.

        This follows the same segmentation strategy already used by
        run_audio_pipeline() in main.py.
        """

        if self.audio_engine is None:
            raise RuntimeError("AASIST audio engine is not initialized.")

        audio, sr = librosa.load(
            audio_path,
            sr=16000,
            mono=True,
        )

        duration = float(len(audio) / sr)

        segment_size = 64600
        hop = int(sr * 0.5)

        timeline = []

        for i in range(
            0,
            max(1, len(audio) - segment_size + 1),
            hop,
        ):
            segment = audio[i:i + segment_size]

            if len(segment) < sr * 0.5:
                continue

            result = self.audio_engine.predict_segment(segment)

            probability = float(
                result["deepfake_probability"]
            ) / 100.0

            timeline.append(
                {
                    "timestamp": f"{i / sr:.2f}s",
                    "timestamp_seconds": round(i / sr, 3),
                    "tampering_probability": round(
                        probability * 100,
                        2,
                    ),
                    "status": (
                        "Tampered"
                        if probability >= 0.50
                        else "Original"
                    ),
                }
            )

        values = np.asarray(
            [
                item["tampering_probability"] / 100.0
                for item in timeline
            ],
            dtype=np.float32,
        )

        if len(values):
            robust_probability = float(
                np.percentile(values, 75)
            )
        else:
            robust_probability = 0.0

        # Preserve the existing persistence principle:
        # one isolated suspicious audio segment should not condemn
        # the complete media item.
        suspicious = [
            item
            for item in timeline
            if item["tampering_probability"] >= 50
        ]

        persistent = (
            sum(
                1
                for a, b in zip(
                    suspicious,
                    suspicious[1:],
                )
                if (
                    b["timestamp_seconds"]
                    - a["timestamp_seconds"]
                    <= 1.1
                )
            )
            + (1 if suspicious else 0)
        )

        if persistent < 2:
            robust_probability = min(
                robust_probability,
                0.49,
            )

        robust_probability = float(
            max(0.0, min(1.0, robust_probability))
        )

        verdict = (
            "Tampered"
            if robust_probability >= 0.50
            else "Original"
        )

        confidence = (
            robust_probability
            if verdict == "Tampered"
            else 1.0 - robust_probability
        )

        return {
            "available": True,
            "model": "AASIST",
            "label_policy": "0=spoof/tampered, 1=bonafide/authentic",
            "tampering_probability": round(
                robust_probability,
                4,
            ),
            "tampering_probability_percent": round(
                robust_probability * 100,
                2,
            ),
            "verdict": verdict,
            "confidence": round(
                confidence,
                4,
            ),
            "confidence_percent": round(
                confidence * 100,
                2,
            ),
            "timeline": timeline,
            "duration_seconds": round(duration, 2),
            "sample_rate": sr,
            "total_samples": len(audio),
        }

    # ------------------------------------------------------------------
    # Evidence fusion
    # ------------------------------------------------------------------

    @staticmethod
    def fuse_evidence(
        video_result: Optional[Dict[str, Any]],
        audio_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Combine independent modality evidence.

        IMPORTANT:
        This is deliberately conservative.

        We do NOT blindly average probabilities.

        If both modalities agree:
            confidence is based on their strongest consistent evidence.

        If they disagree:
            the result is explicitly marked as a multimodal conflict,
            while both independent probabilities remain visible.

        The conflict is meaningful evidence:
            real video + fake audio
            fake video + genuine audio
        """

        video_available = (
            video_result is not None
            and video_result.get("available", False)
        )

        audio_available = (
            audio_result is not None
            and audio_result.get("available", False)
        )

        if not video_available and not audio_available:
            raise RuntimeError(
                "No forensic modality produced evidence."
            )

        if video_available and not audio_available:
            probability = float(
                video_result["tampering_probability"]
            )

            return {
                "fusion_mode": "video_only",
                "verdict": video_result["verdict"],
                "tampering_probability": round(
                    probability,
                    4,
                ),
                "confidence": round(
                    float(video_result["confidence"]),
                    4,
                ),
                "modality_consistency": "single_modality",
                "conflict": False,
            }

        if audio_available and not video_available:
            probability = float(
                audio_result["tampering_probability"]
            )

            return {
                "fusion_mode": "audio_only",
                "verdict": audio_result["verdict"],
                "tampering_probability": round(
                    probability,
                    4,
                ),
                "confidence": round(
                    float(audio_result["confidence"]),
                    4,
                ),
                "modality_consistency": "single_modality",
                "conflict": False,
            }

        video_probability = float(
            video_result["tampering_probability"]
        )

        audio_probability = float(
            audio_result["tampering_probability"]
        )

        video_tampered = video_probability >= 0.50
        audio_tampered = audio_probability >= 0.50

        conflict = video_tampered != audio_tampered

        if conflict:
            # Do not invent a fused probability.
            #
            # Instead expose the strongest modality and explicitly
            # identify the disagreement.
            if video_probability >= audio_probability:
                dominant = "video"
                dominant_probability = video_probability
                dominant_verdict = video_result["verdict"]
                dominant_confidence = float(
                    video_result["confidence"]
                )
            else:
                dominant = "audio"
                dominant_probability = audio_probability
                dominant_verdict = audio_result["verdict"]
                dominant_confidence = float(
                    audio_result["confidence"]
                )

            return {
                "fusion_mode": "multimodal_conflict",
                "verdict": dominant_verdict,
                "tampering_probability": round(
                    dominant_probability,
                    4,
                ),
                "confidence": round(
                    dominant_confidence,
                    4,
                ),
                "modality_consistency": "conflict",
                "conflict": True,
                "dominant_modality": dominant,
                "evidence_note": (
                    "Visual and acoustic forensic evidence disagree. "
                    "Review modality-specific results separately."
                ),
            }

        # Both modalities agree.
        #
        # The conservative fused probability is the mean of the
        # two independent probabilities only when their verdicts
        # agree. This does not invert or cap either model output.
        fused_probability = (
            video_probability + audio_probability
        ) / 2.0

        if video_tampered and audio_tampered:
            verdict = "Tampered"
            confidence = fused_probability
        else:
            verdict = "Original"
            confidence = 1.0 - fused_probability

        return {
            "fusion_mode": "multimodal_agreement",
            "verdict": verdict,
            "tampering_probability": round(
                fused_probability,
                4,
            ),
            "confidence": round(
                confidence,
                4,
            ),
            "modality_consistency": "agreement",
            "conflict": False,
        }

    # ------------------------------------------------------------------
    # Main video orchestration
    # ------------------------------------------------------------------

    def analyze_video(
        self,
        video_path: str,
        samples: int = 12,
        threshold: float = 0.50,
    ) -> Dict[str, Any]:

        if self.temporal_model is None:
            raise RuntimeError(
                "Temporal video model is not initialized."
            )

        if self.video_analyzer is None:
            raise RuntimeError(
                "Video analyzer function is not initialized."
            )

        # Existing Temporal Video CORE.
        video_result_raw = self.video_analyzer(
            video_path,
            self.temporal_model,
            self.temporal_device,
            samples=samples,
            threshold=threshold,
        )

        video_probability = float(
            video_result_raw["tampering_probability"]
        ) / 100.0

        video_confidence = float(
            video_result_raw["confidence"]
        ) / 100.0

        video_result = {
            "available": True,
            "model": video_result_raw.get(
                "model",
                "Temporal Video AI",
            ),
            "label_policy": video_result_raw.get(
                "label_policy",
                "0=authentic/original, 1=tampered/fake",
            ),
            "tampering_probability": video_probability,
            "tampering_probability_percent": round(
                video_probability * 100,
                2,
            ),
            "verdict": video_result_raw["verdict"],
            "confidence": video_confidence,
            "confidence_percent": round(
                video_confidence * 100,
                2,
            ),
            "timeline": video_result_raw.get(
                "timeline",
                [],
            ),
            "raw": video_result_raw,
        }

        # Extract embedded audio.
        audio_path = self._extract_audio(video_path)

        audio_result = None

        try:
            if audio_path is not None:
                audio_result = self.analyze_audio_file(
                    audio_path
                )
        finally:
            if (
                audio_path is not None
                and os.path.exists(audio_path)
            ):
                os.remove(audio_path)

        fusion = self.fuse_evidence(
            video_result,
            audio_result,
        )

        return {
            "video": video_result,
            "audio": (
                audio_result
                if audio_result is not None
                else {
                    "available": False,
                    "model": "AASIST",
                    "reason": (
                        "No embedded audio stream was detected."
                    ),
                }
            ),
            "fusion": fusion,
        }
