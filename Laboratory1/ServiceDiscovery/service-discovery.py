import logging
import os

import redis
from flask import Flask, request, jsonify
from flask_limiter import Limiter

# Choose the config based on the environment variable
config_mode = os.environ.get('CONFIG_MODE', 'default')
if config_mode == 'docker':
    import serviceConfigDocker as serviceConfig

    print("Using Docker Configuration")
else:
    import serviceConfigDefault as serviceConfig

    print("Using Default Configuration")

logging.basicConfig(level=logging.INFO)

# Flask application.
app = Flask(__name__)
redis_conn = redis.StrictRedis(host=serviceConfig.REDIS_HOST, port=serviceConfig.REDIS_PORT, db=serviceConfig.REDIS_DB)


def get_remote_address():
    return request.remote_addr


# Set up rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=serviceConfig.REDIS_URL
)
limiter.init_app(app)

# In-memory store for simple load balancing
round_robin_store = {}


@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register_service():
    data = request.json
    name = data.get('name')
    url = data.get('url')

    if not redis_conn.get(name):
        logging.info(f"New service {name} registered with url {url}")
    else:
        logging.info(f"Service {name} updated with new url {url}")

    redis_conn.set(name, url)
    return jsonify({"message": "Registered successfully"}), 200


@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
def discover_service(service):
    address = redis_conn.get(service)
    if address:
        address = address.decode('utf-8')  # Decode the byte data to string
        logging.info(f"Service {service} discovered. Directing to address {address}")
        return jsonify({"service_address": address}), 200
    else:
        logging.warning(f"Service {service} not found")
        return jsonify({"error": f"Service {service} not found"}), 404


@app.route('/health', methods=['GET'])
@limiter.limit("10 per minute")
def status():
    return jsonify({"health": "Service Discovery is up and running!"}), 200


# Too Many Requests
@app.errorhandler(429)
def ratelimit_error(e):
    logging.warning(f"ALERT: Critical load reached from IP {get_remote_address()}")
    return jsonify(error="ratelimit exceeded"), 429


if __name__ == '__main__':
    logging.info(f"Starting Service Discovery on port {serviceConfig.FLASK_PORT}")
    app.run(host=serviceConfig.FLASK_HOST, port=serviceConfig.FLASK_PORT, debug=True)
