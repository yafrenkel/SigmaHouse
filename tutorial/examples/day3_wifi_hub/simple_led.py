"""Day 3 - The simplest possible smart house (LED only).

This is the smallest firmware that talks to the hub:
  1. Connects to WiFi
  2. Registers with the hub
  3. Loops: sends a keepalive; if the hub says "state_update", pulls the
     new state and switches the LED
  4. On Ctrl-C, unregisters cleanly

Compare it to implementation/smart_house/app_sync.py (~130 lines). Same
protocol, stripped to one device. Once this works, the full firmware is
the same idea with more devices.

To use:
  1. Edit the four lines under "EDIT THESE" (your WiFi + your laptop's IP).
  2. In Thonny: File -> Save as -> MicroPython device -> simple_led.py
  3. Press F5. Watch the shell.
  4. Click the LED button in the dashboard -> the LED switches. Ctrl-C to stop.
"""

import network
import time
import ubinascii
import urequests
from machine import Pin, unique_id

# ----- EDIT THESE -----
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
HUB_URL   = "http://192.168.1.10:8080"   # your laptop's IP + port 8080
LED_PIN   = 12
# ----------------------


led = Pin(LED_PIN, Pin.OUT)
led.value(0)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    # We try the whole thing up to 5 times. Each try does a FULL radio reset
    # (active off -> on) before connecting. A soft reboot or a brownout can
    # leave the WiFi driver wedged, and then connect() throws
    # "Wifi Internal Error" -- resetting the radio and retrying clears it.
    for attempt in range(1, 6):
        try:
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            time.sleep(1)
            if not wlan.isconnected():
                print("Connecting to WiFi... (attempt %d of 5)" % attempt)
                wlan.connect(WIFI_SSID, WIFI_PASS)
                for _ in range(30):            # wait up to ~15 seconds
                    if wlan.isconnected():
                        break
                    time.sleep(0.5)
            if wlan.isconnected():
                ip = wlan.ifconfig()[0]
                print("WiFi connected, my IP:", ip)
                return ip
            print("  not connected yet; resetting radio and retrying...")
        except OSError as e:
            print("  WiFi error (%s); resetting radio and retrying..." % e)
            time.sleep(2)
    raise RuntimeError("WiFi failed after 5 tries - check SSID/password and that it's 2.4GHz")


def hub_call(method, path, body=None):
    """One HTTP call. Returns dict or None on error. Always closes."""
    url = HUB_URL + path
    try:
        if body is None:
            r = urequests.request(method, url)
        else:
            r = urequests.request(
                method, url, json=body,
                headers={"Content-Type": "application/json"},
            )
    except Exception as e:
        print("HTTP error:", e)
        return None
    try:
        return r.json()
    finally:
        r.close()


def apply_led_state(state):
    """Compare the hub's desired LED state to the real one and switch if needed."""
    want_on = bool(state["led"]["active"])
    is_on   = bool(led.value())
    if want_on and not is_on:
        led.value(1)
        print("LED -> ON  (from dashboard)")
    elif not want_on and is_on:
        led.value(0)
        print("LED -> OFF (from dashboard)")


def main():
    ip = connect_wifi()
    uid = ubinascii.hexlify(unique_id()).decode().upper()
    print("My uid:", uid)

    hub_call("POST", "/api/houses", {"unique_id": uid, "ip_address": ip})
    print("Registered with hub.")

    POLL_MS = 200    # check the hub 5x/second. Lower = snappier LED, more WiFi traffic.

    try:
        while True:
            try:
                resp = hub_call(
                    "PUT", "/api/houses/" + uid + "/keepalive",
                    {"ip_address": ip},
                )
                if resp and resp.get("state_update"):
                    state = hub_call("GET", "/api/houses/" + uid + "/state")
                    if state:
                        apply_led_state(state)
            except KeyboardInterrupt:
                raise                       # let the outer handler stop us cleanly
            except Exception as e:
                print("loop hiccup (ignored):", e)   # one bad request won't crash us
            time.sleep_ms(POLL_MS)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        try:
            hub_call("DELETE", "/api/houses/" + uid)
        except Exception:
            pass
        led.value(0)
        print("Unregistered. Goodbye.")


main()
