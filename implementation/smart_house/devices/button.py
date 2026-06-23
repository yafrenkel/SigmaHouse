"""Push button with internal pull-up. Active LOW.

The button uses an interrupt (IRQ) so we don't miss presses while the
main loop is busy. The IRQ handler just sets a flag; the main loop reads
the flag with was_pressed() which returns True ONCE per press.
"""

from machine import Pin


class Button:
    def __init__(self, pin_num):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._pressed = False
        # FALLING = the moment the pin goes from 1 -> 0 (button pushed).
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_irq)

    def _on_irq(self, _pin):
        # Keep this short -- it runs in interrupt context.
        self._pressed = True

    def was_pressed(self):
        """Return True once per press, then reset the flag."""
        if self._pressed:
            self._pressed = False
            return True
        return False
