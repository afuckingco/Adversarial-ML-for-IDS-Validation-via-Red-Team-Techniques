#!/usr/bin/env python3
"""
Replication of adversarial ML experiments on NIDS using UNSW-NB15 subset.
This script uses synthetic data for demonstration due to resource constraints.
"""

import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import argparse

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

def generate_synthetic_data(n_samples=1200, n_features=49, random_state=42):
    """
    Generate synthetic data mimicking UNSW-NB15 structure.
    Returns:
        X: features (n_samples, n_features)
        y: labels (0 for normal, 1 for attack)
    """
    np.random.seed(random_state)
    # Generate features from a mixture of Gaussians to simulate some structure
    X = np.random.randn(n_samples, n_features)
    # Create labels: 20% attacks
    y = np.zeros(n_samples, dtype=int)
    attack_idx = np.random.choice(n_samples, size=int(0.2 * n_samples), replace=False)
    y[attack_idx] = 1
    # Make attack samples slightly shifted to be separable
    X[attack_idx] += 0.5 * np.random.randn(len(attack_idx), n_features)
    return X, y

class SimpleMLP(nn.Module):
    def __init__(self, n_features, n_hidden=64):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(n_features, n_hidden)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(n_hidden, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return x

def train_model(model, X_train, y_train, epochs=20, lr=0.01):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
        if (epoch+1) % 5 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

def evaluate_model(model, X, y):
    model.eval()
    with torch.no_grad():
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y).unsqueeze(1)
        outputs = model(X_tensor)
        predicted = (outputs > 0.5).float()
        accuracy = accuracy_score(y_tensor.numpy(), predicted.numpy())
    return accuracy

def fgsm_attack(model, X, y, epsilon=0.1):
    """
    Fast Gradient Sign Method (FGSM) attack.
    """
    model.eval()
    X_tensor = torch.FloatTensor(X).requires_grad_(True)
    y_tensor = torch.FloatTensor(y).unsqueeze(1)
    
    outputs = model(X_tensor)
    loss = nn.BCELoss()(outputs, y_tensor)
    
    model.zero_grad()
    loss.backward()
    
    # Get the sign of the gradients
    grad_sign = X_tensor.grad.data.sign()
    
    # Create perturbed image
    X_adv = X_tensor + epsilon * grad_sign
    # Clamp to [0,1] if we normalized, but we'll just return as is
    return X_adv.detach().numpy()

def main():
    parser = argparse.ArgumentParser(description='Replicate adversarial ML on NIDS')
    parser.add_argument('--epsilon', type=float, default=0.1, help='FGSM epsilon')
    parser.add_argument('--samples', type=int, default=1200, help='Total samples')
    parser.add_argument('--features', type=int, default=49, help='Number of features')
    args = parser.parse_args()
    
    print("Generating synthetic data...")
    X, y = generate_synthetic_data(n_samples=args.samples, n_features=args.features)
    
    # Split into train and test (80% train, 20% test)
    n_train = int(0.8 * len(X))
    X_train, X_test = X[:n_train], X[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    
    # Normalize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    print(f"Training samples: {np.sum(y_train==0)} normal, {np.sum(y_train==1)} attack")
    print(f"Test samples: {np.sum(y_test==0)} normal, {np.sum(y_test==1)} attack")
    
    # Initialize model
    model = SimpleMLP(n_features=args.features)
    
    # Train
    print("\nTraining model...")
    train_model(model, X_train, y_train, epochs=20)
    
    # Evaluate on benign test set
    benign_acc = evaluate_model(model, X_test, y_test)
    print(f"\nBenign test accuracy: {benign_acc:.4f}")
    
    # Generate adversarial examples using FGSM
    print(f"\nGenerating FGSM adversarial examples with epsilon={args.epsilon}...")
    X_adv = fgsm_attack(model, X_test, y_test, epsilon=args.epsilon)
    
    # Evaluate on adversarial examples
    adv_acc = evaluate_model(model, X_adv, y_test)
    evasion_rate = 1.0 - adv_acc  # proportion of adversarial examples that are misclassified
    print(f"Adversarial test accuracy: {adv_acc:.4f}")
    print(f"Evasion rate (FGSM): {evasion_rate:.4f}")
    
    # Save results
    os.makedirs('results', exist_ok=True)
    with open('results/metrics.txt', 'w') as f:
        f.write(f'Benign accuracy: {benign_acc:.4f}\\n')
        f.write(f'Adversarial accuracy: {adv_acc:.4f}\\n')
        f.write(f'Evasion rate (FGSM): {evasion_rate:.4f}\\n')
    print("\nResults saved to results/metrics.txt")

if __name__ == '__main__':
    main()