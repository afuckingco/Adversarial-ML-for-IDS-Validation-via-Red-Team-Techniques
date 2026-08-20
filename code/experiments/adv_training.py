#!/usr/bin/env python3
"""
Experiment: Adversarial training to improve IDS robustness.
"""

import sys
import os
import json
import time
import numpy as np
import requests
import redis
import tls_client
import random
from pathlib import Path

# Add the adversarial-traffic-generator directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'adversarial-traffic-generator'))

from new_traffic_gen import generate_request, random_ja3, random_ja4, AdaptiveEvasionTrafficGenerator

def extract_features_from_traffic_result(traffic_result):
    """
    Extract the 6 features used by the IDS from a traffic result.
    This mirrors the feature extraction in the IDS service.
    """
    # Default values (the mean from the training data)
    total_packets = 5051
    avg_packet_size = traffic_result.get('response_length', 0)  # we use the actual response length as avg_packet_size
    std_packet_size = 103
    unique_src_ips = 251
    unique_dst_ips = 149
    # Determine common_ja3 from JA3 string
    ja3_str = traffic_result.get('ja3') or traffic_result.get('ja4', '')
    # List of known benign JA3 strings (subset) for common_ja3 feature
    benign_ja3_list = [
        'chrome_116', 'firefox_108', 'safari_15_3', 'edge_101',
        'okhttp4_android_8', 'nike_android_mobile'
    ]
    common_ja3 = 0
    if ja3_str:
        for benign in benign_ja3_list:
            if benign in ja3_str:
                common_ja3 = 1
                break
    return [total_packets, avg_packet_size, std_packet_size, unique_src_ips, unique_dst_ips, common_ja3]

def generate_benign_traffic(n=100, target_url="http://localhost:8082"):
    """
    Generate benign traffic (using fixed, common JA3 and no adaptation).
    We'll use a common JA3 to make it look benign.
    """
    benign_flows = []
    for _ in range(n):
        # Use a fixed common JA3 to make it benign
        result = generate_request(
            target_url=target_url,
            ja3='chrome_116',  # a common JA3
            jitter_range=(0.1, 0.5)
        )
        features = extract_features_from_traffic_result(result)
        benign_flows.append({
            'features': features,
            'label': 0,  # benign
            'raw_result': result
        })
    return benign_flows

def generate_adversarial_traffic(n=100, target_url="http://localhost:8082", ids_feedback=True):
    """
    Generate adversarial traffic using the adaptive evasion traffic generator with IDS feedback.
    """
    # Initialize the adaptive generator
    aetg = AdaptiveEvasionTrafficGenerator(
        ids_feedback=ids_feedback,
        redis_host='localhost',
        redis_port=6379,
        log_ingest_url='http://localhost:5000/log'
    )
    # Context: we'll use a fixed context for simplicity
    context = [0.1, 0.1, 0]  # [alert_rate, jitter, protocol]
    adversarial_flows = []
    for i in range(n):
        result = aetg.generate_traffic(context=context, target_url=target_url)
        features = extract_features_from_traffic_result(result)
        adversarial_flows.append({
            'features': features,
            'label': 1,  # adversarial
            'raw_result': result,
            'strategy': result.get('strategy')
        })
    return adversarial_flows, aetg

def load_ids_model():
    """
    Load the XGBoost model and scaler parameters from the mini-SoC.
    """
    model_path = os.path.join(os.path.dirname(__file__), '..', 'mini-soc-enterprise-arch', 'shared', 'model', 'xgb_model.json')
    scaler_path = os.path.join(os.path.dirname(__file__), '..', 'mini-soc-enterprise-arch', 'shared', 'model', 'scaler_params.json')
    
    import xgboost as xgb
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    
    with open(scaler_path, 'r') as f:
        scaler_params = json.load(f)
    scaler_mean = np.array(scaler_params['mean'])
    scaler_scale = np.array(scaler_params['scale'])
    
    return model, scaler_mean, scaler_scale

def train_model(X_train, y_train):
    """
    Train an XGBoost model on the given data.
    Returns the trained model.
    """
    import xgboost as xgb
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        eval_metric='logloss',
        use_label_encoder=False,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, scaler_mean, scaler_scale, X, y):
    """
    Evaluate the model on the given data.
    Returns the predictions and probabilities.
    """
    X_normalized = (X - scaler_mean) / scaler_scale
    pred_proba = model.predict_proba(X_normalized)
    pred_label = model.predict(X_normalized)
    return pred_label, pred_proba[:, 1]  # probability of adversarial class

def main():
    print("Starting adversarial training experiment...")
    
    # Generate benign traffic
    print("Generating benign traffic...")
    benign_flows = generate_benign_traffic(n=300)
    print(f"Generated {len(benign_flows)} benign flows.")
    
    # Generate adversarial traffic
    print("Generating adversarial traffic (adaptive with IDS feedback)...")
    adversarial_flows, aetg = generate_adversarial_traffic(n=300, ids_feedback=True)
    print(f"Generated {len(adversarial_flows)} adversarial flows.")
    
    # Prepare data
    X_benign = np.array([f['features'] for f in benign_flows])
    y_benign = np.array([f['label'] for f in benign_flows])
    X_adv = np.array([f['features'] for f in adversarial_flows])
    y_adv = np.array([f['label'] for f in adversarial_flows])
    
    # Split into train and test (70% train, 30% test)
    from sklearn.model_selection import train_test_split
    X_benign_train, X_benign_test, y_benign_train, y_benign_test = train_test_split(
        X_benign, y_benign, test_size=0.3, random_state=42, stratify=y_benign
    )
    X_adv_train, X_adv_test, y_adv_train, y_adv_test = train_test_split(
        X_adv, y_adv, test_size=0.3, random_state=42, stratify=y_adv
    )
    
    # Combine for training
    # Baseline: train on benign only
    X_train_baseline = X_benign_train
    y_train_baseline = y_benign_train
    
    # Adversarial training: train on 50% benign, 50% adversarial (from the training splits)
    # We'll take half of each
    n_benign_half = len(X_benign_train) // 2
    n_adv_half = len(X_adv_train) // 2
    X_train_mixed = np.vstack([
        X_benign_train[:n_benign_half],
        X_adv_train[:n_adv_half]
    ])
    y_train_mixed = np.hstack([
        y_benign_train[:n_benign_half],
        y_adv_train[:n_adv_half]
    ])
    
    # Test set: combine benign and adversarial test sets
    X_test = np.vstack([X_benign_test, X_adv_test])
    y_test = np.hstack([y_benign_test, y_adv_test])
    
    # Load the scaler parameters (we'll use the same scaler as the original model)
    # We need to compute the mean and scale from the training data? 
    # But the original model was trained on some data and we have the scaler parameters.
    # We'll use the scaler parameters from the original model for consistency.
    _, scaler_mean, scaler_scale = load_ids_model()
    
    # Train baseline model (on benign only)
    print("Training baseline model (benign only)...")
    model_baseline = train_model(X_train_baseline, y_train_baseline)
    
    # Train adversarially trained model (on mixed)
    print("Training adversarially trained model (50% benign, 50% adversarial)...")
    model_mixed = train_model(X_train_mixed, y_train_mixed)
    
    # Evaluate baseline model on test set
    print("Evaluating baseline model...")
    y_pred_baseline, y_pred_proba_baseline = evaluate_model(model_baseline, scaler_mean, scaler_scale, X_test, y_test)
    
    # Evaluate adversarially trained model on test set
    print("Evaluating adversarially trained model...")
    y_pred_mixed, y_pred_proba_mixed = evaluate_model(model_mixed, scaler_mean, scaler_scale, X_test, y_test)
    
    # Compute metrics
    from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
    
    # Baseline
    f1_baseline = f1_score(y_test, y_pred_baseline)
    precision_baseline = precision_score(y_test, y_pred_baseline)
    recall_baseline = recall_score(y_test, y_pred_baseline)
    try:
        auc_baseline = roc_auc_score(y_test, y_pred_proba_baseline)
    except:
        auc_baseline = 0.5
    
    # Mixed (adversarially trained)
    f1_mixed = f1_score(y_test, y_pred_mixed)
    precision_mixed = precision_score(y_test, y_pred_mixed)
    recall_mixed = recall_score(y_test, y_pred_mixed)
    try:
        auc_mixed = roc_auc_score(y_test, y_pred_proba_mixed)
    except:
        auc_mixed = 0.5
    
    # Evasion rate (for adversarial test samples: percentage predicted as benign)
    # We need to separate the adversarial test samples
    n_benign_test = len(X_benign_test)
    # The test set is [benign_test, adv_test]
    y_test_adv = y_test[n_benign_test:]
    y_pred_baseline_adv = y_pred_baseline[n_benign_test:]
    y_pred_mixed_adv = y_pred_mixed[n_benign_test:]
    
    evasion_rate_baseline = np.mean(y_pred_baseline_adv == 0)  # predicted as benign when actual is adversarial
    evasion_rate_mixed = np.mean(y_pred_mixed_adv == 0)
    
    print("\n=== Results ===")
    print("Baseline model (trained on benign only):")
    print(f"  F1-Score: {f1_baseline:.4f}")
    print(f"  Precision: {precision_baseline:.4f}")
    print(f"  Recall: {recall_baseline:.4f}")
    print(f"  AUC-ROC: {auc_baseline:.4f}")
    print(f"  Evasion Rate: {evasion_rate_baseline:.4f}")
    
    print("\nAdversarially trained model (50% benign, 50% adversarial):")
    print(f"  F1-Score: {f1_mixed:.4f}")
    print(f"  Precision: {precision_mixed:.4f}")
    print(f"  Recall: {recall_mixed:.4f}")
    print(f"  AUC-ROC: {auc_mixed:.4f}")
    print(f"  Evasion Rate: {evasion_rate_mixed:.4f}")
    
    # Improvement
    print("\nImprovement with adversarial training:")
    print(f"  F1-Score change: {f1_mixed - f1_baseline:.4f}")
    print(f"  Evasion Rate change: {evasion_rate_mixed - evasion_rate_baseline:.4f} (negative improvement means lower evasion rate)")
    
    # Save results
    results = {
        'baseline': {
            'f1': f1_baseline,
            'precision': precision_baseline,
            'recall': recall_baseline,
            'auc': auc_baseline,
            'evasion_rate': evasion_rate_baseline
        },
        'adversarially_trained': {
            'f1': f1_mixed,
            'precision': precision_mixed,
            'recall': recall_mixed,
            'auc': auc_mixed,
            'evasion_rate': evasion_rate_mixed
        },
        'n_benign_train': len(X_benign_train),
        'n_adv_train': len(X_adv_train),
        'n_benign_test': len(X_benign_test),
        'n_adv_test': len(X_adv_test)
    }
    results_path = os.path.join(os.path.dirname(__file__), 'adv_training_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

if __name__ == '__main__':
    main()