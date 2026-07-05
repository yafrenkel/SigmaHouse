"""Day 2 - Read a button by POLLING (asking over and over).

Button A is on GPIO 26. It's wired active-LOW with a pull-up resistor:
  not pressed -> reads 1
  pressed     -> reads 0

This loop checks the button 10x a second. Hold the button and you'll get a
flood of "Pressed!" -- because one press covers many loops. That's exactly
why the next example switches to interrupts.

Press Ctrl-C to stop.
"""

from machine import Pin
import time

button = Pin(26, Pin.IN, Pin.PULL_UP)

while True:
    if button.value() == 0:
        print("Pressed!")
    time.sleep(0.1)
