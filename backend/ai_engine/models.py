import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class VideoEvidenceAI(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = models.vit_b_16(weights=models.ViT_B_16_Weights.DEFAULT)
        self.backbone.heads.head = nn.Linear(self.backbone.heads.head.in_features, 2)

        for param in self.backbone.parameters():
            param.requires_grad = False
        for param in self.backbone.heads.head.parameters():
            param.requires_grad = True

    def forward(self, x):
        return self.backbone(x)

class EfficientNetBackend(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        self.backbone.classifier[1] = nn.Linear(self.backbone.classifier[1].in_features, 2)

    def forward(self, x):
        return self.backbone(x)

class SwinTransformerBackend(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = models.swin_t(weights=models.Swin_T_Weights.DEFAULT)
        self.backbone.head = nn.Linear(self.backbone.head.in_features, 2)

    def forward(self, x):
        return self.backbone(x)

class ForensicEnsembleEngine(nn.Module):
    def __init__(self, vit_model, eff_weights_path=None, swin_weights_path=None):
        super().__init__()
        self.vit_model = vit_model
        self.vit_core = vit_model
        self.eff_model = EfficientNetBackend()
        self.swin_model = SwinTransformerBackend()

        if eff_weights_path:
            if not os.path.exists(eff_weights_path):
                raise FileNotFoundError(f"Missing EfficientNet weights: {eff_weights_path}")
            state = torch.load(eff_weights_path, map_location="cpu")
            self.eff_model.load_state_dict(state, strict=True)

        if swin_weights_path:
            if not os.path.exists(swin_weights_path):
                raise FileNotFoundError(f"Missing Swin weights: {swin_weights_path}")
            state = torch.load(swin_weights_path, map_location="cpu")
            self.swin_model.load_state_dict(state, strict=True)

        self.eval()

    def forward(self, x):
        p1 = F.softmax(self.vit_model(x), dim=1)
        p2 = F.softmax(self.eff_model(x), dim=1)
        p3 = F.softmax(self.swin_model(x), dim=1)
        return 0.15 * p1 + 0.50 * p2 + 0.35 * p3