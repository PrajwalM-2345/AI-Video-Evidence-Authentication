class DatasetRegistry:
    def __init__(self):
        self.primary_datasets = {
            "FaceForensics++": "Focuses on classic manipulation (Deepfakes, Face2Face, FaceSwap, NeuralTextures) with multi-compression tiers.",
            "DFDC": "Deepfake Detection Challenge dataset. High variation in lighting, backgrounds, and diverse ethnicities.",
            "Celeb-DF v2": "High-quality deepfakes with significantly reduced visual artifacts, ideal for testing fine-boundary blending.",
            "WildDeepfake": "Real-world deepfakes harvested completely from the internet, reflecting diverse real-world scales and compressions.",
            "ForgeryNet": "Massive-scale benchmark containing multi-task annotations for both image and video-level forgery detection."
        }
        
        self.advanced_datasets = {
            "DeepFakeTIMIT": "Audio-visual deepfake dataset focusing heavily on high-quality facial swaps paired with voice mismatches.",
            "DeeperForensics-1.0": "Large-scale dataset featuring realistic face swaps with added real-world perturbations (blur, noise, transmission errors).",
            "KoDF": "Korean DeepFake dataset, addressing demographic bias by providing high-quality domestic synthetic variations.",
            "FakeAVCeleb": "Multimodal deepfake dataset featuring fully synthesized audio and video tracking simultaneously.",
            "USe this": "Custom baseline protocol buffer for manual user-targeted adversarial forensic uploads."
        }

    def get_benchmark_metadata(self):
        return {
            "primary_benchmarks": self.primary_datasets,
            "advanced_benchmarks": self.advanced_datasets
        }

dataset_registry = DatasetRegistry()
