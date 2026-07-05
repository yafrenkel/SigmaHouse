"""Day 2 - Read a button with an INTERRUPT (IRQ).

Instead of constantly asking, the hardware tells us the MOMENT the pin
changes. IRQ_FALLING fires when the pin goes 1 -> 0 (the press).

One press = one message -- much better than polling. (You may occasionally
get 2-3 from contact "bounce"; that's real, and we fix it with debounce in
the full firmware's button.py.)

RULE OF INTERRUPTS: keep the handler tiny. We print here just for the demo,
but in real code the handler should only set a flag (see 4_button_led.py).

Press Ctrl-C to stop.
"""

from machine import Pin
import time

button = Pin(26, Pin.IN, Pin.PULL_UP)


def on_press(pin):
    print("Button pressed!")


button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)

# The main loop is now free -- the button is handled by the interrupt.
while True:
    time.sleep(1)
