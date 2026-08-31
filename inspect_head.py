# inspect_head.py

import torch

ckpt = torch.load(
    "models_weights/vit_evidence_checkpoint.pth",
    map_location="cpu"
)

print("HEAD WEIGHT")
print(ckpt["backbone.heads.head.weight"])

print("\nHEAD BIAS")
print(ckpt["backbone.heads.head.bias"])