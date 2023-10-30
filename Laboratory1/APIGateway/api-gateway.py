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

# Choose the config based on the environment variable
config_mode = os.environ.get('CONFIG_MODE', 'default')
if config_mode == 'docker':
    import gatewayConfigDocker as gatewayConfig

    print("Using Docker Configuration")
else:
    import gatewayConfigDefault as gatewayConfig

    print("Using Default Configuration")

# Circuit Breaker Configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # number of failures before changing to open state
    reset_timeout=10  # seconds after which the state should change from open to half-open
)

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

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


@app.route('/health', methods=['GET'])
def status():
    print("Health check endpoint hit")
    return jsonify({"health": "Api gateway is up and running!"}), 200


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


@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    print("Clearing the cache")
    redis_conn.flushdb()
    print("Cache cleared successfully")
    return jsonify({"status": "Cache cleared successfully"}), 200


# Exemption logic (keep this as-is, as per your instructions)
@limiter.request_filter
def exempt_users():
    return False


def check_service_discovery_health():
    print("Checking Service Discovery Health")
    retries = 5
    backoff_factor = 2  # Time delay factor
    for i in range(retries):
        try:
            print(f"Service Discovery Health Check Attempt {i + 1}")
            response = requests.get(f"{SERVICE_DISCOVERY_URL}/health", timeout=gatewayConfig.REQUEST_TIMEOUT)
            if response.status_code == 200:
                print("Service Discovery is healthy and running.")
                return True
            else:
                logging.warning(f"Service Discovery returned status {response.status_code}. Retrying...")
                time.sleep(i * backoff_factor)  # Exponential backoff
        except requests.RequestException as e:
            logging.warning(f"Failed to connect to Service Discovery. Error: {e}. Retrying...")
            time.sleep(i * backoff_factor)  # Exponential backoff
    print("Failed to connect to Service Discovery after multiple retries. Starting API Gateway with caution.")
    return False


@app.route('/<service>/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path=''):
    print(f"Received request for service: {service}, path: {path}")

    # Query the Service Discovery for the service address
    print(f"Querying Service Discovery to find service address for {service}")
    service_address = get_service_address_from_discovery(service)
    if not service_address:
        print(f"Service {service} not found in Service Discovery")
        return jsonify({"error": f"Service {service} not found"}), 404

    # Construct the cache key and attempt to retrieve the cached response
    cache_key = f"GET_{service}_{path}_response" if path else f"GET_{service}_response"  # Consistent cache key
    cached_response = redis_conn.get(cache_key)
    if cached_response:
        print(f"Cache hit for {service}, {path}. Data from cache: {cached_response}")
        return Response(cached_response, mimetype='application/json'), 200
    else:
        print("Cache miss, forwarding request")

    # If not in cache, forward the request
    forward_url = construct_forward_url(service_address, service, path)
    print(f"Forwarding request to {forward_url}")
    response = forward_request(forward_url, request)
    print(f"Received response from {forward_url} with status code {response.status_code}")

    # Handle caching operations based on the response
    handle_cache_operations(service, path, request, response)

    return Response(response.content, mimetype='application/json'), response.status_code



def get_service_address_from_cache(service):
    return services_cache.get(service)


def get_service_address_from_discovery(service):
    try:
        print(f"Calling Service Discovery to find service address for {service}")
        response = call_service_discovery(f"{SERVICE_DISCOVERY_URL}discover/{service}")
        if response.status_code == 200:
            print(f"Service Discovery found service address for {service}")
            return response.json().get("service_address")
        else:
            logging.warning(
                f"Service Discovery did not find service address for {service}, status code {response.status_code}")
            return None
    except pybreaker.CircuitBreakerError:
        print("Circuit Breaker is open, not making request to Service Discovery")
        return None
    except Exception as e:
        print(f"Failed to call Service Discovery. Error: {e}")
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


def forward_request(url, req):
    try:
        print(f"Forwarding request to {url}")
        response = requests.request(
            method=req.method,
            url=url,
            headers={key: value for (key, value) in req.headers if key != 'Host'},
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            timeout=gatewayConfig.REQUEST_TIMEOUT
        )
        print(f"Received response from {url} with status code {response.status_code}")
        return response
    except pybreaker.CircuitBreakerError:
        print("Circuit Breaker is open, not making request")
        return Response(jsonify({"error": "Circuit Breaker is open, not making request"}),
                        status=503)  # 503 Service Unavailable
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out.")
        return Response("Timeout", mimetype='application/json'), 504

    except Exception as e:
        print(f"Failed to forward request. Error: {e}")
    return Response(jsonify({"error": "Service error"}), status=500)


def handle_cache_operations(service, path, req, res):
    cache_expiration_time = 300  # 5 minutes, can be set based on your needs

    if req.method in ["POST", "PUT", "DELETE"]:
        cache_key = f"{service}_{path}_response" if path else f"{service}_response"
        redis_conn.delete(cache_key)  # Clear only the response cache

    if req.method == "GET":
        cache_key = f"{req.method}_{service}_{path}_response" if path else f"{req.method}_{service}_response"
        redis_conn.setex(cache_key, cache_expiration_time, res.content)  # Set cache with expiration time


if __name__ == '__main__':
    check_service_discovery_health()
    print(f"Starting API Gateway on port {gatewayConfig.FLASK_PORT}")
    app.run(host=gatewayConfig.FLASK_HOST, port=gatewayConfig.FLASK_PORT, debug=True)
