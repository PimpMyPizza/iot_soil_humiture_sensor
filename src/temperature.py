import machine
import onewire
import ds18x20
import time
from src.constants import *

# Set up the 1-Wire bus
ds_pin = machine.Pin(TEMPERATURE_DATA_PIN)
temperature_switch_on_off_pin = machine.Pin(
    TEMPERATURE_SWITCH_ON_OFF_PIN,
    machine.Pin.OUT,
)
temperature_switch_on_off_pin.value(PIN_ON)
ow = onewire.OneWire(ds_pin)
ds = ds18x20.DS18X20(ow)

# Scan for devices on the bus
roms = ds.scan()
print("Found DS18B20 devices:", roms)


def read():
    """Reads temperature in Celsius from the first DS18B20 sensor found."""
    if not roms:
        # No sensor found
        return None
    ds.convert_temp()
    # Wait for conversion
    time.sleep(0.75)
    # Read from the first (only) found sensor
    temp = ds.read_temp(roms[0])
    print(f"Temperature: {temp}°C")
    return temp
