# Adversarial Traffic Generator

A CLI tool to generate TLS traffic with randomized JA3 fingerprints for testing and research purposes.

## Features

- Random JA3/JA3S client identifier selection (using tls-client)
- Timing jitter to avoid detection
- Custom HTTP headers support
- HTTP request generation with configurable target
- Verbose and machine-readable (JSONL) output modes
- Lightweight dependencies (tls-client)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/adversarial-traffic-generator.git
cd adversarial-traffic-generator

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a single request with random JA3 to default test endpoint:

```bash
python src/traffic_gen.py
```

### With Specific JA3

```bash
python src/traffic_gen.py --ja3 chrome_103
```

### Multiple Requests

```bash
python src/traffic_gen.py -n 10 --min-jitter 0.05 --max-jitter 0.2
```

### With Custom Headers

```bash
python src/traffic_gen.py -H "User-Agent: CustomAgent/1.0" -H "X-Test: value"
```

### Machine-readable Output (JSONL)

```bash
python src/traffic_gen.py -n 5
```

Output example:
```json
{"status": 200, "ja3": "chrome_103", "url": "https://httpbin.org/get", "jitter_applied": 0.123, "response_length": 456}
{"status": 200, "ja3": "firefox_96", "url": "https://httpbin.org/get", "jitter_applied": 0.045, "response_length": 456}
```

## Project Structure

```
adversarial-traffic-generator/
├── src/
│   └── traffic_gen.py          # Main CLI script
├── data/                       # For storing generated traffic traces (not implemented yet)
├── notebooks/                  # Jupyter notebooks for analysis
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Example Run

```bash
$ python src/traffic_gen.py -n 3 -v
Target URL: https://httpbin.org/get
JA3: random
Number of requests: 3
Jitter range: [0.1, 0.5]
--------------------------------------------------
Request 1/3: Status: 200, JA3: nike_android_mobile, Length: 306
Request 2/3: Status: 200, JA3: chrome_116_PSK_PQ, Length: 306
Request 3/3: Status: 200, JA3: firefox_108, Length: 306
--------------------------------------------------
Summary:
Successful requests: 3/3
Unique JA3s observed: 3
```

## Testing JA3 Randomization

To verify that the JA3 fingerprint is being randomized, you can run:

```bash
python src/traffic_gen.py -n 2 -v
```

You should see two different JA3 strings in the output (though there is a small chance they could be the same due to randomness).

## Dependencies

- [tls-client](https://github.com/naptha/tls-client): For TLS fingerprint randomization and HTTP impersonation
- Python 3.8+

## Notes

- This tool is intended for legitimate security research and testing only.
- Do not use against systems without explicit permission.
- The default target (httpbin.org) is a public test service; be respectful of rate limits.
- The JA3 string is taken from the requested client_identifier (as tls-client does not expose the actual JA3 string post-request). This is sufficient for testing JA3 randomization capabilities.

## License

MIT