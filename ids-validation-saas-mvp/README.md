# IDS Validation SaaS MVP

A simple landing page for a SaaS product that validates Intrusion Detection Systems (IDS) using adversarial traffic and machine learning models.

## Features
- Landing page with showcase of services
- Responsive design
- Flask backend

## Installation
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Usage
Run the application:
```bash
python src/app.py
```
Then visit `http://localhost:5000` in your browser.

## Project Structure
- `src/app.py`: Main Flask application
- `templates/index.html`: Landing page template
- `requirements.txt`: Python dependencies
- `static/`: Placeholder for static assets (CSS, JS, images)

## Notes
This is a minimal MVP for demonstration purposes. In a full product, you would integrate:
- Adversarial traffic generator (from `adversarial-traffic-generator`)
- Trained IDS models (from `ids-architecture-comparison`)
- Real-time dashboard and alerting (from `mini-soc-enterprise-arch`)
- Threat intelligence feeds (from `threat-intel-aggregator`)

## License
MIT