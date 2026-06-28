"""Push button with internal pull-up. Active LOW.

The button uses an interrupt (IRQ) so we don't miss presses while the
main loop is busy. The IRQ handler just sets a flag; the main loop reads
the flag with was_pressed() which returns True ONCE per press.

DEBOUNCE: a real metal button "bounces" -- one physical press makes the
contacts open/close many times in a few milliseconds, so the IRQ can fire
a dozen times for a single push. We ignore any new edge that arrives
within DEBOUNCE_MS of the last accepted one, collapsing that burst into a
single clean press.
"""

from machine import Pin
from time import ticks_ms, ticks_diff

DEBOUNCE_MS = 250    # one press = one event; ignore repeat edges within this window


class Button:
    def __init__(self, pin_num):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._pressed = False
        self._last_ms = 0
        # FALLING = the moment the pin goes from 1 -> 0 (button pushed).
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_irq)

    def _on_irq(self, _pin):
        # Runs in interrupt context -- keep it tiny.
        # ticks_ms()/ticks_diff() are safe to call inside an IRQ.
        now = ticks_ms()
        if ticks_diff(now, self._last_ms) >= DEBOUNCE_MS:
            self._pressed = True
            self._last_ms = now

    def was_pressed(self):
        """Return True once per press, then reset the flag."""
        if self._pressed:
            self._pressed = False
            return True
        return False
