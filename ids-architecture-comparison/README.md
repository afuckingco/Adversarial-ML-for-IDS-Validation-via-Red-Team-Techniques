# IDS Architecture Comparison

This project compares the performance of different machine learning models (XGBoost, CatBoost, MLP) for Network Intrusion Detection Systems (NIDS). It includes:
- Loading a processed dataset (from the network-traffic-analytics-pipeline or generating a dummy one)
- Training and evaluating XGBoost, CatBoost, and MLP classifiers
- Performing light hyperparameter tuning (grid search) for each model
- Conducting an ablation study to assess feature importance
- Saving results (metrics, ablation, tuned parameters) to the `results/` directory

## Features
- **Model Comparison**: XGBoost, CatBoost, and a simple MLP (from scikit-learn)
- **Evaluation Metrics**: Accuracy, Precision, Recall, F1-score, AUC-ROC
- **Hyperparameter Tuning**: Light grid search over a couple of key hyperparameters for each model
- **Ablation Study**: Measures the drop in performance when each feature is removed
- **Reproducibility**: Fixed random seeds for train/test split and model initialization

## Project Structure
```
ids-architecture-comparison/
├── src/
│   └── train.py                  # Main training script
├── data/
│   └── (optional) processed dataset from network-traffic-analytics-pipeline
├── notebooks/                    # For exploratory analysis (not implemented yet)
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── results/                      # Generated after running train.py (metrics, ablation, etc.)
```

## Installation
```bash
# Clone the repository
git clone <repository-url>
cd ids-architecture-comparison

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage
Run the training script:
```bash
python src/train.py
```

The script will:
1. Check for an existing processed dataset at `../network-traffic-analytics-pipeline/data/processed/dataset.parquet`
   - If found, load it.
   - If not found, generate a synthetic dataset with features mimicking network traffic.
2. Split the data into train and test sets (70/30, stratified).
3. Scale the features using StandardScaler.
4. Train three models: XGBoost, CatBoost, and MLPClassifier (with default hyperparameters).
5. Evaluate each model on the test set and print metrics.
6. Perform light hyperparameter tuning for each model (via a small grid search) and report the best F1 score and parameters.
7. Conduct an ablation study for XGBoost (removing one feature at a time) and report the drop in accuracy and F1.
8. Save all results to the `results/` directory as JSON files.

## Example Output
After running the script, you should see output similar to:
```
=== IDS Architecture Comparison ===
Dataset shape: (2000, 7)
Label distribution: {0: 1050, 1: 950}
Train size: (1400, 7), Test size: (600, 7)

--- Training XGBoost ---
XGBoost metrics: {'accuracy': 0.85, 'precision': 0.83, 'recall': 0.88, 'f1': 0.85, 'auc': 0.92}

--- Training CatBoost ---
CatBoost metrics: {'accuracy': 0.84, 'precision': 0.82, 'recall': 0.87, 'f1': 0.84, 'auc': 0.91}

--- Training MLP ---
MLP metrics: {'accuracy': 0.82, 'precision': 0.80, 'recall': 0.85, 'f1': 0.82, 'auc': 0.89}

--- Light Hyperparameter Tuning (XGBoost) ---
Best params: {'max_depth': 5, 'learning_rate': 0.1}, Best F1: 0.87

--- Ablation Study (XGBoost) ---
Base model metrics: {'accuracy': 0.85, 'precision': 0.83, 'recall': 0.88, 'f1': 0.85, 'auc': 0.92}
Feature importance (drop in accuracy when removed):
  total_packets: accuracy drop = 0.12, F1 drop = 0.11
  avg_packet_size: accuracy drop = 0.09, F1 drop = 0.08
  std_packet_size: accuracy drop = 0.04, F1 drop = 0.03
  unique_src_ips: accuracy drop = 0.03, F1 drop = 0.02
  unique_dst_ips: accuracy drop = 0.02, F1 drop = 0.01
  common_ja3: accuracy drop = 0.01, F1 drop = 0.01

Results saved to results/ directory
=== Training pipeline completed ===
```

## Dependencies
- pandas>=2.0
- numpy>=1.20
- scikit-learn>=1.0
- xgboost>=2.0
- catboost>=1.0
- matplotlib>=3.0 (for potential plotting)
- seaborn>=0.10 (for potential plotting)

## Notes
- The synthetic dataset generation is for demonstration and testing purposes only.
- For real-world usage, replace the data loading part with actual processed data from the `network-traffic-analytics-pipeline` or another source.
- The hyperparameter tuning and ablation study are kept light to respect computational constraints (as per the thesis requirements).
- Random seeds are fixed for reproducibility.

## Results
After running, check the `results/` directory for:
- `metrics.json`: Contains the evaluation metrics for each model (XGBoost, CatBoost, MLP).
- `ablation.json`: Contains the base metrics and the ablation results (drop in accuracy and F1 for each feature).
- `tuned_params.json`: Contains the best hyperparameters found and the corresponding F1 score.

## License
MIT