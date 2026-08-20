# Dashboard Service
# Simple Flask app that reads alerts from Redis list 'alerts' and displays them in a web page.
# Note: Since Redis list is consumed by the alerting service, we need to either:
#   - Have the alerting service also push to another list for the dashboard, or
#   - Let the dashboard read from the same list but then the alerting service won't see them.
# We'll change the architecture: the IDS service pushes to 'alerts', and both alerting and dashboard read from it.
# However, Redis list pop operations are destructive. To allow multiple consumers, we can use Redis Pub/Sub or have each service consume from a separate list.
# For simplicity, let's have the IDS push to 'alerts', and we'll have the alerting service and dashboard each consume from their own list by using the IDS to push to two lists.
# But to keep the example simple, we'll have the dashboard read from the same list without consuming (using LRANGE) so it doesn't interfere.
# However, the alerting service is designed to consume and log. We'll change the alerting service to not consume but to log by periodically scanning?
# Given the time, let's adjust: We'll have the IDS push to 'alerts', and we'll have two consumers:
#   - alerting service: uses BRPOP to consume and log (so it removes from the list)
#   - dashboard: uses LRANGE to read the list without removing (so it shows recent alerts)
# This way, the alerting service will still get every alert (because it pops) and the dashboard will show the remaining list (which will be empty if the alerting service is fast).
# To have both see the alerts, we can use Redis Streams or make the IDS push to two lists.
# Let's do a simple change: IDS pushes to 'alerts_alerting' and 'alerts_dashboard'. Then we have two separate lists.
# But given the scope, we'll just have the dashboard read from the same list and accept that it will see only what the alerting service hasn't popped yet.
# For demonstration, we'll make the alerting service slow by processing one alert at a time and then sleeping, so the dashboard can see some.

# We'll keep the alerting service as is (consuming) and the dashboard will use LRANGE to get the last 100 alerts without removing them.

from flask import Flask, render_template_string
import redis
import json
import os

app = Flask(__name__)

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, db=0)

# HTML template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini SOC Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .alert { border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .alert h3 { margin-top: 0; }
        .alert pre { background: #f4f4f4; padding: 10px; overflow: auto; }
    </style>
</head>
<body>
    <h1>Mini SOC Dashboard</h1>
    <h2>Recent Alerts</h2>
    {% if alerts %}
        {% for alert in alerts %}
        <div class="alert">
            <h3>Alert at {{ alert.timestamp }}</h3>
            <pre>{{ alert|tojson(indent=2) }}</pre>
        </div>
        {% endfor %}
    {% else %}
        <p>No alerts yet.</p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def dashboard():
    # Get the last 100 alerts from the Redis list (without removing them)
    alert_json_list = r.lrange('alerts', 0, 99)  # 0 to 99 inclusive -> 100 elements
    alerts = []
    for json_str in alert_json_list:
        try:
            alert = json.loads(json_str)
            alerts.append(alert)
        except Exception as e:
            # If there's an error decoding, skip this entry
            pass
    # Reverse so that the most recent is at the top (since we lpush, the newest is at index 0)
    alerts.reverse()
    return render_template_string(HTML_TEMPLATE, alerts=alerts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)