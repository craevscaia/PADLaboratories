# serviceConfig.py
import os

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# Flask Configuration
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 6000))

# Rate Limiting Configuration
REGISTER_LIMIT = os.environ.get('REGISTER_LIMIT', "5 per minute")
DISCOVER_LIMIT = os.environ.get('DISCOVER_LIMIT', "10 per second")

# Redis Retry Configuration
RETRY_COUNT = int(os.environ.get('RETRY_COUNT', 5))
