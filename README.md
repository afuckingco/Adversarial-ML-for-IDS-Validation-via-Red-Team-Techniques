```markdown
<div align="center">

```bash
   ▄▀█ █▀▀ █░█ █▀▀ █▄▀ █ █▄░█ █▀▀ █▀▀ █▀█
   █▀█ █▀░ █▄█ █▄▄ █░█ █ █░▀█ █▄█ █▄▄ █▄█
```

# Adaptive Evasion Traffic Generator (AETG)

**A Framework for Adaptive IDS Validation via Red‑Team Techniques**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![Paper](https://img.shields.io/badge/paper-AETG_2026-blue)](AETG_paper/output/AETG_paper.pdf)

</div>

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

$$
\hat{y} = \begin{cases}
1 & \text{if } P(y=1 \mid x) \geq 0.5 \\
0 & \text{otherwise}
\end{cases}
$$

### 6. Evaluation Metrics

$$
\text{Precision} = \frac{TP}{TP + FP}, \qquad
\text{Recall} = \frac{TP}{TP + FN}
$$

$$
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$

$$
\text{AUC} = \int_{0}^{1} \mathrm{TPR}(t) \cdot d(\mathrm{FPR}(t))
$$

$$
\text{Evasion Rate} = \frac{\#\{\text{adversarial} \to \text{benign}\}}{\#\{\text{total adversarial}\}}
$$

### 7. Alert Pipeline

$$
\text{Suricata} \xrightarrow{\text{eve.json}} \text{push\_alerts.py} \xrightarrow{\text{Redis}} \text{eval\_ids.py}
$$

$$
\text{alert\_count} = \left| \left\{ \text{key} \mid \text{key} \in \text{Redis},\; \text{key} \succeq \text{"alert:"} \right\} \right|
$$

### 8. Final Aggregation

$$
\text{results} = \{
F_1,\; \text{Precision},\; \text{Recall},\; \text{AUC},\; \text{Evasion Rate},\; \text{alert\_count}
\}
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
| **Recall** | **1.0** |
| **Precision** | 0.5 |
| **F1‑Score** | 0.667 |
| **AUC‑ROC** | 0.5025 |
| **Evasion Rate (vs ML)** | **0.0%** |
| **Alert Count (Redis)** | **0**¹ |

> ¹ The zero alert count for the 200‑flow evaluation batch was traced to a key‑pattern mismatch in the evaluation script (`r.llen('alerts')` vs. `r.set('alert:*', ...)`). The alert pipeline itself was confirmed functional in separate tests. After fixing the script to use `r.keys('alert:*')`, the pipeline returned `alert_count = 5`; the paper reports the original `0` value observed during the experiment.

### Adversarial Training

| Model | F1‑Score | Evasion Rate |
|-------|----------|--------------|
| Baseline | 0.0 | 1.0 |
| Adversarially Trained | **0.953** | **0.089** |

> Adversarial training dramatically improved robustness, reducing evasion rate from 1.0 to 0.089. This experiment is documented as future work in the paper.

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
│       ├── eval_results.json           # Results (alert_count=0, auc=0.5025)
│       └── calibration_results.json    # Calibration data (96.8%, ESM 0.14)
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

> *"Build systems. Break systems. Learn from both."*  
> *"Security is an invariant, not a feature."*

**◎** — target · **⡇** — theorem

---

*Last updated: 20 August 2026*
```
