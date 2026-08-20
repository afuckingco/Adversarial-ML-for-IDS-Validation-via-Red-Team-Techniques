import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_aetg_selects_action():
    # We'll implement AdaptiveEvasionTrafficGenerator in traffic_gen.py
    from traffic_gen import AdaptiveEvasionTrafficGenerator
    aetg = AdaptiveEvasionTrafficGenerator()
    action = aetg.select_strategy(context=[0.3, 0.1, 0])
    assert action in aetg.action_space

def test_esm_calculation():
    from stealth_metric import calculate_esm
    benign = [{"length": 60, "iat": 0.1}] * 10
    adv = [{"length": 62, "iat": 0.12}] * 10
    esm = calculate_esm(benign, adv)
    assert 0 <= esm <= 1  # KL-divergence based, normalized

def test_mab_update():
    from mab_optimizer import ContextualMAB
    mab = ContextualMAB(n_actions=5, context_dim=2)
    mab.update(context=[0.5, 0.5], action=2, reward=1.0)
    assert mab.action_counts[2] == 1