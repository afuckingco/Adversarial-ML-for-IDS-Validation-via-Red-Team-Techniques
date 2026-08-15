#!/usr/bin/env python3
"""
Deep Learning Anomaly Detection Fundamentals
Implements custom CNN, LSTM, Transformer, and Autoencoder models for anomaly detection using PyTorch.
Compares performance with supervised models from Task 4 (ids-architecture-comparison).
"""

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import json
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED)

def load_dataset(data_path='../network-traffic-analytics-pipeline/data/processed/dataset.parquet'):
    """
    Load the processed dataset. If it doesn't exist, generate a synthetic dataset.
    """
    if os.path.exists(data_path):
        print(f"Loading dataset from {data_path}")
        df = pd.read_parquet(data_path)
    else:
        print(f"Dataset not found at {data_path}. Generating a synthetic dataset.")
        # Create a synthetic dataset with 2000 samples and 6 features
        n_samples = 2000
        # Features: total_packets, avg_packet_size, std_packet_size, unique_src_ips, unique_dst_ips, common_ja3 (encoded as binary for simplicity)
        X = np.random.randn(n_samples, 6)
        X[:, 0] = np.random.randint(100, 10000, n_samples)   # total_packets
        X[:, 1] = np.random.uniform(50, 1500, n_samples)     # avg_packet_size
        X[:, 2] = np.random.uniform(5, 200, n_samples)       # std_packet_size
        X[:, 3] = np.random.randint(1, 500, n_samples)       # unique_src_ips
        X[:, 4] = np.random.randint(1, 300, n_samples)       # unique_dst_ips
        X[:, 5] = np.random.randint(0, 2, n_samples)         # common_ja3 (binary)
        # Label: 1 if total_packets > 5000 and avg_packet_size < 400 (adversarial pattern)
        y = ((X[:, 0] > 5000) & (X[:, 1] < 400)).astype(int)
        # Add some noise
        flip_idx = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
        y[flip_idx] = 1 - y[flip_idx]
        
        feature_names = ['total_packets', 'avg_packet_size', 'std_packet_size',
                         'unique_src_ips', 'unique_dst_ips', 'common_ja3']
        df = pd.DataFrame(X, columns=feature_names)
        df['label'] = y
        
        # Save the dataset
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_parquet(data_path, index=False)
        print(f"Saved synthetic dataset to {data_path}")
    
    return df

def prepare_data(df, test_size=0.2):
    """
    Prepare data: split into train/test, normalize features.
    Returns: X_train, X_test, y_train, y_test, scaler
    """
    feature_cols = [c for c in df.columns if c != 'label']
    X = df[feature_cols].values
    y = df['label'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=SEED, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

class CNN(nn.Module):
    def __init__(self, input_length, dropout_rate=0.2):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc1 = nn.Linear(32, 64)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        x = x.permute(0, 2, 1)  # -> (batch, input_size, seq_len)
        x = torch.relu(self.conv1(x))
        x = self.pool(x)  # (batch, 32, 1)
        x = x.view(x.size(0), -1)  # (batch, 32)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x

class LSTM(nn.Module):
    def __init__(self, input_length, dropout_rate=0.2):
        super(LSTM, self).__init__()
        self.lstm1 = nn.LSTM(input_size=1, hidden_size=50, batch_first=True)
        self.lstm2 = nn.LSTM(input_size=50, hidden_size=50, batch_first=True)
        self.fc1 = nn.Linear(50, 64)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # x: (batch, seq_len, input_size) -> we expect (batch, input_length, 1)
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)
        x = x[:, -1, :]  # Take the last time step
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x

class Transformer(nn.Module):
    def __init__(self, input_length, d_model=64, nhead=2, num_encoder_layers=2, dropout_rate=0.2):
        super(Transformer, self).__init__()
        self.input_length = input_length
        self.d_model = d_model
        self.embedding = nn.Linear(1, d_model)  # Embed each feature value to d_model dimensions
        self.pos_encoder = PositionalEncoding(d_model, dropout_rate)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dropout=dropout_rate, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        self.fc1 = nn.Linear(d_model, 64)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # x: (batch, input_length, 1)
        x = self.embedding(x)  # (batch, input_length, d_model)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)  # (batch, input_length, d_model)
        x = x.mean(dim=1)  # Global average pooling over the sequence length
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class Autoencoder(nn.Module):
    def __init__(self, input_length, encoding_dim=32, dropout_rate=0.2):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_length, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, encoding_dim),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, input_length),
            nn.Sigmoid()  # Assuming normalized inputs between 0 and 1
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def create_dataloader(X, y=None, batch_size=32, shuffle=True):
    if y is not None:
        dataset = TensorDataset(torch.FloatTensor(X), torch.FloatTensor(y))
    else:
        dataset = TensorDataset(torch.FloatTensor(X))
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

def train_model(model, train_loader, criterion, optimizer, epochs=20, device='cpu'):
    model.train()
    model.to(device)
    for epoch in range(epochs):
        running_loss = 0.0
        for batch in train_loader:
            if len(batch) == 2:
                inputs, labels = batch
                inputs, labels = inputs.to(device), labels.to(device)
            else:
                inputs = batch[0]
                inputs = inputs.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            if len(batch) == 2:
                loss = criterion(outputs.squeeze(), labels)
            else:
                loss = criterion(outputs, inputs)  # For autoencoder
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        # Optional: print epoch loss
        # print(f'Epoch {epoch+1}, Loss: {running_loss/len(train_loader):.4f}')

def evaluate_supervised(model, X_test, y_test, device='cpu'):
    model.eval()
    model.to(device)
    with torch.no_grad():
        inputs = torch.FloatTensor(X_test).to(device)
        outputs = model(inputs)
        probs = outputs.squeeze().cpu().numpy()
        preds = (probs > 0.5).astype(int)
    
    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    auc = roc_auc_score(y_test, probs)
    
    return {
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'auc': auc
    }

def evaluate_autoencoder(autoencoder, X_test_normal, X_test_all, y_test_all, device='cpu'):
    autoencoder.eval()
    autoencoder.to(device)
    with torch.no_grad():
        # Normal data for threshold
        normal_tensor = torch.FloatTensor(X_test_normal).to(device)
        normal_recon = autoencoder(normal_tensor)
        mse_normal = torch.mean((normal_tensor - normal_recon) ** 2, dim=1).cpu().numpy()
        threshold = float(np.mean(mse_normal) + 2 * np.std(mse_normal))
        
        # All test data
        all_tensor = torch.FloatTensor(X_test_all).to(device)
        all_recon = autoencoder(all_tensor)
        mse_all = torch.mean((all_tensor - all_recon) ** 2, dim=1).cpu().numpy()
        
        preds = (mse_all > threshold).astype(int)
    
    acc = float(accuracy_score(y_test_all, preds))
    prec = float(precision_score(y_test_all, preds, zero_division=0))
    rec = float(recall_score(y_test_all, preds, zero_division=0))
    f1 = float(f1_score(y_test_all, preds, zero_division=0))
    auc = float(roc_auc_score(y_test_all, mse_all))
    
    return {
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'auc': auc,
        'threshold': threshold,
        'mse_mean': float(np.mean(mse_all)),
        'mse_std': float(np.std(mse_all))
    }

def main():
    print("=== Deep Learning Anomaly Detection Fundamentals (PyTorch) ===")
    # Load data
    df = load_dataset()
    print(f"Dataset shape: {df.shape}")
    print(f"Label distribution: {df['label'].value_counts().to_dict()}")
    
    # Prepare data
    X_train, X_test, y_train, y_test, scaler = prepare_data(df)
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    
    # Reshape data for models that expect sequences
    # For CNN, LSTM, Transformer: we want (batch, sequence_length, input_size)
    # We'll treat each sample as a sequence of 6 timesteps (one per feature) with 1 feature per timestep.
    X_train_seq = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test_seq = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    input_length = X_train_seq.shape[1]  # 6
    
    # For Autoencoder, we use the original shape (n_features,)
    X_train_ae = X_train
    X_test_ae = X_test
    
    # Extract normal data from training set for Autoencoder training
    X_train_normal = X_train[y_train == 0]
    X_test_normal = X_test[y_test == 0]
    print(f"Normal training samples: {X_train_normal.shape[0]}")
    print(f"Normal test samples: {X_test_normal.shape[0]}")
    print(f"Anomalous test samples: {np.sum(y_test == 1)}")
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Define models
    results = {}
    
    # 1. CNN
    print("\n--- Building and Training CNN ---")
    cnn_model = CNN(input_length=input_length, dropout_rate=0.2)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(cnn_model.parameters(), lr=0.001)
    train_loader = create_dataloader(X_train_seq, y_train, batch_size=32, shuffle=True)
    train_model(cnn_model, train_loader, criterion, optimizer, epochs=20, device=device)
    cnn_metrics = evaluate_supervised(cnn_model, X_test_seq, y_test, device=device)
    results['cnn'] = cnn_metrics
    print(f"CNN Metrics: {cnn_metrics}")
    
    # 2. LSTM
    print("\n--- Building and Training LSTM ---")
    lstm_model = LSTM(input_length=input_length, dropout_rate=0.2)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(lstm_model.parameters(), lr=0.001)
    train_loader = create_dataloader(X_train_seq, y_train, batch_size=32, shuffle=True)
    train_model(lstm_model, train_loader, criterion, optimizer, epochs=20, device=device)
    lstm_metrics = evaluate_supervised(lstm_model, X_test_seq, y_test, device=device)
    results['lstm'] = lstm_metrics
    print(f"LSTM Metrics: {lstm_metrics}")
    
    # 3. Transformer
    print("\n--- Building and Training Transformer ---")
    transformer_model = Transformer(input_length=input_length, d_model=64, nhead=2, num_encoder_layers=2, dropout_rate=0.2)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(transformer_model.parameters(), lr=0.001)
    train_loader = create_dataloader(X_train_seq, y_train, batch_size=32, shuffle=True)
    train_model(transformer_model, train_loader, criterion, optimizer, epochs=20, device=device)
    transformer_metrics = evaluate_supervised(transformer_model, X_test_seq, y_test, device=device)
    results['transformer'] = transformer_metrics
    print(f"Transformer Metrics: {transformer_metrics}")
    
    # 4. Autoencoder (unsupervised)
    print("\n--- Building and Training Autoencoder ---")
    autoencoder = Autoencoder(input_length=X_train.shape[1], encoding_dim=32, dropout_rate=0.2)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(autoencoder.parameters(), lr=0.001)
    # Train on normal data only
    normal_loader = create_dataloader(X_train_normal, batch_size=32, shuffle=True)
    train_model(autoencoder, normal_loader, criterion, optimizer, epochs=20, device=device)
    ae_metrics = evaluate_autoencoder(autoencoder, X_test_normal, X_test_ae, y_test, device=device)
    results['autoencoder'] = ae_metrics
    print(f"Autoencoder Metrics: {ae_metrics}")
    
    # Ablation study: effect of dropout rate on CNN (as an example)
    print("\n--- Ablation Study: Dropout Rate on CNN ---")
    dropout_rates = [0.0, 0.2, 0.5]
    ablation_results = []
    for dr in dropout_rates:
        model = CNN(input_length=input_length, dropout_rate=dr)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        train_loader = create_dataloader(X_train_seq, y_train, batch_size=32, shuffle=True)
        train_model(model, train_loader, criterion, optimizer, epochs=10, device=device)  # fewer epochs for speed
        metrics = evaluate_supervised(model, X_test_seq, y_test, device=device)
        ablation_results.append({'dropout_rate': dr, 'metrics': metrics})
        print(f"  Dropout {dr}: F1 = {metrics['f1']:.4f}")
    
    # Load results from Task 4 (ids-architecture-comparison) for comparison
    task4_results_path = '../ids-architecture-comparison/results/metrics.json'
    if os.path.exists(task4_results_path):
        with open(task4_results_path, 'r') as f:
            task4_results = json.load(f)
        print("\n--- Task 4 Results (Supervised Models) ---")
        for model_name, metrics in task4_results.items():
            print(f"{model_name}: {metrics}")
    else:
        print("\n--- Task 4 results not found. Skipping comparison. ---")
        task4_results = {}
    
    # Save results
    os.makedirs('results', exist_ok=True)
    with open('results/metrics.json', 'w') as f:
        json.dump(results, f, indent=2)
    with open('results/ablation_dropout_cnn.json', 'w') as f:
        json.dump(ablation_results, f, indent=2)
    
    print("\nResults saved to results/ directory")
    print("=== Deep Learning Anomaly Detection Fundamentals completed ===")

if __name__ == '__main__':
    main()