from flask import Flask, request, jsonify, redirect
from flask_caching import Cache
import requests
import config
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Set up caching with Redis
app.config['CACHE_TYPE'] = config.CACHE_TYPE
app.config['CACHE_REDIS_URL'] = config.REDIS_URL
cache = Cache(app)

SERVICE_DISCOVERY_URL =  config.SERVICE_DISCOVERY

@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path):
    # Check if service address is in cache
    service_address = cache.get(service)

    if not service_address:
        # If not in cache, ask Service Discovery
        response = requests.get(SERVICE_DISCOVERY_URL + service)
        if response.status_code == 200:
            service_address = response.json().get("service_address")
            cache.set(service, service_address)
        else:
            return jsonify({"error": f"Service {service} not found"}), 404

    # Forward the request to the microservice
    forward_url = f"{service_address}/{path}"
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
        cache.set(f"{service}_{path}", response.content)

    # Return the response from the microservice
    return (response.content, response.status_code, response.headers.items())


if __name__ == '__main__':
    logging.info(f"Starting API Gateway on port {config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT)
