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

DEVICES = ("led", "fan", "buzzer")

# Filled in by run(), and left as module globals ON PURPOSE. After you press
# Ctrl-C to stop the loop, you can still reach your house from the REPL to
# send a message to a friend:
#   >>> import app_sync
#   >>> app_sync.hub.send_message("FRIENDS_ID", "hello from my house!")
# Then Ctrl-D to restart the firmware.
hub = None
uid = None


# ---------- helpers ----------

def _show_messages(hub, lcd, buzzer):
    """Fetch our mailbox and PRINT every message to the Thonny console.

    The console print is the main event (works on every board). The LCD line
    and the little beep are optional extras -- delete them if you don't have
    an LCD/buzzer wired.
    """
    data = hub.get_messages()
    if not data:
        return
    msgs = data.get("messages", [])
    for m in msgs:
        print(">>> MESSAGE from", m["from"], ":", m["text"])
    if msgs:                                  # optional: show newest on the LCD + beep
        latest = msgs[-1]
        lcd.show("Msg " + latest["from"][-6:], latest["text"][:16])
        buzzer.beep(60)


def _build_menu(hub, uid):
    """The list button A scrolls through: the 3 devices, then the message target.

    In "fixed"/"broadcast" mode that target is a single "msg" entry.
    In "pick" mode it should be the list of OTHER houses -- YOUR EXERCISE below.
    """
    if config.SEND_MODE == "pick":
        # ===== EXERCISE (part 1 of 2): build the recipient list =====
        # Goal: let button A scroll through the OTHER houses so you can choose
        # who to message. Right now it returns only the devices, so there's
        # nobody to send to yet -- add the houses.
        #
        # HINTS:
        #   1. hub.get_houses() gives a LIST of house dicts (or None on error).
        #      Guard it:  houses = hub.get_houses() or []
        #   2. Each dict has h["unique_id"].
        #   3. Skip your OWN house:   h["unique_id"] != uid
        #   4. Return  list(DEVICES) + <the other houses' ids>
        #
        # TODO: replace the line below with the real list.
        return list(DEVICES)                      # <-- no houses yet!
    return list(DEVICES) + ["msg"]


def _send_from_button(hub, uid, selected, lcd):
    """Button B was pressed on a non-device entry -> send a message.

    Three interchangeable styles, chosen by config.SEND_MODE. This is the
    piece a camper can rewrite as an exercise.
    """
    text = config.MESSAGE_TEXT
    if config.SEND_MODE == "fixed":
        # --- simplest: always the one friend in config.MESSAGE_TO ---
        result = hub.send_message(config.MESSAGE_TO, text)
        print("Button B -> sent to", config.MESSAGE_TO, ":", result)
        lcd.show("Sent to", config.MESSAGE_TO)
    elif config.SEND_MODE == "broadcast":
        # --- everyone at once: fetch the roster, message each house ---
        others = [h["unique_id"] for h in (hub.get_houses() or [])
                  if h["unique_id"] != uid]
        for to in others:
            hub.send_message(to, text)
        print("Button B -> broadcast to", len(others), "houses:", text)
        lcd.show("Broadcast!", str(len(others)) + " houses")
    elif config.SEND_MODE == "pick":
        # ===== EXERCISE (part 2 of 2): send to the chosen house =====
        # Once part 1 adds house IDs to the menu, `selected` will be the house
        # ID button A landed on. Send the message to it.
        #
        # HINTS:
        #   * hub.send_message(<to_id>, text) does the send (returns {'ok': True}).
        #   * The "fixed" branch above is almost identical -- the only change is
        #     the recipient is `selected` instead of config.MESSAGE_TO.
        #   * Print and lcd.show() like the other modes so you get feedback.
        #
        # TODO: send `text` to `selected`.
        print("pick mode isn't built yet -- that's your exercise! selected =", selected)


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

    global hub, uid          # module globals so the REPL can send after Ctrl-C
    ip = _connect_wifi(lcd)
    uid = ubinascii.hexlify(unique_id()).decode().upper()
    hub = HubClient(config.HUB_URL, uid)
    hub.register(ip)
    print("My house ID:", uid, " -- give this to a friend so they can message you!")
    lcd.show("Ready " + uid[-6:], ip)

    menu = _build_menu(hub, uid)      # button A scrolls this
    menu_index = 0
    last_keepalive = time.ticks_ms()
    last_roster = time.ticks_ms()

    try:
        while True:
            # --- button A: scroll the menu (devices, then the message target) ---
            if button_a.was_pressed():
                menu_index = (menu_index + 1) % len(menu)
                print("Button A -> selected:", menu[menu_index])
                lcd.show("Select:", menu[menu_index])

            # --- button B: toggle a device, OR send a message ---
            if button_b.was_pressed():
                selected = menu[menu_index]
                if selected in DEVICES:
                    _toggle(selected, led, fan, buzzer)
                    print("Button B -> toggled:", selected)
                    hub.push_state(_build_state(led, fan, buzzer, motion))
                else:
                    _send_from_button(hub, uid, selected, lcd)

            # --- motion -> tell the hub ---
            if motion.was_triggered():
                hub.report_motion()

            # --- refresh the menu every few seconds ---
            # In "pick" mode this pulls the current list of houses (so newly
            # arrived houses appear and Lost ones drop off). In the other modes
            # it's a cheap no-op that just re-adds the "msg" entry.
            if time.ticks_diff(time.ticks_ms(), last_roster) >= 3000:
                last_roster = time.ticks_ms()
                menu = _build_menu(hub, uid)
                if menu_index >= len(menu):    # list shrank -> stay in bounds
                    menu_index = 0

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
                    if resp.get("message"):
                        _show_messages(hub, lcd, buzzer)

            time.sleep_ms(50)
    finally:
        hub.deregister()
        led.off()
        fan.off()
        buzzer.off()
