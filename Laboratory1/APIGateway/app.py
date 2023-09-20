from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory store of registered microservices
microservices = {}


@app.route('/register', methods=['POST'])
def register_service():
    """
    Endpoint for microservices to register themselves.
    """
    # Log the registration attempt
    print(f"Registration request received from {request.remote_addr}")

    data = request.json
    name = data.get('name')
    address = data.get('address')

    if name and address:
        microservices[name] = address
        return jsonify({"message": "Registered successfully"}), 200
    else:
        return jsonify({"error": "Invalid registration data"}), 400


@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path):
    """
    Endpoint to route requests to appropriate microservices.
    """
    # Log the access
    print(f"Access request for service {service} received from {request.remote_addr}")

    # Route request to the appropriate microservice
    if service in microservices:
        # For simplicity, just show the address here.
        # You would use an HTTP client like requests to actually
        # forward the request and get a response.
        return jsonify({"service_address": microservices[service]})
    else:
        return jsonify({"error": f"Service {service} not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
