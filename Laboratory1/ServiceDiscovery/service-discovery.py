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

    service_list_key = f"{name}_list"
    service_set_key = f"{name}_set"

    if not redis_conn.exists(service_list_key):
        print(f"New service {name} registered with url {url}")
        redis_conn.rpush(service_list_key, url)  # Store the service URL in a list
        redis_conn.sadd(service_set_key, url)  # Also store the service URL in a set
    else:
        # Check if the URL is already registered
        if not redis_conn.sismember(service_set_key, url):
            print(f"New instance of service {name} registered with url {url}")
            redis_conn.rpush(service_list_key, url)  # Store the service URL in a list
            redis_conn.sadd(service_set_key, url)  # Also store the service URL in a set
        else:
            print(f"Instance of service {name} with url {url} is already registered")

    return jsonify({"message": "Registered successfully"}), 200


@app.route('/discover', methods=['GET'])
def list_services():
    services = {}
    for key in redis_conn.keys("*_list"):
        service_name = key.decode('utf-8').replace("_list", "")
        service_urls = [url.decode('utf-8') for url in redis_conn.lrange(key, 0, -1)]
        services[service_name] = service_urls

    return jsonify(services), 200


@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    try:
        redis_conn.flushdb()
        print("Cache cleared successfully")
        return jsonify({"message": "Cache cleared successfully"}), 200
    except Exception as e:
        print(f"Failed to clear cache: {str(e)}")
        return jsonify({"error": "Failed to clear cache", "details": str(e)}), 500


@app.route('/discover/<service>', methods=['GET'])
@limiter.limit("10 per second")
def discover_service(service):
    service_list_key = f"{service}_list"
    service_urls = [url.decode('utf-8') for url in redis_conn.lrange(service_list_key, 0, -1)]

    if not service_urls:
        print(f"Service {service} not found")
        return jsonify({"error": f"Service {service} not found"}), 404

    if service not in round_robin_store:
        round_robin_store[service] = 0
    else:
        round_robin_store[service] = (round_robin_store[service] + 1) % len(service_urls)

    address = service_urls[round_robin_store[service]]
    print(f"Service {service} discovered. Directing to address {address}")
    return jsonify({"service_address": address}), 200


@app.route('/health', methods=['GET'])
@limiter.limit("10 per minute")
def status():
    return jsonify({"health": "Service Discovery is up and running!"}), 200


# Too Many Requests
@app.errorhandler(429)
def ratelimit_error(e):
    print(f"ALERT: Critical load reached from IP {get_remote_address()}")
    return jsonify(error="ratelimit exceeded"), 429


def health_check_services():
    for service_name in redis_conn.keys():
        if not service_name.endswith(b"_list"):  # Ensure that it's a service list key
            continue
        service_urls = [url.decode('utf-8') for url in redis_conn.lrange(service_name, 0, -1)]
        for service_url in service_urls:
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                if response.status_code != 200:
                    print(f"Removing unhealthy instance: {service_url} of service {service_name}")
                    redis_conn.lrem(service_name, 1,
                                    service_url.encode('utf-8'))  # Removes the unhealthy service URL from Redis
            except requests.RequestException:
                print(f"Removing unreachable instance: {service_url} of service {service_name}")
                redis_conn.lrem(service_name, 1,
                                service_url.encode('utf-8'))  # Removes the unreachable service URL from Redis


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(health_check_services, 'interval', minutes=5)  # Run health check every 5 minutes.
    scheduler.start()

    print(f"Starting Service Discovery on port {serviceConfig.FLASK_PORT}")
    app.run(host=serviceConfig.FLASK_HOST, port=serviceConfig.FLASK_PORT, debug=True)
