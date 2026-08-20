#!/usr/bin/env python3
"""
Evaluation script for IDS model using adversarial traffic.
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
        # Update the MAB with a simulated reward (we don't have the actual alert yet, but we can use the IDS feedback later)
        # For now, we'll assume that if the IDS alerts, it's bad for the evader (reward=0), else good (reward=1)
        # We'll update after we check for alerts? But we are generating and then checking separately.
        # We'll do the update in a separate step if needed.
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

def evaluate_model(model, scaler_mean, scaler_scale, flows):
    """
    Evaluate the model on a list of flows.
    Returns the predictions and probabilities.
    """
    features = np.array([f['features'] for f in flows])
    features_normalized = (features - scaler_mean) / scaler_scale
    pred_proba = model.predict_proba(features_normalized)
    pred_label = model.predict(features_normalized)
    return pred_label, pred_proba[:, 1]  # probability of adversarial class

def main():
    print("Starting IDS evaluation with adversarial traffic...")
    
    # Generate benign traffic
    print("Generating benign traffic...")
    benign_flows = generate_benign_traffic(n=200)
    print(f"Generated {len(benign_flows)} benign flows.")
    
    # Generate adversarial traffic
    print("Generating adversarial traffic (adaptive with IDS feedback)...")
    adversarial_flows, aetg = generate_adversarial_traffic(n=200, ids_feedback=True)
    print(f"Generated {len(adversarial_flows)} adversarial flows.")
    
    # Combine for evaluation
    all_flows = benign_flows + adversarial_flows
    true_labels = [f['label'] for f in all_flows]
    
    # Load the IDS model
    print("Loading IDS model...")
    model, scaler_mean, scaler_scale = load_ids_model()
    
    # Evaluate
    print("Evaluating model...")
    pred_labels, pred_proba = evaluate_model(model, scaler_mean, scaler_scale, all_flows)
    
    # Compute metrics
    from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
    
    f1 = f1_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels)
    recall = recall_score(true_labels, pred_labels)
    try:
        auc = roc_auc_score(true_labels, pred_proba)
    except:
        auc = 0.5  # if only one class present
    
    print("\n=== Results ===")
    print(f"F1-Score: {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    
    # Compute evasion rate (for adversarial flows: percentage predicted as benign)
    adversarial_pred_labels = pred_labels[len(benign_flows):]
    evasion_rate = np.mean(adversarial_pred_labels == 0)  # predicted as benign (0) when actual is adversarial (1)
    print(f"Evasion Rate (adversarial flows predicted as benign): {evasion_rate:.4f}")
    
    # --- FIX: Check alerts from Redis using the correct key pattern ---
    # Previously used r.llen('alerts') which reads a LIST, but push_alerts.py
    # stores each alert as an individual key using r.set('alert:*', ...).
    # Now we count keys matching the pattern 'alert:*' instead.
    alert_count = 0
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        # Use SCAN to count keys with pattern 'alert:*' (efficient for large datasets)
        # Fallback to keys() for simplicity in small-scale experiments
        alert_keys = r.keys('alert:*')
        alert_count = len(alert_keys)
        if alert_count > 0:
            print(f"\n✅ Found {alert_count} alert(s) in Redis (keys: alert:*)")
            # Print first 5 alert keys for verification
            for key in alert_keys[:5]:
                print(f"   - {key}")
        else:
            print("\n⚠️ No alerts found in Redis (pattern: alert:*)")
            print("   This could mean:")
            print("   1. Suricata did not generate alerts for this batch")
            print("   2. push_alerts.py is not running or not connected to Redis")
            print("   3. The alert:* keys were not created")
    except Exception as e:
        print(f"\n⚠️ Could not connect to Redis: {e}")
        alert_count = 0
    
    # Print some adversarial flows that evaded detection (for analysis)
    evaded_indices = [i for i, (label, pred) in enumerate(zip(true_labels, pred_labels)) if label == 1 and pred == 0]
    if evaded_indices:
        print(f"\nNumber of evaded adversarial flows: {len(evaded_indices)}")
        print("First few evaded flows (strategy used):")
        for idx in evaded_indices[:5]:
            flow = all_flows[idx]
            print(f"  Flow {idx}: strategy={flow['raw_result'].get('strategy', 'N/A')}, features={flow['features']}")
    
    # Save results to a file for later use in thesis
    results = {
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'auc': auc,
        'evasion_rate': evasion_rate,
        'n_benign': len(benign_flows),
        'n_adversarial': len(adversarial_flows),
        'alert_count_in_redis': alert_count
    }
    results_path = os.path.join(os.path.dirname(__file__), 'eval_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

if __name__ == '__main__':
    main()
