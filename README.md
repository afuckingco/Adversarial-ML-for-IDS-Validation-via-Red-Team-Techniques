# 🎯 Adaptive Evasion Traffic Generator (AETG)

**A Framework for Adaptive IDS Validation via Red‑Team Techniques**

<div align="center">

```bash
   ▄▀█ █▀▀ █░█ █▀▀ █▄▀ █ █▄░█ █▀▀ █▀▀ █▀█
   █▀█ █▀░ █▄█ █▄▄ █░█ █ █░▀█ █▄█ █▄▄ █▄█
```

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-pytest-blue)]()
[![Thesis](https://img.shields.io/badge/status-ACTIVE-green)]()

</div>

---

## 📋 Abstract

AETG is a cutting-edge framework for validating Intrusion Detection Systems (IDS) through adversarial attack generation. It combines:

- **LinUCB multi-armed bandit** for adaptive strategy selection
- **Jensen-Shannon Divergence** (Evasion Stealth Metric) to measure attack similarity to benign traffic
- **Suricata + XGBoost** for real-world IDS testing
- **Docker Compose** for reproducible mini-SOC deployment

**Key Results:**
- 96.8% evasion rate (calibration environment)
- Adversarial training improves detection from F1=0.0 → F1=0.953
- Alert pipeline now fixed and fully operational

---

## 📐 Mathematical Formulation

### 1. Feature Extraction

$$
f_{\text{flow}} = \big[\,p,\; \bar{s},\; \sigma_s,\; u_{\text{src}},\; u_{\text{dst}},\; c_{\text{ja3}}\,\big]
$$

### 2. Evasion Stealth Metric (ESM)

$$
P_i(k) = \frac{n_{\text{benign}}^{(i)}(k)}{N_{\text{benign}}}, \qquad
Q_i(k) = \frac{n_{\text{adv}}^{(i)}(k)}{N_{\text{adv}}}
$$

$$
\mathrm{JSD}_i = \frac{1}{2} \sum_{k=1}^{K} \left[
P_i(k) \log \frac{2P_i(k)}{P_i(k) + Q_i(k)} +
Q_i(k) \log \frac{2Q_i(k)}{P_i(k) + Q_i(k)}
\right]
$$

$$
\mathrm{ESM} = \frac{\sum_{i=1}^{m} w_i \cdot \mathrm{JSD}_i}{\sum_{i=1}^{m} w_i}, \quad w_i = 1,\; m = 6
$$

$$
\mathrm{ESM}_{\text{norm}} = \frac{\mathrm{ESM}}{\ln 2}
$$

### 3. LinUCB Arm Selection

$$
x_t \in \mathbb{R}^{16}
$$

$$
A_a = I_d + \sum_{s} x_s x_s^\top, \qquad
b_a = \sum_{s} r_s x_s, \qquad
\hat{\theta}_a = A_a^{-1} b_a
$$

$$
a_t = \arg\max_a \left( x_t^\top \hat{\theta}_a + \alpha \sqrt{x_t^\top A_a^{-1} x_t} \right)
$$

$$
A_a \leftarrow A_a + x_t x_t^\top, \qquad
b_a \leftarrow b_a + r_t x_t
$$

### 4. Reward

$$
r_t = (1 - \text{alert\_rate}_t) \cdot (1 - \mathrm{ESM}_t)
$$

### 5. XGBoost Inference

$$
x_{\text{norm}} = \frac{x - \mu}{\sigma}
$$

$$
P(y=1 \mid x) = \frac{1}{1 + e^{-F(x)}}, \qquad
F(x) = \sum_{m=1}^{M} f_m(x)
$$

### 6. Evaluation Metrics

$$
\text{Precision} = \frac{TP}{TP + FP}, \qquad
\text{Recall} = \frac{TP}{TP + FN}, \qquad
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$

$$
\text{AUC} = \int_{0}^{1} \mathrm{TPR}(t) \cdot d(\mathrm{FPR}(t))
$$

$$
\text{Evasion Rate} = \frac{\#\{\text{adversarial} \to \text{benign}\}}{\#\{\text{total adversarial}\}}
$$

### 7. Alert Pipeline (Fixed)

$$
\text{Suricata} \xrightarrow{\text{eve.json}} \text{push\_alerts.py} \xrightarrow{\text{Redis}} \text{eval\_ids.py}
$$

$$
\text{alert\_count} = \left| \left\{ \text{key} \mid \text{key} \in \text{Redis},\; \text{key} \text{ matches } "alert:\*" \right\} \right|
$$

---

## 📊 Key Results

### Calibration Environment (Mock HTTP Server, No IDS)

| Metric | Value |
|--------|-------|
| **Evasion Rate** | **96.8%** |
| **Mean ESM** | 0.14 |
| **Adaptation Speed** | 38 rounds |

### Mini‑SOC Deployment (Suricata + 52k ET Rules + ML Detector)

| Metric | Value |
|--------|-------|
| **Recall** | 1.0 |
| **Precision** | 0.5 |
| **F1‑Score** | 0.667 |
| **AUC‑ROC** | 0.5025 |
| **Evasion Rate (vs ML)** | 0.0% |
| **Alert Count (Redis)** | ✅ **FIXED** |

> **✅ FIXED:** The alert pipeline now correctly uses Redis key pattern `alert:*` matching (via `r.keys()` or `r.scan()`) instead of list operations. See `code/experiments/eval_ids.py` lines 174-198 for implementation.

### Adversarial Training

| Model | F1‑Score | Evasion Rate |
|-------|----------|--------------|
| Baseline (no training) | 0.0 | 1.0 |
| Adversarially Trained | **0.953** | **0.089** |

> Adversarial training dramatically improved robustness. Future work: scale to 10k+ flows, implement online learning.

---

## 🗂️ Repository Structure

```
.
├── AETG_paper/                         # 📄 Paper manuscript & artifacts
│   ├── manuscript/                     # .tex, .docx, references.bib
│   ├── figures/                        # Architecture diagrams, result plots
│   ├── tables/                         # LaTeX tables
│   ├── data/                           # Experiment results (JSON)
│   ├── notes/                          # Cover letter, highlights
│   └── output/                         # PDF final & LaTeX aux
│
├── code/                               # 🔬 Core implementation
│   ├── adversarial-traffic-generator/  # AETG framework (Python + Scapy)
│   │   ├── new_traffic_gen.py          # CLI entry point
│   │   ├── src/
│   │   │   ├── traffic_gen.py          # HTTP, DNS, SSH generation
│   │   │   ├── mab_optimizer.py        # LinUCB implementation
│   │   │   └── stealth_metric.py       # ESM (Jensen-Shannon)
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── mini-soc-enterprise-arch/       # 🏢 Mini-SOC (Suricata + XGBoost)
│   │   ├── docker-compose.yml          # All services
│   │   ├── ids/                        # Suricata + ML model
│   │   ├── alerting/                   # Alert processing (FIXED)
│   │   ├── dashboard/                  # Web UI (port 8080)
│   │   ├── push_alerts.py              # Redis alert pusher (FIXED)
│   │   └── README.md
│   │
│   └── experiments/                    # 🧪 Evaluation
│       ├── eval_ids.py                 # FIXED: Correct Redis key matching
│       ├── eval_results.json           # Results
│       └── calibration_results.json
│
├── tests/                              # 🧪 Unit tests (NEW)
│   ├── test_stealth_metric.py
│   ├── test_mab_optimizer.py
│   └── test_traffic_gen.py
│
├── .github/workflows/                  # 🔄 CI/CD (NEW)
│   └── ci.yml                          # pytest, Docker build verification
│
├── verify.py                           # Syntax verification
├── CONTRIBUTING.md                     # Contribution guidelines
├── LICENSE                             # MIT License
└── README.md                           # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with `venv`
- **Docker & Docker Compose**
- **Redis** (included in Docker Compose)
- **Suricata** (included in Docker image)

### 1. Clone & Setup

```bash
git clone https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques.git
cd Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques

python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
```

### 2. Install Dependencies

```bash
# Core framework
pip install -r code/adversarial-traffic-generator/requirements.txt

# For experiments (includes mini-soc)
pip install -r code/mini-soc-enterprise-arch/requirements.txt
```

### 3. Run Experiments

#### Option A: Calibration (No IDS)

```bash
cd code/adversarial-traffic-generator
python new_traffic_gen.py \
    --url http://localhost:8082 \
    --attack c2_beacon \
    --adaptive \
    --n 100
```

#### Option B: Mini-SOC (Suricata + Redis + XGBoost)

```bash
cd code/mini-soc-enterprise-arch
docker compose up -d

# Wait for services to start (5-10 seconds)
sleep 5

# Run evaluation
cd ../../code/experiments
python eval_ids.py \
    --benign-flows 100 \
    --adv-flows 100 \
    --output results.json
```

#### Option C: Check Redis Alerts (FIXED)

```bash
# Connect to Redis CLI
redis-cli

# Count alerts with pattern matching
> KEYS alert:*
> SCAN 0 MATCH "alert:*"
```

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Verify Code Syntax

```bash
python verify.py
```

### Generate Example Dataset

```bash
cd code/experiments
python -c "
from code.adversarial_traffic_generator.new_traffic_gen import *
import json

# Generate 50 benign + 50 adversarial flows
benign = [{'flow': i, 'ja3': 'chrome_116'} for i in range(50)]
adv = [{'flow': i+50, 'ja3': 'random_' + str(i)} for i in range(50)]

with open('example_flows.json', 'w') as f:
    json.dump({'benign': benign, 'adversarial': adv}, f, indent=2)
"
```

---

## 🔧 Troubleshooting

### Alert Pipeline (FIXED)

**Problem:** `alert_count=0` in results

**Solution:** 
- Verify `push_alerts.py` is running: `ps aux | grep push_alerts.py`
- Check Redis keys: `redis-cli KEYS 'alert:*'`
- Ensure Suricata is generating alerts: Check `shared/logs/eve.json`
- Implementation uses `r.keys('alert:*')` (see `eval_ids.py` line 183)

### Docker Issues

```bash
# Clean up
docker compose down -v

# Rebuild from scratch
docker compose up --build --force-recreate

# View logs
docker compose logs -f ids
docker compose logs -f alerting
```

### Redis Connection

```bash
# Test connection
redis-cli ping  # Should return PONG

# Check alert keys
redis-cli SCAN 0 MATCH "alert:*" COUNT 100
```

---

## 📚 References

- **LinUCB**: Li et al., "A Contextual-Bandit Approach to Personalized News Recommendation" (2010)
- **Jensen-Shannon Divergence**: Lin, "Divergence Measures Based on the Shannon Entropy" (1991)
- **Adversarial ML for IDS**: Carlini & Wagner, "Towards Evaluating the Robustness of Neural Networks" (2016)
- **Suricata**: https://suricata.io/
- **XGBoost**: Chen & Guestrin, "XGBoost: A Scalable Tree Boosting System" (2016)

---

## 📜 License

MIT License – see [LICENSE](LICENSE)

---

## 👤 Author

**Afiq Andico Pangimpian**  
- GitHub: [@afuckingco](https://github.com/afuckingco)  
- Email: afiqandico13@gmail.com  
- Affiliation: Institut Teknologi dan Bisnis STIKOM Bali  
- Thesis: *Adversarial Machine Learning for IDS Validation via Red-Team Techniques*

---

## 🙏 Acknowledgments

- STIKOM Bali for research support
- Suricata, Scapy, Redis, XGBoost communities
- Emerging Threats for ET rules

---

> **"Build systems. Break systems. Learn from both."**

*Last updated: 31 August 2026*
