"""Constants for the dLight integration."""

DOMAIN = "dlight"

# Configuration
CONF_DEVICE_ID = "device_id"
DEFAULT_PORT = 3333
DEFAULT_NAME = "dLight"

# Update interval
UPDATE_INTERVAL = 30  # seconds

# Color temperature range (in Kelvin)
MIN_KELVIN = 2600
MAX_KELVIN = 6000

# Color temperature range (in mireds)
# Mireds = 1000000 / Kelvin
MIN_MIREDS = 167  # 1000000 / 6000
MAX_MIREDS = 385  # 1000000 / 2600

# Brightness range
MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 100

# Command types
COMMAND_QUERY_DEVICE_INFO = "QUERY_DEVICE_INFO"
COMMAND_QUERY_DEVICE_STATES = "QUERY_DEVICE_STATES"
COMMAND_EXECUTE = "EXECUTE"

# Socket timeout
SOCKET_TIMEOUT = 5  # seconds
