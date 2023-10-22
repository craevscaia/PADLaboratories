import os

config_mode = os.environ.get('CONFIG_MODE', 'default')
if config_mode == 'docker':
    import gatewayConfigDocker as gatewayConfig
    print("Using Docker Configuration")
else:
    import gatewayConfigDefault as gatewayConfig
    print("Using Default Configuration")

SERVICE_DISCOVERY_URL = gatewayConfig.SERVICE_DISCOVERY
