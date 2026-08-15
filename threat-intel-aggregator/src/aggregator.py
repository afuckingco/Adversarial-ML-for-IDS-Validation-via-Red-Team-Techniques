#!/usr/bin/env python3
"""
Threat Intelligence Aggregator
Aggregates threat intelligence from various OSINT feeds and provides correlation & scoring.
"""

import requests
import json
import time
import hashlib
from datetime import datetime, timedelta
import os


class ThreatIntelAggregator:
    def __init__(self):
        self.feeds = []
        self.indicators = {}  # Store indicators with metadata
        self.score_weights = {
            'source_reliability': 0.3,
            'confidence': 0.25,
            'recency': 0.2,
            'prevalence': 0.15,
            'severity': 0.1
        }

    def load_local_sample(self, filepath='data/threat_intel_sample.json'):
        """Load threat intelligence from a local JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            indicators = []
            for item in data.get('indicators', []):
                # Ensure required fields
                indicator = {
                    'id': item.get('id') or hashlib.md5(str(item).encode()).hexdigest(),
                    'type': item.get('type', 'unknown'),
                    'value': item.get('value') or item.get('indicator') or item.get('hash'),
                    'description': item.get('description', item.get('summary', '')),
                    'tags': item.get('tags', []),
                    'confidence': float(item.get('confidence', 50)),
                    'source': item.get('source', 'Local Sample'),
                    'timestamp': item.get('timestamp', datetime.now().isoformat()),
                    'raw_data': item
                }
                if indicator['value']:
                    indicators.append(indicator)
            # Calculate scores
            for indicator in indicators:
                indicator['score'] = self.calculate_score(indicator)
            # Deduplicate by id
            unique = {ind['id']: ind for ind in indicators}
            self.indicators = unique
            print(f"Loaded {len(self.indicators)} indicators from local sample {filepath}")
            return list(self.indicators.values())
        except Exception as e:
            print(f"Error loading local sample: {e}")
            return []

    def add_feed(self, name, url, feed_type='json', headers=None, parser_func=None):
        """Add a threat intelligence feed."""
        self.feeds.append({
            'name': name,
            'url': url,
            'type': feed_type,
            'headers': headers or {},
            'parser': parser_func or self.default_parser
        })

    def default_parser(self, response):
        """Default parser for JSON feeds."""
        try:
            return response.json()
        except:
            return None

    def fetch_feed(self, feed):
        """Fetch and parse a single feed."""
        try:
            response = requests.get(
                feed['url'],
                headers=feed['headers'],
                timeout=30
            )
            response.raise_for_status()
            return feed['parser'](response)
        except Exception as e:
            print(f"Error fetching feed {feed['name']}: {e}")
            return None

    def extract_indicators(self, feed_data, feed_name):
        """Extract indicators from feed data."""
        indicators = []

        # Handle different feed structures
        if isinstance(feed_data, dict):
            # Common structures
            if 'indicators' in feed_data:
                items = feed_data['indicators']
            elif 'data' in feed_data:
                items = feed_data['data']
            elif 'results' in feed_data:
                items = feed_data['results']
            else:
                items = [feed_data]  # Treat the whole dict as one item
        elif isinstance(feed_data, list):
            items = feed_data
        else:
            items = []

        for item in items:
            if not isinstance(item, dict):
                continue

            # Extract common indicator types
            indicator = {
                'id': item.get('id') or item.get('hash') or item.get('indicator') or
                       hashlib.md5(str(item).encode()).hexdigest(),
                'type': item.get('type', 'unknown'),
                'value': item.get('value') or item.get('indicator') or item.get('hash'),
                'description': item.get('description', item.get('summary', '')),
                'tags': item.get('tags', item.get('malware_families', [])),
                'confidence': float(item.get('confidence', item.get('confidence_level', 50))),
                'source': feed_name,
                'timestamp': item.get('timestamp', item.get('created', item.get('first_seen'))),
                'raw_data': item
            }

            # Only add if we have a value
            if indicator['value']:
                indicators.append(indicator)

        return indicators

    def calculate_score(self, indicator):
        """Calculate a threat score for an indicator."""
        score = 0.0

        # Source reliability (based on source name)
        source_reliability = {
            'alienvault': 0.9,
            'abuse.ch': 0.85,
            'urlhaus': 0.8,
            'malwarebazaar': 0.8,
            'virustotal': 0.9,
            'hybrid-analysis': 0.85
        }.get(indicator['source'].lower().split()[0], 0.5)

        # Confidence (normalize to 0-1)
        confidence = min(indicator.get('confidence', 50) / 100.0, 1.0)

        # Recency (more recent = higher score)
        try:
            if isinstance(indicator['timestamp'], str):
                # Try to parse common timestamp formats
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        ts = datetime.strptime(indicator['timestamp'][:len(fmt)], fmt)
                        break
                    except:
                        continue
                else:
                    ts = datetime.now() - timedelta(days=30)  # Default to old if can't parse
            else:
                ts = indicator['timestamp'] if isinstance(indicator['timestamp'], datetime) else datetime.now() - timedelta(days=30)

            days_old = (datetime.now() - ts).days
            recency_score = max(0, 1 - (days_old / 30))  # 30 days decay
        except:
            recency_score = 0.5

        # Prevalence (based on number of tags/sources)
        prevalence_score = min(len(indicator.get('tags', [])) / 10.0, 1.0)

        # Severity (based on indicator type)
        severity_scores = {
            'ip': 0.8,
            'domain': 0.7,
            'url': 0.6,
            'hash': 0.9,
            'malware': 0.9,
            'cve': 0.8
        }
        severity = severity_scores.get(indicator['type'], 0.5)

        # Calculate weighted score
        score = (
            self.score_weights['source_reliability'] * source_reliability +
            self.score_weights['confidence'] * confidence +
            self.score_weights['recency'] * recency_score +
            self.score_weights['prevalence'] * prevalence_score +
            self.score_weights['severity'] * severity
        )

        return min(score, 1.0)  # Cap at 1.0

    def aggregate(self):
        """Fetch all feeds and aggregate indicators."""
        print("Starting threat intelligence aggregation from feeds...")

        all_indicators = []

        for feed in self.feeds:
            print(f"Fetching feed: {feed['name']}")
            feed_data = self.fetch_feed(feed)

            if feed_data:
                indicators = self.extract_indicators(feed_data, feed['name'])
                print(f"  Extracted {len(indicators)} indicators")

                for indicator in indicators:
                    # Calculate score
                    indicator['score'] = self.calculate_score(indicator)
                    all_indicators.append(indicator)
            else:
                print(f"  Failed to fetch data from {feed['name']}")

        # If we got no indicators from feeds, try loading local sample
        if not all_indicators:
            print("No indicators from feeds, loading local sample...")
            all_indicators = self.load_local_sample()

        # Deduplicate by ID
        unique_indicators = {}
        for indicator in all_indicators:
            ind_id = indicator['id']
            if ind_id not in unique_indicators or \
               indicator['score'] > unique_indicators[ind_id]['score']:
                unique_indicators[ind_id] = indicator

        self.indicators = unique_indicators
        print(f"Aggregation complete. Total unique indicators: {len(self.indicators)}")

        return list(self.indicators.values())

    def get_top_threats(self, limit=10):
        """Get top threats by score."""
        sorted_indicators = sorted(
            self.indicators.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        return sorted_indicators[:limit]

    def search_indicators(self, query):
        """Search indicators by value or description."""
        query = query.lower()
        results = []
        for indicator in self.indicators.values():
            if (query in str(indicator['value']).lower() or
                query in indicator['description'].lower()):
                results.append(indicator)
        return results

    def save_to_file(self, filename='threat_intel.json'):
        """Save aggregated indicators to a file."""
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_indicators': len(self.indicators),
            'indicators': list(self.indicators.values())
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Saved threat intelligence to {filename}")

    def load_from_file(self, filename='threat_intel.json'):
        """Load indicators from a file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)

            self.indicators = {}
            for indicator in data.get('indicators', []):
                # Convert timestamp strings back if needed
                self.indicators[indicator['id']] = indicator

            print(f"Loaded {len(self.indicators)} indicators from {filename}")
            return list(self.indicators.values())
        else:
            print(f"File {filename} not found")
            return []


def setup_sample_feeds():
    """Set up sample OSINT feeds for demonstration."""
    aggregator = ThreatIntelAggregator()

    # Add some sample feeds (these are examples - actual feeds may require API keys)
    # Note: For demo purposes, we'll use endpoints that might not work without modification
    # In a real implementation, you would use actual OSINT feeds

    # Example: Abuse.ch URLHaus (may work without API key for basic usage)
    aggregator.add_feed(
        name='URLHaus',
        url='https://urlhaus.abuse.ch/downloads/json_online/',
        feed_type='json',
        parser_func=lambda r: r.json().get('urls', []) if r.status_code == 200 else None
    )

    # Example: A simple mock feed for demonstration
    # In practice, you would replace these with real OSINT feeds
    aggregator.add_feed(
        name='Sample Feed',
        url='https://httpbin.org/json',  # This returns sample JSON
        feed_type='json',
        parser_func=lambda r: [{
            'value': '192.168.1.100',
            'type': 'ip',
            'description': 'Sample malicious IP',
            'tags': ['botnet', 'c2'],
            'confidence': 75,
            'timestamp': datetime.now().isoformat()
        }] if r.status_code == 200 else None
    )

    return aggregator


def main():
    """Main function to run the threat intelligence aggregator."""
    print("=== Threat Intelligence Aggregator ===")

    # First, try to load from local sample (reliable and fast)
    aggregator = ThreatIntelAggregator()
    indicators = aggregator.load_local_sample()

    if not indicators:
        # If local sample fails, fall back to trying feeds
        print("Local sample not available or empty, trying feeds...")
        aggregator = setup_sample_feeds()
        indicators = aggregator.aggregate()

    if indicators:
        # Show top threats
        print("\n--- Top 5 Threats ---")
        top_threats = aggregator.get_top_threats(5)
        for i, threat in enumerate(top_threats, 1):
            print(f"{i}. [{threat['score']:.2f}] {threat['type']}: {threat['value']}")
            print(f"   Source: {threat['source']} | Confidence: {threat.get('confidence', 'N/A')}%")
            print(f"   Description: {threat['description'][:100]}...")
            print()

        # Save to file
        aggregator.save_to_file('threat_intel.json')

        # Example search
        print("--- Example Search Results for '192.168' ---")
        search_results = aggregator.search_indicators('192.168')
        for result in search_results[:3]:
            print(f"- {result['type']}: {result['value']} (Score: {result['score']:.2f})")
    else:
        print("No indicators were aggregated. Check local sample and feed connections.")

    print("=== Aggregation Complete ===")


if __name__ == '__main__':
    main()