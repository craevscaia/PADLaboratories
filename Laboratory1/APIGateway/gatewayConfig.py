# gatewayConfig.py
import os

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')

# Flask Configuration
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))

# Service Discovery
SERVICE_DISCOVERY = "http://localhost:6000/"
REQUEST_TIMEOUT = 5
