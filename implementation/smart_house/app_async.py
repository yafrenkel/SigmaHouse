"""Async firmware -- ADVANCED version (set USE_ASYNC=True in config.py).

Same logical behavior as app_sync.py, but split into independent tasks:
  - task_buttons:   handle button presses
  - task_motion:    forward motion to hub
  - task_keepalive: heartbeat + apply remote commands

The device drivers and HubClient are EXACTLY the same -- compare this
file to app_sync.py to see what `async/await` actually changes.

Note: urequests itself is blocking, so during an HTTP call the other
tasks pause for ~100 ms. That's fine for our update rate.
"""

import time
import network
import ubinascii
import uasyncio as asyncio
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


# ---------- tasks ----------

async def task_buttons(button_a, button_b, led, fan, buzzer, motion, hub, lcd, ctx):
    while True:
        if button_a.was_pressed():
            ctx["menu"] = (ctx["menu"] + 1) % len(MENU)
            print("Button A -> selected:", MENU[ctx["menu"]])
            lcd.show("Select:", MENU[ctx["menu"]])
        if button_b.was_pressed():
            _toggle(MENU[ctx["menu"]], led, fan, buzzer)
            print("Button B -> toggled:", MENU[ctx["menu"]])
            hub.push_state(_build_state(led, fan, buzzer, motion))
        await asyncio.sleep_ms(30)


async def task_motion(motion, hub):
    while True:
        if motion.was_triggered():
            hub.report_motion()
        await asyncio.sleep_ms(50)


async def task_keepalive(hub, ip, led, fan, buzzer):
    while True:
        await asyncio.sleep_ms(config.UPDATE_INTERVAL_MS)
        resp = hub.keepalive(ip)
        if not resp:
            continue
        if resp.get("alarm"):
            buzzer.on()
        if resp.get("state_update"):
            new_state = hub.get_state()
            if new_state:
                _apply_state(new_state, led, fan, buzzer)


# ---------- entry ----------

async def _amain():
    # Built "safely" -- a missing/loose part becomes a warning + stub,
    # not a crash. Same as app_sync.
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

    ctx = {"menu": 0}

    asyncio.create_task(task_buttons(button_a, button_b, led, fan, buzzer, motion, hub, lcd, ctx))
    asyncio.create_task(task_motion(motion, hub))
    asyncio.create_task(task_keepalive(hub, ip, led, fan, buzzer))

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        hub.deregister()
        led.off()
        fan.off()
        buzzer.off()


def run():
    asyncio.run(_amain())
