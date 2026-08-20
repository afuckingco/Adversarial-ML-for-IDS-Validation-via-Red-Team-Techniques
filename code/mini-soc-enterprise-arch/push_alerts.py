import json
import redis
import time
import os

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
alert_file = './shared/logs/eve.json'
last_position = 0

print(f"Monitoring {alert_file} for alerts...")

while True:
    try:
        # Cek apakah file ada
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                f.seek(last_position)
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if 'alert' in data:
                            alert_id = data['alert']['signature_id']
                            key = f"alert:{alert_id}"
                            r.set(key, json.dumps(data))
                            print(f"✅ Alert pushed: {key}")
                    except json.JSONDecodeError:
                        pass
                last_position = f.tell()
        time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
