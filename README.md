<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:061A2F,50:0B4F8A,100:00C2FF&animation=fadeIn" alt="Banner" width="100%" />

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=800&size=40&duration=3000&pause=5000&color=00C2FF&center=true&vCenter=true&width=600&height=70&lines=AI+Video+Evidence+Authentication" alt="AI Video Evidence Authentication" />

<h1>AI Video Evidence Authentication</h1>

<h3>Multimodal AI • Video Forensics • Audio Forensics • Digital Evidence • Blockchain</h3>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Blockchain-Evidence%20Integrity-F7931A?style=for-the-badge&logo=ethereum&logoColor=white" />
</p>

<p>
  <a href="https://github.com/PrajwalM-2345/AI-Video-Evidence-Authentication">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white" />
  </a>
</p>

</div>

---

# 🔎 Overview

**AI Video Evidence Authentication** is a multimodal forensic AI platform designed to analyze digital video evidence and determine whether media is **authentic/original or tampered/manipulated**.

The system combines:

- 🎥 Video deepfake detection
- 🎞️ Temporal video analysis
- 🎙️ Audio forensic analysis
- 🧠 Multiple computer-vision models
- 👤 Face analysis
- 🔬 Tampering localization
- 📊 Evidence scoring
- 🔗 Blockchain-backed evidence integrity
- 📄 Automated forensic reporting
- 🌐 Web-based investigation interface
- 🐳 Dockerized deployment

The objective is to provide a complete pipeline from **media upload → AI forensic analysis → evidence interpretation → report generation → integrity verification**.

---

# 🧠 AI Forensic Pipeline

```text
                    ┌──────────────────────┐
                    │      Media Upload    │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │  Video Analysis │          │  Audio Analysis │
       └────────┬────────┘          └────────┬────────┘
                │                            │
                ▼                            ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Frame Extraction│          │ Audio Extraction│
       └────────┬────────┘          └────────┬────────┘
                │                            │
                ▼                            ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Vision Models   │          │ AASIST Forensics│
       │ ViT             │          │ Spectral/Audio  │
       │ EfficientNet    │          │ Analysis        │
       │ Swin Transformer│          └────────┬────────┘
       └────────┬────────┘                   │
                │                            │
                ▼                            ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Temporal Video  │          │ Audio Evidence  │
       │ Transformer     │          │ Score           │
       └────────┬────────┘          └────────┬────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Multimodal Evidence  │
                    │ Fusion / Ensemble    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Forensic Verdict     │
                    │ Authentic / Tampered │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌─────────────┐
        │ Evidence   │ │ Blockchain │ │ Forensic    │
        │ Timeline   │ │ Integrity  │ │ Report      │
        └────────────┘ └────────────┘ └─────────────┘
