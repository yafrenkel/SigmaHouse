"""Synchronous firmware -- DEFAULT teaching version.

One while-True loop, one tick every 50 ms. The loop:
  1. Checks button flags (set by interrupts).
  2. Checks the motion flag.
  3. Sends a keepalive once per UPDATE_INTERVAL_MS.
  4. Applies any commands the hub sent back.

No async, no event queues, no threads. Read it top to bottom.
"""

import time
import network
import ubinascii
from machine import unique_id

import config
from hub_client import HubClient
from devices.led import LED
from devices.button import Button
from devices.motion import Motion
from devices.fan import Fan
from devices.buzzer import Buzzer
from devices.lcd import LCD
from devices.safe import safe

MENU = ("led", "fan", "buzzer")


# ---------- helpers ----------

def _connect_wifi(lcd):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        lcd.show("Connecting to", config.WIFI_SSID)
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        deadline = time.time() + config.WIFI_TIMEOUT_S
        while not wlan.isconnected() and time.time() < deadline:
            time.sleep_ms(200)
    if not wlan.isconnected():
        lcd.show("WiFi FAILED")
        raise RuntimeError("WiFi connect failed")
    return wlan.ifconfig()[0]


def _build_state(led, fan, buzzer, motion):
    return {
        "led":    led.state(),
        "fan":    fan.state(),
        "buzzer": buzzer.state(),
        "motion": motion.state(),
    }


def _apply_state(s, led, fan, buzzer):
    """Apply hub's desired state to the local devices, only if changed."""
    if s["led"]["active"] != led.is_on():
        led.on() if s["led"]["active"] else led.off()
    if s["fan"]["active"] != fan.is_on():
        if s["fan"]["active"]:
            fan.on(s["fan"].get("clockwise", True))
        else:
            fan.off()
    if s["buzzer"]["active"] != buzzer.is_on():
        buzzer.on() if s["buzzer"]["active"] else buzzer.off()


def _toggle(name, led, fan, buzzer):
    if name == "led":
        led.off() if led.is_on() else led.on()
    elif name == "fan":
        fan.off() if fan.is_on() else fan.on()
    elif name == "buzzer":
        buzzer.off() if buzzer.is_on() else buzzer.on()


# ---------- main ----------

def run():
    # Each device is built "safely": if a part isn't wired, you get a
    # warning + a harmless stub instead of a crash. Watch the REPL for
    # any "WARNING: X not available" lines to see what's missing.
    lcd      = safe(lambda: LCD(config.PIN_I2C_SCL, config.PIN_I2C_SDA,
                                config.LCD_I2C_ADDR, config.LCD_ROWS,
                                config.LCD_COLS), "LCD")
    led      = safe(lambda: LED(config.PIN_LED), "LED")
    button_a = safe(lambda: Button(config.PIN_BUTTON_A), "Button A")
    button_b = safe(lambda: Button(config.PIN_BUTTON_B), "Button B")
    motion   = safe(lambda: Motion(config.PIN_PIR), "Motion")
    fan      = safe(lambda: Fan(config.PIN_FAN_A, config.PIN_FAN_B), "Fan")
    buzzer   = safe(lambda: Buzzer(config.PIN_BUZZER), "Buzzer")

    ip = _connect_wifi(lcd)
    uid = ubinascii.hexlify(unique_id()).decode().upper()
    hub = HubClient(config.HUB_URL, uid)
    hub.register(ip)
    lcd.show("Ready " + uid[-6:], ip)

    menu_index = 0
    last_keepalive = time.ticks_ms()

    try:
        while True:
            # --- button A: rotate menu ---
            if button_a.was_pressed():
                menu_index = (menu_index + 1) % len(MENU)
                print("Button A -> selected:", MENU[menu_index])
                lcd.show("Select:", MENU[menu_index])

            # --- button B: toggle selected device ---
            if button_b.was_pressed():
                _toggle(MENU[menu_index], led, fan, buzzer)
                print("Button B -> toggled:", MENU[menu_index])
                hub.push_state(_build_state(led, fan, buzzer, motion))

            # --- motion -> tell the hub ---
            if motion.was_triggered():
                hub.report_motion()

            # --- keepalive ---
            if time.ticks_diff(time.ticks_ms(), last_keepalive) >= config.UPDATE_INTERVAL_MS:
                last_keepalive = time.ticks_ms()
                resp = hub.keepalive(ip)
                if resp:
                    if resp.get("alarm"):
                        buzzer.on()
                    if resp.get("state_update"):
                        new_state = hub.get_state()
                        if new_state:
                            _apply_state(new_state, led, fan, buzzer)

            time.sleep_ms(50)
    finally:
        hub.deregister()
        led.off()
        fan.off()
        buzzer.off()
