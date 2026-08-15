# Adversarial ML for IDS Validation via Red-Team Techniques

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub tag](https://img.shields.io/github/v/tag/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques)](https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques/tags)
[![GitHub issues](https://img.shields.io/github/issues/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques)](https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques)](https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques/pulls)

This repository contains the complete portfolio of **12 tasks** (plus optional tasks) for an S2 thesis research in cybersecurity/TLS fingerprint spoofing detection. It includes:

- **Adversarial traffic generator** – JA3-randomizing HTTP traffic to test IDS evasion.
- **Aksara Bali OCR demonstration** – Simple CNN for character recognition (portfolio item).
- **Deep learning anomaly detection fundamentals** – CNN, LSTM, Transformer, Autoencoder implementations.
- **IDS architecture comparison** – XGBoost, CatBoost, MLP performance comparison.
- **Threat intelligence aggregator** – OSINT feed collector with scoring.
- **Mini-SoC enterprise architecture** – Docker‑Compose stack (log‑ingest, IDS, alerting, dashboard, Redis).
- **Network traffic analytics pipeline** – ETL producing Parquet dataset.
- **Paper replication (IDS adversarial)** – FGSM attack replication.
- **IDS validation SaaS MVP** – Flask landing page for a validation service.
- **IS transformation case study** – Documentation of IDS transformation using adversarial ML.
- **Thesis research design** – Full research design for the S2 thesis.
- **Thesis paper draft** – LaTeX source, compiled PDF, and editable DOCX.

All tasks are lightweight, zero‑cost, and suitable for hardware without CUDA.

## 📦 Packages & Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| **Python packages** (per task) | `*/requirements.txt` | Minimal dependencies (e.g., `torch`, `flask`, `xgboost`, `scikit-learn`, `redis`). |
| **Docker images** | `mini-soc-enterprise-arch/` | Built via `docker compose`: `log-ingest`, `ids`, `alerting`, `dashboard`, `redis`. |
| **Trained model** | `ids-architecture-comparison/xgb_model.json` & `scaler_params.json` | XGBoost model and scaler used in the mini‑SoC IDS service. |
| **OCR model** | `aksara-bali-ocr/../model/aksara_bali_cnn.pth` | Simple CNN demo model (shared `model/` folder). |
| **Thesis** | `thesis-paper-draft/main.tex`, `main.pdf`, `thesis.docx` | LaTeX source, compiled PDF, and editable Word document. |
| **Verification script** | `verify.py` | Checks syntax of all Python files in the repository. |

You can pull or build the Docker images locally:
```bash
cd mini-soc-enterprise-arch
docker compose build   # or `docker compose up -d` to run
```

## 🏗️ Structure

Each task follows a standard layout:
- `src/` – source code
- `data/` – sample or processed data
- `notebooks/` – Jupyter notebooks (if any)
- `docs/` – additional documentation
- `README.md` – task‑specific description

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques.git
   cd Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques
   ```

2. **(Optional) Set up virtual environments**  
   Many tasks include a `requirements.txt`. Example:
   ```bash
   cd ids-architecture-comparison
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the verification script** (uses only the standard library)
   ```bash
   python verify.py
   ```

4. **Explore individual tasks** – see each folder’s `README.md` for specific instructions.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## ℹ️ About

See [ABOUT.md](ABOUT.md) for more information about the project's goals and background.

## 📢 Contact

For questions or feedback, please open an issue in this repository.