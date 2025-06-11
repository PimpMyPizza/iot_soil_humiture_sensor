from umqtt.simple import MQTTClient
import network
import time
import json
from src.config import Config


def publish(topic: str, payload, config: Config, retain: bool = False):
    """
    Sends a payload to a MQTT topic.
    """
    message = json.dumps(payload).encode('utf-8')
    print(f"Send following message to {config.mqtt.broker_hostname}:{config.mqtt.broker_port} on topic {topic}")
    print(f"Client id {config.mqtt.object_id} \t Retain={retain}")
    print(f"{message}\n\n")
    client = MQTTClient(
        config.mqtt.object_id,
        config.mqtt.broker_hostname,
        config.mqtt.broker_port,
        config.mqtt.username,
        config.mqtt.password,
    )
    client.connect()
    client.publish(topic, message, retain=retain)
    client.disconnect()


def send_discovery(config: Config):
    payload = {
        "state_topic": f"my/plant/{config.mqtt.object_id}/state",
        "qos": 0,
        "dev": {
            "ids": config.mqtt.object_id,
            "name": "", # Optional, prefix to components in HA.
            "mf": "Stilmant.dev",
            "mdl": "Humidity and Temperature",
            "sw": "1.0.0",
            "sn": config.mqtt.object_id,
            "hw": "1.0.0"
        },
        "o": {
            "name": "stilmant.dev",
            "sw": "1.0.1",
            "url": "https://stilmant.dev/blog/"
        },
        "cmps": {
            f"comp_{config.mqtt.object_id}_temperature": {
                "p": "sensor",
                "device_class": "temperature",
                "unit_of_measurement": "°C",
                "value_template": "{{ value_json.temperature | round(1) }}",
                "unique_id": f"{config.mqtt.object_id}_temperature",
            },
            f"comp_{config.mqtt.object_id}_humidity": {
                "p": "sensor",
                "device_class": "humidity",
                "unit_of_measurement": "%",
                "value_template": "{{ value_json.humidity | round(1) }}",
                "unique_id": f"{config.mqtt.object_id}_humidity",
            }
        },
    }
    try:
        publish(
            topic=config.mqtt.discovery_topic,
            payload=payload,
            config=config,
            retain=True,
        )
    except Exception as e:
        print("Publish discovery failed. Error: ", e)
        return False
    return True


def delete_device(config: Config):
    publish(
        topic=config.mqtt.discovery_topic,
        payload="",
        config=config,
        retain=False,
    )
