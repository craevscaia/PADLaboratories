import logging
import os

import redis
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from apscheduler.schedulers.background import BackgroundScheduler
import requests

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

    # Check if the service already exists
    existing_service_urls = redis_conn.lrange(name, 0, -1)
    if url.encode('utf-8') not in existing_service_urls:
        logging.info(f"New instance for service {name} registered with url {url}")
        redis_conn.rpush(name, url)  # Add the new instance to the end of the list
    else:
        logging.info(f"Instance with URL {url} for service {name} already exists")

    return jsonify({"message": "Registered successfully"}), 200


@app.route('/services', methods=['GET'])
@limiter.limit("10 per minute")
def get_all_services():
    services = {}
    for service_name in redis_conn.keys():
        service_urls = [url.decode('utf-8') for url in redis_conn.lrange(service_name, 0, -1)]
        services[service_name.decode('utf-8')] = service_urls

    return jsonify(services), 200


@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
def discover_service(service):
    urls = redis_conn.lrange(service, 0, -1)
    if urls:
        if service not in round_robin_store:
            round_robin_store[service] = 0
        address = urls[round_robin_store[service]].decode('utf-8')

        # Update the round-robin index for the next call
        round_robin_store[service] = (round_robin_store[service] + 1) % len(urls)

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


def health_check_services():
    for service_name in redis_conn.keys():
        service_urls = [url.decode('utf-8') for url in redis_conn.lrange(service_name, 0, -1)]
        for service_url in service_urls:
            try:
                # Assuming each service has a `/health` endpoint.
                response = requests.get(f"{service_url}/health", timeout=5)
                if response.status_code != 200:
                    logging.warning(f"Removing unhealthy instance: {service_url} of service {service_name}")
                    redis_conn.lrem(service_name, 1, service_url)  # Removes the unhealthy service URL from Redis
            except requests.RequestException:
                logging.warning(f"Removing unreachable instance: {service_url} of service {service_name}")
                redis_conn.lrem(service_name, 1, service_url)  # Removes the unreachable service URL from Redis


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(health_check_services, 'interval', minutes=5)  # Run health check every 5 minutes.
    scheduler.start()

    logging.info(f"Starting Service Discovery on port {serviceConfig.FLASK_PORT}")
    app.run(host=serviceConfig.FLASK_HOST, port=serviceConfig.FLASK_PORT, debug=True)
