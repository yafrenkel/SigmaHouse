"""Copy this file to secrets.py and edit with your real WiFi + hub address.

secrets.py must NOT be committed to git -- it has the WiFi password.
"""

WIFI_SSID = "your-wifi-ssid"
WIFI_PASS = "your-wifi-password"

# IP of the laptop running iot_hub/app.py, plus port 8080.
# Find the laptop IP with `ipconfig` (Windows) or `ifconfig` (mac/linux).
HUB_URL = "http://192.168.1.10:8080"
