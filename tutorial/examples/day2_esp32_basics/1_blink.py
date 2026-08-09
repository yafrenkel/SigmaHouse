"""Day 2 - Blink the LED.

The kit's LED is on GPIO 12. This turns it on and off once a second.

Run it in Thonny (F5) and watch the LED. Press Ctrl-C in the shell to stop.
"""

from machine import Pin
import time

led = Pin(12, Pin.OUT)

while True:
    led.value(1)      # 3.3V on the pin -> LED on
    time.sleep(0.5)
    led.value(0)      # 0V -> LED off
    time.sleep(0.5)
