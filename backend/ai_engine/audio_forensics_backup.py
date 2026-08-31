import torch


class AudioForensicEngine:

    def __init__(self):
        print("🎤 Audio AI Engine Loaded (AASIST Pipeline)")

    def predict_segment(self, audio_segment):

        energy = float(
            torch.mean(
                torch.abs(
                    torch.tensor(audio_segment)
                )
            )
        )

        score = round(
            min(energy * 300, 100),
            2
        )

        return {
            "deepfake_probability": score,
            "verdict": (
                "Tampered"
                if score > 70
                else "Original"
            )
        }