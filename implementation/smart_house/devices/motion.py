"""PIR motion sensor.

The PIR pulls its pin HIGH when it detects motion. We use a rising-edge
interrupt to set a flag, just like the button. was_triggered() returns
True ONCE per detection event.
"""

from machine import Pin


class Motion:
    def __init__(self, pin_num):
        self._pin = Pin(pin_num, Pin.IN)
        self._triggered = False
        self._pin.irq(trigger=Pin.IRQ_RISING, handler=self._on_irq)

    def _on_irq(self, _pin):
        self._triggered = True

    def was_triggered(self):
        if self._triggered:
            self._triggered = False
            return True
        return False

    def is_active(self):
        """Current pin value -- True if motion is happening RIGHT NOW."""
        return self._pin.value() == 1

    def state(self):
        return {"detected": self.is_active()}
