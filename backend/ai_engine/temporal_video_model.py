import torch
import torch.nn as nn
import torchvision.models as models


class TemporalVideoEvidenceAI(nn.Module):
    """Video-level detector with per-frame auxiliary scores.

    Labels are fixed globally:
      0 = authentic/original
      1 = tampered/fake
    """

    def __init__(self, pretrained=True, feature_dim=512, nhead=8, layers=2, dropout=0.15):
        super().__init__()
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        backbone = models.efficientnet_b0(weights=weights)
        in_features = backbone.classifier[1].in_features
        backbone.classifier = nn.Identity()
        self.backbone = backbone
        self.feature_proj = nn.Sequential(
            nn.Linear(in_features, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        enc_layer = nn.TransformerEncoderLayer(
            d_model=feature_dim,
            nhead=nhead,
            dim_feedforward=feature_dim * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.temporal = nn.TransformerEncoder(enc_layer, num_layers=layers)
        self.frame_head = nn.Sequential(
            nn.LayerNorm(feature_dim),
            nn.Linear(feature_dim, 2),
        )
        self.video_head = nn.Sequential(
            nn.LayerNorm(feature_dim),
            nn.Linear(feature_dim, 2),
        )
        self.positional = nn.Parameter(torch.zeros(1, 64, feature_dim))
        nn.init.trunc_normal_(self.positional, std=0.02)

    def forward(self, frames):
        # frames: [B,T,3,H,W]
        b, t, c, h, w = frames.shape
        x = frames.reshape(b * t, c, h, w)
        feats = self.backbone(x)
        feats = self.feature_proj(feats).reshape(b, t, -1)
        feats = feats + self.positional[:, :t]
        feats = self.temporal(feats)

        frame_logits = self.frame_head(feats)
        # Attention-like robust pooling: use mean of temporal features.
        video_feat = feats.mean(dim=1)
        video_logits = self.video_head(video_feat)
        return video_logits, frame_logits

    def freeze_backbone(self):
        for p in self.backbone.parameters():
            p.requires_grad = False

    def unfreeze_last_backbone_blocks(self, n=2):
        self.freeze_backbone()
        blocks = list(self.backbone.features.children())
        for block in blocks[-n:]:
            for p in block.parameters():
                p.requires_grad = True


class TemporalVideoEvidenceAIForInference(TemporalVideoEvidenceAI):
    pass
