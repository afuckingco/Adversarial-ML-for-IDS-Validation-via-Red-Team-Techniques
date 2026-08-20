# About This Project

## Project Overview

This repository contains the complete implementation and manuscript for the **Adaptive Evasion Traffic Generator (AETG)** project — a research initiative that bridges adversarial machine learning theory and network security practice.

The project was conducted as part of an S2 (Master's) thesis research in Cybersecurity at **Institut Teknologi dan Bisnis STIKOM Bali**.

## Research Goals

The primary goals of this research are:

1. **Develop AETG Framework**: Create a protocol-compliant, adaptive evasion traffic generator for IDS validation.

2. **Validate Against Production-Grade IDS**: Test the framework against a realistic mini-SOC deployment with Suricata, Redis, and ML-based detection.

3. **Quantify Stealth**: Introduce a rigorous Evasion Stealth Metric (ESM) based on Jensen-Shannon Divergence.

4. **Demonstrate Adaptive Evasion**: Show that contextual bandit (LinUCB) can adapt evasion strategies based on real-time IDS feedback.

## What's Included

- **Paper Manuscript**: Full academic paper in LaTeX, Word, and PDF formats.
- **Source Code**: Complete implementation of AETG framework (Python + Scapy).
- **Mini-SOC Deployment**: Docker Compose stack for Suricata IDS, Redis, and alerting pipeline.
- **Experiment Results**: JSON files containing evaluation metrics and logs.

## Key Findings

- **Calibration**: AETG achieved 96.8% evasion rate against a mock HTTP server.
- **ML Detection**: XGBoost detector achieved recall = 1.0 on 200 adversarial flows.
- **Alert Pipeline**: Suricata alerts successfully flow to Redis (verified functional).
- **Feedback Loop**: Closed-loop integration remains as future work.

## Repository Structure
.
├── AETG_paper/ # Manuscript and artifacts
├── code/ # Source code (AETG, mini-SOC, experiments)
├── other-projects/ # Previous research artifacts
├── README.md # Main documentation
├── LICENSE # MIT License
└── verify.py # Syntax verification script


## Author

**Afiq Andico Pangimpian**
- Email: afiqandico13@gmail.com
- Institution: Institut Teknologi dan Bisnis STIKOM Bali

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Last Updated

August 20, 2026
