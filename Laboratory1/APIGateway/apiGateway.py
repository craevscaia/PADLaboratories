import logging
import time
import requests
from flask import Flask, jsonify, request
from flask_caching import Cache

import gatewayConfig

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Set up caching with Redis
app.config['CACHE_TYPE'] = gatewayConfig.CACHE_TYPE
app.config['CACHE_REDIS_URL'] = gatewayConfig.REDIS_URL
cache = Cache(app)

SERVICE_DISCOVERY_URL = gatewayConfig.SERVICE_DISCOVERY


def check_service_discovery_health():
    retries = 5
    for i in range(retries):
        try:
            response = requests.get(f"{SERVICE_DISCOVERY_URL}/health")
            if response.status_code == 200:
                logging.info("Service Discovery is healthy and running.")
                return True
            else:
                logging.warning(f"Service Discovery returned status {response.status_code}. Retrying...")
                time.sleep(5)
        except requests.RequestException as e:
            logging.warning(f"Failed to connect to Service Discovery. Error: {e}. Retrying...")
            time.sleep(5)
    logging.warning("Failed to connect to Service Discovery after multiple retries. Starting API Gateway with caution.")
    return False


@app.route('/<service>/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path=''):
    # Check if service address is in cache
    service_address = cache.get(service)

    if not service_address:
        # If not in cache, ask Service Discovery
        response = requests.get(f"{SERVICE_DISCOVERY_URL}/{service}")
        if response.status_code == 200:
            service_address = response.json().get("service_address")
            cache.set(service, service_address)
        else:
            return jsonify({"error": f"Service {service} not found"}), 404

    # Forward the request to the microservice
    if path:
        forward_url = f"{service_address}/{service}/{path}"
    else:
        forward_url = f"{service_address}/{service}"

    response = requests.request(
        method=request.method,
        url=forward_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    # Invalidate cache for POST and PUT requests
    if request.method in ["POST", "PUT"]:
        cache.delete(service)

    # Cache the response for GET requests
    if request.method == "GET":
        cache_key = f"{service}_{path}" if path else f"{service}"
        cache.set(cache_key, response.content)

    # Return the response from the microservice in JSON format
    return jsonify(response.content.decode('utf-8')), response.status_code


@app.route('/health', methods=['GET'])
def status():
    return jsonify({"health": "Api gateway is up and running!"}), 200


if __name__ == '__main__':
    check_service_discovery_health()
    logging.info(f"Starting API Gateway on port {gatewayConfig.FLASK_PORT}")
    app.run(host=gatewayConfig.FLASK_HOST, port=gatewayConfig.FLASK_PORT, debug=True)
