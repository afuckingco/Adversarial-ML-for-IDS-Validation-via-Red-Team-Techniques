import numpy as np
from scipy.stats import entropy

def calculate_esm(benign_traffic, adv_traffic, bins=10):
    """
    Calculate Evasion Stealth Metric as 1 - normalized JS-divergence
    between benign and adversarial traffic feature distributions.
    Returns value in [0,1] where 1 = indistinguishable.
    """
    # Extract features: packet length, inter-arrival time (iat)
    def extract_features(traffic):
        lengths = [p['length'] for p in traffic if 'length' in p]
        iats = [p['iat'] for p in traffic if 'iat' in p]
        return np.array(lengths + iats)  # Simple concatenation
    
    benign_feat = extract_features(benign_traffic)
    adv_feat = extract_features(adv_traffic)
    
    if len(benign_feat) == 0 or len(adv_feat) == 0:
        return 0.0
    
    # Create histograms
    min_val = min(np.min(benign_feat), np.min(adv_feat))
    max_val = max(np.max(benign_feat), np.max(adv_feat))
    bins_edges = np.linspace(min_val, max_val, bins+1)
    
    hist_b, _ = np.histogram(benign_feat, bins=bins_edges, density=True)
    hist_a, _ = np.histogram(adv_feat, bins=bins_edges, density=True)
    
    # Avoid zeros for KL
    hist_b = np.clip(hist_b, 1e-10, None)
    hist_a = np.clip(hist_a, 1e-10, None)
    
    # JS divergence
    m = (hist_b + hist_a) / 2
    js = (entropy(hist_b, m) + entropy(hist_a, m)) / 2
    
    # Normalize JS to [0,1] (max JS for binary is log2)
    max_js = np.log(2)
    esm = 1 - (js / max_js)
    return np.clip(esm, 0, 1)

def calculate_esm_from_dicts(benign_dicts, adv_dicts):
    """Helper for traffic dicts from generator"""
    return calculate_esm(benign_dicts, adv_dicts)