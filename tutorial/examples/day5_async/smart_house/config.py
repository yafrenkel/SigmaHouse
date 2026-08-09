"""All tunable values for the smart house live here.

Pin numbers match the Keyestudio ESP32 Smart Home kit. If you wire
something differently, change the number, not the rest of the code.
"""

from secrets import WIFI_SSID, WIFI_PASS, HUB_URL  # noqa: F401  (re-exported)

# True  -> use the async firmware (app_async.py).
# False -> use the simple synchronous loop (app_sync.py). DEFAULT.
USE_ASYNC = False

# How often to send a keepalive to the hub.
UPDATE_INTERVAL_MS = 1000

# WiFi connection timeout.
WIFI_TIMEOUT_S = 10

# --- Day 5: sending a message FROM the house with button B ---
# Scroll button A past led/fan/buzzer to the message target, then press B.
# SEND_MODE picks how the recipient is chosen -- switch it and re-run:
#   "fixed"     -> always send to MESSAGE_TO           (simplest)
#   "broadcast" -> send to EVERY other house at once
#   "pick"      -> (YOUR EXERCISE) button A scrolls other houses' IDs; B sends
#                  to the selected one. It's stubbed in app_sync.py -- finish it!
SEND_MODE    = "fixed"
# Used by "fixed" mode. Paste a friend's full house ID -- copy it from their
# Thonny boot line ("My house ID: ...") or from the dashboard.
MESSAGE_TO   = "PASTE_FRIEND_ID_HERE"
# The canned message every mode sends (there's no keyboard on the board!).
MESSAGE_TEXT = "HELLO FROM MY HOUSE"

# --- GPIO pins ---
PIN_LED      = 12
PIN_BUTTON_A = 26
PIN_BUTTON_B = 25
PIN_PIR      = 13
PIN_FAN_A    = 18
PIN_FAN_B    = 19
PIN_BUZZER   = 4

# --- I2C bus (used by the LCD) ---
PIN_I2C_SCL  = 22
PIN_I2C_SDA  = 21
LCD_I2C_ADDR = 0x27
LCD_ROWS     = 2
LCD_COLS     = 16
