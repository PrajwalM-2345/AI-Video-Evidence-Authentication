import torch
import torch.nn as nn
import torchvision.models as models


class TemporalVideoEvidenceAI(nn.Module):
    """
    V3 temporal video forensic detector.

    Labels:
        0 = authentic/original
        1 = tampered/fake

    Architecture:
        EfficientNet-B0
            -> feature projection
            -> temporal Transformer
            -> learned attention pooling
            -> video classifier
    """

    def __init__(
        self,
        pretrained=True,
        feature_dim=256,
        nhead=4,
        layers=2,
        dropout=0.20,
    ):
        super().__init__()

        weights = (
            models.EfficientNet_B0_Weights.DEFAULT
            if pretrained
            else None
        )

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

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=feature_dim,
            nhead=nhead,
            dim_feedforward=feature_dim * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )

        self.temporal = nn.TransformerEncoder(
            encoder_layer,
            num_layers=layers,
        )

        # Learned temporal attention.
        self.attention = nn.Sequential(
            nn.LayerNorm(feature_dim),
            nn.Linear(feature_dim, 128),
            nn.Tanh(),
            nn.Linear(128, 1),
        )

        self.video_head = nn.Sequential(
            nn.LayerNorm(feature_dim),
            nn.Linear(feature_dim, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, 2),
        )

        self.positional = nn.Parameter(
            torch.zeros(1, 64, feature_dim)
        )

        nn.init.trunc_normal_(
            self.positional,
            std=0.02,
        )

    def forward(self, frames):
        """
        frames:
            [B, T, 3, H, W]

        Returns:
            video_logits: [B, 2]
            attention:    [B, T]
        """

        b, t, c, h, w = frames.shape

        x = frames.reshape(
            b * t,
            c,
            h,
            w,
        )

        feats = self.backbone(x)

        feats = self.feature_proj(feats)

        feats = feats.reshape(
            b,
            t,
            -1,
        )

        feats = feats + self.positional[:, :t]

        temporal_features = self.temporal(feats)

        attention_logits = self.attention(
            temporal_features
        ).squeeze(-1)

        attention = torch.softmax(
            attention_logits,
            dim=1,
        )

        video_feat = torch.sum(
            temporal_features * attention.unsqueeze(-1),
            dim=1,
        )

        video_logits = self.video_head(
            video_feat
        )

        return video_logits, attention

    def freeze_backbone(self):
        for p in self.backbone.parameters():
            p.requires_grad = False

    def unfreeze_last_backbone_blocks(self, n=2):
        self.freeze_backbone()

        blocks = list(
            self.backbone.features.children()
        )

        for block in blocks[-n:]:
            for p in block.parameters():
                p.requires_grad = True

    def unfreeze_last_backbone_blocks_and_bn(self, n=3):
        self.freeze_backbone()

        blocks = list(
            self.backbone.features.children()
        )

        for block in blocks[-n:]:
            for p in block.parameters():
                p.requires_grad = True


class TemporalVideoEvidenceAIForInference(
    TemporalVideoEvidenceAI
):
    pass
