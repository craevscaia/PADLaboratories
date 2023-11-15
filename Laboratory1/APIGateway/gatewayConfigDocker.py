import os

# Hazelcast Configuration
HAZELCAST_HOST = os.environ.get('HAZELCAST_HOST', 'hazelcast')
HAZELCAST_PORT = int(os.environ.get('HAZELCAST_PORT', 5701))
# Additional Hazelcast configurations can be added here if needed

# Flask Configuration
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))

# Service Discovery
SERVICE_DISCOVERY = "http://servicediscovery:6000/"
REQUEST_TIMEOUT = 60
