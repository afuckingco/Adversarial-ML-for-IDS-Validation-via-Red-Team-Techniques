# Deep Learning Anomaly Detection Fundamentals

Implementation of fundamental deep learning models for anomaly detection in network traffic.

## Contents
- `src/train.py`: Training script implementing CNN, LSTM, Transformer, and Autoencoder models
- `requirements.txt`: Python dependencies (torch, torchvision, numpy, scikit-learn, pandas, matplotlib)
- `results/`: Directory containing training metrics and ablation studies

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Train models: `python src/train.py`
3. Results will be saved in the `results/` directory

## Models Implemented
- CNN: 1D convolutional network with adaptive pooling
- LSTM: Two-layer LSTM network
- Transformer: Small transformer encoder with positional encoding
- Autoencoder: Unsupervised model for reconstruction-based anomaly detection

## Notes
This script uses synthetic data if the processed dataset from `network-traffic-analytics-pipeline` is not available. For real-world usage, ensure the dataset is available at `data/processed/dataset.parquet`.