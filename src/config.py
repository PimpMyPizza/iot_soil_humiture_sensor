import json

from src.constants import (
    DEFAULT_WIFI_SSID,
    DEFAULT_WIFI_PASSWORD,
    DEFAULT_MQTT_BROKER_NAME,
    DEFAULT_MQTT_BROKER_PORT,
    DEFAULT_MQTT_USERNAME,
    DEFAULT_MQTT_PASSWORD,
    DEFAULT_MQTT_DEVICE_STATE_TOPIC,
    DEFAULT_MQTT_DISCOVERY_TOPIC,
    DEFAULT_MQTT_DISCOVERY_ENABLED,
    DEFAULT_MEASUREMENTS_PER_DAY,
    UNDEFINED_OBJECT_ID,
)


class WifiConfig:
    
    def __init__(self):
        self.ssid = DEFAULT_WIFI_SSID
        self.password = DEFAULT_WIFI_PASSWORD

    def load(self, data: dict):
        try:
            self.ssid = data.get("ssid", DEFAULT_WIFI_SSID)
            self.password = data.get("password", DEFAULT_WIFI_PASSWORD)
        except Exception as e:
            print(f"Error while loading wifi config: {e}")
    
    def to_dict(self):
        return {
            "ssid": self.ssid,
            "password": self.password,
        }
    
    def set_values(self, ssid, password):
        self.ssid = ssid
        self.password = password
    
    def valid(self):
        if not self.ssid:
            print(f"Invalid WiFi SSID in config {self.ssid}")
            return False
        return True


class MQTTConfig:

    def __init__(self):
        # MQTT broker name or IP
        self.broker_hostname = DEFAULT_MQTT_BROKER_NAME
        # MQTT broker port to use for publishing message (not WS)
        self.broker_port = DEFAULT_MQTT_BROKER_PORT
        # Username to use for connection to home assistant
        self.username = DEFAULT_MQTT_USERNAME
        # Home assistant user password
        self.password = DEFAULT_MQTT_PASSWORD
        # Unique ID based on MAC to use for topics naming
        self.object_id = UNDEFINED_OBJECT_ID
        # Topic to use for publishing device state
        self.device_state_topic = DEFAULT_MQTT_DEVICE_STATE_TOPIC
        # Topic to use for publishing device discovery config
        self.discovery_topic = DEFAULT_MQTT_DISCOVERY_TOPIC
        # Used to enable/disable discovery feature
        self.discovery_enabled = DEFAULT_MQTT_DISCOVERY_ENABLED

    def to_dict(self):
        return {
            "broker_hostname": self.broker_hostname,
            "broker_port": self.broker_port,
            "device_state_topic": self.device_state_topic,
            "username": self.username,
            "password": self.password,
            "object_id": self.object_id,
            "discovery_enabled": self.discovery_enabled,
            "discovery_topic": self.discovery_topic,
        }

    def load(self, data: dict):
        try:
            self.broker_hostname = data.get(
                "broker_hostname", DEFAULT_MQTT_BROKER_NAME
            )
            self.broker_port = data.get(
                "broker_port", DEFAULT_MQTT_BROKER_PORT
            )
            self.device_state_topic = data.get(
                "device_state_topic",
                DEFAULT_MQTT_DEVICE_STATE_TOPIC)
            self.discovery_enabled = data.get(
                "discovery_enabled",
                DEFAULT_MQTT_DISCOVERY_ENABLED
            )
            self.discovery_topic = data.get(
                "discovery_topic",
                DEFAULT_MQTT_DISCOVERY_TOPIC
            )
            self.username = data.get("username", DEFAULT_MQTT_USERNAME)
            self.password = data.get("password", DEFAULT_MQTT_PASSWORD)
            self.object_id = data.get("object_id", UNDEFINED_OBJECT_ID)
        except Exception as e:
            print(f"Error while loading wifi config: {e}")
    
    def set_values(self, broker_host, broker_port, username,
                   password, enable_discovery):
        self.broker_hostname = broker_host
        if isinstance(broker_port, int):
            self.broker_port = broker_port
        else:
            self.broker_port = int(broker_port)
        self.username = username
        self.password = password
        if str(enable_discovery).lower() == "true":
            self.discovery_enabled = True
        else:
            self.discovery_enabled = enable_discovery
    
    
    def valid(self):
        if not self.broker_hostname:
            print(f"Invalid broker hostname in config {self.broker_hostname}")
            return False
        if len(self.object_id) <= 5 or any(c in "<>" for c in self.object_id):
            # object id must contain only letters, number, "-" 
            # or "_" and have a length betweem 5 and 20.
            print(f"Invalid object_id in config {self.object_id}")
            return False
        return True


class Config:

    def __init__(self):
        self.mqtt = MQTTConfig()
        self.wifi = WifiConfig()
        self.output_path = "config.json"
        # Number of sensor samples to read each day
        self.measurements_per_day = DEFAULT_MEASUREMENTS_PER_DAY

    def load(self):
        try:
            with open(self.output_path, "r") as f:
                data = json.load(f)
                self.mqtt.load(data["mqtt"])
                self.wifi.load(data["wifi"])
                self.measurements_per_day = data.get(
                    "measurements_per_day",
                    DEFAULT_MEASUREMENTS_PER_DAY
                )
        except Exception as e:
            print(f"Error while loading config file: {e}")
    
    def valid(self) -> bool:
        if (
            not self.measurements_per_day or
            not isinstance(self.measurements_per_day, int)
        ):
            print(
                "Invalid measurements per day value " \
                f"{self.measurements_per_day}"
            )
            return False
        if not self.mqtt.valid():
            return False
        if not self.wifi.valid():
            return False
        return True
    
    def to_dict(self):
        return {
            "measurements_per_day": self.measurements_per_day,
            "wifi": self.wifi.to_dict(),
            "mqtt": self.mqtt.to_dict(),
        }

    def save(self):
        print("Save config", self.to_dict())
        with open(self.output_path, "w") as f:
            json.dump(self.to_dict(), f)
        print("Config saved.")
    
    def set_object_id(self, new_object_id: str):
        if not new_object_id:
            print("Cannot set an empty MQTT object ID.")
            return
        self.mqtt.object_id = new_object_id
        self.mqtt.discovery_topic = self.mqtt.discovery_topic.replace(
            UNDEFINED_OBJECT_ID, self.mqtt.object_id
        )
        self.mqtt.device_state_topic = self.mqtt.device_state_topic.replace(
            UNDEFINED_OBJECT_ID, self.mqtt.object_id
        )
        print(f"Set MQTT unique object id to {self.mqtt.object_id}")
    
    def set_values(
        self,
        wifi_ssid: str,
        wifi_pw: str,
        broker_host: str,
        broker_port: int | str,
        username: str,
        password: str,
        enable_discovery: bool | str,
        measurements_per_day: int | str,
    ) -> None:
        self.wifi.set_values(
            ssid=wifi_ssid,
            password=wifi_pw,
        )
        self.mqtt.set_values(
            broker_host=broker_host,
            broker_port=broker_port,
            username=username,
            password=password,
            enable_discovery=enable_discovery,
        )
        try:
            if isinstance(measurements_per_day, int):
                self.measurements_per_day = measurements_per_day
            else:
                self.measurements_per_day = int(measurements_per_day)
        except Exception:
            self.measurements_per_day = DEFAULT_MEASUREMENTS_PER_DAY
