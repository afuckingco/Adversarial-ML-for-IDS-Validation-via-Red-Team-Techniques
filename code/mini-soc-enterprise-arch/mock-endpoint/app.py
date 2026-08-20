from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path=''):
    app.logger.info(f"Received {request.method} request to /{path}")
    app.logger.info(f"Headers: {dict(request.headers)}")
    # Get the length from query parameter 'length', default to 754
    length = request.args.get('length', default=754, type=int)
    # Ensure length is non-negative
    if length < 0:
        length = 754
    return 'X' * length, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
