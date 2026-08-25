# backend/report_generator.py
import io
import base64
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    PageBreak,
    Flowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab import pdfbase
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as pdfcanvas


# ============================================================
# FONT SETUP
# ============================================================

FONT_NAME = "Times-Roman"
FONT_BOLD = "Times-Bold"
FONT_MONO = "Courier"

try:
    pdfbase.registerFont(TTFont("Cambria", "Cambria.ttf"))
    pdfbase.registerFont(TTFont("Cambria-Bold", "Cambriab.ttf"))
    FONT_NAME = "Cambria"
    FONT_BOLD = "Cambria-Bold"
except Exception:
    pass


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_get(d: Dict[str, Any], keys: List[str], default: Any = "N/A") -> Any:
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] not in [None, ""]:
            return d[k]
    return default


def _safe_text(value: Any, default: str = "N/A") -> str:
    if value in [None, ""]:
        return default
    return str(value)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in [None, ""]:
            return default
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in [None, ""]:
            return default
        return float(value)
    except Exception:
        return default


def _decode_b64_image(b64_value: str) -> Optional[io.BytesIO]:
    try:
        return io.BytesIO(base64.b64decode(b64_value))
    except Exception:
        return None


def _fmt_dt_utc() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def _short_hash(v: str, n: int = 20) -> str:
    v = _safe_text(v, "")
    if len(v) <= n:
        return v
    return v[:n] + "..."


def _risk_level(score: float) -> Tuple[str, str, colors.Color]:
    if score < 25:
        return "LOW", "#059669", colors.HexColor("#ECFDF5")
    if score < 50:
        return "MEDIUM", "#D97706", colors.HexColor("#FFFBEB")
    if score < 75:
        return "HIGH", "#EA580C", colors.HexColor("#FFF7ED")
    return "CRITICAL", "#DC2626", colors.HexColor("#FEF2F2")


def _verdict_palette(verdict: str) -> Tuple[bool, colors.Color, colors.Color, str]:
    is_tampered = ("Tampering" in verdict) or ("Synthetic" in verdict)
    bg = colors.HexColor("#FEF2F2") if is_tampered else colors.HexColor("#ECFDF5")
    border = colors.HexColor("#FCA5A5") if is_tampered else colors.HexColor("#6EE7B7")
    txt = "#991B1B" if is_tampered else "#065F46"
    return is_tampered, bg, border, txt


def _legend_items() -> List[List[str]]:
    return [
        ["Indicator", "Meaning", "Action"],
        ["VERIFIED", "No strong tampering indicators detected", "Proceed with normal review"],
        ["FLAGGED", "Suspicious inconsistencies were found", "Manual examination recommended"],
        ["Risk LOW", "Minor anomalies only", "Document and archive"],
        ["Risk MEDIUM", "Noticeable irregularities", "Escalate for review"],
        ["Risk HIGH", "Strong manipulation signals", "Deep forensic analysis"],
        ["Risk CRITICAL", "Severe evidence compromise", "Immediate escalation"],
    ]


def _resolve_forensics_item(forensics: Dict[str, Any], primary: str, fallback: List[str] = None) -> Dict[str, Any]:
    fallback = fallback or []
    if isinstance(forensics.get(primary), dict):
        return forensics.get(primary, {})
    for key in fallback:
        if isinstance(forensics.get(key), dict):
            return forensics.get(key, {})
    return {}


# ============================================================
# FLOWABLES
# ============================================================

class SectionBookmark(Flowable):
    def __init__(self, key: str, title: str, level: int = 0):
        super().__init__()
        self.key = key
        self.title = title
        self.level = level

    def wrap(self, availWidth, availHeight):
        return 0, 0

    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, level=self.level, closed=False)


class Badge(Flowable):
    def __init__(self, text: str, fill: str, text_color: str = "#ffffff", width: int = 92, height: int = 18):
        super().__init__()
        self.text = text
        self.fill = colors.HexColor(fill)
        self.text_color = colors.HexColor(text_color)
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(self.fill)
        self.canv.setStrokeColor(self.fill)
        self.canv.roundRect(0, 0, self.width, self.height, 6, stroke=1, fill=1)
        self.canv.setFillColor(self.text_color)
        self.canv.setFont(FONT_BOLD, 8)
        self.canv.drawCentredString(self.width / 2, 5, self.text)
        self.canv.restoreState()


class SummaryCard(Flowable):
    def __init__(self, title: str, value: str, accent: str, width: int = 125, height: int = 58):
        super().__init__()
        self.title = title
        self.value = value
        self.accent = colors.HexColor(accent)
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(colors.HexColor("#F8FAFC"))
        self.canv.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.canv.roundRect(0, 0, self.width, self.height, 10, stroke=1, fill=1)

        self.canv.setFillColor(colors.HexColor("#475569"))
        self.canv.setFont(FONT_BOLD, 8.4)
        self.canv.drawString(10, self.height - 16, self.title)

        self.canv.setFillColor(self.accent)
        self.canv.setFont(FONT_BOLD, 12.2)
        self.canv.drawString(10, self.height - 36, self.value[:24])

        self.canv.restoreState()


# ============================================================
# PAGE NUMBER CANVAS
# ============================================================

class PageNumCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(page_count)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont(FONT_NAME, 8)
        self.setFillColor(colors.HexColor("#64748B"))
        width, _ = letter
        self.drawRightString(width - 45, 28, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


# ============================================================
# STAMP DRAWING
# ============================================================

def _draw_verified_stamp(c: pdfcanvas.Canvas, x, y, verified: bool = True, angle: int = -12):
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)

    main = colors.HexColor("#047857") if verified else colors.HexColor("#B91C1C")
    fill_tint = (
        colors.Color(0.02, 0.47, 0.34, alpha=0.05)
        if verified
        else colors.Color(0.73, 0.11, 0.11, alpha=0.05)
    )
    label_mid = "VERIFIED" if verified else "FLAGGED"
    top_text = "PHOENIX FORENSICS LAB"
    blockchain_status = (
        data.get("blockchain_ledger_receipt", {})
            .get("status", "")
            .lower()
    )

    verified = blockchain_status == "success" if verified else "MANUAL REVIEW REQUIRED"

    outer_r = 58
    inner_r = 49

    c.setFillColor(fill_tint)
    c.setStrokeColor(main)
    c.setLineWidth(2.4)
    c.circle(0, 0, outer_r, stroke=1, fill=1)
    c.setLineWidth(1)
    c.circle(0, 0, inner_r, stroke=1, fill=0)

    def draw_arc_text(text, radius, start_deg, font, size):
        c.setFont(font, size)
        angle_local = math.radians(start_deg)
        for ch in text.upper():
            ch_width = c.stringWidth(ch, font, size)
            theta = angle_local + (ch_width / 2) / radius
            x2 = radius * math.sin(theta)
            y2 = radius * math.cos(theta)
            c.saveState()
            c.translate(x2, y2)
            c.rotate(-math.degrees(theta))
            c.drawCentredString(0, 0, ch)
            c.restoreState()
            angle_local += ch_width / radius

    c.setFillColor(main)
    draw_arc_text(top_text, outer_r - 9, -70, FONT_BOLD, 6.6)
    draw_arc_text(bot_text, outer_r - 9, 250, FONT_BOLD, 6.2)

    c.setLineWidth(1)
    c.line(-30, 4, -18, 4)
    c.line(18, 4, 30, 4)

    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(0, -2, label_mid)

    c.setLineWidth(2.2)
    c.setStrokeColor(main)
    c.setLineCap(1)
    if verified:
        c.line(-9, -20, -2, -27)
        c.line(-2, -27, 11, -13)
    else:
        c.line(-8, -14, 8, -28)
        c.line(8, -14, -8, -28)

    c.restoreState()


# ============================================================
# PAGE DECORATIONS
# ============================================================

def _page_decorations(c: pdfcanvas.Canvas, doc, data: dict):
    width, height = letter
    c.saveState()

    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.setLineWidth(0.75)
    c.rect(18, 18, width - 36, height - 36, stroke=1, fill=0)

    c.saveState()
    c.setFillColor(colors.Color(0.06, 0.09, 0.16, alpha=0.035))
    c.setFont(FONT_BOLD, 62)
    c.translate(width / 2, height / 2)
    c.rotate(38)
    c.drawCentredString(0, 0, "PHOENIX FORENSIC GATEWAY")
    c.restoreState()

    c.setFillColor(colors.HexColor("#94A3B8"))
    c.setFont(FONT_NAME, 7.5)
    c.drawString(45, 28, "Phoenix Digital Forensics Lab — Confidential Evidentiary Document")

    if doc.page == 1:
        verdict = data.get("ai_model_inference", {}).get("verdict", "")
        is_tampered = ("Tampering" in verdict) or ("Synthetic" in verdict)
        _draw_verified_stamp(c, width - 110, height - 130, verified=not is_tampered)

    c.restoreState()


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_forensic_pdf(data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    story: List[Any] = []

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportDocTitle",
        parent=styles["Heading1"],
        fontName=FONT_BOLD,
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "ReportDocSubtitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#10B981"),
        spaceAfter=10,
    )

    section_heading = ParagraphStyle(
        "ReportSectionHeading",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "ReportBodyText",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#334155"),
    )

    code_style = ParagraphStyle(
        "ReportCodeText",
        parent=styles["Code"],
        fontName=FONT_MONO,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0891B2"),
    )

    center_small = ParagraphStyle(
        "CenterSmall",
        parent=body_style,
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.HexColor("#64748B"),
    )

    # ========================================================
    # DATA RESOLUTION
    # ========================================================

    verdict = _safe_text(data.get("ai_model_inference", {}).get("verdict", "N/A"))
    confidence = _safe_get(
        data.get("ai_model_inference", {}),
        ["confidence_score_percentage", "confidence", "score"],
        "N/A",
    )
    risk = _safe_float(data.get("risk_score", 0), 0.0)
    risk_level, risk_color, risk_bg = _risk_level(risk)
    is_tampered, verdict_bg, verdict_border, verdict_text_color = _verdict_palette(verdict)

    block_receipt = data.get("blockchain_ledger_receipt", {})
    forensics = data.get("forensics", {})
    timeline = (
        data.get("timeline")
        or data.get("audio_timeline")
        or []
    )


    gallery = data.get("tampered_frames_gallery", [])

    waveform_points = data.get("waveform_points", [])

    block_number = _safe_get(block_receipt, ["block_number", "blockNumber", "block_no", "blockNo"])
    tx_hash = _safe_get(block_receipt, ["transaction_hash", "tx_hash", "transactionHash"])
    gas_used = _safe_get(block_receipt, ["gas_used", "gasUsed"])
    status = _safe_get(block_receipt, ["status"])

    evidence_hash = _safe_get(
        data.get("hash_verification", {}),
        ["sha256_hash", "hash", "sha256"],
    )

    cert_id = _short_hash(evidence_hash, 16).upper()
    gen_date = datetime.utcnow().strftime("%d %B %Y")

    # ========================================================
    # COVER PAGE / HERO
    # ========================================================

    story.append(Spacer(1, 4))

    report_title = (
        "AUDIO AUTHENTICITY INVESTIGATION REPORT"
        if data.get("media_type") == "audio"
        else "VIDEO AUTHENTICITY INVESTIGATION REPORT"
    )

    story.append(
        Paragraph(
            "PHOENIX DIGITAL FORENSICS LAB",
            title_style
        )
    )

    story.append(
        Paragraph(
            report_title,
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"Generated: {_fmt_dt_utc()}",
            body_style
        )
    )

    story.append(Spacer(1, 8))

    summary_cards = [
        SummaryCard("Verdict", verdict, verdict_text_color, width=125),
        SummaryCard("Confidence", f"{confidence}%", "#0F766E", width=125),
        SummaryCard("Risk", f"{risk_level}", risk_color, width=125),
        SummaryCard("Certificate", f"PFG-{cert_id}", "#1D4ED8", width=125),
    ]
    story.append(Table([summary_cards], colWidths=[125, 125, 125, 125]))
    story.append(Spacer(1, 10))

    # ========================================================
    # EXECUTIVE SUMMARY
    # ========================================================

    story.append(Paragraph("EXECUTIVE SUMMARY", section_heading))
    story.append(SectionBookmark("executive_summary", "Executive Summary"))

    summary_rows = [
        ["Verdict", verdict],
        ["Confidence", f"{confidence}%"],
        ["Evidence Hash", _short_hash(evidence_hash, 24)],
        ["Blockchain", status],
    ]
    summary_table = Table(summary_rows, colWidths=[180, 340])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # ========================================================
    # SECTION 1: HASH
    # ========================================================

    story.append(Paragraph("1. Cryptographic Integrity Signatures", section_heading))
    story.append(SectionBookmark("cryptographic_integrity", "Cryptographic Integrity Signatures"))

    hash_data = [
        [Paragraph("<b>Target SHA-256 Checksum Fingerprint:</b>", body_style)],
        [Paragraph(f"<code>{evidence_hash}</code>", code_style)],
    ]
    t_hash = Table(hash_data, colWidths=[520])
    t_hash.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("LINELEFT", (0, 0), (0, -1), 3, colors.HexColor("#10B981")),
    ]))
    story.append(t_hash)
    story.append(Spacer(1, 10))

    # ========================================================
    # SECTION 2: AI INFERENCE
    # ========================================================

    story.append(Paragraph("2. Neural Core Classification Output", section_heading))
    story.append(SectionBookmark("neural_core", "Neural Core Classification Output"))

    verdict_html = f"<font color='{verdict_text_color}'><b>{verdict.upper()}</b></font>"
    inference_table_data = [
        [Paragraph("<b>Evaluation Verdict:</b>", body_style), Paragraph(verdict_html, body_style)],
        [Paragraph("<b>Core Classification Profile:</b>", body_style), Paragraph(f"<b>{_safe_text(data.get('ai_model_inference', {}).get('manipulation_classification', 'N/A'))}</b>", body_style)],
        [Paragraph("<b>Model Confidence Score:</b>", body_style), Paragraph(f"{confidence}%", body_style)],
        [Paragraph("<b>Alignment Benchmark Target:</b>", body_style), Paragraph(_safe_text(data.get('ai_model_inference', {}).get('dataset_alignment_benchmark', 'N/A')), body_style)],
    ]
    t_inference = Table(inference_table_data, colWidths=[180, 340])
    t_inference.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), verdict_bg),
        ("BOX", (0, 0), (-1, 0), 1, verdict_border),
        ("GRID", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_inference)
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Risk Classification:</b> <font color='{risk_color}'><b>{risk_level}</b></font> <font color='#94A3B8'>(score: {risk})</font>", body_style))
    story.append(Spacer(1, 10))

    # ========================================================
    # SECTION 3: BITSTREAM PROPERTIES
    # ========================================================

    story.append(Paragraph("3. Bitstream Container Properties", section_heading))
    story.append(SectionBookmark("bitstream_properties", "Bitstream Container Properties"))

    source_profile = _resolve_forensics_item(forensics, "1_source_profile", ["source_profile", "1_source"])
    frame_size = _resolve_forensics_item(forensics, "2_frame_size", ["frame_size", "frame_dimensions"])
    frame_rate = _resolve_forensics_item(forensics, "3_frame_rate", ["frame_rate"])
    compression = _resolve_forensics_item(forensics, "4_video_compression", ["video_compression", "compression"])
    if data.get("media_type") == "audio":

        properties_table_data = [
            [
                Paragraph("<b>Estimated Device Origin:</b>", body_style),
                Paragraph(
                    _safe_text(
                        source_profile.get(
                            "estimated_device_type",
                            "Audio"
                        )
                    ),
                    body_style
                )
            ],
            [
                Paragraph("<b>Sample Rate:</b>", body_style),
                Paragraph(
                    f"{data.get('sample_rate','N/A')} Hz",
                    body_style
                )
            ],
            [
                Paragraph("<b>Duration:</b>", body_style),
                Paragraph(
                    f"{data.get('duration_seconds','N/A')} sec",
                    body_style
                )
            ],
            [
                Paragraph("<b>Total Samples:</b>", body_style),
                Paragraph(
                    str(data.get('total_samples','N/A')),
                    body_style
                )
            ],
            [
                Paragraph("<b>Audio Engine:</b>", body_style),
                Paragraph(
                    "AASIST",
                    body_style
                )
            ],
        ]

    else:

        properties_table_data = [
            [
                Paragraph("<b>Estimated Device Origin:</b>", body_style),
                Paragraph(
                    _safe_text(
                        source_profile.get(
                            "estimated_device_type",
                            "Unknown"
                        )
                    ),
                    body_style
                )
            ],
            [
                Paragraph("<b>Resolution Matrix:</b>", body_style),
                Paragraph(
                    f"{_safe_get(frame_size,['width_pixels'],'N/A')}x{_safe_get(frame_size,['height_pixels'],'N/A')} px",
                    body_style
                )
            ],
            [
                Paragraph("<b>Stream Frame Rate:</b>", body_style),
                Paragraph(
                    f"{_safe_get(frame_rate,['frames_per_second'],'N/A')} FPS",
                    body_style
                )
            ],
            [
                Paragraph("<b>Codec Compression Profile:</b>", body_style),
                Paragraph(
                    _safe_text(
                        compression.get(
                            "extracted_frame_compression",
                            "N/A"
                        )
                    ),
                    body_style
                )
            ],
    ]
    
    t_properties = Table(properties_table_data, colWidths=[180, 340])
    t_properties.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_properties)
    story.append(Spacer(1, 10))

    # ========================================================
    # SECTION 4: MODEL CONSENSUS
    # ========================================================

    story.append(Paragraph("4. Multi-Model Consensus Matrix", section_heading))
    story.append(SectionBookmark("consensus_matrix", "Multi-Model Consensus Matrix"))

    if data.get("media_type") == "audio":

        model_table = Table([
            ["Audio Model", "Status"],
            ["AASIST", "Loaded"],
            ["Audio Deepfake Detector", "Active"],
            ["Segment Analyzer", "Active"],
            ["Waveform Engine", "Active"],
        ], colWidths=[260, 260])

    else:

        model_table = Table([
            ["Model", "Validation Accuracy"],
            ["Vision Transformer", "79.77%"],
            ["EfficientNet", "97.02%"],
            ["Swin Transformer", "92.86%"],
            ["Ensemble V3", "96.96%"],
        ], colWidths=[260, 260])
    model_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(model_table)
    story.append(Spacer(1, 10))

    # ========================================================
    # SECTION 5: BLOCKCHAIN
    # ========================================================

    story.append(Paragraph("5. Ledger Receipts & Cryptographic Verification", section_heading))
    story.append(SectionBookmark("ledger_verification", "Ledger Receipts & Cryptographic Verification"))

    blockchain_table_data = [
        [Paragraph("<b>Blockchain Evidence Registry:</b>", body_style), Paragraph(status, body_style)],
        [Paragraph("<b>Registry Status:</b>", body_style), Paragraph(str(status), body_style)],
        [Paragraph("<b>Smart Contract Tx Hash:</b>", body_style), Paragraph(f"<code>{tx_hash}</code>", code_style)],
        [Paragraph("<b>Block Number:</b>", body_style), Paragraph(str(block_number), body_style)],
        [Paragraph("<b>Gas Used:</b>", body_style), Paragraph(str(gas_used), body_style)],
    ]
    t_blockchain = Table(blockchain_table_data, colWidths=[180, 340])
    t_blockchain.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F9FF")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_blockchain)
    story.append(Spacer(1, 12))

    # ========================================================
    # SECTION 6: TIMELINE
    # ========================================================

    story.append(Paragraph("6. Temporal Tampering Probability Distribution", section_heading))
    story.append(SectionBookmark("temporal_distribution", "Temporal Tampering Probability Distribution"))

    if data.get("media_type") == "audio":
        story.append(
            Paragraph(
                f"Audio segments analyzed: {len(timeline)}",
                body_style
            )
        )
    else:
        story.append(
            Paragraph(
                f"Frames evaluated: {len(timeline)}",
                body_style
            )
        )
        tampered = len(
            [x for x in timeline if x.get("status") == "Tampered"]
        )

        if data.get("media_type") == "audio":
            story.append(
                Paragraph(
                    f"Tampered audio segments detected: {tampered}",
                    body_style
                )
            )
        else:
            story.append(
                Paragraph(
                    f"Tampered frames detected: {tampered}",
                    body_style
                )
            )
        

    graph_b64 = data.get("ai_model_inference", {}).get("timeline_graph_b64")
    if graph_b64:
        img = _decode_b64_image(graph_b64)
        if img:
            story.append(Image(img, width=480, height=200))
        else:
            story.append(Paragraph("<i>[Visual processing index error]</i>", body_style))
    story.append(Spacer(1, 12))
    # ========================================================
    # SECTION 7: SPATIAL GALLERY
    # ========================================================

    if data.get("media_type") != "audio":

        story.append(
            Paragraph(
                "7. Spatial Tampering Evidence Localization Console",
                section_heading
            )
        )

        story.append(
            SectionBookmark(
                "spatial_console",
                "Spatial Tampering Evidence Localization Console"
            )
        )

        story.append(
            Paragraph(
                f"<i>Side-by-side verification mapping. {len(gallery)} tampered frame(s) detected and displayed below:</i>",
                body_style
            )
        )

        story.append(Spacer(1, 6))

        for idx, item in enumerate(gallery, 1):

            story.append(Paragraph(
                f"<b><font color='#DC2626'>⚠ TAMPERED FRAME {idx} — Frame ID {item.get('frame_id','?')}</font></b>",
                body_style
            ))

            console_elements = []

            orig_b64 = item.get("original_frame_b64") or item.get("thumbnail_b64")
            heat_b64 = item.get("heatmap_frame_b64") or data.get(
                "ai_model_inference", {}
            ).get("explainable_ai_heatmap_b64")

            if orig_b64:
                img1 = _decode_b64_image(orig_b64)
                console_elements.append(
                    Image(img1, width=160, height=110)
                    if img1 else Paragraph("[Missing Frame Asset]", body_style)
                )
            else:
                console_elements.append(
                    Paragraph("[Missing Frame Asset]", body_style)
                )

            if heat_b64:
                img2 = _decode_b64_image(heat_b64)
                console_elements.append(
                    Image(img2, width=160, height=110)
                    if img2 else Paragraph("[Heatmap Calculation Error]", body_style)
                )
            else:
                console_elements.append(
                    Paragraph("[Heatmap Calculation Error]", body_style)
                )

            meta_details = [
                Paragraph(
                    f"<b>Target Index:</b> Frame {_safe_text(item.get('frame_id', '?'))}",
                    body_style
                ),
                Paragraph(
                    f"<b>Temporal Step:</b> {_safe_text(item.get('timestamp', 'N/A'))}",
                    body_style
                ),
                Paragraph(
                    f"<b>Risk Score:</b> <font color='red'>{_safe_text(item.get('confidence', 'N/A'))}%</font>",
                    body_style
                ),
            ]

            t_meta = Table(
                [[d] for d in meta_details],
                colWidths=[150]
            )

            t_meta.setStyle(TableStyle([
                ("PADDING", (0, 0), (-1, -1), 2),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                [colors.white, colors.HexColor("#F8FAFC")]),
            ]))

            console_elements.append(t_meta)

            t_row = Table(
                [console_elements],
                colWidths=[175, 175, 170]
            )

            t_row.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (1, -1), "CENTER"),
            ]))

            story.append(
                KeepTogether(
                    [t_row, Spacer(1, 8)]
                )
            )

    else:

        story.append(
            Paragraph(
                "7. Audio Segment Evidence Console",
                section_heading
            )
        )

        story.append(
            Paragraph(
                "Audio evidence does not contain frame-level spatial localization artifacts. Segment-level tampering probabilities were evaluated using the AASIST deepfake detection engine.",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"Audio segments analyzed: {len(timeline)}",
                body_style
            )
        )

        tampered_segments = len(
            [x for x in timeline if x.get("status") == "Tampered"]
        )

        story.append(
            Paragraph(
                f"Tampered segments detected: {tampered_segments}",
                body_style
            )
        )

        story.append(Spacer(1, 8))

    # ========================================================
    # APPENDIX 1: VALIDATION LEGEND
    # ========================================================

    story.append(PageBreak())
    story.append(Paragraph("8. Validation Legend Appendix", section_heading))
    story.append(SectionBookmark("validation_legend", "Validation Legend Appendix"))

    legend_table = Table(_legend_items(), colWidths=[120, 250, 150])
    legend_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "This appendix defines the visual indicators used throughout the report and is intended to make manual review faster and more consistent.",
        body_style,
    ))
    story.append(Spacer(1, 10))

    # ========================================================
    # CERTIFICATE
    # ========================================================

    story.append(Paragraph("9. Premium Certificate of Authentication", section_heading))
    story.append(SectionBookmark("certificate", "Premium Certificate of Authentication"))

    cert_title_style = ParagraphStyle(
        "CertTitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    cert_sub_style = ParagraphStyle(
        "CertSub",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
    )
    cert_body_style = ParagraphStyle(
        "CertBody",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#334155"),
        spaceBefore=10,
        spaceAfter=10,
    )
    cert_verdict_style = ParagraphStyle(
        "CertVerdict",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=13,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor(verdict_text_color),
        spaceAfter=10,
    )
    cert_small_style = ParagraphStyle(
        "CertSmall",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#94A3B8"),
    )
    evidence_type = (
        "audio evidence"
        if data.get("media_type") == "audio"
        else "video evidence"
    )

    certificate_text = (
        f"This is to certify that the submitted {evidence_type} "
        "has undergone automated multi-model forensic analysis by the "
        "Phoenix Forensic Gateway ensemble pipeline, with results "
        "cryptographically sealed for integrity verification."
    )
    cert_inner = [
        [Paragraph("CERTIFICATE OF DIGITAL FORENSIC AUTHENTICATION", cert_title_style)],
        [Paragraph(f"Certificate ID: PFG-{cert_id}", cert_sub_style)],
        [Spacer(1, 10)],
        [Paragraph(certificate_text, cert_body_style)],
        [Paragraph(f"FINAL DETERMINATION: {verdict.upper()}", cert_verdict_style)],
        [Paragraph(
            f"Confidence Score: {confidence}% &nbsp;|&nbsp; Risk Classification: {risk_level} &nbsp;|&nbsp; Date Issued: {gen_date}",
            cert_sub_style
        )],
        [Spacer(1, 10)],
        [Paragraph(
            "████████████████████████████████████████  ████████████████████████████████████████",
            cert_sub_style
        )],
        [Paragraph(
            "Authorized System Signature&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "Blockchain Ledger Anchor",
            cert_small_style
        )],
        [Spacer(1, 6)],
        [Paragraph(
            "This certificate is a system-generated attestation and does not constitute legal certification unless countersigned by an accredited forensic examiner.",
            cert_small_style
        )],
    ]

    cert_table = Table(cert_inner, colWidths=[480])
    cert_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#0F172A")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFBFC")),
        ("PADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether([cert_table]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Phoenix Digital Forensics Lab · Automated AI-Assisted Evidence Authentication System",
        center_small
    ))

    # ========================================================
    # APPENDIX 2: METADATA + BADGES
    # ========================================================

    story.append(PageBreak())
    story.append(Paragraph("10. Report Metadata Appendix", section_heading))
    story.append(SectionBookmark("metadata_appendix", "Report Metadata Appendix"))

    meta_rows = [
        ["Report Generated", _fmt_dt_utc()],
        ["Certificate ID", f"PFG-{cert_id}"],
        ["Verdict", verdict],
        ["Confidence", f"{confidence}%"],
        ["Risk Level", risk_level],
        ["Evidence Hash Prefix", _short_hash(evidence_hash, 32)],
        ["Blockchain Status", status],
        ["Block Number", _safe_text(block_number)],
        ["Transaction Hash", _safe_text(tx_hash)],
        ["Gas Used", _safe_text(gas_used)],
    ]
    meta_table = Table(meta_rows, colWidths=[180, 340])
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF6FF")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("11. Evidence Badges", section_heading))
    story.append(SectionBookmark("evidence_badges", "Evidence Badges"))

    badge_row = Table([
        [
            Badge("HASH LOCK", "#0F766E"),
            Badge("LEDGER LINK", "#1D4ED8"),
            Badge("MODEL FUSION", "#7C3AED"),
            Badge("XAI LAYER", "#B45309"),
        ]
    ], colWidths=[130, 130, 130, 130])
    story.append(badge_row)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "The badges above summarize the report’s strongest assurance layers: cryptographic hashing, ledger anchoring, ensemble inference, and explainable AI localization.",
        body_style,
    ))

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(
        story,
        onFirstPage=lambda c, d: _page_decorations(c, d, data),
        onLaterPages=lambda c, d: _page_decorations(c, d, data),
        canvasmaker=PageNumCanvas,
    )

    buffer.seek(0)
    return buffer