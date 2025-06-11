import time
import machine
from src.config import Config
from src import network
from src import mqtt
from src import soil_humidity
from src import temperature
from src.constants import *


def main():
    config = Config()
    config.load()
    print(f"Loaded config:\n", config.to_dict())

    if not config.valid() or not network.connect_to_wifi(config):
        # Invalid config or unable to connect to wifi: pico acts as an 
        # access point until the user has adapted the wifi config. The 
        # configuration page is accessible via http://192.168.4.1 and 
        # the device reboots after the user saves the new change.
        network.start_ap_mode(config)
    
    # Let Home Assistant know which data is published and how.
    if not mqtt.send_discovery(config):
        # If the discovery failed, go into AP mode again. This could be
        # due to some invalid config, e.g. when user password is wrong,
        # leading to MQTT unauthorized. In that case, the user has to
        # re-enter the right password.
        # TODO: show error in config page to let user what happened.
        network.start_ap_mode(config)

    humidity_switch_on_off_pin = machine.Pin(HUMIDITY_SWITCH_ON_OFF_PIN, machine.Pin.OUT)
    temperature_switch_on_off_pin = machine.Pin(TEMPERATURE_SWITCH_ON_OFF_PIN, machine.Pin.OUT)

    while(True):
        # Save time at which we started measuring to have more precise sleep duration
        measurements_start = time.time()

        # Turn on sensors
        humidity_switch_on_off_pin.value(PIN_ON)
        temperature_switch_on_off_pin.value(PIN_ON)

        # Wait a few seconds for the sensor to stabilize their readings.
        # This is needed, e.g. for the capacitive humidity sensors to heat up
        # If we don't wait, the humidity readings will be overestimated
        time.sleep(45)
        moisture_value = soil_humidity.read()
        temperature_value = temperature.read()
        
        try:
            mqtt.publish(
                config=config,
                topic=config.mqtt.device_state_topic,
                payload={
                    "state": "ON",
                    "timestamp": time.time(),
                    "temperature": temperature_value,
                    "humidity": moisture_value,
                },
                retain=True,
            )
        except Exception as e:
            print("Failed to publish MQTT. Error: ", e)
        
        # Turn off sensors and sleep until next measurement
        humidity_switch_on_off_pin.value(PIN_OFF)
        temperature_switch_on_off_pin.value(PIN_OFF)

        # Adapt time to sleep (user difined period minus measurements duration)
        measurements_duration = time.time() - measurements_start
        sleep_time = (86400 / config.measurements_per_day) - measurements_duration
        print(f"Deactivated sensor. Going to sleep now for {round(sleep_time)} seconds.")
        # TODO: use actual deepsleep functionality of pico W instead of time sleep
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
