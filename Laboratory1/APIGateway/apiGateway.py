import logging
import time
import requests
import redis
from flask import Flask, jsonify, request, Response
import gatewayConfig

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

redis_conn = redis.StrictRedis(host=gatewayConfig.REDIS_HOST, port=gatewayConfig.REDIS_PORT, db=gatewayConfig.REDIS_DB)

SERVICE_DISCOVERY_URL = gatewayConfig.SERVICE_DISCOVERY
services_cache = {}  # In-memory store for service addresses


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
    service_address = get_service_address_from_cache(service)

    if not service_address:
        service_address = get_service_address_from_discovery(service)

        if not service_address:
            return jsonify({"error": f"Service {service} not found"}), 404
        services_cache[service] = service_address  # Store in in-memory dictionary

    # Check for cached response
    cache_key = f"{service}_{path}_response" if path else f"{service}_response"
    cached_response = redis_conn.get(cache_key)
    if cached_response:
        return Response(cached_response, mimetype='application/json'), 200

    forward_url = construct_forward_url(service_address, service, path)

    response = forward_request(forward_url, request)

    handle_cache_operations(service, path, request, response)

    return Response(response.content, mimetype='application/json'), response.status_code


def get_service_address_from_cache(service):
    return services_cache.get(service)


def get_service_address_from_discovery(service):
    response = requests.get(f"{SERVICE_DISCOVERY_URL}discover/{service}")
    if response.status_code == 200:
        return response.json().get("service_address")
    return None


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
        response = requests.request(
            method=req.method,
            url=url,
            headers={key: value for (key, value) in req.headers if key != 'Host'},
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            timeout=gatewayConfig.REQUEST_TIMEOUT
        )
        return response
    except requests.exceptions.Timeout:
        logging.error(f"Request to {url} timed out.")
        return Response(jsonify({"error": "Request timed out"}), status=504)  # 504 Gateway Timeout


def handle_cache_operations(service, path, req, res):
    cache_expiration_time = 300  # 5 minutes, can be set based on your needs

    if req.method in ["POST", "PUT", "DELETE"]:
        cache_key = f"{service}_{path}_response" if path else f"{service}_response"
        redis_conn.delete(cache_key)  # Clear only the response cache

    if req.method == "GET":
        cache_key = f"{service}_{path}_response" if path else f"{service}_response"
        redis_conn.setex(cache_key, cache_expiration_time, res.content)  # Set cache with expiration time


@app.route('/health', methods=['GET'])
def status():
    return jsonify({"health": "Api gateway is up and running!"}), 200


if __name__ == '__main__':
    check_service_discovery_health()
    logging.info(f"Starting API Gateway on port {gatewayConfig.FLASK_PORT}")
    app.run(host=gatewayConfig.FLASK_HOST, port=gatewayConfig.FLASK_PORT, debug=True)
