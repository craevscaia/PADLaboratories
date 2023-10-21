import logging
import time
import redis
from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_limiter import Limiter

import serviceConfig

logging.basicConfig(level=logging.INFO)

# Flask application.
app = Flask(__name__)


def get_remote_address():
    return request.remote_addr


# Set up caching with Redis
app.config['CACHE_TYPE'] = serviceConfig.CACHE_TYPE
app.config['CACHE_REDIS_URL'] = serviceConfig.REDIS_URL
cache = Cache(app)

# Set up rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["12200 per day", "500 per hour"],
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

    # Simple round-robin load balancing setup
    if not cache.get(name):
        round_robin_store[name] = 0
        logging.info(f"New service {name} registered with url {url}")
    else:
        logging.info(f"Service {name} updated with new url {url}")

    cache.set(name, url)
    return jsonify({"message": "Registered successfully"}), 200


@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
def discover_service(service):
    address = cache.get(service)
    if address:
        logging.info(f"Service {service} discovered. Directing to address {address}")
        return jsonify({"service_address": address}), 200
    else:
        logging.warning(f"Service {service} not found")
        return jsonify({"error": f"Service {service} not found"}), 404


@app.route('/health', methods=['GET'])
def status():
    return jsonify({"health": "Service Discovery is up and running!"}), 200


# Too Many Requests
@app.errorhandler(429)
def ratelimit_error(e):
    logging.warning(f"ALERT: Critical load reached from IP {get_remote_address()}")
    return jsonify(error="ratelimit exceeded"), 429


def connect_to_redis():
    retries = serviceConfig.RETRY_COUNT
    for i in range(retries):
        try:
            r = redis.StrictRedis(host=serviceConfig.REDIS_HOST, port=serviceConfig.REDIS_PORT, db=serviceConfig.REDIS_DB)
            r.ping()
            logging.info("Connected to Redis")
            return r
        except redis.ConnectionError:
            wait = 2 ** i
            logging.error(f"Failed to connect to Redis. Retrying in {wait} seconds...")
            time.sleep(wait)
    logging.error("Failed to connect to Redis after multiple retries. Exiting...")
    exit(1)


if __name__ == '__main__':
    # connect_to_redis()
    logging.info(f"Starting Service Discovery on port {serviceConfig.FLASK_PORT}")
    app.run(host=serviceConfig.FLASK_HOST, port=serviceConfig.FLASK_PORT, debug=True)
