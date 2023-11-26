import logging
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter

service_registry = {}

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


def get_remote_address():
    return request.remote_addr


# Set up rate limiting
# Remove the storage_uri parameter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
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

    if name not in service_registry:
        logging.info(f"New service {name} registered with url {url}")
    else:
        logging.info(f"Service {name} updated with new url {url}")

    service_registry[name] = url
    return jsonify({"message": "Registered successfully"}), 200


@app.route('/discover', methods=['GET'])
@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
def discover_service(service=None):
    if service:
        # If a specific service is requested, return its address
        address = service_registry.get(service)
        if address:
            logging.info(f"Service {service} discovered. Directing to address {address}")
            return jsonify({"service_address": address}), 200
        else:
            logging.warning(f"Service {service} not found")
            return jsonify({"error": f"Service {service} not found"}), 404
    else:
        # If no specific service is requested, return all services
        logging.info("Returning all registered services")
        return jsonify(service_registry), 200


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
