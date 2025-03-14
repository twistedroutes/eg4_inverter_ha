# const.py
DOMAIN = "eg4_inverter"
PLATFORMS = ["sensor", "binary_sensor"]

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_BASE_URL = "base_url"
CONF_SERIAL_NUMBER = "serial_number"
CONF_IGNORE_SSL = "ignore_ssl"

# These two must be strings if they are used as keys in entry.data
CONF_RUNTIME_INTERVAL_SECONDS = "runtime_interval_seconds"
CONF_SETTINGS_INTERVAL_SECONDS = "settings_interval_seconds"

DEFAULT_RUNTIME_INTERVAL_SECONDS = 30
DEFAULT_SETTINGS_INTERVAL_SECONDS = 1200
DEFAULT_BASE_URL = "https://monitor.eg4electronics.com"
