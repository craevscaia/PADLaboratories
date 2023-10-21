from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_caching import Cache
import logging
import redis
import time
import config

logging.basicConfig(level=logging.INFO)

# Flask application.
app = Flask(__name__)

# Set up caching with Redis
app.config['CACHE_TYPE'] = config.CACHE_TYPE
app.config['CACHE_REDIS_URL'] = config.REDIS_URL
cache = Cache(app)

# Set up rate limiting
limiter = Limiter(app, key_func=get_remote_address)

# In-memory store for simple load balancing
round_robin_store = {}


def get_remote_address():
    return request.remote_addr


@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register_service():
    data = request.json
    name = data.get('name')
    address = data.get('address')

    # Simple round-robin load balancing setup
    if not cache.get(name):
        round_robin_store[name] = 0
        logging.info(f"New service {name} registered with address {address}")
    else:
        logging.info(f"Service {name} updated with new address {address}")

    cache.set(name, address)
    return jsonify({"message": "Registered successfully"}), 200


@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
def discover_service(service):
    address = cache.get(service)
    if address:
        # Simple round-robin load balancing
        next_index = round_robin_store[service] % len(address)
        round_robin_store[service] += 1
        logging.info(f"Service {service} discovered. Directing to address {address}")
        return jsonify({"service_address": address.decode('utf-8')}), 200
    else:
        logging.warning(f"Service {service} not found")
        return jsonify({"error": f"Service {service} not found"}), 404


@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Service Discovery is up and running!"}), 200


# Too Many Requests
@app.errorhandler(429)
def ratelimit_error(e):
    logging.warning(f"ALERT: Critical load reached from IP {get_remote_address()}")
    return jsonify(error="ratelimit exceeded"), 429


def connect_to_redis():
    retries = config.RETRY_COUNT
    for i in range(retries):
        try:
            r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
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
    connect_to_redis()
    logging.info(f"Starting Service Discovery on port {config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT)
