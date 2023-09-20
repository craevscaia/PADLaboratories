from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_caching import Cache
import requests

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
        return jsonify({"service_address": address}), 200
    else:
        return jsonify({"error": f"Service {service} not found"}), 404

@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify(error="ratelimit exceeded"), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
