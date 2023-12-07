import logging
import os
import time
from html import escape

import pybreaker
import redis
import requests
from flask import Flask, jsonify, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter
from prometheus_client import Summary

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Choose the config based on the environment variable
config_mode = os.environ.get('CONFIG_MODE', 'default')
if config_mode == 'docker':
    import gatewayConfigDocker as gatewayConfig

    app.logger.info("Using Docker Configuration")
else:
    import gatewayConfigDefault as gatewayConfig

    app.logger.info("Using Default Configuration")

# Circuit Breaker Configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # number of failures before changing to open state
    reset_timeout=10  # seconds after which the state should change from open to half-open
)

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
c = Counter('main_endpoint_calls', 'How many times the endpoint is called')

redis_conn = redis.StrictRedis(host=gatewayConfig.REDIS_HOST, port=gatewayConfig.REDIS_PORT, db=gatewayConfig.REDIS_DB)

SERVICE_DISCOVERY_URL = gatewayConfig.SERVICE_DISCOVERY
services_cache = {}  # In-memory store for service addresses

# Setup Flask Limiter with Redis as the storage backend
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri=f"redis://{gatewayConfig.REDIS_HOST}:{gatewayConfig.REDIS_PORT}/{gatewayConfig.REDIS_DB}",
)


@REQUEST_TIME.time()
@app.route('/health', methods=['GET'])
def status():
    app.logger.info("Health check endpoint hit")
    return jsonify({"health": "Api gateway is up and running!"}), 200


@REQUEST_TIME.time()
@app.route('/cache', methods=['GET'])
def get_cache():
    cache_data = {}
    for key in redis_conn.scan_iter():
        value = redis_conn.get(key)
        # Convert bytes to string if necessary
        str_key = key.decode('utf-8') if isinstance(key, bytes) else str(key)
        str_value = value.decode('utf-8') if isinstance(value, bytes) else str(value)
        # Escape HTML characters
        escaped_key = escape(str_key)
        escaped_value = escape(str_value)
        cache_data[escaped_key] = escaped_value
    return jsonify(cache_data)


@REQUEST_TIME.time()
@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    app.logger.info("Clearing the cache")
    redis_conn.flushdb()
    app.logger.info("Cache cleared successfully")
    return jsonify({"status": "Cache cleared successfully"}), 200


# Exemption logic (keep this as-is, as per your instructions)
@limiter.request_filter
def exempt_users():
    return False


def check_service_discovery_health():
    app.logger.info("Checking Service Discovery Health")
    retries = 5
    backoff_factor = 2  # Time delay factor
    for i in range(retries):
        try:
            app.logger.info(f"Service Discovery Health Check Attempt {i + 1}")
            response = requests.get(f"{SERVICE_DISCOVERY_URL}/health", timeout=gatewayConfig.REQUEST_TIMEOUT)
            if response.status_code == 200:
                app.logger.info("Service Discovery is healthy and running.")
                return True
            else:
                logging.warning(f"Service Discovery returned status {response.status_code}. Retrying...")
                time.sleep(i * backoff_factor)  # Exponential backoff
        except requests.RequestException as e:
            logging.warning(f"Failed to connect to Service Discovery. Error: {e}. Retrying...")
            time.sleep(i * backoff_factor)  # Exponential backoff
    app.logger.info("Failed to connect to Service Discovery after multiple retries. Starting API Gateway with caution.")
    return False


@REQUEST_TIME.time()
@app.route('/<service>/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path=''):
    c.inc()
    app.logger.info(f"Received request for service: {service}, path: {path}")

    # Query the Service Discovery for the service address
    app.logger.info(f"Querying Service Discovery to find service address for {service}")
    service_address = get_service_address_from_discovery(service)
    if not service_address:
        app.logger.info(f"Service {service} not found in Service Discovery")
        return jsonify({"error": f"Service {service} not found"}), 404

    # Initialize reroute count
    reroute_count = 0 # Tracks how many times a request has been rerouted.
    max_reroutes = 3  # Set the maximum number of reroutes before tripping the breaker

    while reroute_count < max_reroutes:
        # Construct the URL and forward the request
        forward_url = construct_forward_url(service_address, service, path)
        app.logger.info(f"Forwarding request to {forward_url}")
        response, is_reroute = forward_request(forward_url, request)

        if not is_reroute:
            # If it's not a reroute, handle caching and return the response
            handle_cache_operations(service, path, request, response)
            return Response(response.content, mimetype='application/json'), response.status_code
        else:
            # If a reroute status code is received, increment the reroute count
            reroute_count += 1
            app.logger.warning(
                f"Reroute detected for {service} with status code {response.status_code}, reroute count: {reroute_count}")

            # Check if the reroute count exceeds the maximum allowed before tripping the breaker
            if reroute_count >= max_reroutes:
                # Trip the circuit breaker
                circuit_breaker.fail()
                app.logger.error(f"Circuit breaker tripped due to {max_reroutes} consecutive reroutes for {service}.")
                return jsonify({"error": "Service currently unavailable, please try again later."}), 503

            # Short delay before retrying to prevent immediate repeated requests
            time.sleep(1)

    # If the loop exits without returning, it means the reroute count was not exceeded
    # This is a catch-all to handle unexpected loop exit
    app.logger.error("Unexpected exit from reroute handling loop.")
    return jsonify({"error": "An unexpected error occurred."}), 500


def get_service_address_from_cache(service):
    return services_cache.get(service)


def get_service_address_from_discovery(service):
    try:
        app.logger.info(f"Calling Service Discovery to find service address for {service}")
        response = call_service_discovery(f"{SERVICE_DISCOVERY_URL}discover/{service}")
        if response.status_code == 200:
            app.logger.info(f"Service Discovery found service address for {service}")
            return response.json().get("service_address")
        else:
            logging.warning(
                f"Service Discovery did not find service address for {service}, status code {response.status_code}")
            return None
    except pybreaker.CircuitBreakerError:
        app.logger.info("Circuit Breaker is open, not making request to Service Discovery")
        return None
    except Exception as e:
        app.logger.info(f"Failed to call Service Discovery. Error: {e}")
        return None


@circuit_breaker
def call_service_discovery(url):
    return requests.get(url)


def construct_forward_url(service_address, service, path):
    service_address = service_address.rstrip('/').lstrip('/')
    service = service.rstrip('/').lstrip('/')
    path = path.rstrip('/').lstrip('/')

    # Forward query parameters
    query_params = request.query_string.decode()
    if path:
        return f"{service_address}/{service}/{path}?{query_params}"
    return f"{service_address}/{service}?{query_params}"


# Modify the forward_request function to return both the response and a reroute indicator.
def forward_request(url, req):
    reroute_status_codes = {502, 503}  # Define which status codes indicate a reroute

    try:
        app.logger.info(f"Forwarding request to {url}")
        response = requests.request(
            method=req.method,
            url=url,
            headers={key: value for (key, value) in req.headers if key != 'Host'},
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            timeout=gatewayConfig.REQUEST_TIMEOUT
        )
        app.logger.info(f"Received response from {url} with status code {response.status_code}")
        # Check if the status code is in the reroute list
        is_reroute = response.status_code in reroute_status_codes
        return response, is_reroute

    except pybreaker.CircuitBreakerError:
        app.logger.error("Circuit Breaker is open, not making request")
        return Response(jsonify({"error": "Circuit Breaker is open, not making request"}), status=503), True
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Failed to forward request to {url}. Error: {e}")
        # Assume a reroute in case of network issues
        return Response(jsonify({"error": "Network error"}), status=500), True


def handle_cache_operations(service, path, req, res):
    cache_expiration_time = 10  # 5 minutes, can be set based on your needs

    if req.method in ["POST", "PUT", "DELETE"]:
        cache_key = f"{service}_{path}_response" if path else f"{service}_response"
        redis_conn.delete(cache_key)  # Clear only the response cache

    if req.method == "GET":
        cache_key = f"{req.method}_{service}_{path}_response" if path else f"{req.method}_{service}_response"
        redis_conn.setex(cache_key, cache_expiration_time, res.content)  # Set cache with expiration time


if __name__ == '__main__':
    check_service_discovery_health()
    app.logger.info(f"Starting API Gateway on port {gatewayConfig.FLASK_PORT}")
    app.run(host=gatewayConfig.FLASK_HOST, port=gatewayConfig.FLASK_PORT, debug=True)
