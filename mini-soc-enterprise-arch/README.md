# Mini SOC Enterprise Architecture

This project implements a simplified Security Operations Center (SOC) architecture using Docker Compose. It includes:

## Services
1. **log-ingest** - Receives HTTP POST requests with log data and pushes to Redis
2. **ids** - Intrusion Detection System that reads logs, extracts features, runs inference with a pre-trained XGBoost model, and pushes alerts to Redis
3. **alerting** - Reads alerts from Redis and writes them to a log file
4. **dashboard** - Simple web interface that displays recent alerts
5. **redis** - In-memory data store used for communication between services

## Architecture
```
[Log Sources] --> log-ingest --> [Redis: raw_logs] 
                                      --> ids --> [Redis: alerts] 
                                                                  --> alerting --> [alerts.log]
                                                                  --> dashboard --> [Web Interface]
```

## Features
- Real-time log ingestion via HTTP
- Machine learning-based intrusion detection (using XGBoost model from Task 4)
- Redis-based message queuing for loose coupling
- Persistent alert logging
- Web dashboard for visualization
- Dockerized services for easy deployment

## Prerequisites
- Docker and Docker Compose installed
- The IDS service requires a pre-trained XGBoost model and scaler parameters
  (These should be placed in `shared/model/` - see setup instructions below)

## Setup

1. Clone this repository and navigate to the project directory

2. Prepare the model files:
   The IDS service expects to find:
   - `shared/model/xgb_model.json` - Pre-trained XGBoost model
   - `shared/model/scaler_params.json` - Scaler parameters (mean and scale)
   
   You can generate these by running the training script from the `ids-architecture-comparison` project:
   ```
   cd ../ids-architecture-comparison
   # (Assuming you've already run the training script and have the model)
   cp xgb_model.json scaler_params.json ../mini-soc-enterprise-arch/shared/model/
   ```

3. Build and start the services:
   ```
   docker-compose up --build
   ```

4. The services will be available at:
   - Log Ingest API: http://localhost:5000/log (POST endpoint)
   - Dashboard: http://localhost:8080
   - Redis: localhost:6379

## Testing the System

You can test the system by sending a sample log entry to the log-ingest service:

```bash
curl -X POST http://localhost:5000/log \
  -H "Content-Type: application/json" \
  -d '{
    "total_packets": 7500,
    "avg_packet_size": 200,
    "std_packet_size": 50,
    "unique_src_ips": 100,
    "unique_dst_ips": 50,
    "common_ja3": 1
  }'
```

This sample represents an adversarial pattern (high packet count, small average size) and should trigger an alert.

Check the dashboard at http://localhost:8080 to see the alert, or check the alerts log file at `shared/alerts/alerts.log`.

## Notes
- This is a simplified architecture for demonstration purposes
- In a production system, you would want to:
  - Add proper authentication and encryption
  - Use more robust message queuing (e.g., Apache Kafka, RabbitMQ)
  - Implement model monitoring and retraining
  - Add more sophisticated alert deduplication and enrichment
  - Use a proper database for alert storage instead of flat files
  - Add health checks and restart policies
  - Implement proper logging and monitoring

## Project Structure
```
mini-soc-enterprise-arch/
├── docker-compose.yml          # Docker Compose configuration
├── shared/                     # Shared volumes
│   ├── model/                  # ML model and scaler parameters
│   ├── logs/                   # Log files from services
│   └── alerts/                 # Alert log files
├── log-ingest/                 # Log ingestion service
│   ├── app.py                  # Flask application
│   ├── Dockerfile              # Container definition
│   └── requirements.txt        # Python dependencies
├── ids/                        # Intrusion Detection Service
│   ├── app.py                  # Main application
│   ├── Dockerfile              # Container definition
│   └── requirements.txt        # Python dependencies
├── alerting/                   # Alerting service
│   ├── app.py                  # Main application
│   ├── Dockerfile              # Container definition
│   └── requirements.txt        # Python dependencies
└── dashboard/                  # Web dashboard
    ├── app.py                  # Flask application
    ├── Dockerfile              # Container definition
    └── requirements.txt        # Python dependencies
```

## License
MIT