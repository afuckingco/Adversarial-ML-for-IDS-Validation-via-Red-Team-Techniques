#!/usr/bin/env python3
"""
ETL pipeline for network traffic analytics.
Generates a dummy processed dataset in Parquet format if it doesn't exist.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_processed_data():
    """
    Generate a dummy processed dataset with features for network traffic analysis.
    Returns a pandas DataFrame.
    """
    # Create a time range for two windows: one normal, one adversarial
    base_time = datetime(2026, 8, 15, 12, 0, 0)
    window_duration = timedelta(minutes=5)
    
    data = []
    
    # Normal window
    window_start = base_time
    window_end = window_start + window_duration
    # Normal traffic characteristics
    total_packets = np.random.randint(1000, 2000)
    avg_packet_size = np.random.uniform(400, 600)  # bytes
    std_packet_size = np.random.uniform(50, 150)
    unique_src_ips = np.random.randint(50, 100)
    unique_dst_ips = np.random.randint(30, 80)
    # For JA3, we'll use a list of common JA3s and pick one
    known_ja3 = ['chrome_103', 'chrome_104', 'firefox_102', 'safari_15_6', 'ios_15_5']
    common_ja3 = np.random.choice(known_ja3)
    label = 0  # normal
    
    data.append({
        'window_start': window_start,
        'window_end': window_end,
        'total_packets': total_packets,
        'avg_packet_size': avg_packet_size,
        'std_packet_size': std_packet_size,
        'unique_src_ips': unique_src_ips,
        'unique_dst_ips': unique_dst_ips,
        'common_ja3': common_ja3,
        'label': label
    })
    
    # Adversarial window
    window_start = window_end
    window_end = window_start + window_duration
    # Adversarial traffic characteristics (e.g., more packets, smaller size, more unique IPs)
    total_packets = np.random.randint(5000, 10000)
    avg_packet_size = np.random.uniform(100, 300)  # smaller packets
    std_packet_size = np.random.uniform(20, 100)
    unique_src_ips = np.random.randint(200, 500)  # many sources (like in a scan)
    unique_dst_ips = np.random.randint(50, 150)
    # Generate a random string to represent a JA3 fingerprint (adversarial tool)
    common_ja3 = ''.join(np.random.choice(list('0123456789abcdef'), size=32))
    label = 1  # adversarial
    
    data.append({
        'window_start': window_start,
        'window_end': window_end,
        'total_packets': total_packets,
        'avg_packet_size': avg_packet_size,
        'std_packet_size': std_packet_size,
        'unique_src_ips': unique_src_ips,
        'unique_dst_ips': unique_dst_ips,
        'common_ja3': common_ja3,
        'label': label
    })
    
    df = pd.DataFrame(data)
    return df

def main():
    # Define the path for the processed dataset
    processed_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    processed_path = os.path.join(processed_dir, 'dataset.parquet')
    
    # Check if the processed dataset already exists
    if os.path.exists(processed_path):
        print(f"Processed dataset already exists at {processed_path}")
        print("Loading existing dataset...")
        df = pd.read_parquet(processed_path)
    else:
        print(f"Processed dataset not found. Generating dummy data...")
        df = generate_dummy_processed_data()
        # Save to Parquet
        df.to_parquet(processed_path, index=False)
        print(f"Saved dummy processed dataset to {processed_path}")
    
    # Print some info about the dataset
    print("\nDataset info:")
    print(df.info())
    print("\nDataset contents:")
    print(df)
    
    return df

if __name__ == '__main__':
    main()