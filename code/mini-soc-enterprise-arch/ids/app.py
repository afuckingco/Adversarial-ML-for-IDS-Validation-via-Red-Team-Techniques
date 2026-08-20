# IDS Service
# Continuously reads logs from Redis list 'raw_logs', extracts features, runs inference with XGBoost model,
# and pushes alerts to Redis list 'alerts' if the prediction is adversarial (label 1).

import redis
import json
import os
import numpy as np
import xgboost as xgb
import time

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, db=0)

# Load model and scaler parameters
model_path = '/app/model/xgb_model.json'
scaler_path = '/app/model/scaler_params.json'

# Load the model
model = xgb.XGBClassifier()
model.load_model(model_path)

# Load scaler parameters
with open(scaler_path, 'r') as f:
    scaler_params = json.load(f)
scaler_mean = np.array(scaler_params['mean'])
scaler_scale = np.array(scaler_params['scale'])

def extract_features(log_entry):
    """
    Extract features from a log entry.
    This is a placeholder function. In a real system, you would parse the log and extract relevant features.
    For this example, we assume the log entry is a dictionary with the following keys:
    - total_packets
    - avg_packet_size
    - std_packet_size
    - unique_src_ips
    - unique_dst_ips
    - common_ja3 (encoded as 0 or 1)
    If the log entry does not have these keys, we return a default vector of zeros.
    """
    feature_names = ['total_packets', 'avg_packet_size', 'std_packet_size',
                     'unique_src_ips', 'unique_dst_ips', 'common_ja3']
    features = []
    for fname in feature_names:
        val = log_entry.get(fname, 0)
        features.append(float(val))
    return np.array(features).reshape(1, -1)

def main():
    print("IDS service started. Waiting for logs...")
    while True:
        # Blocking pop from the 'raw_logs' list (with timeout to avoid busy waiting)
        # We use brpop with a timeout of 1 second to allow for graceful shutdown if needed.
        # However, for simplicity, we'll use a non-blocking pop with a sleep.
        # Alternatively, we can use blpop (blocking pop) which waits until an element is available.
        # We'll use blpop with a timeout of 1 second.
        try:
            # blpop returns a tuple (key, value) or None if timeout
            result = r.blpop(['raw_logs'], timeout=1)
            if result is None:
                continue
            key, value = result
            log_entry = json.loads(value)
            
            # Extract features
            features = extract_features(log_entry)
            # Normalize features
            features_normalized = (features - scaler_mean) / scaler_scale
            # Predict
            pred_proba = model.predict_proba(features_normalized)[0]
            pred_label = model.predict(features_normalized)[0]
            
            # If the prediction is adversarial (label 1), push to alerts
            if pred_label == 1:
                alert = {
                    'log_entry': log_entry,
                    'prediction_probability_adversarial': float(pred_proba[1]),
                    'timestamp': time.time()
                }
                r.lpush('alerts', json.dumps(alert))
                print(f"Alert generated: {log_entry}")
            else:
                # Optionally, we can log normal traffic for debugging
                pass
        except Exception as e:
            print(f"Error in IDS service: {e}")
            time.sleep(1)  # Avoid tight loop on error

if __name__ == '__main__':
    main()