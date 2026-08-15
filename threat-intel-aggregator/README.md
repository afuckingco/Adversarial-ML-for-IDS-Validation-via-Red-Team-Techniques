# Threat Intelligence Aggregator

Aggregates threat intelligence from various OSINT feeds and provides correlation & scoring.

## Contents
- `src/aggregator.py`: Main script implementing the ThreatIntelAggregator class
- `requirements.txt`: Python dependencies (requests)
- `data/threat_intel_sample.json`: Sample threat intelligence data for demonstration
- `threat_intel.json`: Output file containing aggregated and scored indicators (generated when running the script)

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the aggregator: `python src/aggregator.py`
3. The script will:
   - Try to fetch data from configured OSINT feeds (URLHaus and a sample feed)
   - If feeds fail, fall back to the local sample data
   - Extract indicators, calculate threat scores (based on source reliability, confidence, recency, prevalence, severity)
   - Save the results to `threat_intel.json`
   - Print the top 5 threats and example search results

## Threat Score Calculation
The threat score is a weighted combination of:
- Source reliability (e.g., Abuse.ch: 0.85, VirusTotal: 0.9)
- Confidence (normalized from 0-100 to 0-1)
- Recency (more recent = higher score, decays over 30 days)
- Prevalence (based on number of tags)
- Severity (based on indicator type: IP, domain, URL, hash, malware, CVE)

## Notes
This is a demonstration script. For production use, you would:
- Add more OSINT feeds (possibly requiring API keys)
- Implement more sophisticated parsing for each feed
- Add caching and update frequency controls
- Integrate with other systems (e.g., SIEM, IDS)