"""Day 4 - Read the PIR motion sensor on its own (no WiFi, no hub).

The PIR is on GPIO 13. It pulls the pin HIGH when it detects an infrared
(heat) change -- i.e. movement. Wave your hand and watch the shell.

Things to know about PIRs (they surprise everyone):
  - They need ~30-60 seconds to "warm up" after power-on. Ignore early triggers.
  - They see ANY heat change -- warm air, sunlight, people/pets nearby -- not
    just you. So occasional triggers with no movement are normal.
  - The little LED on the PIR module may be wired OPPOSITE to "motion". Trust
    THIS readout, not the module's light.
  - Two orange screws on the back tune sensitivity and hold-time. Turn
    sensitivity down (counter-clockwise) if it triggers too easily.

Press Ctrl-C to stop.
"""

from machine import Pin
import time

pir = Pin(13, Pin.IN)

print("PIR ready. Wave your hand...")

while True:
    if pir.value() == 1:
        print("Motion!")
    time.sleep(0.2)
