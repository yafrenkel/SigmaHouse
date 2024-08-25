# -*- coding: utf-8 -*-
"""Stand-alone module to demo WiFi network connectivity."""
from binascii import hexlify
from time import sleep
from urequests import request as http_request

import network

print("WIFI: Initiating")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()

wifi_connect_success = True
wifi_ssid = "TP-Link_3E52"
wifi_pass = "37424916"
wifi_ip_address = ''
wifi_mac_address = ''



if not wlan.isconnected():
    print(f"WIFI: Using SSID: {wifi_ssid}")
    print(f"WIFI: Using PASS: {wifi_pass}")
    wlan.connect(wifi_ssid, wifi_pass)

    wifi_connect_timeout = 10
    print(f"WIFI: Using TOUT: {wifi_connect_timeout}")

    while not wlan.isconnected():
        if wlan.status() == network.STAT_CONNECTING:
            print(f"WIFI: Connecting [timeout: {wifi_connect_timeout:0>2}s]")
        else:
            print(f"WIFI: Connecting with unexpected status: {wlan.status()}")

        sleep(1)  # wait 1 sec

        wifi_connect_timeout -= 1

        if wifi_connect_timeout == 0:
            wifi_connect_success = False
            break

if not wifi_connect_success:
    print(f"WIFI: Could not connect to SSID: {wifi_ssid}")
    raise RuntimeError("WIFI connection failed")
else:
    wifi_ip_address = wlan.ifconfig()[0]
    wifi_mac_address = hexlify(wlan.config("mac"), ":").decode("utf-8").upper()
    print(f"WIFI: Connected to SSID: {wifi_ssid}")
    print(f"WIFI: IP Address: {wifi_ip_address}")
    print(f"WIFI: MAC Address: {wifi_mac_address}")




# Get the serial number from the unique ID of the ESP32
serial_number = hexlify(wlan.config("mac"), ":").decode("utf-8").upper()
user_name = "Lilia Smart"  # Change this for each client

call_url = "http://192.168.0.101//smart?serial_number=" + wifi_mac_address + "&user_name=" + user_name + "&ip_address=" + wifi_ip_address
call_method="GET"

try:
    response = http_request(  # noqa: S113
        method=call_method,
        url=call_url,
        headers={"Content-Type": "application/json"},
    )
    _response = response.json()
    if response.status_code == 200:
        print("Response from server:", response.json().get('message'))
    else:
        print("Failed to get response from server, status code:", response.status_code)
except Exception as e:
    print("An error occurred:", e)


print("WIFI: Disconnecting")
wlan.disconnect()

