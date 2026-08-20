# Alerting Service
# Continuously reads alerts from Redis list 'alerts' and writes them to a log file.
# In a real system, this might send emails, Slack notifications, etc.

import redis
import json
import os
import time

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, db=0)

# Output file
alert_log_path = '/app/alerts/alerts.log'

def main():
    print("Alerting service started. Waiting for alerts...")
    while True:
        # Blocking pop from the 'alerts' list
        result = r.blpop(['alerts'], timeout=1)
        if result is None:
            continue
        key, value = result
        alert = json.loads(value)
        # Write to log file
        with open(alert_log_path, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        print(f"Alert logged: {alert}")

if __name__ == '__main__':
    main()