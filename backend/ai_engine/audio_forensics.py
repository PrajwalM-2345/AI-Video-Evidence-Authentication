import torch
import sys

sys.path.append("/app/aasist")

from models.AASIST import Model


class AudioForensicEngine:

    def __init__(self):

        print("🎤 Loading AASIST Model...")

        self.model = Model({
            "nb_samp": 64600,
            "first_conv": 128,
            "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
            "gat_dims": [64, 32],
            "pool_ratios": [0.5, 0.7, 0.5, 0.5],
            "temperatures": [2.0, 2.0, 100.0, 100.0]
        })

        weights = torch.load(
            "/app/models_weights/aasist/AASIST.pth",
            map_location="cpu"
        )

        self.model.load_state_dict(weights)

        self.model.eval()

        print("✅ AASIST Model Loaded Successfully")

    def predict_segment(self, audio_segment):

        x = torch.tensor(
            audio_segment,
            dtype=torch.float32
        )

        target_len = 64600

        if len(x) < target_len:
            x = torch.nn.functional.pad(
                x,
                (0, target_len - len(x))
            )
        else:
            x = x[:target_len]

        x = x.unsqueeze(0)

        with torch.no_grad():
            _, logits = self.model(x)

        probs = torch.softmax(
            logits,
            dim=1
        )

        fake_prob = float(
            probs[0][1] * 100
        )

        return {
            "deepfake_probability": round(fake_prob, 2),
            "verdict": (
                "Tampered"
                if fake_prob > 50
                else "Original"
            )
        }