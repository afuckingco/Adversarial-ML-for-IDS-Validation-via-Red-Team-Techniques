# Replication of Adversarial Challenges in Network Intrusion Detection Systems

This repository replicates the core experiments from the paper:
"Adversarial Challenges in Network Intrusion Detection Systems: Research ..." 
(arXiv:2409.18736v3, IEEE Access, or similar)

## Paper Information
- **Title**: Adversarial Challenges in Network Intrusion Detection Systems: Research ...
- **Authors**: (to be filled from the paper)
- **Link**: https://arxiv.org/abs/2409.18736v3
- **Dataset**: UNSW-NB15

## Research Question (RQ)
**RQ**: How susceptible are machine learning-based Network Intrusion Detection Systems (NIDS) to adversarial evasion attacks, specifically using gradient-based methods like FGSM, JSMA, and CW?

## Original Methodology
The original paper:
1. Uses the UNSW-NB15 dataset for training and testing ML models (including Random Forest, etc.)
2. Generates adversarial examples using FGSM, JSMA, and CW attacks.
3. Evaluates the detection rate of the models on adversarial examples (evasion rate).
4. Reports the evasion rates and discusses the robustness of ML-based NIDS.

## Replication Plan
Due to resource constraints, we replicate a subset of the experiments:
- **Dataset**: We use a small subset of UNSW-NB15 (1000 samples for training, 200 for testing) to keep experiments lightweight.
- **Model**: We train a Random Forest classifier (as used in the paper) on the subset.
- **Adversarial Attack**: We implement the Fast Gradient Sign Method (FGSM) to generate adversarial examples.
- **Evaluation**: We measure the accuracy of the model on benign test samples and the evasion rate (misclassification rate) on adversarial samples.

## Threats to Validity
1. **Dataset Size**: Using a small subset may not generalize to the full UNSW-NB15 dataset.
2. **Attack Implementation**: We only implement FGSM (a simple gradient-based attack) due to complexity and time constraints; JSMA and CW are omitted.
3. **Model Choice**: We only use Random Forest; the paper may have evaluated multiple models.
4. **Feature Engineering**: We replicate the preprocessing steps from the paper but may miss some nuances.

## How to Run
1. Clone the repository and create a virtual environment:
   ```bash
   git clone <repository-url>
   cd paper-replication-ids-adversarial
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the replication script:
   ```bash
   python src/replicate.py
   ```
   The script will:
   - Download a subset of UNSW-NB15 (if not already present)
   - Preprocess the data (as per the paper)
   - Train a Random Forest model
   - Generate FGSM adversarial examples
   - Report accuracy on benign samples and evasion rate on adversarial samples

## Expected Output
The script will print something like:
```
Benign accuracy: 0.85
Evasion rate (FGSM): 0.62
```

## Files
- `src/replicate.py`: Main replication script.
- `data/`: Directory for storing datasets (will be created automatically).
- `requirements.txt`: Python dependencies.
- `README.md`: This file.

## Notes
- This replication is for educational and research purposes only.
- The adversarial attack implementation is simplified and may not match the exact parameters from the paper.
- For full replication, refer to the original paper and use the complete UNSW-NB15 dataset.

## License
MIT