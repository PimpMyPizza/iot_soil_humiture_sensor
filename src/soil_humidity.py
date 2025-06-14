import machine
import time
from src.constants import SOIL_HUMIDITY_SENSOR_PIN


def read() -> float:
    """
    Reads soil humidity sensor values, averages multiple readings,
    and returns the average moisture percentage.
    """
    values = []
    # ADC max value on pico W 16 bits
    max_adc_value = 65535
    for _ in range(10):
        val = machine.ADC(SOIL_HUMIDITY_SENSOR_PIN).read_u16()
        # Convert ADC value to percentage
        moisture_percent = 100 - (val / max_adc_value * 100)
        values.append(moisture_percent)
        time.sleep(0.1)

    # Increase readings stability by making an average of readings
    average_humidity = sum(values) / len(values)
    print(f"Soil humidity: {round(average_humidity, 3)} %")
    return average_humidity
