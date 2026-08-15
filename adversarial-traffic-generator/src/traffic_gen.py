#!/usr/bin/env python3
"""
Adversarial Traffic Generator
CLI tool to generate TLS traffic with randomized JA3 fingerprints.
"""

import argparse
import sys
import time
import random
import tls_client


def random_ja3():
    """Return a random client identifier from tls_client's supported list."""
    from tls_client.settings import ClientIdentifiers
    # The actual string literals are in ClientIdentifiers.__args__
    choices = list(ClientIdentifiers.__args__)
    return random.choice(choices)


def generate_request(target_url="https://httpbin.org/get", ja3=None, jitter_range=(0.1, 0.5)):
    """Generate a single HTTP request with optional JA3 randomization and timing jitter."""
    if ja3 is None:
        ja3 = random_ja3()
    
    # Apply timing jitter before request
    jitter = random.uniform(*jitter_range)
    time.sleep(jitter)
    
    try:
        session = tls_client.Session(
            client_identifier=ja3,
            random_tls_extension_order=True
        )
        resp = session.get(target_url, timeout_seconds=10)
        # tls_client does not seem to populate ja3_string after request; use client_identifier as proxy
        ja3_out = ja3  # proxy
        return {
            "status": resp.status_code,
            "ja3": ja3_out,
            "url": target_url,
            "jitter_applied": jitter,
            "response_length": len(resp.content)
        }
    except Exception as e:
        return {
            "error": str(e),
            "ja3_attempted": ja3,
            "jitter_applied": jitter
        }
    finally:
        try:
            session.close()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Generate adversarial TLS traffic with randomized JA3 fingerprints."
    )
    parser.add_argument(
        "-u", "--url",
        default="https://httpbin.org/get",
        help="Target URL to send request to (default: https://httpbin.org/get)"
    )
    parser.add_argument(
        "-j", "--ja3",
        help="Specific JA3 client identifier to use (default: random)"
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
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Target URL: {args.url}")
        print(f"JA3: {args.ja3 if args.ja3 else 'random'}")
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
            jitter_range=(args.min_jitter, args.max_jitter)
        )
        results.append(result)
        
        if args.verbose:
            if "error" in result:
                print(f"ERROR: {result['error']}")
            else:
                print(f"Status: {result['status']}, JA3: {result['ja3']}, Length: {result['response_length']}")
    
    if not args.verbose:
        # Machine-readable output (JSON lines)
        import json
        for res in results:
            print(json.dumps(res))
    else:
        print("-" * 50)
        print("Summary:")
        success = sum(1 for r in results if "status" in r)
        print(f"Successful requests: {success}/{args.num_requests}")
        if success > 0:
            ja3s = [r.get("ja3") for r in results if "ja3" in r]
            print(f"Unique JA3s observed: {len(set(ja3s))}")


if __name__ == "__main__":
    main()