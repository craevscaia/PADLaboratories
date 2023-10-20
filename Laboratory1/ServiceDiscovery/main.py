from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_caching import Cache
import logging

logging.basicConfig(level=logging.INFO)

# Flask application with a simple in-memory cache.
app = Flask(__name__)

# Set up caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Set up rate limiting
limiter = Limiter(app, key_func=get_remote_address)

# In-memory store of registered microservices
services = {}
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
    if name not in services:
        services[name] = []
        round_robin_store[name] = 0
        logging.info(f"New service {name} registered with address {address}")
    else:
        logging.info(f"Service {name} updated with new address {address}")

    services[name].append(address)
    return jsonify({"message": "Registered successfully"}), 200


@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
@cache.cached(timeout=50)
def discover_service(service):
    if service in services:
        # Simple round-robin load balancing
        next_index = round_robin_store[service] % len(services[service])
        round_robin_store[service] += 1
        address = services[service][next_index]
        logging.info(f"Service {service} discovered. Directing to address {address}")
        return jsonify({"service_address": address}), 200
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


if __name__ == '__main__':
    logging.info("Starting Service Discovery on port 6000")
    app.run(host='0.0.0.0', port=6000)
