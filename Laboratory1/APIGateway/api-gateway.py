import logging
import os
import time
import requests
import redis
from flask import Flask, jsonify, request, Response
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
import pybreaker
from hashring import HashRing

# Circuit Breaker Configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # number of failures before changing to open state
    reset_timeout=10  # seconds after which the state should change from open to half-open
)

# Choose the config based on the environment variable
config_mode = os.environ.get('CONFIG_MODE', 'default')
if config_mode == 'docker':
    import gatewayConfigDocker as gatewayConfig

    print("Using Docker Configuration")
else:
    import gatewayConfigDefault as gatewayConfig

    print("Using Default Configuration")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


def initialize_redis_clients(nodes):
    clients = {}
    for node in nodes:
        host, port = node.split(':')
        clients[node] = redis.StrictRedis(host=host, port=int(port), db=0)
        logging.info(f"Host: {host}, port: {port} Node: {node}")
    return clients


# Example nodes, replace with your actual Redis nodes
redis_nodes = ['redis:6379']
redis_clients = initialize_redis_clients(redis_nodes)
redis_ring = HashRing(redis_nodes)
logging.info(f"Redis ring: {redis_ring}")


SERVICE_DISCOVERY_URL = gatewayConfig.SERVICE_DISCOVERY
services_cache = {}  # In-memory store for service addresses

logging.info(f"Initializing Flask-Limiter with storage URI: {gatewayConfig.REDIS_URL}")
# Setup Flask Limiter with Redis as the storage backend
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri=f"redis://{gatewayConfig.REDIS_HOST}:{gatewayConfig.REDIS_PORT}/{gatewayConfig.REDIS_DB}",
)


# Exemption logic (keep this as-is, as per your instructions)
@limiter.request_filter
def exempt_users():
    return False


def check_service_discovery_health():
    retries = 5
    backoff_factor = 2  # Time delay factor
    for i in range(retries):
        try:
            response = requests.get(f"{SERVICE_DISCOVERY_URL}/health", timeout=gatewayConfig.REQUEST_TIMEOUT)
            if response.status_code == 200:
                logging.info("Service Discovery is healthy and running.")
                return True
            else:
                logging.warning(f"Service Discovery returned status {response.status_code}. Retrying...")
                time.sleep(i * backoff_factor)  # Exponential backoff
        except requests.RequestException as e:
            logging.warning(f"Failed to connect to Service Discovery. Error: {e}. Retrying...")
            time.sleep(i * backoff_factor)  # Exponential backoff
    logging.warning("Failed to connect to Service Discovery after multiple retries. Starting API Gateway with caution.")
    return False


@app.route('/<service>/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path=''):
    logging.info(f"Proxy called for service: {service} and path: {path}")
    service_address = get_service_address_from_cache(service)

    if not service_address:
        logging.info(f"Service address not found in cache for service: {service}")
        service_address = get_service_address_from_discovery(service)
        if not service_address:
            logging.warning(f"Service address not found in service discovery for service: {service}")
            return jsonify({"error": f"Service {service} not found"}), 404
        services_cache[service] = service_address  # Store in in-memory dictionary
        logging.info(f"Service address for {service} found in service discovery: {service_address}")

    # Check for cached response
    cache_key = f"{service}_{path}_response" if path else f"{service}_response"
    logging.info(f"Checking cache for key: {cache_key}")
    node = redis_ring.get_node(cache_key)
    client = redis_clients[node]
    cached_response = client.get(cache_key)
    if cached_response:
        logging.info(f"Cache hit for key: {cache_key}")
        return Response(cached_response, mimetype='application/json'), 200
    else:
        logging.info(f"Cache miss for key: {cache_key}")

    forward_url = construct_forward_url(service_address, service, path)
    logging.info(f"Forwarding request to: {forward_url}")
    response = forward_request(forward_url, request)
    handle_cache_operations(service, path, request, response)
    return Response(response.content, mimetype='application/json'), response.status_code


def get_service_address_from_cache(service):
    return services_cache.get(service)


def get_service_address_from_discovery(service):
    try:
        response = call_service_discovery(f"{SERVICE_DISCOVERY_URL}discover/{service}")
        if response.status_code == 200:
            return response.json().get("service_address")
        return None
    except pybreaker.CircuitBreakerError:
        logging.error("Circuit Breaker is open, not making request to Service Discovery")
        return None
    except Exception as e:
        logging.error(f"Failed to call Service Discovery. Error: {e}")
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
    logging.info(f"Forwarding request to URL: {url} with method: {req.method}")
    try:
        response = requests.request(
            method=req.method,
            url=url,
            headers={key: value for (key, value) in req.headers if key != 'Host'},
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            timeout=gatewayConfig.REQUEST_TIMEOUT
        )
        logging.info(f"Received response with status code: {response.status_code}")
        return response
    except pybreaker.CircuitBreakerError as e:
        logging.error(f"Circuit Breaker is open, not making request: {e}")
        return Response(jsonify({"error": "Circuit Breaker is open, not making request"}),
                        status=503)  # 503 Service Unavailable
    except requests.exceptions.Timeout as e:
        logging.error(f"Request to {url} timed out: {e}")
        return Response(jsonify({"error": "Request timed out"}), status=504)  # 504 Gateway Timeout
    except Exception as e:
        logging.error(f"Failed to forward request. Error: {e}")
        return Response(jsonify({"error": "Service error"}), status=500)


def handle_cache_operations(service, path, req, res):
    cache_expiration_time = 300  # 5 minutes, can be set based on your needs
    cache_key = f"{service}_{path}_response" if path else f"{service}_response"

    try:
        if req.method in ["POST", "PUT", "DELETE"]:
            node = redis_ring.get_node(cache_key)
            client = redis_clients[node]
            logging.info(f"Attempting to delete cache for key: {cache_key} on node: {node}")
            client.delete(cache_key)  # Clear only the response cache

        if req.method == "GET":
            node = redis_ring.get_node(cache_key)
            client = redis_clients[node]
            logging.info(f"Attempting to set cache for key: {cache_key} on node: {node} with expiration: {cache_expiration_time}")
            client.setex(cache_key, cache_expiration_time, res.content)  # Set cache with expiration time

    except Exception as e:
        logging.error(f"Error during cache operation: {e}")


@app.route('/health', methods=['GET'])
def status():
    return jsonify({"health": "Api gateway is up and running!"}), 200


@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    for client in redis_clients.values():
        client.flushdb()
    return jsonify({"status": "Cache cleared successfully"}), 200


if __name__ == '__main__':
    check_service_discovery_health()
    logging.info(f"Starting API Gateway on port {gatewayConfig.FLASK_PORT}")
    app.run(host=gatewayConfig.FLASK_HOST, port=gatewayConfig.FLASK_PORT, debug=True)
