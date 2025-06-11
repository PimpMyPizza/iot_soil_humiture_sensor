import network
import time
import socket
import machine
from src.constants import *
from src.config import Config


def unquote(s: str):
    s = s.replace("+", " ")
    s = s.replace("%21", "!")
    s = s.replace("%3A", ":")
    s = s.replace("%2F", "/")
    return s


def connect_to_wifi(config: Config, timeout=15):
    """Connect to WiFi in STA mode"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.wifi.ssid, config.wifi.password)
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            print("Could not connect to wifi. Timeout...")
            return False
        time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())
    return True


def start_ap_mode(config: Config):
    """Start AP mode with HTTP server for user configuration"""
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    ap.active(True)
    print("AP started:", AP_SSID)

    if config.mqtt.object_id == UNDEFINED_OBJECT_ID or not config.mqtt.object_id:
        # Initial boot. We never read the MAC address of the pico W
        # So we read it an construct the MQTT object ID based on that
        # in order to have a unique ID to use in MQTT
        mac = ap.config('mac')
        mac_str = ''.join('{:02x}'.format(b) for b in mac)
        config.set_object_id(f"d-{mac_str}")
        config.save()

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Server listening on", addr)

    path_to_tmpl_files = "../res/"
    
    with open(f"{path_to_tmpl_files}config.tmpl", "r") as f:
        config_page = f"HTTP/1.0 200 OK\n\n{f.read()}"
    
    with open(f"{path_to_tmpl_files}changes_successful.tmpl", "r") as f:
        success_page = f"HTTP/1.0 200 OK\n\n{f.read()}"

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        
        request_line = cl_file.readline()
        if not request_line:
            cl.close()
            continue
        print("Request:", request_line)
        
        # Read headers and data
        headers = {}
        while True:
            line = cl_file.readline()
            if line == b'\r\n' or line == b'':
                break
            parts = line.decode().split(":", 1)
            if len(parts) == 2:
                headers[parts[0].strip()] = parts[1].strip()
        
        length = int(headers.get("Content-Length", 0))
        post_data = b""
        if length > 0:
            post_data = cl_file.read(length)
        
        if request_line.startswith(b"POST"):
            # Parse form data
            data = post_data.decode()
            params = {}
            for pair in data.split("&"):
                key, val = pair.split("=")
                params[key] = val.replace("+", " ")

            # Update config
            config.set_values(
                wifi_ssid=unquote(params.get("wifi_ssid", DEFAULT_WIFI_SSID)),
                wifi_pw=unquote(params.get("wifi_password", DEFAULT_WIFI_PASSWORD)),
                broker_host=unquote(params.get("mqtt_broker_hostname", DEFAULT_MQTT_BROKER_NAME)),
                broker_port=unquote(params.get("mqtt_broker_port", DEFAULT_MQTT_BROKER_PORT)),
                username=unquote(params.get("mqtt_username", DEFAULT_MQTT_USERNAME)),
                password=unquote(params.get("mqtt_password", DEFAULT_MQTT_PASSWORD)),
                enable_discovery=params.get("mqtt_enable_discovery", DEFAULT_MQTT_DISCOVERY_ENABLED),
                measurements_per_day=params.get("measurements_per_day", DEFAULT_MEASUREMENTS_PER_DAY),
            )
            config.save()
            cl.send(success_page)
            cl.close()
            print("Rebooting in 3 seconds to apply configuration changes.")
            time.sleep(3)
            machine.reset()
            return
        
        # Serve config page with current values
        config_page_html = config_page.format(
            wifi_ssid=config.wifi.ssid,
            wifi_password=config.wifi.password,
            mqtt_broker_hostname=config.mqtt.broker_hostname,
            mqtt_broker_port=config.mqtt.broker_port,
            mqtt_username=config.mqtt.username,
            mqtt_pw=config.mqtt.password,
            # Set the selected tag depending on if MQTT is enabled or not in the config
            mqtt_discovery_true="selected" if config.mqtt.discovery_enabled else "",
            mqtt_discovery_false="selected" if not config.mqtt.discovery_enabled else "",
            measurements_per_day=config.measurements_per_day,
        )
        cl.send(config_page_html.encode())
        cl.close()