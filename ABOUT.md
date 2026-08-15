# About Adversarial ML for IDS Validation via Red-Team Techniques

This repository consolidates the coursework and research tasks completed as part of an S2 thesis in cybersecurity, focusing on adversarial machine learning techniques for Intrusion Detection System (IDS) validation.

## Motivation

Intrusion Detection Systems are critical for network security, yet they remain vulnerable to adversarial machine learning attacks that can evade detection. This project explores both offensive (generating adversarial traffic) and defensive (robust IDS models, threat intelligence aggregation, mini-SoC) techniques to evaluate and improve IDS resilience.

## Contents

Each directory represents a distinct task or study:

- `adversarial-traffic-generator`: Generates network traffic with randomized JA3 fingerprints to test IDS evasion.
- `aksara-bali-ocr`: A simple CNN demonstrator for character recognition (not security-related, but included as a portfolio item).
- `dl-anomaly-detection-fundamentals`: Implements various deep learning models for anomaly detection in network traffic.
- `ids-architecture-comparison`: Compares classical ML models (XGBoost, CatBoost, MLP) for IDS.
- `ids-validation-saas-mvp`: A Flask-based landing page proposing a SaaS model for IDS validation.
- `is-transformation-case-study`: A case study on transforming traditional IDS using adversarial ML insights.
- `mini-soc-enterprise-arch`: A Docker‑Compose based mini Security Operations Center integrating log ingestion, IDS, alerting, dashboard, and Redis.
- `network-traffic-analytics-pipeline`: An ETL pipeline that extracts features from raw traffic and stores them in Parquet format.
- `paper-replication-ids-adversarial`: Replicates an adversarial attack on an IDS using FGSM.
- `thesis-research-design`: The detailed research design for the S2 thesis.
- `thesis-paper-draft`: The LaTeX draft of the thesis, exported to DOCX for editing.
- `threat-intel-aggregator`: Collects and scores threat intelligence from OSINT feeds.
- `model`: Shared artifacts (trained XGBoost model and scaler parameters) used across tasks.
- `verify.py`: A lightweight verification script that checks syntax of all Python files in the repository.

## Usage

Each task is largely self-contained. Refer to the individual `README.md` files inside each directory for specific instructions on how to run the code, dependencies, and expected outputs.

## Requirements

- Python 3.8+
- Docker (for the mini‑SoC task)
- Standard Python packages (see individual `requirements.txt` files)

## License

This project is licensed under the MIT License – see the `LICENSE` file for details.

## Contact

For questions or feedback, please open an issue in this repository.
