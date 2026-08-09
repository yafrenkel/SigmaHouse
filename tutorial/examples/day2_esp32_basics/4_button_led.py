"""Day 2 - Button toggles the LED (the pattern the real firmware uses).

Press Button A (GPIO 26) -> the LED (GPIO 12) flips on/off.

The interrupt does almost nothing -- it just sets a flag. The MAIN LOOP
reads the flag and does the real work (toggling the LED). This keeps the
interrupt tiny and safe, and it's exactly how devices/button.py works in
the full smart-house firmware.

Press Ctrl-C to stop.
"""

from machine import Pin
import time

led = Pin(12, Pin.OUT)
button = Pin(26, Pin.IN, Pin.PULL_UP)

pressed = False


def on_press(pin):
    global pressed
    pressed = True          # tiny! just raise a flag


button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)

while True:
    if pressed:
        pressed = False
        led.value(not led.value())               # the real work, in the loop
        print("LED ->", "on" if led.value() else "off")
    time.sleep_ms(50)
