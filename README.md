```markdown
# Adversarial ML for IDS Validation via Red-Team Techniques

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/redis-✓-DC382D?logo=redis)](https://redis.io/)
[![Paper](https://img.shields.io/badge/paper-AETG_2026-blue)](AETG_paper/output/AETG_paper.pdf)

> **Adaptive Evasion Traffic Generator (AETG): A Framework for Adaptive IDS Validation via Red-Team Techniques**

This repository contains the complete implementation and manuscript for the **AETG** framework — a research project that bridges adversarial machine learning theory and network security practice. The framework generates protocol-compliant, adaptively evasive network traffic to stress-test Intrusion Detection Systems (IDS) under realistic threat models.

---

## 📌 Key Features

- **Protocol-compliant traffic generation** – HTTP, DNS, SSH, C2 beacon with Scapy.
- **TLS fingerprint randomization** – JA3/JA4 randomization for evading signature-based detection.
- **Adaptive evasion via LinUCB** – Contextual Multi-Armed Bandit with real-time IDS feedback through Redis.
- **Evasion Stealth Metric (ESM)** – Quantitative stealth measurement based on Jensen-Shannon Divergence.
- **Mini-SOC deployment** – Docker Compose stack with Suricata, Redis, alerting, and dashboard.
- **ML-based detector** – XGBoost classifier for flow-level intrusion detection.

---

## 📄 Paper

The manuscript **"Adaptive Evasion Traffic Generator (AETG): A Framework for Adaptive IDS Validation via Red-Team Techniques"** is available in:

| Format | Location |
|--------|----------|
| LaTeX source | `AETG_paper/manuscript/AETG_paper.tex` |
| PDF final | `AETG_paper/output/AETG_paper.pdf` |
| Word (DOCX) | `AETG_paper/manuscript/AETG_paper.docx` |
| References | `AETG_paper/manuscript/references.bib` |

**Abstract:** *The increasing adoption of machine learning for network intrusion detection has introduced a critical vulnerability: adversarial examples that can systematically evade detection. AETG unifies protocol-compliant traffic generation, TLS fingerprint randomization, adaptive evasion via LinUCB with real-time IDS feedback, and a rigorous Evasion Stealth Metric. The framework's pipeline was validated in two distinct settings: (1) a calibration environment achieving 96.8% evasion rate, and (2) a mini-SOC deployment where Suricata alerts were confirmed flowing into Redis, while an ML detector achieved recall = 1.0 on adversarial C2 beacon flows.*

---

## 🗂️ Repository Structure

```
.
├── AETG_paper/                         # 📄 Paper manuscript & artifacts
│   ├── manuscript/                     # .tex, .docx, references.bib
│   ├── figures/                        # Architecture diagram, result plots
│   ├── tables/                         # LaTeX tables
│   ├── data/                           # Experiment results (JSON)
│   ├── notes/                          # Cover letter, highlights, revision notes
│   └── output/                         # PDF final & LaTeX aux files
│
├── code/                               # 🔬 Core implementation
│   ├── adversarial-traffic-generator/  # AETG framework (Python + Scapy)
│   │   ├── new_traffic_gen.py          # CLI entry point
│   │   ├── src/
│   │   │   ├── traffic_gen.py          # HTTP, DNS, SSH generation
│   │   │   ├── mab_optimizer.py        # LinUCB implementation
│   │   │   └── stealth_metric.py       # ESM (Jensen-Shannon Divergence)
│   │   └── requirements.txt
│   │
│   ├── mini-soc-enterprise-arch/       # 🏢 Mini-SOC deployment
│   │   ├── docker-compose.yml          # Suricata, Redis, alerting, dashboard
│   │   ├── ids/                        # Suricata configuration
│   │   ├── alerting/                   # Alert processing service
│   │   ├── dashboard/                  # Web dashboard (port 8080)
│   │   ├── mock-endpoint/              # Mock HTTP server (port 8082)
│   │   └── push_alerts.py              # Redis alert pusher
│   │
│   └── experiments/                    # 🧪 Evaluation scripts
│       ├── eval_ids.py                 # Main evaluation script
│       ├── adv_training.py             # Adversarial training
│       └── eval_results.json           # Latest results
│
├── other-projects/                     # 📚 Previous/pending research
│   ├── ids-architecture-comparison/    # XGBoost, CatBoost, MLP comparison
│   ├── ids-validation-saas-mvp/        # Flask validation service
│   ├── network-traffic-analytics-pipeline/ # ETL pipeline
│   ├── paper-replication-ids-adversarial/  # FGSM replication
│   ├── thesis-paper-draft/             # Thesis LaTeX source
│   ├── dl-anomaly-detection-fundamentals/
│   ├── threat-intel-aggregator/
│   └── ... (other research artifacts)
│
├── venv/                               # Python virtual environment
├── verify.py                           # Syntax verification script
├── README.md                           # This file
├── LICENSE                             # MIT License
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (recommended: use virtual environment)
- **Docker** and **Docker Compose** (for Mini-SOC)
- **Redis** (included in Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques.git
cd Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# or venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
# For AETG framework
pip install -r code/adversarial-traffic-generator/requirements.txt

# For experiments
pip install -r code/experiments/requirements.txt  # if available
```

---

## 🧪 Running Experiments

### Option A: Start Mini-SOC (Suricata + Redis + Dashboard)

```bash
cd code/mini-soc-enterprise-arch
docker compose up -d
```

- **Suricata IDS** – Sniffs traffic and generates alerts.
- **Redis** – Stores alerts (`alert:*` keys).
- **Dashboard** – `http://localhost:8080`
- **Mock endpoint** – `http://localhost:8082`

### Option B: Run Calibration Experiment (Mock Server, No IDS)

```bash
cd code/adversarial-traffic-generator
python new_traffic_gen.py \
    --url http://localhost:8082 \
    --attack c2_beacon \
    --adaptive \
    --n 1000
```

### Option C: Run Mini-SOC Evaluation (Suricata + ML Detector)

```bash
cd code/experiments
python eval_ids.py \
    --attack c2_beacon \
    --benign-flows 500 \
    --adv-flows 200 \
    --rate 10 \
    --redis-host localhost \
    --redis-port 6379 \
    --output eval_results.json
```

### Option D: Push Alerts to Redis (if not automated)

```bash
cd code/mini-soc-enterprise-arch
python push_alerts.py &
```

---

## 📊 Key Results

| Setting | Evasion Rate | ESM (avg) | Adaptation Speed | Note |
|---------|--------------|-----------|------------------|------|
| **Calibration** (mock server, no IDS) | **96.8%** | 0.14 | 38 rounds | Bandit behavior characterization |
| **Mini-SOC** (Suricata + 52k ET rules) | — | — | — | Alert pipeline confirmed functional |
| **ML Detector** (XGBoost) | **0.0%** | — | — | Recall = 1.0 on 200 adversarial flows |

> **Takeaway:** AETG demonstrates effective evasion in calibration, but the closed-loop feedback with Suricata/ML-derived rewards remains the primary future work. The results highlight that flow-level ML detection can be robust to the TLS- and timing-based strategies explored here.

---

## 🔧 Verification

Run the syntax verification script (uses only standard library):

```bash
python verify.py
```

---

## 🤝 Contributing

Contributions to improve the framework, add new attack types, or refine the feedback loop are welcome. Please read [CONTRIBUTING.md](AETG_paper/notes/CONTRIBUTING.md) for guidelines.

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Afiq Andico Pangimpian**  
- GitHub: [@afuckingco](https://github.com/afuckingco)  
- Email: [afiqandico13@gmail.com](mailto:afiqandico13@gmail.com)  
- Affiliation: Institut Teknologi dan Bisnis STIKOM Bali

---

## 🙏 Acknowledgments

- **STIKOM Bali** for supporting this research.
- **Open-source communities** behind Suricata, Scapy, Redis, XGBoost, and Scikit-learn.
- Emerging Threats for the Suricata rule set.

---

*Last updated: 19 August 2026*
```
