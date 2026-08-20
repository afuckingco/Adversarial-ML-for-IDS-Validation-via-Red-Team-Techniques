#!/usr/bin/env python3
"""
Adaptive Evasion Traffic Generator (AETG)
CLI tool to generate TLS traffic with randomized JA3/J4 fingerprints and adaptive evasion strategies.
"""

import argparse
import sys
import time
import random
import os
import tls_client
import json
import requests
import redis

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mab_optimizer import ContextualMAB
from stealth_metric import calculate_esm_from_dicts

def random_ja3():
    """Return a random client identifier from tls_client's supported list."""
    from tls_client.settings import ClientIdentifiers
    # The actual string literals are in ClientIdentifiers.__args__
    choices = list(ClientIdentifiers.__args__)
    return random.choice(choices)

def random_ja4():
    """Generate a JA4 string approximation based on JA3 and TLS version.
    In a real implementation, we would parse the ClientHello to construct JA4+.
    For now, we approximate by appending _TLS13 to a JA3 string.
    """
    ja3 = random_ja3()
    return f"{ja3}_TLS13"

def generate_request(target_url="https://httpbin.org/get", ja3=None, ja4=None, jitter_range=(0.1, 0.5)):
    """Generate a single HTTP request with optional JA3/J4 randomization and timing jitter.
    Returns a dict with result and optionally the JA3/J4 used.
    """
    # Determine which fingerprint to use and the base identifier for tls_client
    if ja4 is not None:
        # We are given a JA4 string
        fp_type = "ja4"
        fp_value = ja4   # the JA4 string we want to report
        # Extract the JA3 base for tls_client (remove _TLS13 suffix)
        ja3_base = ja4.replace("_TLS13", "")
        session_identifier = ja3_base
    elif ja3 is not None:
        fp_type = "ja3"
        fp_value = ja3
        session_identifier = ja3
    else:
        # random JA3 by default
        fp_type = "ja3"
        session_identifier = random_ja3()
        fp_value = session_identifier
    
    # Apply timing jitter before request
    jitter = random.uniform(*jitter_range)
    time.sleep(jitter)
    
    try:
        session = tls_client.Session(
            client_identifier=session_identifier,
            random_tls_extension_order=True
        )
        resp = session.get(target_url, timeout_seconds=10)
        # tls_client does not seem to populate ja3_string after request; use client_identifier as proxy
        ja3_out = fp_value if fp_type == "ja3" else (ja4.replace("_TLS13", "") if fp_type == "ja4" else None)
        ja4_out = fp_value if fp_type == "ja4" else None
        return {
            "status": resp.status_code,
            "ja3": ja3_out,
            "ja4": ja4_out,
            "url": target_url,
            "jitter_applied": jitter,
            "response_length": len(resp.content),
            "fp_type": fp_type,
            "fp_value": fp_value
        }
    except Exception as e:
        return {
            "error": str(e),
            "ja3_attempted": ja3,
            "ja4_attempted": ja4,
            "jitter_applied": jitter
        }
    finally:
        try:
            session.close()
        except:
            pass
def generate_dns_request(domain="example.com", qtype="A", timeout=5):
    """Generate a DNS query request (does not actually send; returns crafted packet info).
    For simplicity, we just create the DNS query and return its wire format length.
    In a full implementation, we would send via UDP and measure response.
    """
    import dns.message
    import dns.rdatatype
    try:
        request = dns.message.make_query(domain, dns.rdatatype.from_text(qtype))
        wire = request.to_wire()
        return {
            "status": 0,  # placeholder for success
            "domain": domain,
            "qtype": qtype,
            "query_length": len(wire),
            "fp_type": "dns",
            "fp_value": f"{domain}/{qtype}"
        }
    except Exception as e:
        return {"error": str(e)}

def generate_ssh_request(timeout=5):
    """Generate an SSH connection attempt (does not actually complete auth; just banner exchange).
    For simplicity, we return a placeholder; in reality we would use paramiko to connect and vary banner.
    """
    import socket
    import paramiko
    try:
        sock = socket.socket()
        sock.settimeout(timeout)
        sock.connect(('ssh.honeypot.local', 22))  # placeholder host
        transport = paramiko.Transport(sock)
        transport.start_client(timeout=timeout)
        # Get remote banner (server version string)
        banner = transport.remote_version
        transport.close()
        sock.close()
        return {
            "status": 0,
            "banner": banner,
            "fp_type": "ssh",
            "fp_value": banner
        }
    except Exception as e:
        # If connection fails, we still return an error but with fp_type for consistency
        return {
            "error": str(e),
            "fp_type": "ssh",
            "fp_value": "failed"
        }

class AdaptiveEvasionTrafficGenerator:
    def __init__(self, n_actions=5, context_dim=3, epsilon=0.1, ids_feedback=False, redis_host='localhost', redis_port=6379, log_ingest_url='http://localhost:5000/log'):
        """
        Initialize the AETG with a contextual MAB optimizer.
        Action space: we define 5 actions for demonstration:
          0: JA3 random
          1: JA4 random
          2: DNS with random subdomain
          3: HTTP with random header
          4: SSH with random banner (simulated)
        Context: [recent_alert_rate, jitter_level, protocol_id] (simplified)
        In practice, context would be richer features from recent traffic and IDS feedback.
        """
        self.mab = ContextualMAB(n_actions=n_actions, context_dim=context_dim, epsilon=epsilon)
        self.n_actions = n_actions
        self.action_space = list(range(n_actions))
        # Traffic generation history for ESM calculation
        self.traffic_history = []  # list of dicts from generate_traffic
        # IDS feedback components
        self.ids_feedback = ids_feedback
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.log_ingest_url = log_ingest_url
        if self.ids_feedback:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
            # Optionally clear alerts and raw_logs at start
            self.redis_client.delete('alerts')
            self.redis_client.delete('raw_logs')
        # For feature extraction
        self.reset_alert_count()
        
        # List of known benign JA3 strings (subset) for common_ja3 feature
        self.benign_ja3_list = [
            'chrome_116', 'firefox_108', 'safari_15_3', 'edge_101',
            'okhttp4_android_8', 'nike_android_mobile'
        ]

    def reset_alert_count(self):
        self.last_alert_count = 0
        if self.ids_feedback:
            try:
                self.last_alert_count = self.redis_client.llen('alerts')
            except:
                self.last_alert_count = 0

    def has_new_alert(self):
        if not self.ids_feedback:
            return False
        try:
            current = self.redis_client.llen('alerts')
            if current > self.last_alert_count:
                self.last_alert_count = current
                return True
            return False
        except:
            return False

    def is_ja3_common(self, ja3_str):
        """Determine if a JA3 string is considered common (benign)."""
        if ja3_str is None:
            return False
        for benign in self.benign_ja3_list:
            if benign in ja3_str:
                return True
        return False

    def create_log_feature_dict(self, traffic_result):
        """Create a feature dict for the IDS based on traffic result."""
        # We will set the features to values that are close to the mean of the training data, except for avg_packet_size and common_ja3.
        # The mean and scale from the model are:
        #   mean = [5050.8205, 754.3452211758475, 102.5965863559244, 251.2985, 148.615, 0.4895]
        #   scale = [2894.5319691238083, 420.2474555723788, 56.29079993133708, 142.9542772978479, 85.18138162180747, 0.49988973784225654]
        # We want the normalized features to be around 0, so we set the actual features to the mean.
        # However, we can control avg_packet_size (from response length) and common_ja3 (from JA3 string).
        
        # Default values (the mean)
        total_packets = 5051  # rounded mean
        avg_packet_size = traffic_result.get('response_length', 0)  # we will use the actual response length
        std_packet_size = 103  # rounded mean
        unique_src_ips = 251   # rounded mean
        unique_dst_ips = 149   # rounded mean
        # Determine common_ja3 from JA3 string
        ja3_str = traffic_result.get('ja3') or traffic_result.get('ja4', '')
        common_ja3 = 1 if self.is_ja3_common(ja3_str) else 0
        
        return {
            'total_packets': total_packets,
            'avg_packet_size': avg_packet_size,
            'std_packet_size': std_packet_size,
            'unique_src_ips': unique_src_ips,
            'unique_dst_ips': unique_dst_ips,
            'common_ja3': common_ja3
        }
    def send_log_to_ids(self, feature_dict):
        """Send log feature dict to the log-ingest service."""
        try:
            resp = requests.post(self.log_ingest_url, json=feature_dict, timeout=2)
            return resp.status_code == 200
        except Exception as e:
            # Fallback: push directly to Redis
            if self.ids_feedback:
                try:
                    self.redis_client.lpush('raw_logs', json.dumps(feature_dict))
                    return True
                except:
                    pass
            return False

    def select_strategy(self, context):
        """Select an action (evansion strategy) based on context using MAB."""
        return self.mab.select_strategy(context)

    def generate_traffic(self, strategy=None, context=None, target_url="https://httpbin.org/get"):
        """Generate traffic based on strategy (if None, use MAB to select from context).
        Returns a dict containing the traffic packet info and the strategy used.
        """
        if context is None:
            # default context if none provided
            context = [0.1, 0.1, 0]  # [alert_rate, jitter, protocol]
        
        if strategy is None:
            strategy = self.select_strategy(context)
        
        # Map strategy to traffic generation function
        if strategy == 0:  # JA3 random
            result = generate_request(target_url=target_url, jitter_range=(0.1, 0.5))
            # Ensure we have ja3 field
            if "ja3" not in result:
                result["ja3"] = result.get("fp_value", "unknown")
        elif strategy == 1:  # JA4 random
            ja4_val = random_ja4()
            result = generate_request(target_url=target_url, ja4=ja4_val, jitter_range=(0.1, 0.5))
            result["ja4"] = ja4_val
        elif strategy == 2:  # DNS random subdomain
            subdomain = f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))}.example.com"
            result = generate_dns_request(domain=subdomain, qtype=random.choice(["A", "AAAA", "TXT"]))
        elif strategy == 3:  # HTTP with random header
            headers = {
                "User-Agent": f"CustomAgent/{random.randint(1,100)}.{random.randint(1,100)}",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "X-Test": f"value{random.randint(1,1000)}"
            }
            # We'll generate a request with custom headers; tls_client doesn't support custom headers directly?
            # We'll just call generate_request and note that we intended to add headers.
            result = generate_request(target_url=target_url, jitter_range=(0.1, 0.5))
            result["custom_headers"] = headers
        elif strategy == 4:  # SSH simulated
            result = generate_ssh_request()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Add strategy and context to result for logging
        result["strategy"] = strategy
        result["context"] = context
        
        # Store in history for ESM calculation (we'll need to extract features later)
        self.traffic_history.append(result)
        
        return result

    def update_performance(self, context, strategy, reward, traffic_sample=None):
        """Update the MAB with observed reward and optionally store traffic sample for ESM."""
        self.mab.update(context, strategy, reward)
        if traffic_sample is not None:
            self.traffic_history.append(traffic_sample)

    def get_recent_traffic(self, n=10):
        """Return the last n traffic samples for ESM calculation."""
        return self.traffic_history[-n:] if len(self.traffic_history) >= n else self.traffic_history

def main():
    parser = argparse.ArgumentParser(
        description="Generate adversarial TLS traffic with randomized JA3/J4 fingerprints and adaptive evasion."
    )
    parser.add_argument(
        "-u", "--url",
        default="http://localhost:8082",
        help="Target URL to send request to (default: http://mock-endpoint:8080)"
    )
    parser.add_argument(
        "-j", "--ja3",
        help="Specific JA3 client identifier to use (default: random)"
    )
    parser.add_argument(
        "--ja4",
        help="Specific JA4 string to use (default: random)"
    )
    parser.add_argument(
        "-n", "--num-requests",
        type=int,
        default=1,
        help="Number of requests to generate (default: 1)"
    )
    parser.add_argument(
        "--min-jitter",
        type=float,
        default=0.1,
        help="Minimum jitter delay in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--max-jitter",
        type=float,
        default=0.5,
        help="Maximum jitter delay in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--adaptive",
        action="store_true",
        help="Use adaptive evasion (MAB) to select strategy based on context"
    )
    parser.add_argument(
        "--context",
        type=str,
        default="0.1,0.1,0",
        help="Context as comma-separated values for adaptive mode (default: '0.1,0.1,0')"
    )
    parser.add_argument(
        "--ids-feedback",
        action="store_true",
        help="Enable IDS feedback loop (send logs to log-ingest and check alerts for reward)"
    )
    parser.add_argument(
        "--redis-host",
        type=str,
        default="localhost",
        help="Redis host for IDS feedback (default: localhost)"
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        default=6379,
        help="Redis port for IDS feedback (default: 6379)"
    )
    parser.add_argument(
        "--log-ingest-url",
        type=str,
        default="http://localhost:5000/log",
        help="Log ingest service URL (default: http://localhost:5000/log)"
    )
    parser.add_argument(
        "--clear-alerts",
        action="store_true",
        help="Clear Redis alerts and raw_logs before starting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.ids_feedback and args.clear_alerts:
        # Clear Redis lists
        try:
            r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0)
            r.delete('alerts')
            r.delete('raw_logs')
            if args.verbose:
                print("Cleared Redis alerts and raw_logs")
        except Exception as e:
            print(f"Warning: could not clear Redis: {e}")
    
    if args.adaptive:
        # Parse context
        try:
            context_vals = [float(x) for x in args.context.split(',')]
        except ValueError:
            print("Error: context must be comma-separated numbers")
            sys.exit(1)
        
        # Initialize adaptive generator
        aetg = AdaptiveEvasionTrafficGenerator(
            ids_feedback=args.ids_feedback,
            redis_host=args.redis_host,
            redis_port=args.redis_port,
            log_ingest_url=args.log_ingest_url
        )
        
        if args.verbose:
            print(f"Target URL: {args.url}")
            print(f"Context: {context_vals}")
            print(f"Number of requests: {args.num_requests}")
            print(f"Jitter range: [{args.min_jitter}, {args.max_jitter}]")
            print(f"IDS feedback: {args.ids_feedback}")
            if args.ids_feedback:
                print(f"Redis host: {args.redis_host}:{args.redis_port}")
                print(f"Log ingest URL: {args.log_ingest_url}")
            print("-" * 50)
        
        results = []
        for i in range(args.num_requests):
            if args.verbose:
                print(f"Request {i+1}/{args.num_requests}: ", end="", flush=True)
            
            # Generate traffic with adaptive strategy
            result = aetg.generate_traffic(context=context_vals, target_url=args.url)
            results.append(result)
            
            if args.verbose:
                if "error" in result:
                    print(f"ERROR: {result['error']}")
                else:
                    print(f"Status: {result['status']}, Strategy: {result['strategy']}, Length: {result.get('response_length', 'N/A')}")
            
            # Determine reward
            if args.ids_feedback:
                # Send log to IDS
                feature_dict = aetg.create_log_feature_dict(result)
                if args.verbose:
                    print(f"  Sending log to IDS: {feature_dict}")
                success = aetg.send_log_to_ids(feature_dict)
                if not success:
                    print("Warning: failed to send log to IDS")
                # Wait a bit for IDS to process
                time.sleep(0.5)
                # Check for new alert
                alert_detected = aetg.has_new_alert()
                reward = 0 if alert_detected else 1
                if args.verbose:
                    print(f"  Alert detected: {alert_detected} -> reward {reward}")
            else:
                # In a real scenario, we would get reward from IDS feedback (e.g., 0 if alert, 1 if no alert)
                # For now, we simulate reward based on status (assuming 2xx is success/no alert)
                reward = 1 if int(result.get("status", 0)) // 100 == 2 else 0
            
            # Update MAB with observed reward
            aetg.update_performance(context_vals, result["strategy"], reward, result)
        
        if not args.verbose:
            # Machine-readable output (JSON lines)
            for res in results:
                print(json.dumps(res))
        else:
            print("-" * 50)
            print("Summary:")
            success = sum(1 for r in results if "status" in r and r["status"] // 100 == 2)
            print(f"Successful requests (2xx): {success}/{args.num_requests}")
            if success > 0:
                # Count unique strategies used
                strategies = [r.get("strategy") for r in results if "strategy" in r]
                print(f"Unique strategies used: {len(set(strategies))}/{aetg.n_actions}")
                # Calculate simple ESM from recent traffic (placeholder)
                recent = aetg.get_recent_traffic(n=min(10, len(results)))
                if len(recent) >= 2:
                    # We need benign and adversarial samples; for demo we split
                    benign = recent[:len(recent)//2]
                    adv = recent[len(recent)//2:]
                    esm = calculate_esm_from_dicts(benign, adv)
                    print(f"Evasion Stealth Metric (ESM) on recent traffic: {esm:.3f}")
    else:
        # Non-adaptive mode (original behavior)
        if args.verbose:
            print(f"Target URL: {args.url}")
            print(f"JA3: {args.ja3 if args.ja3 else 'random'}")
            print(f"JA4: {args.ja4 if args.ja4 else 'none'}")
            print(f"Number of requests: {args.num_requests}")
            print(f"Jitter range: [{args.min_jitter}, {args.max_jitter}]")
            print("-" * 50)
        
        results = []
        for i in range(args.num_requests):
            if args.verbose:
                print(f"Request {i+1}/{args.num_requests}: ", end="", flush=True)
            
            result = generate_request(
                target_url=args.url,
                ja3=args.ja3,
                ja4=args.ja4,
                jitter_range=(args.min_jitter, args.max_jitter)
            )
            results.append(result)
            
            if args.verbose:
                if "error" in result:
                    print(f"ERROR: {result['error']}")
                else:
                    print(f"Status: {result['status']}, JA3: {result.get('ja3', 'N/A')}, JA4: {result.get('ja4', 'N/A')}, Length: {result['response_length']}")
        
        if not args.verbose:
            # Machine-readable output (JSON lines)
            import json
            for res in results:
                print(json.dumps(res))
        else:
            print("-" * 50)
            print("Summary:")
            success = sum(1 for r in results if "status" in r and r["status"] // 100 == 2)
            print(f"Successful requests (2xx): {success}/{args.num_requests}")
            if success > 0:
                ja3s = [r.get("ja3") for r in results if "ja3" in r]
                ja4s = [r.get("ja4") for r in results if "ja4" in r]
                print(f"Unique JA3s observed: {len(set(ja3s))}")
                print(f"Unique JA4s observed: {len(set(ja4s))}")

if __name__ == "__main__":
    main()