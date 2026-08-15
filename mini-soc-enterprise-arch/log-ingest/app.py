# Log Ingest Service
# Receives HTTP POST requests with log data and pushes to Redis list 'raw_logs'

from flask import Flask, request, jsonify
import redis
import json
import os

app = Flask(__name__)

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, db=0)

@app.route('/log', methods=['POST'])
def receive_log():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    log_data = request.get_json()
    # Push to Redis list
    r.lpush('raw_logs', json.dumps(log_data))
    return jsonify({"status": "log received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)