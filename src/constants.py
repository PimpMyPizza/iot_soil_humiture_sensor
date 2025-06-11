# Change these only if you want to skip the setup of the device via the AP/HTTP server
# and directly use your own settings for your home. If you left unchanged, you'll be
# able to edit these by connecting to the pico W AP and connect to http://192.168.4.1
# at initial boot.

# Default Access Point settings
AP_SSID = "Soil Sensor"
AP_PASSWORD = "password"

# Default wifi settings
DEFAULT_WIFI_SSID = "Your-Wifi SSID"
DEFAULT_WIFI_PASSWORD = ""

# Default MQTT settings
UNDEFINED_OBJECT_ID = "<undefined>"
DEFAULT_MQTT_DISCOVERY_ENABLED = True
DEFAULT_MQTT_DEVICE_STATE_TOPIC = f"my/plant/{UNDEFINED_OBJECT_ID}/state"
# See https://www.home-assistant.io/integrations/mqtt/#discovery-topic
DEFAULT_MQTT_DISCOVERY_TOPIC = f"homeassistant/device/{UNDEFINED_OBJECT_ID}/config"
DEFAULT_MQTT_BROKER_NAME = "homeassistant"
DEFAULT_MQTT_BROKER_PORT = 1883
DEFAULT_MQTT_USERNAME = ""
DEFAULT_MQTT_PASSWORD = ""

# Default sensor readings frequency per day.
DEFAULT_MEASUREMENTS_PER_DAY = 24

# 1-wire temperature data sensor pin
TEMPERATURE_DATA_PIN = 16
# GPIO pin used to turn on/off the temperature sensor
TEMPERATURE_SWITCH_ON_OFF_PIN = 17

# GPIO pin used to read soil humidity sensor data
SOIL_HUMIDITY_SENSOR_PIN = 26
# GPIO pin used to deactivate humidity sensor in deepsleep mode
HUMIDITY_SWITCH_ON_OFF_PIN = 15

PIN_ON = 1
PIN_OFF = 0
